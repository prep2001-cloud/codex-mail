"""Agent that archives invoices to cloud storage."""
from __future__ import annotations

import logging
from pathlib import Path

from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload

from mail_agent.config import StorageSettings
from mail_agent.core.models import ExtractionResult

LOGGER = logging.getLogger(__name__)


class ArchiveAgent:
    """Uploads invoice files and metadata to cloud storage."""

    def __init__(self, settings: StorageSettings) -> None:
        self._settings = settings

    async def archive(self, extraction: ExtractionResult) -> None:
        if self._settings.provider == "gdrive":
            await self._archive_to_drive(extraction)
        else:
            await self._archive_to_local(extraction)

    async def _archive_to_drive(self, extraction: ExtractionResult) -> None:
        file_metadata = {
            "name": extraction.invoice.filename,
            "parents": [self._settings.root_folder_id] if self._settings.root_folder_id else None,
        }
        media = MediaInMemoryUpload(extraction.invoice.content, mimetype=extraction.invoice.mime_type)
        drive_service = build("drive", "v3")
        drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
        LOGGER.info("Uploaded %s to Google Drive", extraction.invoice.filename)

    async def _archive_to_local(self, extraction: ExtractionResult) -> None:
        target_dir = Path(self._settings.bucket or "archive")
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / extraction.invoice.filename
        target.write_bytes(extraction.invoice.content)
        LOGGER.info("Archived %s locally at %s", extraction.invoice.filename, target)
