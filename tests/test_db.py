from pathlib import Path

from packages.eval_observatory.db import count_runs, write_run_store


def test_write_run_store(tmp_path: Path):
    db_path = tmp_path / "runs.duckdb"
    write_run_store(
        [
            {
                "run_id": "r1",
                "task_id": "t1",
                "agent_type": "rule",
                "passed": True,
                "total_steps": 2,
                "failure_label": "passed",
                "stop_reason": "completed",
                "input_tokens": 0,
                "output_tokens": 0,
                "estimated_cost_usd": 0,
                "trace_dir": "trace",
            }
        ],
        db_path,
    )
    assert count_runs(db_path) == 1

