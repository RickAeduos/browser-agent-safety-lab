from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


class TraceWriter:
    def __init__(self, trace_root: Path, task_id: str, agent_type: str) -> None:
        self.run_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{task_id}_{uuid.uuid4().hex[:8]}"
        self.trace_dir = trace_root / self.run_id
        self.trace_dir.mkdir(parents=True, exist_ok=True)
        self.path = self.trace_dir / "trace.jsonl"
        self.task_id = task_id
        self.agent_type = agent_type

    def write_step(self, record: dict[str, Any]) -> None:
        record = {
            "run_id": self.run_id,
            "task_id": self.task_id,
            "agent_type": self.agent_type,
            "timestamp": utc_now(),
            **record,
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    def write_summary(self, summary: dict[str, Any]) -> Path:
        summary = {
            "run_id": self.run_id,
            "task_id": self.task_id,
            "agent_type": self.agent_type,
            "timestamp": utc_now(),
            **summary,
        }
        path = self.trace_dir / "summary.json"
        path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def read_steps(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        return [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]

