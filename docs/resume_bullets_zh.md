# Resume Bullets

中文：

- 构建 Browser Agent Harness，基于 Playwright 实现浏览器任务执行、Action DSL、DOM/文本观测、截图采集和 JSONL trace，支持本地 deterministic smoke eval。
- 设计 Agent Eval 流水线，支持 task schema、rule/LLM agent、validator、failure label、token/cost ledger 和 Markdown/HTML 报告导出。
- 实现最小 Tool Runtime，封装 `browser_snapshot`、`file_read_limited`、`trace_query`、`kb_search`，支持权限 preset、路径白名单、错误结构化和审计日志。
- 建立安全回归任务，覆盖 domain allowlist、path traversal deny、CSV artifact validator、错误恢复和知识库工具检索。

English:

- Built a Browser Agent Harness with Playwright-based execution, an action DSL, DOM/text observations, screenshots, and JSONL traces for deterministic local smoke evaluation.
- Designed an agent evaluation pipeline with task schemas, rule/fake-LLM agents, validators, failure labels, token/cost ledgers, and Markdown/HTML reports.
- Implemented a minimal tool runtime for browser snapshots, limited file reads, trace queries, and local KB search with permission presets, path allowlists, structured errors, and audit logs.
- Added safety regression tasks covering domain allowlists, path traversal denial, CSV artifact validation, recovery flows, and knowledge-base tool retrieval.

