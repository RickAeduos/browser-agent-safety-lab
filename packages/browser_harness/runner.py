from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from packages.agents.actions import Action, validate_action
from packages.agents.llm_agent import LlmAgent
from packages.agents.rule_agent import RuleAgent
from packages.browser_harness.browser import BrowserSession
from packages.browser_harness.static_server import StaticServer
from packages.browser_harness.task_schema import TaskSpec, load_task
from packages.browser_harness.trace import TraceWriter
from packages.browser_harness.validators import validate_task
from packages.tool_runtime.registry import ToolRuntime


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def run_task(
    task_path: str | Path,
    agent_type: str = "rule",
    max_steps: int | None = None,
    max_cost_usd: float | None = None,
    headless: bool = True,
) -> dict[str, Any]:
    root = project_root()
    task = load_task(task_path)
    agent = LlmAgent(fake=agent_type == "fake_llm") if agent_type in {"llm", "fake_llm"} else RuleAgent()
    trace = TraceWriter(root / "traces", task.id, agent.agent_type)
    steps: list[dict[str, Any]] = []
    history: list[dict[str, Any]] = []
    totals = {"input_tokens": 0, "output_tokens": 0, "estimated_cost_usd": 0.0}
    stop_reason = "completed"
    static_root = root / "apps" / "mock_sites"
    limit_steps = max_steps or task.max_steps
    cost_limit = max_cost_usd if max_cost_usd is not None and max_cost_usd >= 0 else None

    with StaticServer(static_root, port=int(task.fixtures.get("static_port", 8765))):
        with BrowserSession(trace.trace_dir, headless=headless) as browser:
            tools = ToolRuntime(root, root / "traces", browser=browser, permission_preset="eval_runner")
            tools.set_audit_path(trace.trace_dir / "tool_audit.jsonl")
            for step_index in range(limit_steps):
                observation = browser.observe()
                action_data, usage = agent.next_action(task, observation, history)
                for key in totals:
                    totals[key] += usage.get(key, 0)
                action, error = validate_action(action_data, task.allowed_actions)
                if error:
                    result = {"ok": False, "error_type": "invalid_action", "message": error}
                    record = _step_record(step_index, observation, action_data, result, usage, browser, trace)
                    trace.write_step(record)
                    steps.append(record)
                    stop_reason = "invalid_action"
                    break
                result = execute_action(action, browser, task, tools, trace.run_id, step_index)
                record = _step_record(step_index, observation, action.model_dump(), result, usage, browser, trace)
                trace.write_step(record)
                steps.append(record)
                history.append(record)
                if cost_limit is not None and totals["estimated_cost_usd"] > cost_limit:
                    stop_reason = "max_cost_usd"
                    break
                if action.type == "done":
                    break
            else:
                stop_reason = "max_steps"

            validation = validate_task(task, browser, steps, trace.trace_dir)

    last_step = steps[-1] if steps else {}
    summary = {
        "task_id": task.id,
        "title": task.title,
        "goal": task.goal,
        "tags": task.tags,
        "risk_tags": [tag for tag in task.tags if tag.startswith("risk:")],
        "task_path": str(task_path),
        "agent_type": agent.agent_type,
        "passed": validation.passed,
        "validation": validation.to_dict(),
        "failure_label": "passed" if validation.passed else validation.label,
        "total_steps": len(steps),
        "stop_reason": stop_reason,
        "last_action": last_step.get("action", {}),
        "last_result": {
            "ok": last_step.get("result", {}).get("ok"),
            "error_type": last_step.get("result", {}).get("error_type"),
            "message": str(last_step.get("result", {}).get("message", ""))[:240],
        },
        "input_tokens": totals["input_tokens"],
        "output_tokens": totals["output_tokens"],
        "estimated_cost_usd": round(totals["estimated_cost_usd"], 6),
        "trace_path": str(trace.path),
        "trace_dir": str(trace.trace_dir),
    }
    trace.write_summary(summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def execute_action(action: Action, browser: BrowserSession, task: TaskSpec, tools: ToolRuntime, run_id: str, step_index: int) -> dict[str, Any]:
    if action.type == "goto":
        return browser.goto(action.url or "", task.allowed_domains)
    if action.type == "click":
        if action.expect_download and not task.fixtures.get("allow_downloads", True):
            return {
                "ok": False,
                "duration_ms": 0.0,
                "error_type": "unsafe_download_blocked",
                "message": "Download blocked because this task does not allow downloads",
            }
        return browser.click(action.selector or "", expect_download=action.expect_download)
    if action.type == "fill":
        return browser.fill(action.selector or "", action.value or "")
    if action.type == "press":
        return browser.press(action.selector or "", action.key or "")
    if action.type == "extract_text":
        return browser.extract_text(action.selector or "body")
    if action.type == "screenshot":
        return {"ok": True, "screenshot_path": browser.screenshot(step_index)}
    if action.type == "tool":
        return tools.call(action.tool_name or "", action.input, run_id=run_id, step_index=step_index)
    if action.type == "done":
        return {"ok": True, "message": "Agent marked task done"}
    return {"ok": False, "error_type": "invalid_action", "message": f"Unsupported action: {action.type}"}


def _step_record(
    step_index: int,
    observation: dict[str, Any],
    action: dict[str, Any],
    result: dict[str, Any],
    usage: dict[str, Any],
    browser: BrowserSession,
    trace: TraceWriter,
) -> dict[str, Any]:
    screenshot = browser.screenshot(step_index)
    return {
        "step_index": step_index,
        "observation": observation,
        "action": action,
        "result": result,
        "usage": usage,
        "screenshot_path": screenshot,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("task_path")
    parser.add_argument("--agent", default="rule", choices=["rule", "llm", "fake_llm"])
    parser.add_argument("--max-steps", type=int, default=None)
    parser.add_argument("--max-cost-usd", type=float, default=None)
    parser.add_argument("--headed", action="store_true")
    args = parser.parse_args()
    run_task(args.task_path, args.agent, args.max_steps, args.max_cost_usd, headless=not args.headed)


if __name__ == "__main__":
    main()
