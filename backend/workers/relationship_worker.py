"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from memory.schemas import MemoryCandidate
from memory.service import MemoryService
from workers.derived_jobs import DerivedJob


class RelationshipWorker:
    """Create a small Agent-Agent relationship memory from idle evidence."""

    def __init__(self, memory_service: MemoryService):
        self.memory_service = memory_service

    def handle(self, job: DerivedJob) -> None:
        self.memory_service.accept_candidate(
            job.user_id,
            MemoryCandidate(
                scope="idle",
                owner_type="agent_pair",
                owner_id="agent_1:agent_2",
                memory_type="relationship",
                summary="Nora and Vale shared another idle interaction.",
                source_message_ids=job.source_message_ids,
                source_sender_types=["agent"],
                importance_score=0.4,
                confidence=0.5,
                metadata={"extractor": "relationship_worker_v0"},
            ),
        )
