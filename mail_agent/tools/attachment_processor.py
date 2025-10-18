"""Attachment processing tool."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable

from mail_agent.core.models import EmailAttachment, InvoiceDocument, Observation, ToolResult

LOGGER = logging.getLogger(__name__)


class AttachmentProcessor:
    """Save attachments locally and return invoice documents."""

    def __init__(self, download_dir: Path) -> None:
        self._download_dir = download_dir
        self._download_dir.mkdir(parents=True, exist_ok=True)

    def handle(self, attachments: Iterable[EmailAttachment]) -> list[InvoiceDocument]:
        documents: list[InvoiceDocument] = []
        for attachment in attachments:
            if not attachment.data:
                LOGGER.debug("Skipping attachment %s with no data", attachment.filename)
                continue
            target = self._download_dir / attachment.filename
            target.write_bytes(attachment.data)
            doc = InvoiceDocument(
                filename=attachment.filename,
                content=attachment.data,
                mime_type=attachment.mime_type,
                metadata={"source": "email_attachment"},
            )
            documents.append(doc)
            LOGGER.info("Saved attachment to %s", target)
        return documents

    def run(self, attachments: Iterable[EmailAttachment]) -> ToolResult:
        documents = self.handle(attachments)
        description = f"Processed {len(documents)} attachment(s)."
        observation = Observation(description=description, payload={"documents": documents})
        return ToolResult(success=bool(documents), observation=observation)
