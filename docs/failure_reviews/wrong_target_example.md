# Failure Review: wrong_target

示例场景：LLM 或 rule 输出错误 selector，导致点击不到目标元素。

排查路径：

1. 打开 report 中失败任务的 trace dir。
2. 查看 `trace.jsonl` 中失败 step 的 action selector。
3. 查看同一步 screenshot。
4. 对比页面 DOM 和 action DSL。

修复方向：

- 为 observation 增加更稳定的可点击元素摘要。
- validator 标注为 `wrong_target`。

