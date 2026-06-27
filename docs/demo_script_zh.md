# 5 分钟 Demo 脚本

1. 说明项目：这是 Browser Agent Harness，不是普通网页自动化。
2. 跑环境检查：

```powershell
.\scripts\doctor.ps1
```

3. 跑本地 smoke eval：

```powershell
.\scripts\run_eval.ps1 --suite smoke --agent rule
```

4. 导出报告：

```powershell
.\scripts\export_report.ps1 --run-dir .\traces --out .\reports\latest
```

5. 打开 `reports\latest\index.html`，讲成功率、步骤数、失败标签和成本。
6. 打开一个 trace 目录，展示 `trace.jsonl`、`screenshots`、`tool_audit.jsonl`。
7. 讲两个安全案例：`forbidden_domain` 和 `path_deny_tool`。
8. 结尾说明边界：没有完整复现 WebArena/OSWorld，当前是 subset-ready harness。

