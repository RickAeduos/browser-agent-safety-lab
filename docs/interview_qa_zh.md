# Interview Q&A

## 1. 这个项目解决什么问题？

它解决 Browser Agent 如何被安全运行、评测、审计和复盘的问题。证据：`scripts\run_eval.ps1`、`traces\*\trace.jsonl`、`reports\latest\index.html`。

## 2. 和 browser-use 有什么区别？

browser-use 更偏现成浏览器 agent runtime。本项目重点在 harness：trace、validator、failure taxonomy、权限审计和成本感知评测。

## 3. 为什么要 rule agent？

rule agent 不需要 API，适合 CI 和回归。它能区分 harness 失败和模型失败。

## 4. 为什么不完整复现 WebArena？

WebArena 自托管成本高。个人作品集更适合先做一个小而完整的 harness，再用 adapter/subset 证明可扩展性。

## 5. 安全边界在哪里？

domain allowlist、path allowlist、permission preset、dangerous action blocking。证据：`forbidden_domain.yaml`、`path_deny_tool.yaml`。

## 6. 如何定位失败？

从 report 找失败 label，打开 trace dir，看 `trace.jsonl`、screenshot 和 `tool_audit.jsonl`。

## 7. 当前限制是什么？

LLM agent 默认 fake model；外部 benchmark 只是 subset-ready；没有生产级多用户隔离。

## 8. 真实 LLM 为什么还需要 Harness pre-check？

真实模型可能在页面已经包含答案后继续尝试点击不存在的链接。Harness pre-check 用 validator 判断任务是否已满足，直接停止 run，减少无效动作和 API 成本。证据：`packages\agents\llm_agent.py`。
