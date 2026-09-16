from fastapi import HTTPException, Request, status

from app.core.trace_context import TraceContext


def get_trace_context(
    request: Request,
) -> TraceContext:
    trace_context = getattr(
        request.state,
        "trace_context",
        None,
    )

    if not isinstance(trace_context, TraceContext):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Trace context is not available.",
        )

    return trace_context