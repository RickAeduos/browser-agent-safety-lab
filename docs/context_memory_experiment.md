# Context / Memory Experiment

本项目只做小规模可复现实验，不声称实现生产级长期记忆系统。

## 策略

| 策略 | 实现 | 用途 |
|---|---|---|
| `recent_steps` | 保留最近 N 步 action/result/URL | 无摘要损失，token 较高 |
| `summary_memory` | 汇总已完成动作和最近步骤 | 降低 token，可能丢细节 |
| `retrieval_memory` | 从历史 step 中按 query 检索 | 长任务中找回相关失败或证据 |

## 指标

- success
- steps
- estimated chars/tokens
- context_loss failure count

## 当前结论

MVP 中已实现三种 context policy 的 deterministic builder，并提供导出命令：

```powershell
.\scripts\context_experiment.ps1 --run-dir .\traces --out .\reports\context_memory_experiment.md
```

当前实验先衡量不同策略在已有 trace 上产生的上下文字符量。后续如果接入真实 LLM，可继续比较 success、token、cost 和 `context_loss` 标签。
