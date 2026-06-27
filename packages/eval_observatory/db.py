from __future__ import annotations

from pathlib import Path
from typing import Any

import duckdb


def write_run_store(summaries: list[dict[str, Any]], db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(db_path)) as conn:
        conn.execute(
            """
            create or replace table runs (
                run_id varchar,
                task_id varchar,
                agent_type varchar,
                passed boolean,
                total_steps integer,
                failure_label varchar,
                stop_reason varchar,
                input_tokens integer,
                output_tokens integer,
                estimated_cost_usd double,
                trace_dir varchar
            )
            """
        )
        rows = [
            (
                item.get("run_id"),
                item.get("task_id"),
                item.get("agent_type"),
                bool(item.get("passed")),
                int(item.get("total_steps", 0)),
                item.get("failure_label"),
                item.get("stop_reason"),
                int(item.get("input_tokens", 0)),
                int(item.get("output_tokens", 0)),
                float(item.get("estimated_cost_usd", 0.0)),
                item.get("trace_dir"),
            )
            for item in summaries
        ]
        conn.executemany("insert into runs values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", rows)


def count_runs(db_path: Path) -> int:
    with duckdb.connect(str(db_path)) as conn:
        return int(conn.execute("select count(*) from runs").fetchone()[0])

