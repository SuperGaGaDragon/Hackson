"""
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Any

from workers.derived_jobs import DerivedJobService
from workers.diary_worker import DiaryWorker
from workers.memory_worker import MemoryWorker
from workers.relationship_worker import RelationshipWorker
from workers.summary_worker import SummaryWorker


class DerivedWorkerRunner:
    """Compose concrete derived workers behind one runner entrypoint."""

    def __init__(
        self,
        job_service: DerivedJobService,
        summary_worker: SummaryWorker,
        memory_worker: MemoryWorker,
        diary_worker: DiaryWorker,
        relationship_worker: RelationshipWorker,
    ):
        self.job_service = job_service
        self.summary_worker = summary_worker
        self.memory_worker = memory_worker
        self.diary_worker = diary_worker
        self.relationship_worker = relationship_worker

    def run_once(
        self,
        limit: int = 10,
        *,
        user_id: str | None = None,
        conversation_id: str | None = None,
        newest_first: bool = False,
    ) -> int:
        return self.job_service.run_pending(
            {
                "summary": self.summary_worker.handle,
                "memory_candidate": self.memory_worker.handle,
                "diary": self.diary_worker.handle,
                "relationship": self.relationship_worker.handle,
            },
            limit=limit,
            user_id=user_id,
            conversation_id=conversation_id,
            newest_first=newest_first,
        )


@dataclass
class DerivedWorkerLoop:
    runner: DerivedWorkerRunner
    interval_seconds: float
    batch_size: int
    _stop_event: threading.Event | None = None
    _thread: threading.Thread | None = None

    def start(self) -> None:
        """Start a bounded daemon loop for best-effort derived work."""
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run, name="hackson-derived-worker", daemon=True)
        self._thread.start()

    def stop(self, timeout: float = 2.0) -> None:
        if self._stop_event is not None:
            self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=timeout)

    def _run(self) -> None:
        assert self._stop_event is not None
        while not self._stop_event.is_set():
            try:
                self.runner.run_once(limit=self.batch_size)
                freshness_limit = max(1, min(5, self.batch_size // 4))
                self.runner.run_once(limit=freshness_limit, newest_first=True)
            except Exception:
                pass
            self._stop_event.wait(self.interval_seconds)


def build_derived_worker_runner(database: Any) -> DerivedWorkerRunner:
    from conversations.repository import ConversationRepository
    from conversations.service import ConversationService
    from diary.repository import DiaryRepository
    from diary.service import DiaryService
    from memory.repository import MemoryRepository
    from memory.service import MemoryService
    from summaries.repository import SummaryRepository
    from summaries.service import SummaryService
    from workers.derived_jobs import DerivedJobRepository, DerivedJobService

    conversation_service = ConversationService(ConversationRepository(database))
    memory_service = MemoryService(MemoryRepository(database))
    return DerivedWorkerRunner(
        DerivedJobService(DerivedJobRepository(database)),
        SummaryWorker(conversation_service, SummaryService(SummaryRepository(database))),
        MemoryWorker(conversation_service, memory_service),
        DiaryWorker(DiaryService(DiaryRepository(database))),
        RelationshipWorker(conversation_service, memory_service),
    )


def start_derived_worker_loop(database: Any, *, interval_seconds: float, batch_size: int) -> DerivedWorkerLoop:
    loop = DerivedWorkerLoop(
        runner=build_derived_worker_runner(database),
        interval_seconds=max(interval_seconds, 0.2),
        batch_size=max(batch_size, 1),
    )
    loop.start()
    return loop
