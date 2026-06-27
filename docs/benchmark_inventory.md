# Benchmark Inventory

| 项目 | 决策 | 原因 |
|---|---|---|
| BrowserGym | adapter_candidate | 统一 web agent 环境，可做 subset adapter |
| AgentLab | reference | 实验框架成熟，本项目不替代它 |
| WebArena | reference | 自托管成本高，不做完整复现 |
| VisualWebArena | reference | 多模态成本高，只借鉴截图观测 |
| WorkArena | out_of_scope | ServiceNow 环境依赖重 |
| MiniWoB++ | adapter_candidate | 小型网页任务适合 subset |
| WebLINX | reference | 偏离线 interaction 数据 |
| OSWorld | out_of_scope | VM/桌面环境成本高 |
| browser-use | reference | 通用浏览器 agent runtime |
| Stagehand | reference | AI + deterministic browser automation SDK |

第 6 周目标仅为 adapter/subset，不宣称完整 benchmark reproduction。

