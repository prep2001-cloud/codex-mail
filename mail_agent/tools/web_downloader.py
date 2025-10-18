"""Downloader for direct invoice URLs."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import httpx

from mail_agent.core.models import InvoiceDocument, Observation, ToolResult

LOGGER = logging.getLogger(__name__)


class WebDownloader:
    """Download invoices from HTTP URLs."""

    def __init__(self, download_dir: Path, *, timeout: float = 30.0) -> None:
        self._download_dir = download_dir
        self._download_dir.mkdir(parents=True, exist_ok=True)
        self._timeout = timeout

    async def download(self, url: str, *, filename: Optional[str] = None) -> ToolResult:
        LOGGER.info("Downloading invoice from %s", url)
        async with httpx.AsyncClient(timeout=self._timeout, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()
            content_type = response.headers.get("content-type", "application/octet-stream")
            data = response.content

        name = filename or url.split("/")[-1] or "invoice.pdf"
        target = self._download_dir / name
        target.write_bytes(data)

        document = InvoiceDocument(
            filename=name,
            content=data,
            mime_type=content_type,
            metadata={"source": "direct_url", "url": url},
        )
        observation = Observation(
            description=f"Downloaded {name} from {url}",
            payload={"documents": [document]},
        )
        return ToolResult(success=True, observation=observation)
