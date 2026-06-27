from __future__ import annotations

from typing import Any


def compute_metrics(summaries: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(summaries)
    passed = sum(1 for item in summaries if item.get("passed"))
    failure_counts: dict[str, int] = {}
    risk_counts: dict[str, int] = {}
    agent_counts: dict[str, int] = {}
    for item in summaries:
        label = item.get("failure_label", "unknown")
        failure_counts[label] = failure_counts.get(label, 0) + 1
        agent = item.get("agent_type", "unknown")
        agent_counts[agent] = agent_counts.get(agent, 0) + 1
        for tag in item.get("tags", []):
            if tag.startswith("risk:"):
                risk = tag.removeprefix("risk:")
                risk_counts[risk] = risk_counts.get(risk, 0) + 1
    return {
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "success_rate": round(passed / total, 3) if total else 0.0,
        "avg_steps": round(sum(item.get("total_steps", 0) for item in summaries) / total, 2) if total else 0.0,
        "input_tokens": sum(item.get("input_tokens", 0) for item in summaries),
        "output_tokens": sum(item.get("output_tokens", 0) for item in summaries),
        "estimated_cost_usd": round(sum(item.get("estimated_cost_usd", 0) for item in summaries), 6),
        "failure_counts": failure_counts,
        "risk_counts": risk_counts,
        "agent_counts": agent_counts,
    }
