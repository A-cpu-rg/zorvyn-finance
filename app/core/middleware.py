"""
Industry-grade middleware stack:
  1. Request ID tracing (X-Request-ID in every response)
  2. Structured request/response logging (method, path, status, duration)
  3. Rate limiting via slowapi
"""

import time
import uuid
import logging

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

logger = logging.getLogger("zorvyn.middleware")


# ── Request ID Middleware ──────────────────────────────────────────────────────

class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Generates a unique X-Request-ID for every request.
    If the client supplies one, it is preserved; otherwise a UUID4 is generated.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        # Store on request state so other layers can access it
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


# ── Request Logging Middleware ─────────────────────────────────────────────────

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs every request with: method, path, status code, and duration in ms.
    Skips health-check and docs endpoints to reduce noise.
    """

    SKIP_PATHS = {"/health", "/docs", "/redoc", "/openapi.json", "/"}

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)

        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000

        request_id = getattr(request.state, "request_id", "N/A")
        logger.info(
            "%s %s → %s (%.1fms) [%s]",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            request_id,
        )
        return response
