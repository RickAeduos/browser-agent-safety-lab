# Final Project Summary

项目名：Browser Agent Harness and Evaluation Infrastructure

当前完成状态：

- 本地 smoke suite：11 个 deterministic tasks。
- benchmark adapter subset：1 个 MiniWoB-like local adapter task。
- rule agent：可无 API 跑完整评测。
- fake LLM agent：可无 API 演示 LLM action loop、token/cost ledger。
- real LLM agent：`--agent llm` 读取 `DEEPSEEK_API_KEY` 或 `docs\API_key.txt` 调用 DeepSeek Chat Completions。
- LLM completion pre-check：如果当前 observation 已满足简单 validator，Harness 会直接输出 `done`，避免模型继续点击不存在元素和浪费 token。
- Trace：JSONL、截图、summary、tool audit。
- Validator：文本、URL、CSV、blocked action、tool error、tool result。
- Report：Markdown/HTML。
- 安全：domain allowlist、path allowlist、permission preset。

不夸大声明：

- 没有训练模型。
- 没有完整复现 WebArena、OSWorld、WorkArena。
- 没有生产级多用户隔离。

面试定位：

```text
这是一个最小可信的 Browser Agent Harness：任务定义、浏览器执行、工具调用、trace、validator、失败标签和报告反馈闭环。
```
