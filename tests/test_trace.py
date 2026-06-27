import json
from pathlib import Path

from packages.browser_harness.trace import TraceWriter


def test_trace_writer(tmp_path: Path):
    writer = TraceWriter(tmp_path, "task_a", "rule")
    writer.write_step({"step_index": 0, "action": {"type": "done"}, "result": {"ok": True}})
    summary_path = writer.write_summary({"passed": True})
    assert writer.path.exists()
    assert summary_path.exists()
    record = json.loads(writer.path.read_text(encoding="utf-8").splitlines()[0])
    assert record["task_id"] == "task_a"
    assert record["agent_type"] == "rule"

