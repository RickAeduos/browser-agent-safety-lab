from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any

from packages.browser_harness.runner import project_root
from packages.eval_observatory.db import write_run_store
from packages.eval_observatory.metrics import compute_metrics


def load_summaries(run_dir: Path, tag: str | None = None) -> list[dict[str, Any]]:
    summaries = []
    for path in sorted(run_dir.glob("*/summary.json")):
        item = json.loads(path.read_text(encoding="utf-8"))
        if tag and tag not in item.get("tags", []):
            continue
        summaries.append(item)
    return summaries


def export_report(run_dir: Path, out: Path, tag: str | None = None) -> None:
    out.mkdir(parents=True, exist_ok=True)
    summaries = load_summaries(run_dir, tag=tag)
    metrics = compute_metrics(summaries)
    write_run_store(summaries, out / "run_store.duckdb")
    md = render_markdown(metrics, summaries)
    (out / "index.md").write_text(md, encoding="utf-8")
    html_body = (
        "<html><meta charset='utf-8'><title>Browser Agent Safety Lab Report</title>"
        "<style>body{font-family:Arial,sans-serif;margin:32px;line-height:1.45}"
        "pre{background:#f6f8fa;padding:8px;overflow:auto}.passed{color:#116329}"
        ".failed{color:#a40e26}</style><body>"
        f"{markdown_to_simple_html(md)}</body></html>"
    )
    (out / "index.html").write_text(html_body, encoding="utf-8")
    print(f"report={out / 'index.html'}")


def render_markdown(metrics: dict[str, Any], summaries: list[dict[str, Any]]) -> str:
    lines = [
        "# Browser Agent Safety Lab Report",
        "",
        "## Safety Scoreboard",
        "",
        f"- total: {metrics['total']}",
        f"- passed: {metrics['passed']}",
        f"- failed: {metrics['failed']}",
        f"- success_rate: {metrics['success_rate']}",
        f"- avg_steps: {metrics['avg_steps']}",
        f"- input_tokens: {metrics['input_tokens']}",
        f"- output_tokens: {metrics['output_tokens']}",
        f"- estimated_cost_usd: {metrics['estimated_cost_usd']}",
        "",
        "## Risk Coverage",
        "",
    ]
    if metrics.get("risk_counts"):
        for risk, count in sorted(metrics["risk_counts"].items()):
            lines.append(f"- {risk}: {count}")
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Agent Runs",
            "",
        ]
    )
    for agent, count in sorted(metrics.get("agent_counts", {}).items()):
        lines.append(f"- {agent}: {count}")
    lines.extend(
        [
            "",
            "## Runs",
            "",
            "| task | agent | passed | risk | steps | label | last_action | validator_evidence | trace |",
            "|---|---|---:|---|---:|---|---|---|---|",
        ]
    )
    for item in summaries:
        trace = item.get("trace_dir", "")
        risk = ", ".join(tag.removeprefix("risk:") for tag in item.get("risk_tags", []))
        last_action = _compact(item.get("last_action", {}), 120)
        validation = item.get("validation", {})
        validator_evidence = _compact(
            {
                "message": validation.get("message"),
                "evidence": validation.get("evidence"),
                "last_result": item.get("last_result"),
            },
            180,
        )
        lines.append(
            f"| {item.get('task_id')} | {item.get('agent_type')} | {item.get('passed')} | "
            f"{risk} | {item.get('total_steps')} | {item.get('failure_label')} | "
            f"{last_action} | {validator_evidence} | `{trace}` |"
        )
    lines.extend(["", "## Failure Counts", ""])
    for label, count in metrics["failure_counts"].items():
        lines.append(f"- {label}: {count}")
    return "\n".join(lines)


def markdown_to_simple_html(md: str) -> str:
    rows = []
    for line in md.splitlines():
        if line.startswith("# "):
            rows.append(f"<h1>{html.escape(line[2:])}</h1>")
        elif line.startswith("## "):
            rows.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.startswith("- "):
            rows.append(f"<li>{html.escape(line[2:])}</li>")
        elif line.startswith("|"):
            rows.append(f"<pre>{html.escape(line)}</pre>")
        elif line.strip():
            rows.append(f"<p>{html.escape(line)}</p>")
    return "\n".join(rows)


def _compact(value: Any, limit: int) -> str:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    text = text.replace("|", "/").replace("\n", " ")
    if len(text) > limit:
        return text[: limit - 3] + "..."
    return text


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", default="traces")
    parser.add_argument("--out", default="reports/latest")
    parser.add_argument("--tag", default=None, help="Only include runs whose summary contains this tag.")
    args = parser.parse_args()
    root = project_root()
    export_report(root / args.run_dir, root / args.out, tag=args.tag)


if __name__ == "__main__":
    main()
