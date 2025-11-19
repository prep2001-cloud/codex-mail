"""
Communication tools for notifications and messaging
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from .base import Tool, ToolOutput
from ..core.logger import get_logger

logger = get_logger(__name__)


class SendEmailTool(Tool):
    """Send email notifications"""

    async def execute(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[List[str]] = None,
        attachments: Optional[List[str]] = None
    ) -> ToolOutput:
        """
        Send email

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body
            cc: CC recipients
            attachments: Attachment file paths

        Returns:
            Email send status
        """
        try:
            # Simulated email sending
            # In production, integrate with SMTP or email service

            logger.info(f"Sending email to {to}: {subject}")

            result = {
                "message_id": f"MSG{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "to": to,
                "subject": subject,
                "cc": cc or [],
                "sent_at": datetime.now().isoformat(),
                "status": "sent"
            }

            return ToolOutput(
                success=True,
                result=result
            )

        except Exception as e:
            return ToolOutput(
                success=False,
                result=None,
                error=str(e)
            )

    def _get_parameters(self) -> Dict[str, Any]:
        return {
            "to": {
                "type": "string",
                "description": "Recipient email address"
            },
            "subject": {
                "type": "string",
                "description": "Email subject"
            },
            "body": {
                "type": "string",
                "description": "Email body content"
            },
            "cc": {
                "type": "array",
                "description": "CC recipients",
                "items": {"type": "string"}
            },
            "attachments": {
                "type": "array",
                "description": "Attachment file paths",
                "items": {"type": "string"}
            }
        }

    def _get_required_params(self) -> List[str]:
        return ["to", "subject", "body"]


class SendNotificationTool(Tool):
    """Send instant notifications via WhatsApp/WeChat/Slack"""

    async def execute(
        self,
        channel: str,
        recipient: str,
        message: str,
        priority: str = "normal"
    ) -> ToolOutput:
        """
        Send instant notification

        Args:
            channel: Communication channel (whatsapp, wechat, slack)
            recipient: Recipient ID
            message: Message content
            priority: Message priority (low, normal, high, urgent)

        Returns:
            Send status
        """
        try:
            logger.info(f"Sending {channel} notification to {recipient}")

            result = {
                "notification_id": f"NOTIF{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "channel": channel,
                "recipient": recipient,
                "priority": priority,
                "sent_at": datetime.now().isoformat(),
                "status": "delivered"
            }

            return ToolOutput(
                success=True,
                result=result
            )

        except Exception as e:
            return ToolOutput(
                success=False,
                result=None,
                error=str(e)
            )

    def _get_parameters(self) -> Dict[str, Any]:
        return {
            "channel": {
                "type": "string",
                "description": "Communication channel",
                "enum": ["whatsapp", "wechat", "slack", "telegram"]
            },
            "recipient": {
                "type": "string",
                "description": "Recipient ID or phone number"
            },
            "message": {
                "type": "string",
                "description": "Message content"
            },
            "priority": {
                "type": "string",
                "description": "Message priority",
                "enum": ["low", "normal", "high", "urgent"]
            }
        }

    def _get_required_params(self) -> List[str]:
        return ["channel", "recipient", "message"]
