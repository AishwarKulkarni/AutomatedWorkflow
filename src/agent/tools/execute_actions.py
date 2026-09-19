import json
from .base import BaseTool

class ExecuteActionsTool(BaseTool):
    @property
    def name(self) -> str:
        return "execute_actions"
        
    def get_schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
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
        }

    def execute(self, context, **kwargs) -> str:
        actions = kwargs.get("actions", [])
        batch_results = []
        for action in actions:
            a_name = action.get("action_name", "")
            a_args = action.get("args", [])
            a_app = action.get("target_app")
            # context is AgentManager, which has action_controller
            res = context.action_controller.execute_action(a_name, a_args, a_app)
            batch_results.append(res)
            if not res.get("success", False):
                break
        return json.dumps(batch_results)
