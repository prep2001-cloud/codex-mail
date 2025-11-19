"""
Salexx Agent - Sales Agent (销售顾问)
Handles customer inquiries, quotes, and sales support
"""

from typing import Dict, Any, List
from .base import BaseAgent
from ..tools.wms_tools import GetWarehouseInfoTool
from ..tools.base import ToolRegistry
from ..core.logger import get_logger

logger = get_logger(__name__)


class SalexxAgent(BaseAgent):
    """
    Salexx - Sales & Customer Service Agent

    Responsibilities:
    - Customer inquiries (RAG-based)
    - Pricing and quotes
    - Service recommendations
    - 24/7 customer support
    """

    def __init__(self, vector_store=None):
        # Initialize tools
        tools = ToolRegistry()
        tools.register(GetWarehouseInfoTool())

        super().__init__(
            agent_id="salexx",
            role="Sales Agent",
            description="Provides customer support, quotes, and sales assistance",
            tools=tools
        )

        self.vector_store = vector_store  # For RAG

    async def perceive(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Understand customer inquiry

        Args:
            input_data: Customer question/request

        Returns:
            Processed inquiry context
        """
        logger.info(f"[Salexx] Processing customer inquiry")

        return {
            "customer_query": input_data.get("user_input", ""),
            "customer_id": input_data.get("customer_id"),
            "channel": input_data.get("channel", "whatsapp"),
            "context": input_data.get("context", {})
        }

    async def plan(self, perception: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Plan customer interaction

        Args:
            perception: Customer context

        Returns:
            Interaction plan
        """
        steps = [
            {
                "action": "retrieve_knowledge",
                "description": "Search knowledge base (RAG)"
            },
            {
                "action": "get_warehouse_info",
                "tool": "GetWarehouseInfoTool",
                "description": "Get warehouse details"
            },
            {
                "action": "calculate_quote",
                "description": "Calculate pricing if needed"
            },
            {
                "action": "generate_response",
                "description": "Generate customer response"
            }
        ]

        return steps

    async def execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute customer service step

        Args:
            step: Service step

        Returns:
            Step result
        """
        action = step.get("action")
        tool_name = step.get("tool")

        logger.info(f"[Salexx] Executing: {action}")

        if action == "retrieve_knowledge":
            # RAG retrieval
            if self.vector_store:
                results = self.vector_store.search_knowledge(
                    query="food storage temperature control",
                    n_results=3
                )
                return {"knowledge": results}
            else:
                return {"knowledge": "Mock knowledge base data"}

        elif tool_name == "GetWarehouseInfoTool":
            tool = self.tools.get(tool_name)
            result = await tool(warehouse_id="WH001")
            return result.result if hasattr(result, 'result') else result

        elif action == "calculate_quote":
            return {
                "quote": {
                    "labeling": 0.71,  # QAR per piece
                    "sorting": "Variable",
                    "storage": "Contact for details"
                }
            }

        elif action == "generate_response":
            # Generate natural language response
            response = """您好！

我们推荐 Milaha Logistics City 仓库，非常适合食品存储：

🌡️ **温控服务**：
- 冷冻: -22°C
- 冷藏: +2°C 至 +7°C
- 恒温: +24°C

📦 **增值服务**：
- 贴标服务: 0.71里亚尔/件（不含物料）
- 分拣服务: 按件计费
- 交叉理货

需要为您预留库位吗？"""

            return {
                "response": response,
                "next_action": "await_customer_confirmation"
            }

        return {"action": action, "completed": True}
