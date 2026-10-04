import json
from .base import BaseTool

class MarkTaskCompletedTool(BaseTool):
    @property
    def name(self) -> str:
        return "mark_task_completed"
        
    def get_schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": "Call this tool when you have successfully completed all parts of the current assigned task in a workflow. This signals the system to move to the next task.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "success": {
                            "type": "boolean",
                            "description": "Whether the task was completed successfully."
                        },
                        "notes": {
                            "type": "string",
                            "description": "Any brief notes, results, or context to remember for the next steps."
                        }
                    },
                    "required": ["success", "notes"]
                }
            }
        }
        
    def execute(self, context, **kwargs) -> str:
        success = kwargs.get("success", True)
        notes = kwargs.get("notes", "")
        
        try:
            context.advance_workflow()
            return json.dumps({
                "status": "Task marked as completed",
                "success": success,
                "notes": notes
            })
        except AttributeError:
            return json.dumps({
                "success": False,
                "error": "Cannot advance workflow: context is missing advance_workflow method."
            })
