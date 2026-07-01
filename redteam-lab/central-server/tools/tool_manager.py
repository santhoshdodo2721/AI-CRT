import logging
from typing import List, Dict, Type
from .base import BaseTool

logger = logging.getLogger("tools.manager")

class ToolManager:
    _registry: Dict[str, Type[BaseTool]] = {}
    
    @classmethod
    def register(cls, tool_class: Type[BaseTool]):
        cls._registry[tool_class.name] = tool_class
        logger.info(f"Registered tool: {tool_class.name}")
        
    @classmethod
    def get_tool(cls, name: str) -> BaseTool:
        tool_cls = cls._registry.get(name)
        if not tool_cls:
            raise ValueError(f"Tool {name} not found in registry")
        return tool_cls()
        
    @classmethod
    def get_all_tools(cls) -> List[dict]:
        return [
            {
                "name": name,
                "description": tool.description,
                "category": tool.category,
                "mitre_techniques": tool.mitre_techniques
            }
            for name, tool in cls._registry.items()
        ]
