from __future__ import annotations

import time
from collections import defaultdict
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

CLEANUP_INTERVAL = 300


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, max_requests: int = 30, window: int = 60) -> None:
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window
        self.clients: dict[str, list[float]] = defaultdict(list)
        self._last_cleanup = time.monotonic()

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        if request.method in ("POST", "DELETE"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        timestamps = self.clients[client_ip]

        while timestamps and timestamps[0] < now - self.window:
            timestamps.pop(0)

        if len(timestamps) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded", "retry_after": self.window},
            )

        timestamps.append(now)

        if time.monotonic() - self._last_cleanup > CLEANUP_INTERVAL:
            cutoff = now - self.window
            self.clients = {
                ip: ts for ip, ts in self.clients.items() if ts and ts[-1] > cutoff
            }
            self._last_cleanup = time.monotonic()

        return await call_next(request)
