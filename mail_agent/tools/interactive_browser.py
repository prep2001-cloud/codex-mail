"""Interactive browser agent used for iterative planning."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import playwright.async_api as playwright_async

from mail_agent.core.models import Observation, PlannerAction, ToolResult

LOGGER = logging.getLogger(__name__)


@dataclass
class BrowserState:
    url: str
    title: str
    text_snapshot: str


class InteractiveBrowser:
    """Executes planner actions in a real browser context."""

    def __init__(self, *, headless: bool = True) -> None:
        self._headless = headless
        self._playwright: Optional[playwright_async.Playwright] = None
        self._browser: Optional[playwright_async.Browser] = None
        self._page: Optional[playwright_async.Page] = None

    async def __aenter__(self) -> "InteractiveBrowser":
        self._playwright = await playwright_async.async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=self._headless)
        self._page = await self._browser.new_page()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._page:
            await self._page.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def execute(self, action: PlannerAction) -> ToolResult:
        if not self._page:
            raise RuntimeError("InteractiveBrowser must be used as an async context manager")

        command = action.action
        params = action.params
        LOGGER.info("Executing browser action: %s", action.as_json())

        try:
            if command == "goto":
                await self._page.goto(params["url"], wait_until="domcontentloaded")
            elif command == "click":
                await self._page.click(params["selector"])
            elif command == "type":
                await self._page.fill(params["selector"], params.get("text", ""))
            elif command == "wait_for":
                await self._page.wait_for_selector(params["selector"], timeout=params.get("timeout", 10000))
            elif command == "submit":
                await self._page.click(params["selector"])
            elif command == "screenshot":
                await self._page.screenshot(path=params.get("path", "browser.png"))
            else:
                raise ValueError(f"Unknown browser command: {command}")

            state = await self._capture_state()
            observation = Observation(
                description=f"Executed {command}",
                payload={"state": state.__dict__},
            )
            return ToolResult(success=True, observation=observation)
        except Exception as exc:  # pragma: no cover - dependent on runtime browser env
            LOGGER.exception("Browser action failed: %s", exc)
            observation = Observation(
                description=f"Failed to execute {command}",
                payload={"error": str(exc)},
            )
            return ToolResult(success=False, observation=observation, error=str(exc))

    async def _capture_state(self) -> BrowserState:
        assert self._page
        content = await self._page.inner_text("body")
        return BrowserState(
            url=self._page.url,
            title=await self._page.title(),
            text_snapshot=content[:5000],
        )
