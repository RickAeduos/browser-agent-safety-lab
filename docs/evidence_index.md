# Evidence Index

| 证据 | 路径 |
|---|---|
| 环境自检 | `scripts\doctor.ps1` |
| 单任务运行 | `scripts\run_one_task.ps1` |
| 批量评测 | `scripts\run_eval.ps1` |
| 报告导出 | `scripts\export_report.ps1` |
| 任务定义 | `tasks\smoke\*.yaml` |
| benchmark adapter subset | `tasks\benchmark_adapters\miniwob_like_click_button.yaml` |
| trace | `traces\*\trace.jsonl` |
| 截图 | `traces\*\screenshots\*.png` |
| 工具审计 | `traces\*\tool_audit.jsonl` |
| 报告 | `reports\latest\index.html` |
| Run store | `reports\latest\run_store.duckdb` |
| Context experiment | `reports\context_memory_experiment.md` |
| Real DeepSeek LLM smoke | `scripts\run_one_task.ps1 ... --agent llm` |
| 安全策略 | `docs\safety_policy.md` |
| 架构说明 | `docs\architecture.md` |
| GitHub Browser Agent 对比与前沿方向 | `docs\github_browser_agent_landscape_zh.md` |
| Adversarial suite | `tasks\adversarial\*.yaml` |
| Adversarial mock sites | `apps\mock_sites\adversarial\*` |
| Adversarial suite docs | `docs\adversarial_suite.md` |
| Optional Skyvern adapter boundary | `docs\skyvern_adapter.md` |
