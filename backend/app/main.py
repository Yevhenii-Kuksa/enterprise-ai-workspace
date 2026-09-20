from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api import approvals, erp, erp_intelligence, executions, executive, integrations
from app.api.audit import router as audit_router
from app.api.knowledge import router as knowledge_router
from app.api.rag import router as rag_router
from app.core.structured_logging import configure_structured_logging
from app.core.trace_middleware import TraceContextMiddleware
from app.db.dependencies import get_db

configure_structured_logging()

app = FastAPI(
    title="Enterprise AI Workspace API",
    version="0.1.0",
    description="Backend API for the Enterprise AI Workspace platform.",
)

app.add_middleware(TraceContextMiddleware)

app.include_router(rag_router)
app.include_router(knowledge_router)
app.include_router(audit_router)
app.include_router(erp.router)
app.include_router(erp_intelligence.router)
app.include_router(executive.router)
app.include_router(approvals.router)
app.include_router(executions.router)
app.include_router(integrations.router)

db_dependency = Depends(get_db)


@app.get("/health", tags=["System"])
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "enterprise-ai-workspace-api",
    }


@app.get("/ready", tags=["System"])
def readiness_check(
    db: Session = db_dependency,
) -> dict[str, str]:
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service is not ready.",
        ) from exc

    return {
        "status": "ready",
        "service": "enterprise-ai-workspace-api",
        "database": "ok",
    }