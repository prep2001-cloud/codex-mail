"""
Connexx Agent - Dispatch Agent (调度中枢)
Routes tasks to appropriate specialized agents
"""

from typing import Dict, Any, List
from .base import BaseAgent
from ..core.logger import get_logger

logger = get_logger(__name__)


class ConnexxAgent(BaseAgent):
    """
    Connexx - Dispatch Agent

    Responsibilities:
    - User interaction entry point
    - Intent recognition
    - Task routing to specialized agents
    - Result aggregation
    """

    def __init__(self):
        super().__init__(
            agent_id="connexx",
            role="Dispatch Agent",
            description="Routes user requests to appropriate specialized agents"
        )

    async def perceive(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Understand user input

        Args:
            input_data: User request

        Returns:
            Processed input with intent
        """
        logger.info(f"[Connexx] Perceiving user input")

        return {
            "user_input": input_data.get("user_input", ""),
            "context": input_data.get("context", {}),
            "timestamp": input_data.get("timestamp")
        }

    async def plan(self, perception: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Plan task routing

        Args:
            perception: Processed perception

        Returns:
            Routing plan
        """
        steps = [
            {
                "action": "recognize_intent",
                "description": "Recognize user intent from input"
            },
            {
                "action": "route_to_agent",
                "description": "Route to specialized agent"
            },
            {
                "action": "aggregate_results",
                "description": "Aggregate and format results"
            }
        ]

        return steps

    async def execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute routing step

        Args:
            step: Step to execute

        Returns:
            Step result
        """
        action = step.get("action")

        if action == "recognize_intent":
            # Intent recognition logic
            return {
                "intent": "data_analysis",
                "confidence": 0.9
            }

        elif action == "route_to_agent":
            # Route to appropriate agent
            return {
                "target_agent": "annexx",
                "routed": True
            }

        elif action == "aggregate_results":
            # Aggregate results from specialists
            return {
                "aggregated": True,
                "formatted_response": "Results aggregated successfully"
            }

        return {"action": action, "completed": True}
