"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from conversations.service import ConversationService
from summaries.schemas import SummaryCreateRequest
from summaries.service import SummaryService
from workers.derived_jobs import DerivedJob


class SummaryWorker:
    """Create a rebuildable summary from the source message range."""

    def __init__(self, conversation_service: ConversationService, summary_service: SummaryService):
        self.conversation_service = conversation_service
        self.summary_service = summary_service

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
        messages = [message for message in page["messages"] if message["id"] in source_ids]
        if not messages:
            raise RuntimeError("summary_source_messages_not_found")
        content = _compact_messages(messages)
        self.summary_service.create_summary(
            job.user_id,
            SummaryCreateRequest(
                conversation_id=job.conversation_id,
                summary_type=job.metadata.get("summary_type", "session"),
                content=content,
                source_message_start_id=job.source_message_ids[0],
                source_message_end_id=job.source_message_ids[-1],
            ),
        )


def _compact_messages(messages: list[dict]) -> str:
    lines = []
    for message in messages:
        speaker = message.get("senderSlot") or message.get("senderId") or message.get("senderType")
        lines.append(f"{speaker}: {message['content']}")
    return "\n".join(lines)[:4000]
