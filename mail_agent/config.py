"""Configuration models for the invoice automation system."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class OAuthSettings:
    """OAuth configuration for Gmail access."""

    client_id: str
    client_secret: str
    refresh_token: str
    token_uri: str = "https://oauth2.googleapis.com/token"
    redirect_uri: Optional[str] = None
    scopes: tuple[str, ...] = ("https://www.googleapis.com/auth/gmail.readonly",)


@dataclass
class StorageSettings:
    """Configuration for Google Drive or alternative storage."""

    provider: str = "gdrive"
    bucket: Optional[str] = None
    root_folder_id: Optional[str] = None


@dataclass
class PlannerSettings:
    """Planner configuration values."""

    model: str = "gpt-4.1"
    max_steps: int = 25
    temperature: float = 0.1


@dataclass
class SystemSettings:
    """Top-level configuration container."""

    oauth: OAuthSettings
    storage: StorageSettings = field(default_factory=StorageSettings)
    planner: PlannerSettings = field(default_factory=PlannerSettings)
    poll_interval_seconds: int = 30
