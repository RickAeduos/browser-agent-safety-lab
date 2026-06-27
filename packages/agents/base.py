from __future__ import annotations

from typing import Any, Protocol

from packages.browser_harness.task_schema import TaskSpec


class Agent(Protocol):
    agent_type: str

    def next_action(
        self,
        task: TaskSpec,
        observation: dict[str, Any],
        history: list[dict[str, Any]],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Return an action dict and usage metadata."""

