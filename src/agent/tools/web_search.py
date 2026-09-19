from .base import BaseTool

class WebSearchToolClass(BaseTool):
    @property
    def name(self) -> str:
        return "web_search"
        
    def get_schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
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
        }

    def execute(self, context, **kwargs) -> str:
        query = kwargs.get("query", "")
        # context is AgentManager, which has self.web_search
        return context.web_search.search(query)
