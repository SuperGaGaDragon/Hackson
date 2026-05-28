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


class MemoryWorker:
    """Generate conservative memory candidates from user-authored source messages."""

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
        for message in page["messages"]:
            if message["id"] not in source_ids or message["senderType"] != "user":
                continue
            candidate = _candidate_from_user_message(job.user_id, message)
            if candidate is not None:
                self.memory_service.accept_candidate(job.user_id, candidate)


def _candidate_from_user_message(user_id: str, message: dict) -> MemoryCandidate | None:
    content = message["content"].strip()
    if not _looks_like_explicit_preference(content):
        return None
    return MemoryCandidate(
        scope="account",
        owner_type="user",
        owner_id=user_id,
        memory_type="preference",
        summary=f"User explicitly said: {content}",
        source_message_ids=[message["id"]],
        source_sender_types=["user"],
        importance_score=0.65,
        confidence=0.75,
        metadata={"extractor": "memory_worker_v0"},
    )


def _looks_like_explicit_preference(content: str) -> bool:
    lowered = content.lower()
    direct_preference_markers = [
        "我喜欢",
        "我更喜欢",
        "我偏好",
        "我不喜欢",
        "不喜欢",
        "我讨厌",
        "请记住",
        "帮我记住",
        "记住",
        "i like",
        "i prefer",
        "i don't like",
        "i do not like",
        "please remember",
        "remember that",
        "remember:",
    ]
    response_preference_prefixes = [
        "希望你",
        "请你",
        "以后你",
        "你可以",
        "你应该",
        "不要先",
        "不要总",
        "别先",
        "别总",
        "直接指出",
        "don't",
        "do not",
    ]
    response_context_markers = ["回复", "回应", "反馈", "指出", "安慰", "解释", "reply", "respond", "feedback", "reassure"]
    if any(marker in lowered for marker in direct_preference_markers):
        return True
    if any(marker in lowered for marker in response_preference_prefixes):
        return any(marker in lowered for marker in response_context_markers)
    return False
