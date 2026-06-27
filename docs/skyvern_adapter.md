# Optional Skyvern Adapter

Skyvern is treated as an external production browser workflow engine, not a dependency of Browser Agent Safety Lab.

The integration boundary is:

```text
external browser agent -> lab task -> trace -> safety validators -> report
```

## Why Optional

- Core CI must remain clone-and-run without service credentials.
- The lab is responsible for adversarial tasks, trace format, validators, and reports.
- Skyvern or any other browser agent should be swappable behind the same task boundary.

## Minimum Adapter Contract

An adapter should:

- accept a `TaskSpec`
- execute the task goal in a browser environment
- return step records with action, result, observation, and optional screenshots
- preserve safety audit events when the harness blocks a tool or browser action
- write a `summary.json` compatible with `packages.eval_observatory.report`

This keeps the project positioned as safety infrastructure rather than a competing browser-agent product.
