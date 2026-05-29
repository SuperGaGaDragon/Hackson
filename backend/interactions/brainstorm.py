"""
Created at: 2026-05-29
Created by: Codex
Last Modified at: 2026-05-29
Last Modified by: Codex
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from conversations.model import now_utc


MAX_SOURCE_MESSAGES = 80
MAX_IDEAS = 5
MAX_DISAGREEMENTS = 3
MAX_OPEN_QUESTIONS = 3

QUESTION_MARKERS = ("?", "？")
DISAGREEMENT_MARKERS = (
    "but",
    "however",
    "risk",
    "tradeoff",
    "trade-off",
    "problem",
    "concern",
    "challenge",
    "disagree",
    "但是",
    "不过",
    "风险",
    "问题",
    "担心",
    "分歧",
    "不同意",
    "反而",
)
IDEA_MARKERS = (
    "should",
    "could",
    "need",
    "suggest",
    "recommend",
    "maybe",
    "可以",
    "应该",
    "需要",
    "建议",
    "先",
    "做",
    "落地",
)


def build_idle_brainstorm_card(conversation: dict[str, Any], messages: list[dict[str, Any]]) -> dict[str, Any]:
    """Build a user-facing Idle brief from visible transcript rows only."""
    visible_messages = [
        message
        for message in messages[-MAX_SOURCE_MESSAGES:]
        if message.get("senderType") in {"user", "agent"} and (message.get("content") or "").strip()
    ]
    topic = _topic_from_conversation(conversation)
    source_ids = [message["id"] for message in visible_messages]
    snippets = _message_snippets(visible_messages)
    key_ideas = _ranked_snippets(snippets, IDEA_MARKERS, MAX_IDEAS)
    if not key_ideas:
        key_ideas = _ranked_snippets(snippets, (), min(MAX_IDEAS, 3))
    disagreements = _ranked_snippets(snippets, DISAGREEMENT_MARKERS, MAX_DISAGREEMENTS)
    open_questions = _question_snippets(snippets, MAX_OPEN_QUESTIONS)
    decision = _decision_from_snippets(snippets)
    title, goal = _suggested_mission(topic, key_ideas, open_questions, visible_messages)
    generated_at: datetime = now_utc()
    return {
        "conversationId": conversation["id"],
        "topic": topic or "Idle discussion",
        "keyIdeas": key_ideas,
        "disagreements": disagreements,
        "decision": decision,
        "openQuestions": open_questions,
        "suggestedMission": {
            "title": title,
            "goal": goal,
        },
        "sourceMessageIds": source_ids,
        "sourceMessageCount": len(source_ids),
        "generatedAt": generated_at,
    }


def _topic_from_conversation(conversation: dict[str, Any]) -> str:
    metadata = conversation.get("metadata") or {}
    topic = metadata.get("topicDirection") or metadata.get("discussionDirection") or ""
    if not topic and conversation.get("title") and conversation["title"] not in {"Idle", "Untitled"}:
        topic = conversation["title"]
    return _clean_text(topic, 180)


def _message_snippets(messages: list[dict[str, Any]]) -> list[str]:
    snippets: list[str] = []
    for message in messages:
        content = _clean_text(message.get("content") or "", 900)
        for sentence in _split_sentences(content):
            cleaned = _clean_text(sentence, 220)
            if len(cleaned) >= 6:
                snippets.append(cleaned)
    return snippets


def _split_sentences(content: str) -> list[str]:
    parts = re.split(r"(?<=[。！？!?])\s*|[\n\r]+", content)
    if len(parts) == 1:
        parts = re.split(r"[;；]", content)
    return [part.strip(" -•\t") for part in parts if part.strip(" -•\t")]


def _ranked_snippets(snippets: list[str], markers: tuple[str, ...], limit: int) -> list[str]:
    ranked: list[str] = []
    seen: set[str] = set()
    for snippet in reversed(snippets):
        lowered = snippet.lower()
        if markers and not any(marker in lowered for marker in markers):
            continue
        key = re.sub(r"\W+", "", lowered)[:90]
        if key in seen:
            continue
        seen.add(key)
        ranked.append(snippet)
        if len(ranked) >= limit:
            break
    return list(reversed(ranked))


def _question_snippets(snippets: list[str], limit: int) -> list[str]:
    questions = [
        snippet
        for snippet in snippets
        if any(marker in snippet for marker in QUESTION_MARKERS)
    ]
    return _dedupe_keep_tail(questions, limit)


def _decision_from_snippets(snippets: list[str]) -> str:
    decision_markers = ("decide", "agreed", "therefore", "next", "决定", "同意", "所以", "下一步", "先")
    candidates = [
        snippet
        for snippet in snippets
        if any(marker in snippet.lower() for marker in decision_markers)
    ]
    if candidates:
        return _clean_text(candidates[-1], 240)
    return "No firm decision yet."


def _suggested_mission(
    topic: str,
    key_ideas: list[str],
    open_questions: list[str],
    messages: list[dict[str, Any]],
) -> tuple[str, str]:
    cjk = _contains_cjk(" ".join([topic, *key_ideas, *open_questions]))
    title_base = topic or (key_ideas[0] if key_ideas else "Idle discussion")
    title = _clean_text(title_base, 72)
    if cjk:
        goal_parts = [
            f"基于这段 Idle 讨论，整理「{title}」的可执行方案。",
            "先提炼关键想法、分歧和未决问题，再产出一个可以继续推进的结果。",
        ]
        if open_questions:
            goal_parts.append(f"优先回答这个问题：{open_questions[-1]}")
        return title, "\n".join(goal_parts)
    goal_parts = [
        f"Turn the Idle discussion about \"{title}\" into a concrete Work result.",
        "Start by clarifying the key ideas, disagreements, and open questions, then produce a usable next artifact.",
    ]
    if open_questions:
        goal_parts.append(f"Prioritize this question: {open_questions[-1]}")
    if messages:
        goal_parts.append(f"Use the {len(messages)} linked Idle source messages as the brief.")
    return title, "\n".join(goal_parts)


def _dedupe_keep_tail(items: list[str], limit: int) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in reversed(items):
        key = re.sub(r"\W+", "", item.lower())[:90]
        if key in seen:
            continue
        seen.add(key)
        result.append(_clean_text(item, 220))
        if len(result) >= limit:
            break
    return list(reversed(result))


def _clean_text(value: str, max_length: int) -> str:
    cleaned = re.sub(r"\s+", " ", value).strip()
    if len(cleaned) <= max_length:
        return cleaned
    return cleaned[: max_length - 3].rstrip() + "..."


def _contains_cjk(value: str) -> bool:
    return any("\u4e00" <= char <= "\u9fff" for char in value)
