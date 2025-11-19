"""
Annexx Agent - Data Analyst Agent (数据分析师)
Handles data analysis, BI, metrics calculation, and anomaly detection
"""

from typing import Dict, Any, List
from .base import BaseAgent
from ..tools.data_tools import QueryDatabaseTool, GenerateChartTool, CalculateMetricsTool
from ..tools.base import ToolRegistry
from ..core.logger import get_logger

logger = get_logger(__name__)


class AnnexxAgent(BaseAgent):
    """
    Annexx - Data Analyst Agent

    Responsibilities:
    - SQL query generation
    - Data visualization
    - Statistical analysis
    - Anomaly detection
    - Root cause analysis
    """

    def __init__(self):
        # Initialize tools
        tools = ToolRegistry()
        tools.register(QueryDatabaseTool())
        tools.register(GenerateChartTool())
        tools.register(CalculateMetricsTool())

        super().__init__(
            agent_id="annexx",
            role="Data Analyst Agent",
            description="Performs data analysis, visualization, and provides insights",
            tools=tools
        )

    async def perceive(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Understand analytical request

        Args:
            input_data: Analysis request

        Returns:
            Processed analysis requirements
        """
        logger.info(f"[Annexx] Analyzing request")

        return {
            "query": input_data.get("user_input", ""),
            "context": input_data.get("context", {}),
            "analysis_type": input_data.get("analysis_type", "general")
        }

    async def plan(self, perception: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Plan data analysis workflow

        Args:
            perception: Analysis requirements

        Returns:
            Analysis plan
        """
        steps = [
            {
                "action": "query_data",
                "tool": "QueryDatabaseTool",
                "description": "Query warehouse database for relevant data"
            },
            {
                "action": "calculate_metrics",
                "tool": "CalculateMetricsTool",
                "description": "Calculate statistics and detect anomalies"
            },
            {
                "action": "generate_visualization",
                "tool": "GenerateChartTool",
                "description": "Generate visual charts"
            },
            {
                "action": "reason_about_findings",
                "description": "Analyze results and provide insights"
            }
        ]

        return steps

    async def execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute analysis step

        Args:
            step: Analysis step

        Returns:
            Step result with data/insights
        """
        action = step.get("action")
        tool_name = step.get("tool")

        logger.info(f"[Annexx] Executing: {action}")

        if tool_name:
            tool = self.tools.get(tool_name)
            if tool:
                if tool_name == "QueryDatabaseTool":
                    result = await tool(
                        query="SELECT * FROM shuttle_energy WHERE month = 'current'"
                    )
                elif tool_name == "CalculateMetricsTool":
                    # Get mock data for calculation
                    query_tool = self.tools.get("QueryDatabaseTool")
                    data_result = await query_tool(query="SELECT * FROM shuttle_energy")

                    result = await tool(
                        data=data_result.result["data"],
                        metric_column="energy_kwh",
                        group_by="floor"
                    )
                elif tool_name == "GenerateChartTool":
                    # Get data first
                    query_tool = self.tools.get("QueryDatabaseTool")
                    data_result = await query_tool(query="SELECT * FROM shuttle_energy")

                    result = await tool(
                        data=data_result.result["data"],
                        chart_type="bar",
                        title="Energy Consumption by Floor",
                        x_column="floor",
                        y_column="energy_kwh"
                    )
                else:
                    result = await tool()

                return result.result if hasattr(result, 'result') else result

        # Reasoning step
        if action == "reason_about_findings":
            # Use LLM to analyze findings
            reasoning = await self.reason(
                observation="Found anomalies in shuttles 1704 and 2921",
                goal="Identify root cause of high energy consumption"
            )

            return {
                "insights": reasoning["analysis"],
                "recommendations": [
                    "Replace batteries on shuttles 1704 and 2921",
                    "Implement eco-routing algorithm",
                    "Redistribute inventory from floor 6 to floors 4 and 7"
                ]
            }

        return {"action": action, "completed": True}
