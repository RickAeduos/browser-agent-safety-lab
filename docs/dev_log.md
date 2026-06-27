# Development Log

## 2026-06-27

目标：按执行计划创建 Browser Agent Harness MVP。

完成：

- 建立项目骨架。
- 实现 task schema、runner、rule agent、trace、validator、tool runtime、eval runner 和 report exporter。
- 放入本地 mock sites 和 deterministic smoke tasks。

边界：

- 已实现：本地 deterministic smoke eval。
- 模拟：LLM agent 默认 fake model；没有 API key 也可演示。
- 未来工作：外部 benchmark adapter、真实 LLM 对比、context/memory 实验。

## 2026-06-27 Real DeepSeek LLM

完成：

- 将 `--agent llm` 从 fake client 切换为真实 DeepSeek Chat Completions。
- API key 读取顺序：环境变量 `DEEPSEEK_API_KEY`，然后 `docs\API_key.txt`。
- `docs\API_key.txt` 已加入 `.gitignore`。
- 保留 `--agent fake_llm` 用于无 API 回归。
- 增加 LLM completion pre-check：observation 已满足简单 validator 时直接 `done`，减少无效点击和 token。

验证命令：

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pytest
.\scripts\run_one_task.ps1 .\tasks\smoke\docs_search.yaml --agent llm --max-steps 6 --max-cost-usd 0.05
```

验证结果：

- ruff: passed
- pytest: 12 passed
- real DeepSeek LLM docs_search: passed
- steps: 2
- stop_reason: completed
- input_tokens: 314
- output_tokens: 25
- estimated_cost_usd: 0.000051

