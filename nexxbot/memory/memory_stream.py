"""
Memory Stream - Manages short-term and long-term memory for agents
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from ..core.logger import get_logger

logger = get_logger(__name__)


class MemoryType(Enum):
    """Types of memory entries"""
    SHORT_TERM = "short_term"  # Current conversation context
    LONG_TERM = "long_term"    # Historical decisions, SOPs
    EPISODIC = "episodic"      # Specific events and cases
    SEMANTIC = "semantic"      # General knowledge


@dataclass
class MemoryEntry:
    """Single memory entry"""
    content: str
    memory_type: MemoryType
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    importance: float = 1.0  # 0-1 scale
    access_count: int = 0
    agent_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "content": self.content,
            "memory_type": self.memory_type.value,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "importance": self.importance,
            "access_count": self.access_count,
            "agent_id": self.agent_id
        }


class MemoryStream:
    """
    Memory Stream Manager

    Manages different types of memory for agents:
    - Short-term: Current session context
    - Long-term: Historical patterns and knowledge
    - Episodic: Specific past experiences
    - Semantic: Domain knowledge
    """

    def __init__(self, agent_id: str, max_short_term: int = 50):
        """
        Initialize memory stream

        Args:
            agent_id: Agent identifier
            max_short_term: Maximum short-term memory entries
        """
        self.agent_id = agent_id
        self.max_short_term = max_short_term
        self.short_term_memory: List[MemoryEntry] = []
        self.long_term_memory: List[MemoryEntry] = []
        logger.info(f"MemoryStream initialized for agent: {agent_id}")

    def add(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.SHORT_TERM,
        importance: float = 1.0,
        metadata: Optional[Dict] = None
    ) -> MemoryEntry:
        """
        Add a new memory entry

        Args:
            content: Memory content
            memory_type: Type of memory
            importance: Importance score (0-1)
            metadata: Additional metadata

        Returns:
            Created memory entry
        """
        entry = MemoryEntry(
            content=content,
            memory_type=memory_type,
            importance=importance,
            metadata=metadata or {},
            agent_id=self.agent_id
        )

        if memory_type == MemoryType.SHORT_TERM:
            self.short_term_memory.append(entry)
            # Maintain max size
            if len(self.short_term_memory) > self.max_short_term:
                # Remove oldest, least important entries
                self.short_term_memory = sorted(
                    self.short_term_memory,
                    key=lambda x: (x.importance, x.timestamp),
                    reverse=True
                )[:self.max_short_term]
        else:
            self.long_term_memory.append(entry)

        logger.debug(f"Added {memory_type.value} memory: {content[:50]}...")
        return entry

    def get_recent(
        self,
        n: int = 10,
        memory_type: Optional[MemoryType] = None
    ) -> List[MemoryEntry]:
        """
        Get recent memory entries

        Args:
            n: Number of entries to retrieve
            memory_type: Optional filter by memory type

        Returns:
            List of recent memory entries
        """
        if memory_type == MemoryType.SHORT_TERM:
            memories = self.short_term_memory
        elif memory_type == MemoryType.LONG_TERM:
            memories = self.long_term_memory
        else:
            memories = self.short_term_memory + self.long_term_memory

        sorted_memories = sorted(
            memories,
            key=lambda x: x.timestamp,
            reverse=True
        )
        return sorted_memories[:n]

    def get_by_importance(
        self,
        threshold: float = 0.7,
        n: int = 10
    ) -> List[MemoryEntry]:
        """
        Get important memory entries

        Args:
            threshold: Minimum importance score
            n: Maximum number to return

        Returns:
            List of important memories
        """
        all_memories = self.short_term_memory + self.long_term_memory
        important = [m for m in all_memories if m.importance >= threshold]
        sorted_important = sorted(
            important,
            key=lambda x: x.importance,
            reverse=True
        )
        return sorted_important[:n]

    def search(
        self,
        query: str,
        n: int = 5
    ) -> List[MemoryEntry]:
        """
        Search memories by keyword (simple implementation)

        Args:
            query: Search query
            n: Number of results

        Returns:
            Matching memories
        """
        all_memories = self.short_term_memory + self.long_term_memory
        query_lower = query.lower()

        # Simple keyword matching
        matches = [
            m for m in all_memories
            if query_lower in m.content.lower()
        ]

        # Sort by relevance (timestamp and importance)
        sorted_matches = sorted(
            matches,
            key=lambda x: (x.importance, x.timestamp),
            reverse=True
        )
        return sorted_matches[:n]

    def consolidate(self):
        """
        Consolidate short-term memory to long-term

        Moves important short-term memories to long-term storage
        """
        threshold = 0.8
        to_consolidate = [
            m for m in self.short_term_memory
            if m.importance >= threshold
        ]

        for memory in to_consolidate:
            # Convert to long-term
            memory.memory_type = MemoryType.LONG_TERM
            self.long_term_memory.append(memory)
            self.short_term_memory.remove(memory)

        logger.info(f"Consolidated {len(to_consolidate)} memories to long-term")

    def clear_short_term(self):
        """Clear short-term memory"""
        count = len(self.short_term_memory)
        self.short_term_memory.clear()
        logger.info(f"Cleared {count} short-term memories")

    def get_context_window(self, n: int = 10) -> str:
        """
        Get formatted context window for LLM

        Args:
            n: Number of recent memories to include

        Returns:
            Formatted context string
        """
        recent = self.get_recent(n, MemoryType.SHORT_TERM)
        if not recent:
            return "No recent context available."

        context_parts = []
        for entry in reversed(recent):  # Chronological order
            timestamp = entry.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            context_parts.append(f"[{timestamp}] {entry.content}")

        return "\n".join(context_parts)

    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return {
            "agent_id": self.agent_id,
            "short_term_count": len(self.short_term_memory),
            "long_term_count": len(self.long_term_memory),
            "total_count": len(self.short_term_memory) + len(self.long_term_memory),
            "avg_importance": sum(
                m.importance for m in (self.short_term_memory + self.long_term_memory)
            ) / max(len(self.short_term_memory) + len(self.long_term_memory), 1)
        }
