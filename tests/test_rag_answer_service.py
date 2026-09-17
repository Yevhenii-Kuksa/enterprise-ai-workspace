import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import patch

from app.ai.provider import AIAnswerResult
from app.ai.rag_service import (
    answer_rag_query,
    answer_rag_query_from_settings,
)
from app.ai.reliability.policy import ReliabilityDecision
from app.core.config import Settings
from app.core.trace_context import TraceContext
from app.retrieval.context import RagContext
from app.retrieval.evidence import CitationSource, EvidenceItem
from app.security.current_user import CurrentUser


class FakeEmbeddingProvider:
    @property
    def model_name(self) -> str:
        return "fake-embedding-model"

    @property
    def dimensions(self) -> int:
        return 1536

    def embed_texts(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        return [
            [0.0] * self.dimensions
            for _ in texts
        ]


class FakeAIAnswerProvider:
    def __init__(self) -> None:
        self.calls: list[dict[str, str]] = []

    @property
    def model_name(self) -> str:
        return "fake-answer-model"

    def generate_answer(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> AIAnswerResult:
        self.calls.append(
            {
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
            }
        )

        return AIAnswerResult(
            text="Odpowiedź oparta na źródle [S1].",
            model_name=self.model_name,
        )


def _current_user() -> CurrentUser:
    return CurrentUser(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        department_id=uuid.uuid4(),
        is_active=True,
        permissions=set(),
    )


def _rag_context(
    *,
    distance: float = 0.1,
) -> RagContext:
    evidence = EvidenceItem(
        chunk_id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        document_version_id=uuid.uuid4(),
        document_title="Procedura magazynowa",
        content="Treść procedury magazynowej.",
        chunk_index=0,
        distance=distance,
        page_number=1,
        section_title="Magazyn",
        source_locator={"page": 1},
        source_system="sharepoint",
        source_uri="https://example.test/procedura",
        source_modified_at=datetime(
            2026,
            9,
            10,
            12,
            0,
            tzinfo=UTC,
        ),
    )

    return RagContext(
        query="Jaka jest procedura magazynowa?",
        sources=[
            CitationSource(
                label="S1",
                evidence=evidence,
            )
        ],
        context_text=(
            "[S1]\n"
            "Document: Procedura magazynowa\n"
            "Content: Treść procedury magazynowej."
        ),
    )


def test_answer_rag_query_orchestrates_context_and_answer() -> None:
    context = _rag_context()
    ai_provider = FakeAIAnswerProvider()

    with patch(
        "app.ai.rag_service.prepare_rag_context",
        return_value=context,
    ) as prepare_context:
        result = answer_rag_query(
            session=None,  # type: ignore[arg-type]
            current_user=_current_user(),
            query="Jaka jest procedura magazynowa?",
            embedding_provider=FakeEmbeddingProvider(),
            ai_answer_provider=ai_provider,
            evaluated_at=datetime(
                2026,
                9,
                15,
                12,
                0,
                tzinfo=UTC,
            ),
            max_evidence_distance=0.35,
            max_source_age=timedelta(days=30),
            conflict_checked=True,
        )

    assert result.context is context
    assert result.answer.text == "Odpowiedź oparta na źródle [S1]."
    assert result.answer.reliability_policy is not None
    assert (
        result.answer.reliability_policy.decision
        is ReliabilityDecision.ALLOW
    )
    assert len(ai_provider.calls) == 1

    prepare_context.assert_called_once()


def test_answer_rag_query_refuses_before_ai_for_weak_evidence() -> None:
    context = _rag_context(distance=0.8)
    ai_provider = FakeAIAnswerProvider()

    with patch(
        "app.ai.rag_service.prepare_rag_context",
        return_value=context,
    ):
        try:
            answer_rag_query(
                session=None,  # type: ignore[arg-type]
                current_user=_current_user(),
                query="Jaka jest procedura magazynowa?",
                embedding_provider=FakeEmbeddingProvider(),
                ai_answer_provider=ai_provider,
                evaluated_at=datetime(
                    2026,
                    9,
                    15,
                    12,
                    0,
                    tzinfo=UTC,
                ),
                max_evidence_distance=0.35,
                max_source_age=timedelta(days=30),
                conflict_checked=True,
            )
        except ValueError as exc:
            assert str(exc) == (
                "Reliability policy refused answer generation: "
                "insufficient_evidence"
            )
        else:
            raise AssertionError("Expected ValueError.")

    assert ai_provider.calls == []

def test_answer_rag_query_from_settings_uses_runtime_config() -> None:
    context = _rag_context()

    settings = Settings(
        database_url="postgresql://test",
        openai_api_key="test-api-key",
        ai_reliability_max_evidence_distance=0.35,
        ai_reliability_max_source_age_days=30,
    )

    embedding_provider = FakeEmbeddingProvider()
    ai_provider = FakeAIAnswerProvider()

    with (
        patch(
            "app.ai.rag_service.create_embedding_provider",
            return_value=embedding_provider,
        ) as create_embedding,
        patch(
            "app.ai.rag_service.create_ai_answer_provider",
            return_value=ai_provider,
        ) as create_ai,
        patch(
            "app.ai.rag_service.prepare_rag_context",
            return_value=context,
        ),
    ):
        result = answer_rag_query_from_settings(
            session=None,  # type: ignore[arg-type]
            current_user=_current_user(),
            query="Jaka jest procedura magazynowa?",
            settings=settings,
            evaluated_at=datetime(
                2026,
                9,
                15,
                12,
                0,
                tzinfo=UTC,
            ),
            conflict_checked=True,
        )

    create_embedding.assert_called_once_with(settings)
    create_ai.assert_called_once_with(settings)

    assert result.answer.reliability is not None
    assert result.answer.reliability_policy is not None
    assert (
        result.answer.reliability_policy.decision
        is ReliabilityDecision.ALLOW
    )
    assert len(ai_provider.calls) == 1

def test_answer_rag_query_passes_trace_context_to_retrieval() -> None:
    context = _rag_context()
    trace_context = TraceContext.create()

    with patch(
        "app.ai.rag_service.prepare_rag_context",
        return_value=context,
    ) as prepare_context:
        answer_rag_query(
            session=None,  # type: ignore[arg-type]
            current_user=_current_user(),
            query="Jaka jest procedura magazynowa?",
            embedding_provider=FakeEmbeddingProvider(),
            ai_answer_provider=FakeAIAnswerProvider(),
            evaluated_at=datetime(
                2026,
                9,
                15,
                12,
                0,
                tzinfo=UTC,
            ),
            max_evidence_distance=0.35,
            max_source_age=timedelta(days=30),
            conflict_checked=True,
            trace_context=trace_context,
        )

    call_kwargs = prepare_context.call_args.kwargs

    assert call_kwargs["trace_context"] is trace_context

def test_answer_rag_query_passes_trace_context_to_ai_generation() -> None:
    context = _rag_context()
    trace_context = TraceContext.create()

    with (
        patch(
            "app.ai.rag_service.prepare_rag_context",
            return_value=context,
        ),
        patch(
            "app.ai.rag_service.generate_grounded_answer",
        ) as generate_answer,
    ):
        answer_rag_query(
            session=None,  # type: ignore[arg-type]
            current_user=_current_user(),
            query="Jaka jest procedura magazynowa?",
            embedding_provider=FakeEmbeddingProvider(),
            ai_answer_provider=FakeAIAnswerProvider(),
            evaluated_at=datetime(
                2026,
                9,
                15,
                12,
                0,
                tzinfo=UTC,
            ),
            max_evidence_distance=0.35,
            max_source_age=timedelta(days=30),
            conflict_checked=True,
            trace_context=trace_context,
        )

    generate_answer.assert_called_once()

    call_kwargs = generate_answer.call_args.kwargs

    assert call_kwargs["trace_context"] is trace_context