from __future__ import annotations

import functools
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class ReusableThreadingHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True


class QuietSimpleHTTPRequestHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:
        return


class StaticServer:
    def __init__(self, root: Path, port: int = 8765) -> None:
        self.root = root
        self.port = port
        self._server: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None

    def __enter__(self) -> StaticServer:
        handler = functools.partial(QuietSimpleHTTPRequestHandler, directory=str(self.root))
        self._server = ReusableThreadingHTTPServer(("127.0.0.1", self.port), handler)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._server:
            self._server.shutdown()
            self._server.server_close()
        if self._thread:
            self._thread.join(timeout=2)
