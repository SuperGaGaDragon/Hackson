"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from diary.schemas import DiaryEntryCreateRequest
from diary.service import DiaryService
from workers.derived_jobs import DerivedJob


class DiaryWorker:
    """Create a short evidence-backed diary entry for an Agent."""

    def __init__(self, diary_service: DiaryService):
        self.diary_service = diary_service

    def handle(self, job: DerivedJob) -> None:
        agent_id = job.metadata.get("agent_id") or job.metadata.get("target_agent_id") or "agent_1"
        self.diary_service.create_entry(
            job.user_id,
            DiaryEntryCreateRequest(
                agent_id=agent_id,
                content="A short idle moment was recorded for later user-visible diary review.",
                source_message_ids=job.source_message_ids,
            ),
        )
