import json
import os
from PyQt6.QtCore import QThread, pyqtSignal
from .llm_client import LLMClient
from .tool_registry import ToolRegistry
from .workflow_manager import WorkflowManager
from automation.action_controller import ActionController

class AgentManager(QThread):
    """
    A deep module that orchestrates the conversational loop.
    Owns the history, communicates with the LLM, and executes actions.
    """
    chunk = pyqtSignal(str)
    history_updated = pyqtSignal(list)
    finished_ok = pyqtSignal()
    failed = pyqtSignal(str)
    status_update = pyqtSignal(str)

    def __init__(self, action_controller: ActionController):
        super().__init__()
        self.history = []
        self.is_cancelled = False
        self.client = LLMClient()
        self.action_controller = action_controller
        self.tool_registry = ToolRegistry()
        self.workflow = WorkflowManager()
        self._new_prompt = None # temporary hold for the latest user prompt

    def process_input(self, text: str):
        import re
        import os
        
        text_lower = text.lower().strip().rstrip(".!")
        # Make "workflow" or "workflows" optional at the end
        nl_match = re.search(r"^(?:start|run|execute) (?:the )?([\w\s-]+?)(?:\s+workflows?)?$", text_lower)
        
        workflow_path = None
        additional_prompt = ""
        if text.startswith("/"):
            parts = text[1:].strip().split(maxsplit=1)
            workflow_name = parts[0]
            if len(parts) > 1:
                additional_prompt = parts[1]
            if not workflow_name.endswith(".md"):
                workflow_name += ".md"
            # Using raw string for windows path to prevent escape character issues
            workflow_path = os.path.join(".agents\\context\\workflows", workflow_name)
        elif nl_match:
            base_name = nl_match.group(1).strip().replace(" ", "-")
            candidates = [
                f"{base_name}.md",
                f"{base_name}-workflow.md",
                f"{base_name}-workflows.md"
            ]
            for candidate in candidates:
                test_path = os.path.join(".agents\\context\\workflows", candidate)
                if os.path.exists(test_path):
                    workflow_path = test_path
                    break
                    
        # If triggered via slash command OR we successfully found a natural language match file
        if workflow_path and (text.startswith("/") or os.path.exists(workflow_path)):
            result = self.workflow.load_workflow(workflow_path)
            
            self.history.append({"role": "user", "content": text})
            if result.get("success"):
                self.status_update.emit("Workflow")
                prompt_content = result["prompt"]
                if additional_prompt:
                    prompt_content += f"\n\nAdditional Instructions from User:\n{additional_prompt}"
                self.history.append({"role": "user", "content": prompt_content, "hide_in_ui": True})
            else:
                self.history.append({"role": "assistant", "content": result.get("error", "Error loading workflow")})
            
            self.history_updated.emit(self.history)
            self._new_prompt = True
            return
            
        self.history.append({"role": "user", "content": text})
        self._new_prompt = True

    def clear_history(self):
        self.history.clear()
        self.workflow.clear()
        self.history_updated.emit(self.history)

    def advance_workflow(self):
        result = self.workflow.advance_workflow()
        self.history.append({
            "role": "user", 
            "content": result["prompt"],
            "hide_in_ui": True
        })
        if result.get("is_complete"):
            self.status_update.emit("")
        self.history_updated.emit(self.history)

    def run(self):
        if not self.client.is_configured():
            if not self.is_cancelled:
                self.failed.emit("No GEMINI_API_KEY set in .env")
            return
            
        system_additions = self.action_controller.get_system_prompt_additions()
        
        tools = self.tool_registry.get_all_schemas()
        
        system_content = (
            "You are a highly advanced, polite, and efficient AI assistant named Notch. "
            "Speak in a crisp, professional, British butler style. Address the user as 'Sir'. "
            "To sound more human and conversational, occasionally use natural filler words (like 'umm', 'ah', 'well') and add short pauses using ellipses ('...'). "
            "Keep your verbal responses relatively concise but extremely helpful. Inject a bit of dry, sarcastic British humor into your responses when appropriate. "
            "Use the execute_actions tool to batch and automate desktop tasks. "
            "They will be executed sequentially and you will receive a structured result for the batch."
            "Before using execute_actions on a specific application, you MUST call the get_app_instructions tool to learn its specific keyboard shortcuts and quirks. If no instructions are found,\n\n"
            + system_additions
        )

        consecutive_failures = 0
        while not self.is_cancelled:
            if not self.history or self.history[-1]["role"] == "assistant":
                break # We wait for user input or tool execution

            messages = [{"role": "system", "content": system_content}] + self.history
            
            clean_messages = []
            for m in messages:
                clean_m = {k: v for k, v in m.items() if k != "hide_in_ui"}
                clean_messages.append(clean_m)

            try:
                tool_calls_accumulator = {}
                self.history.append({"role": "assistant", "content": ""})
                self.history_updated.emit(self.history)
                
                for content_chunk, current_tool_calls in self.client.stream_chat(clean_messages, tools, lambda: self.is_cancelled):
                    if self.is_cancelled:
                        break
                    if content_chunk:
                        self.history[-1]["content"] += content_chunk
                        self.chunk.emit(content_chunk)
                    if current_tool_calls:
                        tool_calls_accumulator.update(current_tool_calls)

                if self.is_cancelled:
                    break
                    
                if tool_calls_accumulator:
                    parsed_calls = []
                    for idx, tc in sorted(tool_calls_accumulator.items()):
                        try:
                            parsed_calls.append({
                                "id": tc["id"],
                                "type": "function",
                                "function": {
                                    "name": tc["name"],
                                    "arguments": tc["arguments"] if tc["arguments"] else "{}"
                                }
                            })
                        except Exception:
                            pass
                            
                    if parsed_calls:
                        self.history[-1]["tool_calls"] = parsed_calls
                        self.history_updated.emit(self.history)
                        
                        # Execute all tool calls
                        for call in parsed_calls:
                            if self.is_cancelled:
                                break
                            fn = call.get("function", {})
                            name = fn.get("name", "")
                            try:
                                args = json.loads(fn.get("arguments", "{}"))
                            except json.JSONDecodeError:
                                args = {}
                                
                            result_content = self.tool_registry.execute_tool(name, self, **args)
                                
                            self.history.append({
                                "role": "tool",
                                "content": result_content,
                                "tool_call_id": call["id"],
                                "name": name,
                            })
                            self.history_updated.emit(self.history)
                            
                            # Parse result_content to track failures
                            is_failure = False
                            try:
                                res_json = json.loads(result_content)
                                if isinstance(res_json, list):
                                    if any(item.get("success") is False for item in res_json if isinstance(item, dict)):
                                        is_failure = True
                                elif isinstance(res_json, dict):
                                    if res_json.get("success") is False:
                                        is_failure = True
                            except Exception:
                                pass
                                
                            if is_failure:
                                consecutive_failures += 1
                            else:
                                consecutive_failures = 0
                        
                        if consecutive_failures >= 3:
                            if not self.is_cancelled:
                                self.failed.emit("Agent automatically stopped to prevent API rate limits due to 3 consecutive tool failures.")
                            break
                        
                        # Continue the loop
                        continue
                        
                # If no tool calls, we are done with this step
                self.finished_ok.emit()
                break

            except Exception as e:
                if not self.is_cancelled:
                    self.failed.emit(str(e))
                break
