import json
from PyQt6.QtCore import QThread, pyqtSignal
from .llm_client import LLMClient
from .web_search import WebSearchTool
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

    def __init__(self, action_controller: ActionController):
        super().__init__()
        self.history = []
        self.is_cancelled = False
        self.client = LLMClient()
        self.action_controller = action_controller
        self.web_search = WebSearchTool()
        self._new_prompt = None # temporary hold for the latest user prompt

    def add_user_message(self, text: str):
        self.history.append({"role": "user", "content": text})
        self._new_prompt = True

    def clear_history(self):
        self.history.clear()
        self.history_updated.emit(self.history)

    def run(self):
        if not self.client.is_configured():
            if not self.is_cancelled:
                self.failed.emit("No GROQ_API_KEY set in .env")
            return
            
        system_additions = self.action_controller.get_system_prompt_additions()
        
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "execute_actions",
                    "description": (
                        "Execute an array of desktop automation actions sequentially. "
                        "They will be executed in order, and you will receive a structured result "
                        "containing the outcomes. Call this tool to batch your actions."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "actions": {
                                "type": "array",
                                "description": "An array of actions to execute sequentially.",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "action_name": {
                                            "type": "string",
                                            "description": "Name of the action to execute.",
                                        },
                                        "args": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                            "description": "Positional arguments for the action.",
                                        },
                                        "target_app": {
                                            "type": "string",
                                            "description": "Optional app variable name (e.g. 'App_Notepad').",
                                        },
                                    },
                                    "required": ["action_name", "args"],
                                },
                            },
                        },
                        "required": ["actions"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "web_search",
                    "description": (
                        "Search the web for information about app-specific shortcuts, "
                        "UI workflows, or any task you are uncertain about. "
                        "Use this before executing an action if you don't know the exact steps."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query."
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
        ]
        
        system_content = (
            "You are a helpful desktop automation assistant. "
            "Use the execute_actions tool to batch and automate desktop tasks. "
            "They will be executed sequentially and you will receive a structured result for the batch. "
            "If you are uncertain about the exact keyboard shortcut, menu path, or steps to perform "
            "a task in a specific application, call the web_search tool first to look it up, "
            "then proceed with execute_actions.\n\n"
            + system_additions
        )

        while not self.is_cancelled:
            if not self.history or self.history[-1]["role"] == "assistant":
                break # We wait for user input or tool execution

            messages = [{"role": "system", "content": system_content}] + self.history

            try:
                tool_calls_accumulator = {}
                self.history.append({"role": "assistant", "content": ""})
                self.history_updated.emit(self.history)
                
                for content_chunk, current_tool_calls in self.client.stream_chat(messages, tools, lambda: self.is_cancelled):
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
                                
                            if name == "execute_actions":
                                actions = args.get("actions", [])
                                batch_results = []
                                for action in actions:
                                    a_name = action.get("action_name", "")
                                    a_args = action.get("args", [])
                                    a_app = action.get("target_app")
                                    res = self.action_controller.execute_action(a_name, a_args, a_app)
                                    batch_results.append(res)
                                    if not res.get("success", False):
                                        break
                                result_content = json.dumps(batch_results)
                            elif name == "web_search":
                                query = args.get("query", "")
                                result_content = self.web_search.search(query)
                            else:
                                result_content = json.dumps({"success": False, "error": f"Unknown tool: {name}"})
                                
                            self.history.append({
                                "role": "tool",
                                "content": result_content,
                                "tool_call_id": call["id"],
                                "name": name,
                            })
                            self.history_updated.emit(self.history)
                        
                        # Continue the loop
                        continue
                        
                # If no tool calls, we are done with this step
                self.finished_ok.emit()
                break

            except Exception as e:
                if not self.is_cancelled:
                    self.failed.emit(str(e))
                break
