import os
import importlib
import inspect
from typing import Dict, List, Any
from .tools.base import BaseTool

class ToolRegistry:
    def __init__(self, tools_package: str = "agent.tools"):
        self.tools_package = tools_package
        self.tools: Dict[str, BaseTool] = {}
        self.load_tools()

    def load_tools(self):
        """Dynamically discover and load all tools in the tools_package."""
        self.tools.clear()
        
        # Get the directory path for the tools package
        current_dir = os.path.dirname(os.path.abspath(__file__))
        tools_dir = os.path.join(current_dir, "tools")
        
        if not os.path.exists(tools_dir):
            return

        for filename in os.listdir(tools_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]
                full_module_name = f"{self.tools_package}.{module_name}"
                
                try:
                    module = importlib.import_module(full_module_name)
                    for name, obj in inspect.getmembers(module):
                        if inspect.isclass(obj) and issubclass(obj, BaseTool) and obj is not BaseTool:
                            tool_instance = obj()
                            self.tools[tool_instance.name] = tool_instance
                except Exception as e:
                    print(f"Failed to load tool from {filename}: {e}")

    def get_all_schemas(self) -> List[Dict[str, Any]]:
        """Return a list of JSON schemas for all registered tools."""
        return [tool.get_schema() for tool in self.tools.values()]

    def execute_tool(self, name: str, context: Any, **kwargs) -> str:
        """Execute a tool by name."""
        tool = self.tools.get(name)
        if not tool:
            import json
            return json.dumps({"success": False, "error": f"Unknown tool: {name}"})
        
        try:
            return tool.execute(context, **kwargs)
        except Exception as e:
            import json
            return json.dumps({"success": False, "error": f"Error executing {name}: {str(e)}"})
