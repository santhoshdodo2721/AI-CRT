from abc import ABC, abstractmethod
from typing import List, Dict, Any

class ToolResult:
    def __init__(self, raw_output: str, parsed_data: Dict[str, Any], status: str = "completed", error: str = None):
        self.raw_output = raw_output
        self.parsed_data = parsed_data
        self.status = status
        self.error = error

class BaseTool(ABC):
    name: str = "base_tool"
    description: str = "Base description"
    mitre_techniques: List[str] = []
    required_ports: List[int] = []
    category: str = "generic"
    
    @abstractmethod
    def build_command(self, params: Dict[str, Any]) -> str:
        """Returns the command string to be executed by the agent."""
        pass
        
    @abstractmethod
    def parse_output(self, raw_output: str) -> Dict[str, Any]:
        """Parses the raw stdout/stderr from the tool into a structured JSON dict."""
        pass
