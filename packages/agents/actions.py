from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

ActionType = Literal["goto", "click", "fill", "press", "extract_text", "screenshot", "tool", "done"]


class Action(BaseModel):
    type: ActionType
    selector: str | None = None
    value: str | None = None
    url: str | None = None
    key: str | None = None
    expect_download: bool = False
    tool_name: str | None = None
    input: dict[str, Any] = Field(default_factory=dict)
    note: str | None = None


def validate_action(data: dict[str, Any], allowed_actions: list[str] | None = None) -> tuple[Action | None, str | None]:
    try:
        action = Action(**data)
    except Exception as exc:  # pydantic keeps the useful detail in str(exc)
        return None, str(exc)

    if allowed_actions and action.type not in allowed_actions:
        return None, f"Action '{action.type}' is not allowed for this task"

    required_by_type = {
        "goto": ["url"],
        "click": ["selector"],
        "fill": ["selector", "value"],
        "press": ["selector", "key"],
        "extract_text": ["selector"],
        "tool": ["tool_name"],
    }
    for field in required_by_type.get(action.type, []):
        if getattr(action, field) in (None, ""):
            return None, f"Action '{action.type}' requires field '{field}'"

    return action, None

