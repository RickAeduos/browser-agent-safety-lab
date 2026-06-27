from pathlib import Path

from packages.tool_runtime.registry import ToolRuntime


def test_path_denied(tmp_path: Path):
    project = tmp_path / "project"
    traces = project / "traces"
    (project / "docs").mkdir(parents=True)
    traces.mkdir(parents=True)
    runtime = ToolRuntime(project, traces, permission_preset="eval_runner")
    result = runtime.call("file_read_limited", {"path": "..\\..\\outside.txt"})
    assert result["ok"] is False
    assert result["error_type"] == "path_denied"


def test_sensitive_file_denied_inside_allowed_docs(tmp_path: Path):
    project = tmp_path / "project"
    traces = project / "traces"
    docs = project / "docs"
    docs.mkdir(parents=True)
    traces.mkdir(parents=True)
    (docs / "API_key.txt").write_text("should-not-be-returned", encoding="utf-8")
    runtime = ToolRuntime(project, traces, permission_preset="eval_runner")
    result = runtime.call("file_read_limited", {"path": "docs/API_key.txt"})
    assert result["ok"] is False
    assert result["error_type"] == "secret_path_denied"
    assert "should-not-be-returned" not in str(result)


def test_kb_search_project_docs(tmp_path: Path):
    project = tmp_path / "project"
    traces = project / "traces"
    docs = project / "docs"
    docs.mkdir(parents=True)
    traces.mkdir(parents=True)
    (docs / "local.md").write_text("RA0L1 operating voltage range evidence.", encoding="utf-8")
    runtime = ToolRuntime(project, traces, permission_preset="eval_runner")
    result = runtime.call("kb_search", {"query": "RA0L1 voltage", "top_k": 2})
    assert result["ok"] is True
    assert result["results"]
