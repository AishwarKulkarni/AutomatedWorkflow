import os
from .base import BaseTool

class ReadContextFileTool(BaseTool):
    @property
    def name(self) -> str:
        return "read_context_file"
        
    def get_schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": "Read the contents of a system context file such as 'ahk_manifest.md' or 'llm_guidelines.md'.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {"type": "string", "description": "The name of the file to read (e.g. 'llm_guidelines.md')."}
                    },
                    "required": ["filename"]
                }
            }
        }

    def execute(self, context, **kwargs) -> str:
        filename = kwargs.get("filename", "")
        # Prevent path traversal
        filename = os.path.basename(filename)
        file_path = os.path.join(".agents", "context", filename)
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                return f"Error reading context file: {e}"
        else:
            return f"Context file '{filename}' not found."
