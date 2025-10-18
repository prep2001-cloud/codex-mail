"""Gmail client wrapper that handles OAuth and message retrieval."""
from __future__ import annotations

import base64
import logging
from typing import AsyncGenerator, Iterable, Optional

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from mail_agent.config import OAuthSettings
from mail_agent.core.models import EmailAttachment, EmailEnvelope

LOGGER = logging.getLogger(__name__)


class GmailClient:
    """Handles Gmail API interactions."""

    def __init__(self, settings: OAuthSettings) -> None:
        self._settings = settings
        self._creds: Optional[Credentials] = None
        self._service = None

    def _credentials(self) -> Credentials:
        if self._creds and self._creds.valid:
            return self._creds

        self._creds = Credentials(
            token=None,
            refresh_token=self._settings.refresh_token,
            token_uri=self._settings.token_uri,
            client_id=self._settings.client_id,
            client_secret=self._settings.client_secret,
            scopes=list(self._settings.scopes),
        )
        self._creds.refresh_request = None
        if not self._creds.valid:
            self._creds.refresh(Request())  # type: ignore[name-defined]
        return self._creds

    def _ensure_service(self) -> None:
        if self._service is None:
            creds = self._credentials()
            self._service = build("gmail", "v1", credentials=creds, cache_discovery=False)

    def list_unprocessed_messages(self, label_ids: Optional[Iterable[str]] = None) -> list[str]:
        """Return message IDs from the inbox."""

        self._ensure_service()
        try:
            response = (
                self._service.users()
                .messages()
                .list(userId="me", labelIds=list(label_ids) if label_ids else None)
                .execute()
            )
        except HttpError as error:
            LOGGER.error("Unable to list messages: %s", error)
            return []

        messages = response.get("messages", [])
        return [m["id"] for m in messages]

    def fetch_message(self, message_id: str) -> Optional[EmailEnvelope]:
        """Fetch a single Gmail message and transform it into an envelope."""

        self._ensure_service()
        try:
            message = (
                self._service.users()
                .messages()
                .get(userId="me", id=message_id, format="full")
                .execute()
            )
        except HttpError as error:
            LOGGER.error("Unable to fetch message %s: %s", message_id, error)
            return None

        payload = message.get("payload", {})
        headers = {h["name"].lower(): h["value"] for h in payload.get("headers", [])}
        parts = payload.get("parts", [])

        attachments: list[EmailAttachment] = []
        body_text = ""
        body_html = None

        def _extract_part(part: dict) -> None:
            nonlocal body_text, body_html
            mime_type = part.get("mimeType", "")
            body = part.get("body", {})
            data = body.get("data")
            filename = part.get("filename")
            if data:
                decoded = base64.urlsafe_b64decode(data)
            else:
                decoded = b""

            if mime_type == "text/plain" and decoded:
                body_text += decoded.decode("utf-8", errors="replace")
            elif mime_type == "text/html" and decoded:
                body_html = decoded.decode("utf-8", errors="replace")
            elif filename:
                attachments.append(
                    EmailAttachment(
                        filename=filename,
                        mime_type=mime_type,
                        data=decoded or None,
                        download_url=body.get("attachmentId"),
                    )
                )

            for child in part.get("parts", []) or []:
                _extract_part(child)

        for part in parts:
            _extract_part(part)

        envelope = EmailEnvelope(
            id=message["id"],
            thread_id=message["threadId"],
            subject=headers.get("subject", ""),
            sender=headers.get("from", ""),
            recipients=tuple(headers.get("to", "").split(",")) if headers.get("to") else (),
            snippet=message.get("snippet", ""),
            body_text=body_text,
            body_html=body_html,
            attachments=tuple(attachments),
        )
        return envelope

    async def watch_inbox(self) -> AsyncGenerator[str, None]:
        """Yield new message IDs as they arrive.

        This generator currently falls back to polling because the push notification
        flow requires external infrastructure. A production deployment should
        configure Gmail push notifications and feed the events into this generator.
        """

        if asyncio is None:
            raise RuntimeError("Asyncio is unavailable; cannot watch inbox")

        label_ids = ["INBOX", "UNREAD"]
        seen_ids: set[str] = set()
        while True:
            for message_id in self.list_unprocessed_messages(label_ids=label_ids):
                if message_id not in seen_ids:
                    seen_ids.add(message_id)
                    yield message_id
            await asyncio.sleep(30)


try:  # pragma: no cover - optional import guard for aiohttp based Request
    import asyncio
    from google.auth.transport.requests import Request
except ImportError:  # pragma: no cover
    asyncio = None  # type: ignore[assignment]
    Request = None  # type: ignore[assignment]
    LOGGER.warning("Asyncio or Google auth Request not available; watch_inbox will not run.")
