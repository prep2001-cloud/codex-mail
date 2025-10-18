"""Central orchestrator that coordinates agents and tools."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Iterable, Optional

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

        status = context.get("status")
        reason = context.get("reason")

        if not documents:
            if status == "failed":
                disposition = MessageDisposition.FAILED
                notes = reason or "Planner actions failed"
            elif status == "ignored":
                disposition = MessageDisposition.IGNORED
                notes = reason or "Planner marked email as ignored"
            else:
                disposition = MessageDisposition.IGNORED
                notes = reason or "No invoice found"

            entry = ProcessingLogEntry(
                message_id=email.id,
                disposition=disposition,
                notes=notes,
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
        for step in range(max_steps):
            LOGGER.info("Planner step %s", step + 1)
            action = await self._deps.planner_agent.plan_next_action(email, context, observation)
            if action is None:
                LOGGER.info("Planner did not return an action; ending loop")
                break

            result = await self._execute_action(action)
            observation = result.observation
            context.update_with(observation.payload.items())

            docs = observation.payload.get("documents")
            if docs:
                documents.extend(docs)
                break

            status = observation.payload.get("status")
            if status == "ignored":
                LOGGER.info("Planner marked email as ignored: %s", observation.payload.get("reason"))
                break
            if status == "finished":
                LOGGER.info("Planner finished without additional actions")
                break

            if not result.success:
                LOGGER.warning("Planner action failed: %s", result.error)
                continue
        return documents

    async def _execute_action(self, action: PlannerAction) -> ToolResult:
        if action.action == "download_url":
            url = action.params["url"]
            filename = action.params.get("filename")
            try:
                return await self._deps.web_downloader.download(url, filename=filename)
            except Exception as exc:  # pragma: no cover - network errors are environment dependent
                reason = f"Failed to download {url}: {exc}"
                observation = Observation(
                    description=reason,
                    payload={"status": "failed", "reason": reason, "url": url},
                )
                return ToolResult(success=False, observation=observation, error=str(exc))
        if action.action == "finish":
            observation = Observation(
                description="Planner finished processing",
                payload={"status": "finished"},
            )
            return ToolResult(success=True, observation=observation)
        if action.action == "ignore":
            reason = action.params.get("reason", "no invoice detected")
            observation = Observation(
                description="Planner requested to ignore message",
                payload={"status": "ignored", "reason": reason},
            )
            return ToolResult(success=True, observation=observation)

        reason = f"Unknown action {action.action}"
        observation = Observation(
            description=reason,
            payload={"status": "failed", "reason": reason, "action": action.action},
        )
        return ToolResult(success=False, observation=observation, error="unknown_action")

    @property
    def logs(self) -> Iterable[ProcessingLogEntry]:
        return list(self._logs)
