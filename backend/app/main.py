from fastapi import FastAPI

from app.api.rag import router as rag_router

app = FastAPI(
    title="Enterprise AI Workspace API",
    version="0.1.0",
    description="Backend API for the Enterprise AI Workspace platform.",
)

app.include_router(rag_router)


@app.get("/health", tags=["System"])
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "enterprise-ai-workspace-api",
    }