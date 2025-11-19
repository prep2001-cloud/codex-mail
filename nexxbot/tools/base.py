"""
Base classes for tools
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from ..core.logger import get_logger

logger = get_logger(__name__)


class ToolInput(BaseModel):
    """Base input model for tools"""
    pass


class ToolOutput(BaseModel):
    """Base output model for tools"""
    success: bool
    result: Any
    error: Optional[str] = None


class Tool(ABC):
    """
    Base class for all tools

    Tools are atomic operations that agents can perform
    """

    def __init__(self):
        self.name = self.__class__.__name__
        self.description = self.__doc__ or "No description"
        self.call_count = 0

    @abstractmethod
    async def execute(self, **kwargs) -> ToolOutput:
        """
        Execute the tool

        Args:
            **kwargs: Tool-specific parameters

        Returns:
            ToolOutput with result
        """
        pass

    async def __call__(self, **kwargs) -> ToolOutput:
        """Make tool callable"""
        self.call_count += 1
        logger.info(f"Executing tool: {self.name} (call #{self.call_count})")
        try:
            result = await self.execute(**kwargs)
            logger.debug(f"Tool {self.name} succeeded")
            return result
        except Exception as e:
            logger.error(f"Tool {self.name} failed: {str(e)}")
            return ToolOutput(
                success=False,
                result=None,
                error=str(e)
            )

    def get_schema(self) -> Dict[str, Any]:
        """Get tool schema for LLM function calling"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": self._get_parameters(),
                "required": self._get_required_params()
            }
        }

    @abstractmethod
    def _get_parameters(self) -> Dict[str, Any]:
        """Define tool parameters"""
        pass

    def _get_required_params(self) -> List[str]:
        """Define required parameters"""
        return []


class ToolRegistry:
    """
    Registry for managing available tools

    Agents use this to discover and access tools
    """

    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        logger.info("ToolRegistry initialized")

    def register(self, tool: Tool):
        """
        Register a new tool

        Args:
            tool: Tool instance to register
        """
        self.tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")

    def get(self, name: str) -> Optional[Tool]:
        """
        Get tool by name

        Args:
            name: Tool name

        Returns:
            Tool instance or None
        """
        return self.tools.get(name)

    def get_all(self) -> Dict[str, Tool]:
        """Get all registered tools"""
        return self.tools

    def get_schemas(self) -> List[Dict[str, Any]]:
        """Get schemas for all tools (for LLM function calling)"""
        return [tool.get_schema() for tool in self.tools.values()]

    def list_tools(self) -> List[str]:
        """List all tool names"""
        return list(self.tools.keys())
