from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.ai.rag_service import answer_rag_query_from_settings
from app.api.schemas import (
    RagCitationResponse,
    RagQueryRequest,
    RagQueryResponse,
    RagReliabilityResponse,
)
from app.core.config import Settings, get_settings
from app.core.trace_context import TraceContext
from app.core.trace_dependencies import get_trace_context
from app.db.dependencies import get_db
from app.security.current_user import CurrentUser
from app.security.dependencies import get_current_user

router = APIRouter(
    prefix="/api/rag",
    tags=["RAG"],
)

db_dependency = Depends(get_db)
current_user_dependency = Depends(get_current_user)
settings_dependency = Depends(get_settings)
trace_context_dependency = Depends(get_trace_context)


@router.post(
    "/query",
    response_model=RagQueryResponse,
)
def query_rag(
    request: RagQueryRequest,
    db: Session = db_dependency,
    current_user: CurrentUser = current_user_dependency,
    settings: Settings = settings_dependency,
    trace_context: TraceContext = trace_context_dependency,
) -> RagQueryResponse:
    try:
        result = answer_rag_query_from_settings(
            db,
            current_user=current_user,
            query=request.query,
            settings=settings,
            trace_context=trace_context,
        )
    except ValueError as exc:
        message = str(exc)

        if message.startswith(
            "Reliability policy refused answer generation:"
        ):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=message,
            ) from exc

        raise

    policy = result.answer.reliability_policy

    if policy is None:
        raise RuntimeError(
            "RAG answer is missing reliability policy metadata."
        )

    citations = [
        RagCitationResponse(
            label=source.label,
            document_title=source.evidence.document_title,
            page_number=source.evidence.page_number,
            section_title=source.evidence.section_title,
            source_system=source.evidence.source_system,
            source_uri=source.evidence.source_uri,
        )
        for source in result.context.sources
    ]

    return RagQueryResponse(
        answer=result.answer.text,
        model_name=result.answer.model_name,
        citations=citations,
        reliability=RagReliabilityResponse(
            decision=policy.decision.value,
            reasons=list(policy.reasons),
        ),
    )