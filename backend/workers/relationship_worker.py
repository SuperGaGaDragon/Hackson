"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from conversations.service import ConversationService
from memory.schemas import MemoryCandidate
from memory.service import MemoryService
from workers.derived_jobs import DerivedJob


class RelationshipWorker:
    """Create a small Agent-Agent relationship memory from idle evidence."""

    def __init__(self, conversation_service: ConversationService, memory_service: MemoryService):
        self.conversation_service = conversation_service
        self.memory_service = memory_service

    def handle(self, job: DerivedJob) -> None:
        page = self.conversation_service.list_messages(
            job.user_id,
            job.conversation_id,
            after_sequence=None,
            created_after=None,
            created_before=None,
            limit=100,
        )
        source_ids = set(job.source_message_ids)
        agent_messages = [
            message
            for message in page["messages"]
            if message["id"] in source_ids and message["senderType"] == "agent" and message["content"].strip()
        ]
        if len(agent_messages) < 2:
            return
        summary = _relationship_summary(agent_messages)
        if summary is None:
            return
        self.memory_service.accept_candidate(
            job.user_id,
            MemoryCandidate(
                scope="idle",
                owner_type="agent_pair",
                owner_id="agent_1:agent_2",
                memory_type="relationship",
                summary=summary,
                source_message_ids=job.source_message_ids,
                source_sender_types=["agent"],
                importance_score=0.58,
                confidence=0.62,
                metadata={"extractor": "relationship_worker_v1"},
            ),
        )


def _relationship_summary(messages: list[dict]) -> str | None:
    first, second = messages[-2], messages[-1]
    first_name = _agent_name(first)
    second_name = _agent_name(second)
    first_text = _compact(first["content"], 76)
    second_text = _compact(second["content"], 76)
    if not first_text or not second_text:
        return None
    return f"{first_name} framed the thread around “{first_text}”; {second_name} responded with “{second_text}”."


def _agent_name(message: dict) -> str:
    if message.get("senderSlot") == "agent_2":
        return "Vale"
    return "Nora"


def _compact(value: str, limit: int) -> str:
    compacted = " ".join(value.strip().split())
    if len(compacted) <= limit:
        return compacted
    return compacted[: limit - 1].rstrip() + "..."
