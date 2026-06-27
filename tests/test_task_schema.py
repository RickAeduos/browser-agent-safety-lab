from pathlib import Path

from packages.browser_harness.task_schema import load_task


def test_load_task_schema():
    task = load_task(Path("tasks/smoke/local_form_fill.yaml"))
    assert task.id == "local_form_fill"
    assert "goto" in task.allowed_actions
    assert task.validators[0].type == "text_present"

