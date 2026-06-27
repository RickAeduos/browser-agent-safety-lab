# Architecture

```text
Task YAML
  -> TaskSpec
  -> Agent(rule/fake LLM)
  -> Action DSL
  -> BrowserSession / ToolRuntime
  -> TraceWriter(JSONL + screenshots + audit)
  -> Validator
  -> Summary JSON
  -> Eval Report
```

Browser Agent Safety Lab 复用这个闭环，但默认入口从普通 smoke eval 切换为 adversarial safety eval：

```text
malicious local webpage
  -> browser agent action
  -> harness policy check
  -> trace/audit
  -> safety validator
  -> GitHub Pages report
```

安全边界：

- `TaskSpec.allowed_domains` 控制浏览器跳转。
- `ToolRuntime` 使用 permission preset。
- `file_read_limited` 使用 path allowlist。
- 敏感路径使用 explicit denylist，即使路径位于 `docs` 目录下也不会读取。
- `fixtures.allow_downloads: false` 可阻止未授权下载。
- 每个 action、tool call、validator result 都写入 trace。

实现边界：

- 已实现：本地 deterministic adversarial harness。
- 已实现：rule/fake LLM/real DeepSeek LLM 三种 agent 路径。
- 已实现：安全 validators、trace、audit、report。
- 未来工作：Skyvern adapter、多模型比较、外部 benchmark subset 扩展。
