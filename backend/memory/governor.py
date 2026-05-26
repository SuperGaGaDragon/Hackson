"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from memory.schemas import MemoryCandidate


class MemoryGovernor:
    """Accept or reject memory candidates before persistence."""

    def should_accept(self, candidate: MemoryCandidate) -> bool:
        if not candidate.source_message_ids:
            return False
        if candidate.owner_type == "user" and candidate.memory_type in {"fact", "preference"}:
            return "user" in candidate.source_sender_types
        if candidate.confidence < 0.35:
            return False
        return True
