import os
from .base import BaseTool

class GetAppInstructionsTool(BaseTool):
    @property
    def name(self) -> str:
        return "get_app_instructions"
        
    def get_schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": "Get specific keyboard shortcuts and automation quirks for a target app before executing actions.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "app_name": {"type": "string", "description": "The name of the app (e.g. 'Antigravity', 'Chrome')."}
                    },
                    "required": ["app_name"]
                }
            }
        }

    def execute(self, context, **kwargs) -> str:
        app_name = kwargs.get("app_name", "")
        file_path = os.path.join(".agents", "context", "apps", f"{app_name}.md")
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                return f"Error reading instructions: {e}"
        else:
            return f"No specific instructions found for {app_name}. Rely on web_search or general knowledge."
