from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    print(f"project_root={root}")
    print(f"python={sys.executable}")
    print(f"python_version={sys.version.split()[0]}")
    import playwright  # noqa: F401

    print("playwright_import=ok")
    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("about:blank")
        print(f"chromium_launch=ok url={page.url}")
        browser.close()
    for rel in ["scripts", "packages", "tasks", "apps", "traces", "reports", "docs"]:
        path = root / rel
        print(f"dir:{rel}={'ok' if path.exists() else 'missing'}")


if __name__ == "__main__":
    main()

