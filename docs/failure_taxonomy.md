# Failure Taxonomy

| Label | 含义 |
|---|---|
| `observation_missing` | 页面状态没有被正确观测 |
| `wrong_target` | 点错元素或进入错误页面 |
| `invalid_action` | Agent 输出非法 action |
| `tool_schema_error` | 工具参数格式错误 |
| `tool_timeout` | 工具或浏览器动作超时 |
| `context_loss` | 忘记早先任务约束 |
| `validator_uncertain` | 自动验证无法判断 |
| `unsafe_action_blocked` | 被安全策略拦截 |
| `path_denied` | 文件路径越界 |
| `model_refusal_or_loop` | 模型拒答或重复动作 |

