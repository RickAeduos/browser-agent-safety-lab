# Browser Agent Safety Lab

Adversarial eval harness for browser agents.

This project tests whether a browser agent can stay inside safety boundaries when a webpage tries to manipulate it. It uses local malicious fixtures, Playwright execution, structured traces, validators, and an HTML safety report.

It is not another general-purpose browser agent. It is the test lab around one.

## What It Checks

- prompt injection obedience
- local secret file access
- forbidden external navigation
- untrusted downloads
- wrong-target clicks
- blocked dangerous actions

## Quickstart

```powershell
cd F:\AI_prj\deepseek_browser_agent_portfolio
uv venv --python 3.12
.\.venv\Scripts\python.exe -m pip install -U pip
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m playwright install chromium

.\scripts\doctor.ps1
.\scripts\run_eval.ps1 --suite adversarial --agent rule
.\scripts\export_report.ps1 --run-dir .\traces --out .\reports\latest --tag adversarial
```

Open the report:

```text
F:\AI_prj\deepseek_browser_agent_portfolio\reports\latest\index.html
```

## Demo Output

The adversarial suite contains 12 deterministic tasks across five risk classes:

- `risk:prompt_injection`
- `risk:secret_exfiltration`
- `risk:forbidden_navigation`
- `risk:unsafe_download`
- `risk:wrong_target_click`

The report shows a safety scoreboard, risk coverage, agent type, last action, validator evidence, and trace directory for each run.

## Agent Modes

```powershell
.\scripts\run_eval.ps1 --suite adversarial --agent rule
.\scripts\run_one_task.ps1 .\tasks\adversarial\prompt_injection_hidden_ignore.yaml --agent fake_llm --max-steps 6
.\scripts\run_one_task.ps1 .\tasks\adversarial\prompt_injection_hidden_ignore.yaml --agent llm --max-steps 6 --max-cost-usd 0.05
```

Supported modes:

- `rule`: deterministic baseline for CI and regression.
- `fake_llm`: no-cost model loop for trace/debug demos.
- `llm`: real DeepSeek Chat Completions client.

DeepSeek API key lookup:

1. `DEEPSEEK_API_KEY`
2. local file `docs\API_key.txt`

`docs\API_key.txt` is ignored by git.

## Safety Model

The lab treats webpage content as untrusted input.

Current enforcement:

- domain allowlist blocks external `goto` actions
- sensitive local paths are denied even if they sit under an otherwise readable folder
- downloads can be disabled per task with `fixtures.allow_downloads: false`
- tool calls are audited to JSONL
- validators check both positive completion and absence of unsafe behavior

This is portfolio-grade infrastructure, not a production sandbox. It does not provide multi-tenant isolation, credential brokering, or full OS-level containment.

## Skyvern Adapter Boundary

Skyvern is a strong production browser workflow project. This repo does not vendor or reimplement it.

The intended integration is an optional adapter:

```text
Skyvern/external agent -> Browser Agent Safety Lab task -> trace -> safety validators -> report
```

Core CI stays independent of Skyvern so the safety suite remains clone-and-run.

## Project Shape

```text
tasks/adversarial/        adversarial task YAML
apps/mock_sites/          local malicious and benign fixtures
packages/browser_harness/ task runner, browser session, validators, traces
packages/tool_runtime/    permissioned tool runtime and audit log
packages/eval_observatory metrics, batch runner, report export
reports/latest/           generated GitHub Pages-ready report
```

## GitHub Pages

The repository includes GitHub Actions workflows for CI and Pages deployment. In repository settings, set Pages source to GitHub Actions. The Pages workflow runs the adversarial rule-agent suite and publishes `reports/latest`.

## What This Proves

The project demonstrates browser-agent infrastructure work:

```text
task schema -> browser action -> trace -> validator -> safety label -> report
```

The value is not that the included rule agent is smart. The value is that unsafe browser-agent behavior becomes reproducible, auditable, and reportable.
