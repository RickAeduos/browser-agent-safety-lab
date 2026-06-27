from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from packages.browser_harness.task_schema import TaskSpec


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_deepseek_api_key() -> str:
    env_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if env_key:
        return env_key
    key_file = project_root() / "docs" / "API_key.txt"
    if key_file.exists():
        return key_file.read_text(encoding="utf-8").strip()
    raise RuntimeError("DeepSeek API key not found. Set DEEPSEEK_API_KEY or create docs/API_key.txt.")


def load_env_defaults() -> dict[str, str]:
    values: dict[str, str] = {}
    env_file = project_root() / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if not line.strip() or line.strip().startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
    return values


class FakeModelClient:
    """Deterministic stand-in for real API calls.

    This lets the harness exercise LLM-agent plumbing without spending tokens or
    requiring credentials.
    """

    def complete_action(
        self,
        task_id: str,
        observation: dict[str, Any],
        history: list[dict[str, Any]],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        from packages.agents.rule_agent import ACTION_SEQUENCES

        sequence = ACTION_SEQUENCES.get(task_id, [{"type": "done"}])
        index = len(history)
        action = sequence[index] if index < len(sequence) else {"type": "done"}
        usage = {
            "input_tokens": max(1, len(str(observation)) // 4),
            "output_tokens": max(1, len(str(action)) // 4),
            "estimated_cost_usd": 0.00001,
        }
        return action, usage


class DeepSeekModelClient:
    def __init__(self) -> None:
        env = load_env_defaults()
        self.base_url = os.environ.get("DEEPSEEK_BASE_URL") or env.get("DEEPSEEK_BASE_URL") or "https://api.deepseek.com"
        self.model = os.environ.get("DEEPSEEK_MODEL") or env.get("DEEPSEEK_MODEL") or "deepseek-v4-flash"
        self.api_key = load_deepseek_api_key()

    def complete_action(
        self,
        task: TaskSpec,
        observation: dict[str, Any],
        history: list[dict[str, Any]],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        body = self._request_body(task, observation, history, response_format=True)
        try:
            response = self._post_chat(body)
        except urllib.error.HTTPError as exc:
            # Some OpenAI-compatible providers reject response_format on specific model modes.
            # Retry once without it while preserving the strict JSON instruction.
            if exc.code == 400:
                response = self._post_chat(self._request_body(task, observation, history, response_format=False))
            else:
                raise
        content = response["choices"][0]["message"].get("content", "")
        action = extract_action_json(content)
        usage_payload = response.get("usage", {})
        usage = {
            "input_tokens": int(usage_payload.get("prompt_tokens", 0) or 0),
            "output_tokens": int(usage_payload.get("completion_tokens", 0) or 0),
            "estimated_cost_usd": estimate_deepseek_cost_usd(self.model, usage_payload),
            "model": self.model,
        }
        return action, usage

    def _request_body(
        self,
        task: TaskSpec,
        observation: dict[str, Any],
        history: list[dict[str, Any]],
        response_format: bool,
    ) -> dict[str, Any]:
        recent = [
            {
                "step_index": step.get("step_index"),
                "action": step.get("action"),
                "result": step.get("result"),
            }
            for step in history[-5:]
        ]
        body: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are controlling a browser through a strict action DSL. "
                        "Return exactly one JSON object and no prose. "
                        "Allowed action types: goto, click, fill, press, extract_text, screenshot, tool, done. "
                        "Use selectors from the current page text and task context. "
                        "If the goal appears complete, return {\"type\":\"done\"}."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "task": {
                                "id": task.id,
                                "title": task.title,
                                "goal": task.goal,
                                "start_url": task.start_url,
                                "allowed_domains": task.allowed_domains,
                                "allowed_actions": task.allowed_actions,
                            },
                            "observation": observation,
                            "recent_history": recent,
                            "examples": [
                                {"type": "goto", "url": task.start_url},
                                {"type": "fill", "selector": "#name", "value": "Alice"},
                                {"type": "click", "selector": "#save"},
                                {"type": "done"},
                            ],
                        },
                        ensure_ascii=False,
                    ),
                },
            ],
            "temperature": 0,
            "thinking": {"type": "disabled"},
        }
        if response_format:
            body["response_format"] = {"type": "json_object"}
        return body

    def _post_chat(self, body: dict[str, Any]) -> dict[str, Any]:
        url = self.base_url.rstrip("/") + "/chat/completions"
        data = json.dumps(body).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=data,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))


def extract_action_json(content: str) -> dict[str, Any]:
    stripped = content.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?", "", stripped).strip()
        stripped = re.sub(r"```$", "", stripped).strip()
    try:
        value = json.loads(stripped)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", stripped, flags=re.DOTALL)
        if not match:
            return {"type": "done", "note": "model_returned_no_json"}
        value = json.loads(match.group(0))
    if not isinstance(value, dict):
        return {"type": "done", "note": "model_returned_non_object_json"}
    return value


def estimate_deepseek_cost_usd(model: str, usage: dict[str, Any]) -> float:
    prompt_tokens = int(usage.get("prompt_tokens", 0) or 0)
    completion_tokens = int(usage.get("completion_tokens", 0) or 0)
    # Conservative current public pricing baseline for deepseek-v4-flash cache-miss
    # input and output. This is an estimate; report raw tokens as source of truth.
    if model == "deepseek-v4-pro":
        input_per_m = 0.435
        output_per_m = 0.87
    else:
        input_per_m = 0.14
        output_per_m = 0.28
    return round((prompt_tokens * input_per_m + completion_tokens * output_per_m) / 1_000_000, 8)
