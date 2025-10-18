"""Agent responsible for extracting structured data from invoices."""
from __future__ import annotations

import logging
from typing import Iterable

from mail_agent.core.models import ExtractionResult, InvoiceDocument

LOGGER = logging.getLogger(__name__)


class ExtractorAgent:
    """Placeholder extraction agent using a simple heuristic."""

    async def extract(self, documents: Iterable[InvoiceDocument]) -> ExtractionResult:
        docs = list(documents)
        if not docs:
            raise ValueError("No documents provided for extraction")
        invoice = docs[0]
        structured = {
            "vendor": "Unknown",
            "total": None,
            "currency": None,
            "source": invoice.metadata.get("source"),
        }
        LOGGER.info("Extracted structured data for %s", invoice.filename)
        return ExtractionResult(invoice=invoice, structured_data=structured)
