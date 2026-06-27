# Action DSL

支持动作：

- `goto`: `{ "type": "goto", "url": "http://127.0.0.1:8765/crm/index.html" }`
- `click`: `{ "type": "click", "selector": "#save" }`
- `fill`: `{ "type": "fill", "selector": "#name", "value": "Alice" }`
- `press`: `{ "type": "press", "selector": "#search", "key": "Enter" }`
- `extract_text`: `{ "type": "extract_text", "selector": "body" }`
- `tool`: `{ "type": "tool", "tool_name": "kb_search", "input": { "query": "RA0L1" } }`
- `done`: `{ "type": "done" }`

所有 action 都经过 schema 校验，并写入 trace。

