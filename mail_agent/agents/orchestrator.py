"""Central orchestrator that coordinates agents and tools."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Iterable

from mail_agent.config import SystemSettings
from mail_agent.core.models import (
    InvoiceDocument,
    MessageDisposition,
    Observation,
    PlannerAction,
    PlannerContext,
    ProcessingLogEntry,
    ToolResult,
)
from mail_agent.services.gmail_client import GmailClient
from mail_agent.tools.attachment_processor import AttachmentProcessor
from mail_agent.tools.interactive_browser import InteractiveBrowser
from mail_agent.tools.web_downloader import WebDownloader

LOGGER = logging.getLogger(__name__)


@dataclass
class OrchestratorDependencies:
    gmail_client: GmailClient
    planner_agent: "PlannerAgent"
    attachment_tool: AttachmentProcessor
    web_downloader: WebDownloader
    extractor_agent: "ExtractorAgent"
    archive_agent: "ArchiveAgent"


class Orchestrator:
    def __init__(self, settings: SystemSettings, deps: OrchestratorDependencies) -> None:
        self._settings = settings
        self._deps = deps
        self._logs: list[ProcessingLogEntry] = []

    async def run_once(self, message_id: str) -> ProcessingLogEntry:
        gmail_client = self._deps.gmail_client
        email = gmail_client.fetch_message(message_id)
        if not email:
            entry = ProcessingLogEntry(
                message_id=message_id,
                disposition=MessageDisposition.FAILED,
                notes="Failed to fetch email",
            )
            self._logs.append(entry)
            return entry

        LOGGER.info("Processing email %s - %s", email.id, email.subject)

        documents: list[InvoiceDocument] = []
        context = PlannerContext()
        observation: Optional[Observation] = None

        # Step 1: Run attachment processor
        attachment_result = self._deps.attachment_tool.run(email.attachments)
        if attachment_result.success:
            documents.extend(attachment_result.observation.payload.get("documents", []))
            observation = attachment_result.observation
        else:
            observation = Observation(description="No attachments processed", payload={})

        # Step 2: Planning loop for complex flows
        if not documents:
            documents.extend(await self._run_planning_loop(email, context, observation))

        if not documents:
            entry = ProcessingLogEntry(
                message_id=email.id,
                disposition=MessageDisposition.IGNORED,
                notes="No invoice found",
            )
            self._logs.append(entry)
            return entry

        extraction = await self._deps.extractor_agent.extract(documents)
        await self._deps.archive_agent.archive(extraction)

        entry = ProcessingLogEntry(
            message_id=email.id,
            disposition=MessageDisposition.SUCCESS,
            notes="Invoice processed",
            details={"documents": [doc.filename for doc in documents]},
        )
        self._logs.append(entry)
        return entry

    async def _run_planning_loop(
        self,
        email: "EmailEnvelope",
        context: PlannerContext,
        observation: Optional[Observation],
    ) -> list[InvoiceDocument]:
        documents: list[InvoiceDocument] = []
        max_steps = self._settings.planner.max_steps
        async with InteractiveBrowser() as browser:
            for step in range(max_steps):
                LOGGER.info("Planner step %s", step + 1)
                action = await self._deps.planner_agent.plan_next_action(email, context, observation)
                if action is None:
                    LOGGER.info("Planner did not return an action; ending loop")
                    break

                result = await self._execute_action(action, browser)
                observation = result.observation
                context.update_with(observation.payload.items())

                docs = observation.payload.get("documents") if observation.payload else None
                if docs:
                    documents.extend(docs)
                    break

                if not result.success:
                    LOGGER.warning("Planner action failed: %s", result.error)
                    continue
        return documents

    async def _execute_action(self, action: PlannerAction, browser: InteractiveBrowser) -> ToolResult:
        if action.action == "download_url":
            url = action.params["url"]
            filename = action.params.get("filename")
            return await self._deps.web_downloader.download(url, filename=filename)
        elif action.action in {"goto", "click", "type", "wait_for", "submit", "screenshot"}:
            return await browser.execute(action)
        else:
            observation = Observation(
                description=f"Unknown action {action.action}",
                payload={},
            )
            return ToolResult(success=False, observation=observation, error="unknown_action")

    @property
    def logs(self) -> Iterable[ProcessingLogEntry]:
        return list(self._logs)
