from packages.agents.actions import validate_action
from packages.agents.llm_agent import _observation_satisfies_simple_validator
from packages.agents.model_client import extract_action_json
from packages.browser_harness.task_schema import TaskSpec, ValidatorSpec


def test_validate_fill_action():
    action, error = validate_action({"type": "fill", "selector": "#name", "value": "Alice"})
    assert error is None
    assert action is not None
    assert action.type == "fill"


def test_reject_missing_selector():
    action, error = validate_action({"type": "click"})
    assert action is None
    assert "requires field" in error


def test_reject_disallowed_action():
    action, error = validate_action({"type": "tool", "tool_name": "kb_search"}, allowed_actions=["goto"])
    assert action is None
    assert "not allowed" in error


def test_extract_action_json_from_fenced_content():
    action = extract_action_json('```json\n{"type":"done"}\n```')
    assert action == {"type": "done"}


def test_llm_precheck_detects_text_validator():
    task = TaskSpec(
        id="t",
        title="T",
        start_url="about:blank",
        goal="find answer",
        validators=[ValidatorSpec(type="text_present", params={"text": "answer found"})],
    )
    assert _observation_satisfies_simple_validator(task, {"text_excerpt": "answer found"})
