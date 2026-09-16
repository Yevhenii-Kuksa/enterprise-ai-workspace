import logging
import uuid
from collections.abc import Awaitable, Callable
from time import perf_counter

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.trace_context import TraceContext

TRACE_ID_HEADER = "X-Trace-ID"
REQUEST_ID_HEADER = "X-Request-ID"

logger = logging.getLogger("enterprise_ai_workspace.http")


class TraceContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        incoming_trace_id = request.headers.get(TRACE_ID_HEADER)

        trace_id: uuid.UUID | None = None

        if incoming_trace_id is not None:
            try:
                trace_id = uuid.UUID(incoming_trace_id)
            except ValueError:
                trace_id = None

        trace_context = TraceContext.create(
            trace_id=trace_id,
        )

        request.state.trace_context = trace_context

        started_at = perf_counter()

        try:
            response = await call_next(request)
        except Exception as exc:
            duration_ms = (perf_counter() - started_at) * 1000

            logger.error(
                "Request failed.",
                extra={
                    "trace_id": str(trace_context.trace_id),
                    "request_id": str(trace_context.request_id),
                    "action_id": (
                        str(trace_context.action_id)
                        if trace_context.action_id is not None
                        else None
                    ),
                    "event_type": "http_request_failed",
                    "method": request.method,
                    "path": request.url.path,
                    "error_type": type(exc).__name__,
                    "duration_ms": duration_ms,
                },
            )

            raise

        duration_ms = (perf_counter() - started_at) * 1000

        response.headers[TRACE_ID_HEADER] = str(
            trace_context.trace_id
        )
        response.headers[REQUEST_ID_HEADER] = str(
            trace_context.request_id
        )

        logger.info(
            "Request completed.",
            extra={
                "trace_id": str(trace_context.trace_id),
                "request_id": str(trace_context.request_id),
                "action_id": (
                    str(trace_context.action_id)
                    if trace_context.action_id is not None
                    else None
                ),
                "event_type": "http_request_completed",
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )

        return response