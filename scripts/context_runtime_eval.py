"""
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

from __future__ import annotations

import time

from agents.catalog import default_agent_snapshots
from context.builder import ContextBuilder
from context.schemas import (
    ContextBuildInput,
    ContextMode,
    ConversationMessage,
    ConversationSummary,
    MemoryCardSnapshot,
    SenderType,
    UserProfileSnapshot,
)


def main() -> None:
    results = [
        _eval_idle_mode_speaker_topic_repetition(),
        _eval_companion_1_transition_and_memory(),
        _eval_companion_2_memory_scope(),
        _eval_work_memory_scope(),
    ]
    failed = [result for result in results if not result["passed"]]
    for result in results:
        status = "ok" if result["passed"] else "fail"
        print(f"{status} {result['name']} latency_ms={result['latency_ms']:.2f}")
        for note in result["notes"]:
            print(f"  - {note}")
    if failed:
        raise SystemExit(1)
    print(f"context_runtime_eval=ok cases={len(results)}")


def _eval_idle_mode_speaker_topic_repetition() -> dict:
    started = time.perf_counter()
    package = ContextBuilder().build(
        ContextBuildInput(
            mode=ContextMode.IDLE,
            conversation_id="idle_eval",
            target_agent_id="agent_1",
            agents=default_agent_snapshots(),
            user_profile=UserProfileSnapshot(id="user_1", display_name="Demo", language_preference="zh"),
            user_direction="只讨论 30 秒 demo 开场",
            summary=ConversationSummary(
                id="summary_idle_1",
                summary_type="session",
                content="Older discussion covered onboarding and pricing.",
            ),
            recent_messages=[
                ConversationMessage(
                    id=f"message_{index}",
                    sender_type=SenderType.AGENT,
                    sender_id="agent_2" if index % 2 else "agent_1",
                    sender_name="Vale" if index % 2 else "Nora",
                    content=f"recent marker {index}",
                )
                for index in range(18)
            ],
            idle_seed="推进 demo 开场，不重复问题。",
            token_budget=6000,
        )
    )
    prompt = _prompt(package)
    notes = _assertions(
        [
            ("mode fit", "Current mode: idle" in prompt),
            ("speaker boundary", "The other Agent is not the User." in prompt and "Current speaking Agent" in prompt),
            ("topic adherence", "只讨论 30 秒 demo 开场" in prompt),
            ("repetition control", "Make one conversational move" in prompt),
            ("relationship stance", "Relationship stance:" in prompt),
            ("turn intent", "Turn intent:" in prompt),
            ("human dialogue", "Respond to the previous Agent's concrete line" in prompt),
            ("anti advice stack", "Do not output stacked frameworks" in prompt),
            ("latest raw messages", "recent marker 17" in prompt and "recent marker 0" not in prompt),
            ("summary audit", package.included_summary_ids == ["summary_idle_1"]),
        ]
    )
    return _result("idle_mode_speaker_topic_repetition", notes, started)


def _eval_companion_1_transition_and_memory() -> dict:
    started = time.perf_counter()
    package = ContextBuilder().build(
        ContextBuildInput(
            mode=ContextMode.COMPANION_1,
            conversation_id="companion1_eval",
            target_agent_id="agent_1",
            agents=default_agent_snapshots(),
            user_message="我加入，帮我压到一句话。",
            idle_recent_messages=[
                ConversationMessage(
                    id="idle_message_1",
                    sender_type=SenderType.AGENT,
                    sender_id="agent_2",
                    sender_name="Vale",
                    content="我们在聊 demo 开场是否太长。",
                )
            ],
            idle_summary=ConversationSummary(
                id="summary_idle_parent",
                summary_type="session",
                content="Parent idle focused on demo opening rhythm.",
            ),
            memory_cards=[
                MemoryCardSnapshot(
                    id="memory_companion_pref",
                    scope="companion",
                    owner_type="user",
                    owner_id="user_1",
                    memory_type="preference",
                    summary="User prefers direct phrasing.",
                    importance_score=0.9,
                    confidence=0.9,
                ),
                MemoryCardSnapshot(
                    id="memory_idle_relation",
                    scope="idle",
                    owner_type="agent_pair",
                    owner_id="agent_1:agent_2",
                    memory_type="relationship",
                    summary="Agents challenge each other softly.",
                    importance_score=0.8,
                    confidence=0.8,
                ),
            ],
            token_budget=6000,
        )
    )
    prompt = _prompt(package)
    notes = _assertions(
        [
            ("mode fit", "Current mode: companion_1 user joined idle" in prompt),
            ("transition quality", "Transition Context" in prompt and "用户刚刚加入了两个 Agent" in prompt),
            ("speaker boundary", "The user is now the center of the turn." in prompt),
            ("memory use", "User prefers direct phrasing." in prompt and "Agents challenge each other softly." in prompt),
            (
                "memory audit",
                set(package.included_memory_ids) == {"memory_companion_pref", "memory_idle_relation"},
            ),
        ]
    )
    return _result("companion_1_transition_memory", notes, started)


def _eval_companion_2_memory_scope() -> dict:
    started = time.perf_counter()
    package = ContextBuilder().build(
        ContextBuildInput(
            mode=ContextMode.COMPANION_2,
            conversation_id="companion2_eval",
            target_agent_id="agent_2",
            agents=default_agent_snapshots(),
            user_message="继续。",
            memory_cards=[
                MemoryCardSnapshot(
                    id="memory_companion_pref",
                    scope="companion",
                    owner_type="user",
                    owner_id="user_1",
                    memory_type="preference",
                    summary="User prefers concise Chinese replies.",
                    importance_score=0.9,
                    confidence=0.9,
                ),
                MemoryCardSnapshot(
                    id="memory_work_hidden",
                    scope="work",
                    owner_type="task",
                    owner_id="task_1",
                    memory_type="task",
                    summary="Hidden work task detail.",
                    importance_score=1.0,
                    confidence=0.9,
                ),
            ],
        )
    )
    prompt = _prompt(package)
    notes = _assertions(
        [
            ("mode fit", "Current mode: companion_2 fresh companion chat" in prompt),
            ("memory use", "User prefers concise Chinese replies." in prompt),
            ("work isolation", "Hidden work task detail." not in prompt),
            ("memory audit", package.included_memory_ids == ["memory_companion_pref"]),
        ]
    )
    return _result("companion_2_memory_scope", notes, started)


def _eval_work_memory_scope() -> dict:
    started = time.perf_counter()
    package = ContextBuilder().build(
        ContextBuildInput(
            mode=ContextMode.WORK,
            conversation_id="work_eval",
            target_agent_id="agent_1",
            agents=default_agent_snapshots(),
            task_state={"goal": "ship context runtime"},
            memory_cards=[
                MemoryCardSnapshot(
                    id="memory_work",
                    scope="work",
                    owner_type="task",
                    owner_id="task_1",
                    memory_type="task",
                    summary="Use non-public target port for smoke.",
                    importance_score=1.0,
                    confidence=0.9,
                ),
                MemoryCardSnapshot(
                    id="memory_companion_hidden",
                    scope="companion",
                    owner_type="user",
                    owner_id="user_1",
                    memory_type="preference",
                    summary="Hidden companion preference.",
                    importance_score=1.0,
                    confidence=0.9,
                ),
            ],
        )
    )
    prompt = _prompt(package)
    notes = _assertions(
        [
            ("mode fit", "Current mode: work" in prompt),
            ("memory use", "Use non-public target port for smoke." in prompt),
            ("companion isolation", "Hidden companion preference." not in prompt),
            ("memory audit", package.included_memory_ids == ["memory_work"]),
        ]
    )
    return _result("work_memory_scope", notes, started)


def _prompt(package) -> str:
    return "\n\n".join(message.content for message in package.messages)


def _assertions(checks: list[tuple[str, bool]]) -> list[str]:
    return [f"{name}={'ok' if passed else 'fail'}" for name, passed in checks]


def _result(name: str, notes: list[str], started: float) -> dict:
    return {
        "name": name,
        "passed": all(note.endswith("=ok") for note in notes),
        "latency_ms": (time.perf_counter() - started) * 1000,
        "notes": notes,
    }


if __name__ == "__main__":
    main()
