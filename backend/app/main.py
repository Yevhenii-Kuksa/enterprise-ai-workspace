from fastapi import FastAPI

from app.api.knowledge import router as knowledge_router
from app.api.rag import router as rag_router
from app.core.trace_middleware import TraceContextMiddleware

app = FastAPI(
    title="Enterprise AI Workspace API",
    version="0.1.0",
    description="Backend API for the Enterprise AI Workspace platform.",
)

app.add_middleware(TraceContextMiddleware)

app.include_router(rag_router)
app.include_router(knowledge_router)


@app.get("/health", tags=["System"])
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "enterprise-ai-workspace-api",
    }