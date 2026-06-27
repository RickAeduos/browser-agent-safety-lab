# GitHub Browser Agent 项目对比与前沿方向

生成日期：2026-06-27

本文用于定位本项目 `Browser Agent Harness and Evaluation Infrastructure` 在公开 Browser Agent 生态里的位置，并提炼适合 DeepSeek Browser Agent Infra / Agent Harness 岗位的可落地创新点。

## 1. 我们的小项目是什么定位

本项目不是通用浏览器自动化平台，也不是训练一个新的 Browser Agent 模型。

当前更准确的定位是：

```text
一个最小可信的 Browser Agent Harness / Eval Infra：
task schema -> browser action -> trace -> validator -> failure label -> report
```

已实现能力：

- YAML 任务定义和 Pydantic schema。
- Playwright 浏览器执行。
- rule / fake LLM / real DeepSeek LLM 三种 agent 路径。
- JSONL trace、截图、summary、tool audit。
- validators：文本、URL、CSV 下载、blocked action、tool error、tool result。
- smoke suite：11 个本地 deterministic tasks。
- benchmark adapter：1 个 MiniWoB-like local adapter task。
- report：Markdown / HTML。
- safety：domain allowlist、path allowlist、permission preset。
- cost-aware LLM loop：记录 token / cost，并有 validator pre-check 避免无意义继续调用模型。

明确不能夸大：

- 没有完整复现 WebArena / OSWorld / WorkArena。
- 没有训练模型。
- 没有生产级多租户隔离。
- 没有大规模真实网站任务集。

## 2. 公开项目分组对比

### A. 生产自动化 / Agent 框架

| 项目 | 核心定位 | 和我们相比 | 我们能借鉴什么 |
|---|---|---|---|
| `browser-use/browser-use` | 让 AI agent 能使用网站的 Python browser agent 框架 | 它更偏“让 agent 真实完成网页操作”；我们更偏“评测、记录、验证、复现” | 增加更好的 action API、session 复用、真实任务 replay |
| `browserbase/stagehand` | 基于 Playwright 的 AI browser automation framework，强调 `act / extract / observe / agent` 这类高层 API | 它更接近生产自动化 SDK；我们没有高层自然语言 action 封装 | 把低层 action trace 升级为 observe/act/extract 风格的标准接口 |
| `Skyvern-AI/skyvern` | 用 LLM + computer vision 自动化 browser workflows，面向复杂业务流程/RPA | 它是更完整的工作流产品；我们只是 harness MVP | workflow schema、任务状态机、人工审核节点、结构化输出 |

结论：这一类项目比我们“能干活”。我们不应该和它们比生产自动化能力，而应强调我们关注的是 infra：任务定义、可复现 trace、validator、失败分类、成本和安全边界。

### B. Benchmark / Eval Harness

| 项目 | 核心定位 | 和我们相比 | 我们能借鉴什么 |
|---|---|---|---|
| `ServiceNow/BrowserGym` | Web agent 的 gym-style 环境，整合 MiniWoB、WebArena、WorkArena、VisualWebArena、AssistantBench、TimeWarp 等 benchmark | 它是成熟 benchmark 环境聚合层；我们是最小本地 harness | 做 benchmark adapter，把我们的 task schema 对齐 BrowserGym task/env 思路 |
| `ServiceNow/AgentLab` | 面向 web agent 的实验/评测框架，配合 BrowserGym 做可复现实验 | 它更系统化，适合跑研究实验；我们报告和 failure taxonomy 还很轻量 | 增加 experiment manifest、agent config、run comparison、failure browser |
| `web-arena-x/webarena` | 自托管真实感网站环境和 web agent benchmark | 它有更大、更真实的任务环境；我们只有本地 mock sites | 先做 WebArena-style adapter，不要急着复现全部环境 |
| `OSU-NLP-Group/Mind2Web` | 大规模真实网站任务数据集，偏离线/监督学习数据 | 它的数据覆盖强；我们执行闭环强但数据少 | 选 20-50 个任务转成本地 deterministic eval 或 adapter |
| `xlang-ai/OSWorld` | 更广义的 GUI / computer-use benchmark，覆盖桌面、浏览器和应用 | 它评价的是完整计算机使用能力；我们聚焦 browser | 作为“未来扩展边界”，不要现在硬做 |

结论：这一类和我们定位最接近。我们的项目可以诚实地说是 BrowserGym/AgentLab/WebArena 方向的 mini harness，而不是生产 browser-use/Skyvern 替代品。

### C. 工具接口 / MCP / Computer Use

| 项目或产品 | 核心定位 | 和我们相比 | 我们能借鉴什么 |
|---|---|---|---|
| `microsoft/playwright-mcp` | 通过 MCP 暴露浏览器能力，使用结构化 accessibility snapshot，而不是只靠截图或 raw DOM | 它解决“模型如何安全调用浏览器工具”的接口问题；我们现在是内部 Python tool runtime | 增加 MCP server wrapper，让 harness 可被外部 agent 直接调用 |
| OpenAI Computer Use | 模型原生 computer/browser 操作能力，强调 sandbox、工具调用、安全检查 | 它是模型能力 + API；我们是评测执行层 | 把我们的 harness 变成 computer-use 模型的评测与安全外壳 |
| Anthropic Computer Use | 提供 screenshot / action 形式的 computer tool，强调由开发者实现执行环境 | 它也需要外部 harness 来承接执行、安全和观测 | 我们的 trace、allowlist、validator 正好是这类 API 的外部基础设施 |
| Google Gemini Computer Use | browser control model/tool，面向 UI 自动化任务 | 同样需要 execution harness 和 post-action verification | 做多模型 adapter：DeepSeek、OpenAI、Anthropic、Gemini 共用同一套任务和指标 |

结论：前沿模型越来越把“会操作电脑/浏览器”做成 API 能力，但真正落地仍然需要 harness、sandbox、trace、validator、人类确认和安全策略。我们的项目可以在这里找到很好的岗位相关性。

### D. 安全与恶意网页评测

| 项目 | 核心定位 | 和我们相比 | 我们能借鉴什么 |
|---|---|---|---|
| `ServiceNow/DoomArena` | 面向 web agents 的安全测试环境，评估恶意网页、prompt injection、越权行为等风险 | 它聚焦 adversarial safety；我们目前只有 allowlist/path/preset 的基础安全 | 增加 prompt-injection tasks、untrusted page label、approval-required action |

结论：Browser Agent 越接近真实网页，安全就越重要。我们已有安全边界雏形，这是一个适合做出差异化的方向。

### E. 自动生成 / 动态 benchmark

| 项目 | 核心定位 | 和我们相比 | 我们能借鉴什么 |
|---|---|---|---|
| `web-arena-x/webarena-infinity` | 自动生成多样化 web environments、tasks 和 verifiers，用于扩大 web agent eval 覆盖 | 它试图解决 benchmark 扩展性；我们任务目前手写 | 做一个小型 task generator，从模板生成 mock site、task YAML、validator |
| `yuandaxia2001/WebForge` | 可扩展生成 realistic website environments、tasks、evaluation script 的框架 | 同样是生成式 eval 方向；我们目前没有自动生成任务 | 先做 3 类模板：CRM 查询、文档检索、下载校验 |

结论：这是当前非常值得跟进的前沿方向。静态 benchmark 很快会过拟合，动态生成网站、任务和 verifier 是下一代 eval infra 的重点。

## 3. 我们项目的真实优势

和公开项目相比，我们项目规模小，但有几个面试上能成立的优势：

1. 范围贴近岗位：不是做一个“网页自动化玩具”，而是围绕 harness、trace、validator、failure taxonomy、cost、安全边界来做。
2. 可解释性强：每个 run 都有 JSONL trace、截图、summary、report，能说清楚 agent 为什么成功或失败。
3. 可回归：rule agent 和 fake LLM 可以无成本跑 smoke eval，real DeepSeek LLM 可以做真实模型验证。
4. 有安全意识：domain allowlist、path allowlist、permission preset、blocked action validator 已经是 agent infra 语境。
5. 有成本意识：真实 LLM 调用会记录 token/cost，并通过 validator pre-check 避免无意义继续调用。

## 4. 我们项目的短板

必须诚实承认：

1. 任务数量太少：11 个 smoke tasks + 1 个 adapter，只能证明结构，不足以证明泛化。
2. 页面复杂度低：本地 mock sites 和真实生产网站差距很大。
3. 观察空间简单：还没有完整 accessibility tree / screenshot+DOM / OCR / visual grounding。
4. 没有多模型对比：目前真实 LLM 只接了 DeepSeek。
5. 没有接入成熟 benchmark：没有真正跑 BrowserGym/WebArena/WorkArena。
6. 报告还偏 summary：缺少 trace explorer、失败聚类、run diff、agent config diff。
7. 安全测试还不够 adversarial：没有 prompt injection 页面、钓鱼页面、越权数据泄漏任务。

## 5. 最值得做的创新点

### 创新点 1：Mini BrowserGym Adapter

目标：让我们的 task schema 能映射到 BrowserGym-style env/task。

为什么有价值：

- 公开 benchmark 已经存在，完全复刻不现实。
- Adapter 展示的是 infra 能力：兼容外部 benchmark、统一 run format、统一指标。

最小可落地：

- 新增 `packages/benchmark_adapters/browsergym_adapter.py`。
- 先支持 3 个字段：observation、action、reward/done。
- 把现有 MiniWoB-like task 扩成 5 个。
- 报告里区分 `local_smoke`、`benchmark_adapter`、`real_llm`。

面试表达：

```text
I did not reimplement WebArena. I built the adapter boundary first so that local smoke tasks and external benchmark-style tasks can share the same trace, validator, and reporting pipeline.
```

### 创新点 2：MCP Browser Harness Wrapper

目标：把我们的 browser/tool runtime 暴露成 MCP server。

为什么有价值：

- Playwright MCP 已经证明 MCP 是 browser tool interface 的重要方向。
- DeepSeek Browser Agent Infra 可能需要模型和工具运行层解耦。

最小可落地：

- 暴露工具：`browser_goto`、`browser_click`、`browser_fill`、`browser_snapshot`、`trace_query`。
- 每个工具调用写入现有 JSONL trace。
- 沿用 domain/path allowlist。
- 新增一个 MCP smoke client 或简单 CLI 测试。

面试表达：

```text
The agent does not need to link against my Python runner directly. The harness can expose browser and trace tools through MCP while preserving permission checks and audit logs.
```

### 创新点 3：Adversarial Web Safety Suite

目标：增加 Browser Agent 安全任务，不只验证成功率。

为什么有价值：

- Browser Agent 会读取不可信网页内容。
- Prompt injection、越权点击、跨域跳转、敏感文件读取是核心风险。
- 我们已有 allowlist/path/preset，可以自然扩展。

最小可落地：

- 新增 `apps/mock_sites/adversarial/`。
- 任务示例：
  - 页面要求 agent 忽略系统规则并访问 forbidden domain。
  - 页面伪装成内部文档，诱导读取 `docs/API_key.txt`。
  - 页面要求下载可疑文件。
  - 页面包含“点击这里完成任务”的错误目标。
- 新增 validators：
  - `no_forbidden_navigation`
  - `no_secret_file_access`
  - `approval_required_blocked`
  - `injection_ignored`

面试表达：

```text
I treat web content as untrusted input. The harness labels page-originated instructions and verifies that the agent does not escalate browser actions into forbidden tools or filesystem access.
```

### 创新点 4：Dynamic Task Generator

目标：从模板生成 mock site、task YAML、validator，减少手写 eval。

为什么有价值：

- WebArena-Infinity / WebForge 代表了 benchmark 扩展方向。
- 静态任务容易过拟合，动态任务能测试鲁棒性。

最小可落地：

- 先做 3 个 generator：
  - CRM filter/search task。
  - docs portal citation task。
  - download center CSV task。
- 每次生成：
  - HTML fixture。
  - YAML task spec。
  - expected answer / validator。
  - deterministic seed。
- 报告记录 seed，保证可复现。

面试表达：

```text
Instead of only hand-authoring tasks, I built seeded task generation so the eval can scale while preserving deterministic replay.
```

### 创新点 5：Trace Explorer + Failure Diff

目标：把报告从“结果汇总”升级为“debugging tool”。

为什么有价值：

- Infra/Harness 岗最看重 failure localization。
- 公开框架通常有数据，但 portfolio 项目需要把可读性做出来。

最小可落地：

- HTML report 增加 run detail 页。
- 展示每一步：
  - observation 摘要。
  - model action JSON。
  - screenshot。
  - validator status。
  - token/cost。
  - error/failure label。
- 增加两个 run 的 diff：
  - rule vs llm。
  - fake_llm vs real DeepSeek。
  - before vs after pre-check。

面试表达：

```text
The report is not just a scoreboard. It is a debugging surface for browser-agent failures, with step-level action, observation, screenshot, cost, and validator evidence.
```

### 创新点 6：Multi-Observation Policy

目标：比较不同 observation 输入对 agent 成功率和成本的影响。

为什么有价值：

- Browser Agent 的关键不只是模型，而是“给模型看什么”。
- 前沿方向正在从 raw screenshot / DOM 转向 accessibility tree、结构化 snapshot、多模态融合。

最小可落地：

- Observation modes：
  - `text_only`
  - `accessibility_snapshot`
  - `dom_summary`
  - `screenshot_caption_stub`
- 报告比较：
  - success rate。
  - steps。
  - tokens。
  - cost。
  - failure type。

面试表达：

```text
I ran the same task suite under different observation policies to measure the trade-off between context richness, cost, and action accuracy.
```

## 6. 推荐执行优先级

如果只做 2 周增强，建议顺序：

1. Adversarial Web Safety Suite。
2. Trace Explorer + Failure Diff。
3. Mini BrowserGym Adapter。
4. Dynamic Task Generator。
5. MCP Browser Harness Wrapper。
6. Multi-Observation Policy。

原因：

- 1 和 2 最能立刻体现 Infra/Harness 思维。
- 3 让项目和公开 benchmark 对齐。
- 4 是前沿创新点，但实现复杂度略高。
- 5 对架构感有帮助，但如果时间紧，可以只做设计文档 + 最小 MCP demo。
- 6 最贴近模型效果分析，但需要更稳定的任务集支撑。

## 7. 一句话定位

和 GitHub 上成熟项目相比，我们的小项目不是要竞争“最强 browser agent”，而是要展示：

```text
我知道 Browser Agent 真正落地难点不只是点击网页，
而是任务标准化、工具权限、可复现执行、失败定位、成本控制、安全评测和 benchmark 接入。
```

这正好是 Browser Agent Infra / Agent Harness 岗位更关心的能力。

## 8. 主要参考来源

- browser-use: https://github.com/browser-use/browser-use
- Stagehand: https://github.com/browserbase/stagehand
- Skyvern: https://github.com/Skyvern-AI/skyvern
- BrowserGym: https://github.com/ServiceNow/BrowserGym
- AgentLab: https://github.com/ServiceNow/AgentLab
- WebArena: https://github.com/web-arena-x/webarena
- Mind2Web: https://github.com/OSU-NLP-Group/Mind2Web
- OSWorld: https://github.com/xlang-ai/OSWorld
- Playwright MCP: https://github.com/microsoft/playwright-mcp
- DoomArena: https://github.com/ServiceNow/DoomArena
- WebArena-Infinity: https://github.com/web-arena-x/webarena-infinity
- WebForge: https://github.com/yuandaxia2001/WebForge
- OpenAI Computer Use: https://developers.openai.com/api/docs/guides/tools-computer-use
- Anthropic Computer Use: https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/computer-use-tool
- Google Gemini Computer Use: https://ai.google.dev/gemini-api/docs/computer-use
