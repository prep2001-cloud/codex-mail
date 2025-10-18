"""Iterative planner agent powered by an LLM."""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI

from mail_agent.config import PlannerSettings
from mail_agent.core.models import EmailEnvelope, Observation, PlannerAction, PlannerContext

LOGGER = logging.getLogger(__name__)


SYSTEM_PROMPT = """You are an expert automation planner tasked with downloading invoices from emails.\n"""


class PlannerAgent:
    """Uses an LLM to determine the next action to take."""

    def __init__(self, settings: PlannerSettings, *, api_key: Optional[str] = None) -> None:
        self._settings = settings
        self._client = AsyncOpenAI(api_key=api_key)

    async def plan_next_action(
        self,
        email: EmailEnvelope,
        context: PlannerContext,
        observation: Optional[Observation],
    ) -> Optional[PlannerAction]:
        messages = self._build_messages(email, context, observation)
        LOGGER.debug("Planner sending messages: %s", messages)
        response = await self._client.chat.completions.create(
            model=self._settings.model,
            temperature=self._settings.temperature,
            messages=messages,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content if response.choices else None
        if not content:
            LOGGER.warning("Planner returned empty content")
            return None
        payload = json.loads(content)
        LOGGER.info("Planner response: %s", payload)
        action = payload.get("action")
        if not action:
            return None
        params = {k: v for k, v in payload.items() if k != "action"}
        return PlannerAction(action=action, params=params)

    def _build_messages(
        self,
        email: EmailEnvelope,
        context: PlannerContext,
        observation: Optional[Observation],
    ) -> List[Dict[str, Any]]:
        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "goal": "Download invoice",
                        "email": {
                            "subject": email.subject,
                            "sender": email.sender,
                            "body_text": email.body_text,
                            "attachments": [a.filename for a in email.attachments],
                        },
                        "context": dict(context),
                    }
                ),
            },
        ]
        if observation:
            messages.append(
                {
                    "role": "assistant",
                    "content": json.dumps(
                        {
                            "observation": observation.payload,
                            "description": observation.description,
                        }
                    ),
                }
            )
        return messages
