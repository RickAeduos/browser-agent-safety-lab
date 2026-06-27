from __future__ import annotations

import argparse
import json
from pathlib import Path

from packages.agents.context_policy import build_context
from packages.browser_harness.runner import project_root


def load_trace(trace_path: Path) -> list[dict]:
    if not trace_path.exists():
        return []
    return [json.loads(line) for line in trace_path.read_text(encoding="utf-8").splitlines() if line.strip()]


def export_context_experiment(run_dir: Path, out: Path, max_runs: int = 5) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for trace_path in sorted(run_dir.glob("*/trace.jsonl"))[:max_runs]:
        history = load_trace(trace_path)
        if not history:
            continue
        goal = f"Analyze trace {trace_path.parent.name}"
        for strategy in ["recent_steps", "summary_memory", "retrieval_memory"]:
            packet = build_context(strategy, goal, history, query=goal, recent_n=3)
            rows.append(
                {
                    "run_id": trace_path.parent.name,
                    "strategy": strategy,
                    "source_step_count": packet.source_step_count,
                    "estimated_chars": packet.estimated_chars,
                }
            )
    lines = [
        "# Context / Memory Experiment Report",
        "",
        "| run_id | strategy | source_step_count | estimated_chars |",
        "|---|---|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['run_id']} | {row['strategy']} | {row['source_step_count']} | {row['estimated_chars']} |"
        )
    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            "- `recent_steps` preserves exact recent actions and errors.",
            "- `summary_memory` is shorter when histories grow, but may drop details.",
            "- `retrieval_memory` depends on query overlap and can be empty for unrelated traces.",
        ]
    )
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"context_experiment={out}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", default="traces")
    parser.add_argument("--out", default="reports/context_memory_experiment.md")
    parser.add_argument("--max-runs", type=int, default=5)
    args = parser.parse_args()
    root = project_root()
    export_context_experiment(root / args.run_dir, root / args.out, args.max_runs)


if __name__ == "__main__":
    main()

