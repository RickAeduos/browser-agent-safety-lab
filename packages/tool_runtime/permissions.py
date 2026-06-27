from __future__ import annotations

PRESETS = {
    "browser_only": {"browser_snapshot"},
    "read_only": {"file_read_limited", "kb_search", "trace_query"},
    "eval_runner": {"browser_snapshot", "file_read_limited", "kb_search", "trace_query"},
    "admin": {"browser_snapshot", "file_read_limited", "kb_search", "trace_query"},
}


def allowed(tool_name: str, preset: str) -> bool:
    return tool_name in PRESETS.get(preset, set())

