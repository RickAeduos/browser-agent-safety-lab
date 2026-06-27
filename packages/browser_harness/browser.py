from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from playwright.sync_api import Page, sync_playwright


class BrowserSession:
    def __init__(self, trace_dir: Path, headless: bool = True, timeout_ms: int = 5000) -> None:
        self.trace_dir = trace_dir
        self.download_dir = trace_dir / "downloads"
        self.screenshot_dir = trace_dir / "screenshots"
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        self.headless = headless
        self.timeout_ms = timeout_ms
        self._playwright = None
        self._browser = None
        self._context = None
        self.page: Page | None = None

    def __enter__(self) -> BrowserSession:
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=self.headless)
        self._context = self._browser.new_context(accept_downloads=True)
        self.page = self._context.new_page()
        self.page.set_default_timeout(self.timeout_ms)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._context:
            self._context.close()
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()

    def observe(self) -> dict[str, Any]:
        page = self._require_page()
        try:
            text = page.locator("body").inner_text(timeout=1000)
        except Exception:
            text = ""
        try:
            title = page.title()
        except Exception:
            title = ""
        try:
            html = page.content()
        except Exception:
            html = ""
        return {
            "url": page.url,
            "title": title,
            "dom_hash": hashlib.sha256(html.encode("utf-8", errors="ignore")).hexdigest()[:16],
            "text_excerpt": text[:2000],
        }

    def screenshot(self, step_index: int) -> str | None:
        page = self._require_page()
        path = self.screenshot_dir / f"step_{step_index:03d}.png"
        try:
            page.screenshot(path=str(path), full_page=True)
            return str(path)
        except Exception:
            return None

    def goto(self, url: str, allowed_domains: list[str]) -> dict[str, Any]:
        start = time.perf_counter()
        host = urlparse(url).hostname or ""
        if host not in allowed_domains:
            return self._result(False, start, "unsafe_action_blocked", f"Domain not allowed: {host}")
        try:
            response = self._require_page().goto(url, wait_until="domcontentloaded")
            return self._result(True, start, message=f"HTTP {response.status if response else 'n/a'}")
        except Exception as exc:
            return self._result(False, start, "browser_error", str(exc))

    def click(self, selector: str, expect_download: bool = False) -> dict[str, Any]:
        start = time.perf_counter()
        page = self._require_page()
        try:
            if expect_download:
                with page.expect_download() as download_info:
                    page.click(selector)
                download = download_info.value
                target = self.download_dir / download.suggested_filename
                download.save_as(str(target))
                return self._result(True, start, extra={"download_path": str(target)})
            page.click(selector)
            return self._result(True, start)
        except Exception as exc:
            return self._result(False, start, "browser_error", str(exc))

    def fill(self, selector: str, value: str) -> dict[str, Any]:
        start = time.perf_counter()
        try:
            self._require_page().fill(selector, value)
            return self._result(True, start)
        except Exception as exc:
            return self._result(False, start, "browser_error", str(exc))

    def press(self, selector: str, key: str) -> dict[str, Any]:
        start = time.perf_counter()
        try:
            self._require_page().press(selector, key)
            return self._result(True, start)
        except Exception as exc:
            return self._result(False, start, "browser_error", str(exc))

    def extract_text(self, selector: str) -> dict[str, Any]:
        start = time.perf_counter()
        try:
            text = self._require_page().locator(selector).inner_text()
            return self._result(True, start, extra={"text": text[:4000]})
        except Exception as exc:
            return self._result(False, start, "browser_error", str(exc))

    def _require_page(self) -> Page:
        if self.page is None:
            raise RuntimeError("BrowserSession has not been started")
        return self.page

    @staticmethod
    def _result(
        ok: bool,
        start: float,
        error_type: str | None = None,
        message: str = "",
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        result = {
            "ok": ok,
            "duration_ms": round((time.perf_counter() - start) * 1000, 2),
            "error_type": error_type,
            "message": message,
        }
        if extra:
            result.update(extra)
        return result

