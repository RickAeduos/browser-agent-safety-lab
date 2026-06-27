from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

Strategy = Literal["recent_steps", "summary_memory", "retrieval_memory"]


@dataclass
class ContextPacket:
    strategy: Strategy
    content: str
    source_step_count: int
    estimated_chars: int


def build_context(
    strategy: Strategy,
    task_goal: str,
    history: list[dict[str, Any]],
    query: str = "",
    recent_n: int = 3,
) -> ContextPacket:
    if strategy == "recent_steps":
        selected = history[-recent_n:]
        content = "\n".join(_compact_step(step) for step in selected)
    elif strategy == "summary_memory":
        content = _summary(task_goal, history, recent_n)
    elif strategy == "retrieval_memory":
        content = _retrieve(history, query or task_goal, recent_n)
    else:
        raise ValueError(f"Unknown context strategy: {strategy}")
    return ContextPacket(strategy, content, len(history), len(content))


def _compact_step(step: dict[str, Any]) -> str:
    action = step.get("action", {})
    result = step.get("result", {})
    observation = step.get("observation", {})
    return (
        f"step={step.get('step_index')} "
        f"url={observation.get('url')} "
        f"action={action.get('type')} "
        f"ok={result.get('ok')} "
        f"error={result.get('error_type')}"
    )


def _summary(task_goal: str, history: list[dict[str, Any]], recent_n: int) -> str:
    completed = [step.get("action", {}).get("type") for step in history]
    recent = "\n".join(_compact_step(step) for step in history[-recent_n:])
    return (
        f"Goal: {task_goal}\n"
        f"Completed action types: {completed}\n"
        f"Recent steps:\n{recent}\n"
        "Open constraints: obey domain allowlist, stop when validator can pass."
    )


def _retrieve(history: list[dict[str, Any]], query: str, top_k: int) -> str:
    terms = [term.lower() for term in query.split() if term.strip()]
    scored: list[tuple[int, dict[str, Any]]] = []
    for step in history:
        blob = str(step).lower()
        score = sum(blob.count(term) for term in terms)
        if score:
            scored.append((score, step))
    scored.sort(key=lambda item: item[0], reverse=True)
    return "\n".join(_compact_step(step) for _, step in scored[:top_k])

