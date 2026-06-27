from __future__ import annotations

import json
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from packages.tool_runtime.permissions import allowed

ToolFunc = Callable[[dict[str, Any]], dict[str, Any]]

SENSITIVE_PATH_MARKERS = ("api_key", "api-key", ".env", "secret", "token", "credential")


@dataclass
class ToolSpec:
    name: str
    description: str
    func: ToolFunc
    permission: str = "eval_runner"
    timeout_ms: int = 3000


class ToolRuntime:
    def __init__(self, project_root: Path, trace_root: Path, browser=None, permission_preset: str = "eval_runner") -> None:
        self.project_root = project_root
        self.trace_root = trace_root
        self.browser = browser
        self.permission_preset = permission_preset
        self._tools: dict[str, ToolSpec] = {}
        self._audit_path: Path | None = None
        self._register_defaults()

    def set_audit_path(self, path: Path) -> None:
        self._audit_path = path

    def register(self, spec: ToolSpec) -> None:
        self._tools[spec.name] = spec

    def call(self, name: str, payload: dict[str, Any], run_id: str = "", step_index: int = -1) -> dict[str, Any]:
        start = time.perf_counter()
        if name not in self._tools:
            result = {"ok": False, "error_type": "unknown_tool", "message": f"Unknown tool: {name}"}
            self._audit(run_id, step_index, name, payload, result, start)
            return result
        if not allowed(name, self.permission_preset):
            result = {"ok": False, "error_type": "permission_denied", "message": f"Tool not allowed: {name}"}
            self._audit(run_id, step_index, name, payload, result, start)
            return result
        try:
            result = self._tools[name].func(payload)
        except Exception as exc:
            result = {"ok": False, "error_type": "tool_error", "message": str(exc)}
        self._audit(run_id, step_index, name, payload, result, start)
        return result

    def _audit(
        self,
        run_id: str,
        step_index: int,
        name: str,
        payload: dict[str, Any],
        result: dict[str, Any],
        start: float,
    ) -> None:
        if not self._audit_path:
            return
        record = {
            "run_id": run_id,
            "step_index": step_index,
            "tool": name,
            "input_summary": str(payload)[:500],
            "output_summary": str(result)[:500],
            "duration_ms": round((time.perf_counter() - start) * 1000, 2),
            "ok": result.get("ok", False),
            "error_type": result.get("error_type"),
        }
        with self._audit_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    def _register_defaults(self) -> None:
        self.register(ToolSpec("browser_snapshot", "Return browser observation.", self._browser_snapshot))
        self.register(ToolSpec("file_read_limited", "Read a whitelisted project file.", self._file_read_limited))
        self.register(ToolSpec("trace_query", "Query a trace JSONL file.", self._trace_query))
        self.register(ToolSpec("kb_search", "Keyword search local knowledge files.", self._kb_search))

    def _browser_snapshot(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not self.browser:
            return {"ok": False, "error_type": "browser_missing", "message": "No browser session"}
        return {"ok": True, "observation": self.browser.observe()}

    def _file_read_limited(self, payload: dict[str, Any]) -> dict[str, Any]:
        raw_path = payload.get("path")
        if not raw_path:
            return {"ok": False, "error_type": "tool_schema_error", "message": "Missing path"}
        candidate = (self.project_root / raw_path).resolve()
        if _is_sensitive_path(str(raw_path), candidate):
            return {
                "ok": False,
                "error_type": "secret_path_denied",
                "message": f"Sensitive path denied: {raw_path}",
            }
        allowed_roots = [
            (self.project_root / name).resolve()
            for name in ["docs", "tasks", "apps", "traces", "reports"]
        ]
        if not any(candidate == root or root in candidate.parents for root in allowed_roots):
            return {"ok": False, "error_type": "path_denied", "message": f"Path denied: {raw_path}"}
        if not candidate.exists() or not candidate.is_file():
            return {"ok": False, "error_type": "file_missing", "message": f"File missing: {raw_path}"}
        return {"ok": True, "text": candidate.read_text(encoding="utf-8", errors="ignore")[: payload.get("max_chars", 4000)]}

    def _trace_query(self, payload: dict[str, Any]) -> dict[str, Any]:
        run_id = payload.get("run_id")
        if not run_id:
            return {"ok": False, "error_type": "tool_schema_error", "message": "Missing run_id"}
        trace_path = self.trace_root / run_id / "trace.jsonl"
        if not trace_path.exists():
            return {"ok": False, "error_type": "trace_missing", "message": f"Trace not found: {run_id}"}
        lines = trace_path.read_text(encoding="utf-8").splitlines()
        return {"ok": True, "records": [json.loads(line) for line in lines[: payload.get("limit", 20)]]}

    def _kb_search(self, payload: dict[str, Any]) -> dict[str, Any]:
        query = str(payload.get("query", "")).strip()
        top_k = int(payload.get("top_k", 3))
        if not query:
            return {"ok": False, "error_type": "tool_schema_error", "message": "Missing query"}
        roots = [self.project_root / "docs", self.project_root.parent / "fae_kb_poc" / "docs_source"]
        terms = [term.lower() for term in query.split() if term.strip()]
        hits: list[dict[str, Any]] = []
        for root in roots:
            if not root.exists():
                continue
            for path in root.rglob("*"):
                if path.suffix.lower() not in {".md", ".txt", ".json"}:
                    continue
                text = path.read_text(encoding="utf-8", errors="ignore")
                lower = text.lower()
                score = sum(lower.count(term) for term in terms)
                if score <= 0:
                    continue
                idx = min([lower.find(term) for term in terms if lower.find(term) >= 0] or [0])
                hits.append(
                    {
                        "score": score,
                        "source_path": str(path),
                        "snippet": text[max(0, idx - 160) : idx + 360],
                    }
                )
        hits.sort(key=lambda item: item["score"], reverse=True)
        return {"ok": True, "query": query, "results": hits[:top_k]}


def _is_sensitive_path(raw_path: str, resolved_path: Path) -> bool:
    normalized = raw_path.replace("\\", "/").lower()
    parts = [part.lower() for part in resolved_path.parts]
    return any(marker in normalized for marker in SENSITIVE_PATH_MARKERS) or any(
        marker in part for part in parts for marker in SENSITIVE_PATH_MARKERS
    )
