from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class ValidatorSpec(BaseModel):
    type: str
    params: dict[str, Any] = Field(default_factory=dict)


class TaskSpec(BaseModel):
    id: str
    title: str
    start_url: str
    goal: str
    allowed_domains: list[str] = Field(default_factory=lambda: ["127.0.0.1", "localhost"])
    allowed_actions: list[str] = Field(
        default_factory=lambda: ["goto", "click", "fill", "press", "extract_text", "screenshot", "tool", "done"]
    )
    max_steps: int = 12
    fixtures: dict[str, Any] = Field(default_factory=dict)
    validators: list[ValidatorSpec] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


def load_task(path: str | Path) -> TaskSpec:
    task_path = Path(path)
    with task_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Task file must contain a mapping: {task_path}")
    return TaskSpec(**data)

