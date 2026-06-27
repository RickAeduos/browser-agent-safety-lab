from __future__ import annotations

import argparse
import json

from packages.browser_harness.runner import project_root, run_task
from packages.eval_observatory.metrics import compute_metrics


def run_suite(suite: str, agent: str, max_tasks: int | None, max_steps: int | None, max_cost_usd: float | None) -> dict:
    root = project_root()
    suite_dir = root / "tasks" / suite
    task_paths = sorted(suite_dir.glob("*.yaml"))
    if max_tasks:
        task_paths = task_paths[:max_tasks]
    summaries = [
        run_task(path, agent_type=agent, max_steps=max_steps, max_cost_usd=max_cost_usd)
        for path in task_paths
    ]
    metrics = compute_metrics(summaries)
    out_dir = root / "reports" / f"{suite}_{agent}_latest"
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {"suite": suite, "agent": agent, "metrics": metrics, "runs": summaries}
    (out_dir / "suite_summary.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload["metrics"], ensure_ascii=False, indent=2))
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", default="smoke")
    parser.add_argument("--agent", default="rule", choices=["rule", "llm", "fake_llm"])
    parser.add_argument("--max-tasks", type=int, default=None)
    parser.add_argument("--max-steps", type=int, default=None)
    parser.add_argument("--max-cost-usd", type=float, default=None)
    args = parser.parse_args()
    run_suite(args.suite, args.agent, args.max_tasks, args.max_steps, args.max_cost_usd)


if __name__ == "__main__":
    main()

