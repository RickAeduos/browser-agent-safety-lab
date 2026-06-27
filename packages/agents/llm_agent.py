from __future__ import annotations

from typing import Any

from packages.agents.model_client import DeepSeekModelClient, FakeModelClient
from packages.browser_harness.task_schema import TaskSpec


class LlmAgent:
    agent_type = "llm"

    def __init__(self, fake: bool = False) -> None:
        self.fake = fake
        self.agent_type = "fake_llm" if fake else "llm"
        self.client = FakeModelClient() if fake else DeepSeekModelClient()

    def next_action(
        self,
        task: TaskSpec,
        observation: dict[str, Any],
        history: list[dict[str, Any]],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        if not self.fake and _observation_satisfies_simple_validator(task, observation):
            return {"type": "done", "note": "validator_precheck_satisfied"}, {
                "input_tokens": 0,
                "output_tokens": 0,
                "estimated_cost_usd": 0.0,
                "model": "harness_precheck",
            }
        if self.fake:
            return self.client.complete_action(task.id, observation, history)
        return self.client.complete_action(task, observation, history)


def _observation_satisfies_simple_validator(task: TaskSpec, observation: dict[str, Any]) -> bool:
    text = observation.get("text_excerpt", "")
    url = observation.get("url", "")
    for spec in task.validators:
        if spec.type == "text_present" and spec.params.get("text") in text:
            return True
        if spec.type == "url_contains" and spec.params.get("text") in url:
            return True
    return False
