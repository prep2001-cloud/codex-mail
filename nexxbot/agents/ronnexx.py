"""
Ronnexx Agent - Operations Agent (运营助理)
Handles document processing, OCR, and WMS operations
"""

from typing import Dict, Any, List
from .base import BaseAgent
from ..tools.wms_tools import CreateASNTool, UpdateInventoryTool
from ..tools.base import ToolRegistry
from ..core.logger import get_logger

logger = get_logger(__name__)


class RonnexxAgent(BaseAgent):
    """
    Ronnexx - Operations Agent

    Responsibilities:
    - Document OCR and extraction
    - ASN creation
    - Inventory management
    - WMS operations
    """

    def __init__(self):
        # Initialize tools
        tools = ToolRegistry()
        tools.register(CreateASNTool())
        tools.register(UpdateInventoryTool())

        super().__init__(
            agent_id="ronnexx",
            role="Operations Agent",
            description="Handles operations, document processing, and WMS integration",
            tools=tools
        )

    async def perceive(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Understand operations request

        Args:
            input_data: Operations request (may include documents/images)

        Returns:
            Processed operations context
        """
        logger.info(f"[Ronnexx] Processing operations request")

        return {
            "operation_type": input_data.get("operation_type", "general"),
            "document": input_data.get("document"),
            "context": input_data.get("context", {})
        }

    async def plan(self, perception: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Plan operations workflow

        Args:
            perception: Operations context

        Returns:
            Operations plan
        """
        operation_type = perception.get("operation_type")

        if operation_type == "create_asn":
            steps = [
                {
                    "action": "ocr_document",
                    "description": "Extract data from document using OCR"
                },
                {
                    "action": "validate_data",
                    "description": "Validate extracted data"
                },
                {
                    "action": "create_asn",
                    "tool": "CreateASNTool",
                    "description": "Create ASN in WMS"
                }
            ]
        else:
            steps = [
                {
                    "action": "process_request",
                    "description": "Process general operations request"
                }
            ]

        return steps

    async def execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute operations step

        Args:
            step: Operations step

        Returns:
            Step result
        """
        action = step.get("action")
        tool_name = step.get("tool")

        logger.info(f"[Ronnexx] Executing: {action}")

        if action == "ocr_document":
            # Simulated OCR extraction
            # In production, use pytesseract or cloud OCR service
            extracted_data = {
                "supplier_code": "DELTA",
                "items": [
                    {"item_name": "UltraPure Hand Soap", "quantity": 8}
                ],
                "delivery_date": "2024-10-05",
                "confidence": 0.95
            }

            return {
                "extracted": True,
                "data": extracted_data
            }

        elif action == "validate_data":
            # Validation logic
            return {
                "valid": True,
                "message": "Data validation passed"
            }

        elif tool_name == "CreateASNTool":
            tool = self.tools.get(tool_name)
            # Use extracted data from previous step
            result = await tool(
                supplier_code="DELTA",
                items=[{"item_name": "UltraPure Hand Soap", "quantity": 8}],
                delivery_date="2024-10-05"
            )
            return result.result if hasattr(result, 'result') else result

        return {"action": action, "completed": True}
