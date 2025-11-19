"""
NEXXBot Supply Chain AI Solution
Multi-Agent Agentic Workflow System
"""

__version__ = "1.0.0"
__author__ = "NEXXBot Team"

from .core.config import settings
from .core.nexxlm import NexxLM

__all__ = ["settings", "NexxLM"]
