"""Core domain models for the agentic invoice system."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Iterable, Mapping, Optional


class MessageDisposition(str, Enum):
    """Final disposition for processed emails."""

    SUCCESS = "success"
    IGNORED = "ignored"
    FAILED = "failed"


@dataclass
class EmailAttachment:
    filename: str
    mime_type: str
    data: bytes | None = None
    download_url: Optional[str] = None


@dataclass
class EmailEnvelope:
    """Represents a Gmail message payload."""

    id: str
    thread_id: str
    subject: str
    sender: str
    recipients: tuple[str, ...]
    snippet: str
    body_text: str
    body_html: Optional[str]
    attachments: tuple[EmailAttachment, ...] = ()


@dataclass
class Observation:
    """Observation returned from tool execution."""

    description: str
    payload: Mapping[str, Any] = field(default_factory=dict)


@dataclass
class PlannerAction:
    """Planner decision encoded as JSON-compatible payload."""

    action: str
    params: Dict[str, Any] = field(default_factory=dict)

    def as_json(self) -> Dict[str, Any]:
        return {"action": self.action, **self.params}


@dataclass
class ToolResult:
    """Represents the result of executing a tool action."""

    success: bool
    observation: Observation
    error: Optional[str] = None


@dataclass
class InvoiceDocument:
    filename: str
    content: bytes
    mime_type: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass
class ExtractionResult:
    invoice: InvoiceDocument
    structured_data: Mapping[str, Any]


@dataclass
class ProcessingLogEntry:
    message_id: str
    disposition: MessageDisposition
    notes: str
    details: Mapping[str, Any] = field(default_factory=dict)


class PlannerContext(dict):
    """Mutable context shared across planning steps."""

    def update_with(self, items: Iterable[tuple[str, Any]]) -> None:
        for key, value in items:
            self[key] = value
