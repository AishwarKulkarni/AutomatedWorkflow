from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseTool(ABC):
    """
    Abstract base class for all agent tools.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the tool as it appears to the LLM."""
        pass
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """
        Return the JSON schema dictionary for this tool.
        """
        pass
    
    @abstractmethod
    def execute(self, context: Any, **kwargs) -> str:
        """
        Execute the tool.
        
        :param context: The AgentManager instance (or a Context object) containing dependencies.
        :param kwargs: The arguments provided by the LLM.
        :return: A string representation of the result (e.g., JSON string or text).
        """
        pass
