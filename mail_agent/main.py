"""Entry point for the smart invoice automation system."""
from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path

from mail_agent.agents.archive import ArchiveAgent
from mail_agent.agents.extractor import ExtractorAgent
from mail_agent.agents.orchestrator import Orchestrator, OrchestratorDependencies
from mail_agent.agents.planner import PlannerAgent
from mail_agent.config import OAuthSettings, PlannerSettings, StorageSettings, SystemSettings
from mail_agent.services.gmail_client import GmailClient
from mail_agent.tools.attachment_processor import AttachmentProcessor
from mail_agent.tools.web_downloader import WebDownloader
from mail_agent.utils.logging import configure_logging

DOWNLOAD_DIR = "downloads"


async def main() -> None:
    configure_logging()
    settings = SystemSettings(
        oauth=OAuthSettings(
            client_id=os.environ["GMAIL_CLIENT_ID"],
            client_secret=os.environ["GMAIL_CLIENT_SECRET"],
            refresh_token=os.environ["GMAIL_REFRESH_TOKEN"],
        ),
        storage=StorageSettings(
            provider=os.environ.get("STORAGE_PROVIDER", "gdrive"),
            bucket=os.environ.get("STORAGE_BUCKET"),
            root_folder_id=os.environ.get("STORAGE_ROOT_FOLDER"),
        ),
        planner=PlannerSettings(
            model=os.environ.get("PLANNER_MODEL", "gpt-4.1"),
            max_steps=int(os.environ.get("PLANNER_MAX_STEPS", "25")),
            temperature=float(os.environ.get("PLANNER_TEMPERATURE", "0.1")),
        ),
        poll_interval_seconds=int(os.environ.get("POLL_INTERVAL", "30")),
    )

    gmail_client = GmailClient(settings.oauth)
    planner_agent = PlannerAgent(settings.planner, api_key=os.environ.get("OPENAI_API_KEY"))
    attachment_tool = AttachmentProcessor(Path(DOWNLOAD_DIR))
    web_downloader = WebDownloader(Path(DOWNLOAD_DIR))
    extractor_agent = ExtractorAgent()
    archive_agent = ArchiveAgent(settings.storage)

    orchestrator = Orchestrator(
        settings,
        OrchestratorDependencies(
            gmail_client=gmail_client,
            planner_agent=planner_agent,
            attachment_tool=attachment_tool,
            web_downloader=web_downloader,
            extractor_agent=extractor_agent,
            archive_agent=archive_agent,
        ),
    )

    async for message_id in gmail_client.watch_inbox():
        await orchestrator.run_once(message_id)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Shutting down invoice automation system")
