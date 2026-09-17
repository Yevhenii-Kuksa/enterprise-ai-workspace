import uuid
from datetime import UTC, datetime, timedelta

from app.ai.answer_service import (
    SYSTEM_PROMPT,
    build_user_prompt,
    generate_grounded_answer,
)
from app.ai.provider import AIAnswerResult
from app.core.trace_context import TraceContext
from app.retrieval.context import RagContext
from app.retrieval.evidence import CitationSource, EvidenceItem


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
            text="Towar naleЕјy przyjД…Д‡ zgodnie z procedurД… [S1].",
            model_name=self.model_name,
        )


def _rag_context() -> RagContext:
    evidence = EvidenceItem(
        chunk_id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        document_version_id=uuid.uuid4(),
        document_title="Procedura magazynowa",
        content="Towar naleЕјy przyjД…Д‡ zgodnie z procedurД….",
        chunk_index=0,
        distance=0.1,
        page_number=3,
        section_title="PrzyjД™cie towaru",
        source_locator={"page": 3},
        source_system="sharepoint",
        source_uri="https://example.test/procedura-magazynowa",
        source_modified_at=None,
    )

    source = CitationSource(
        label="S1",
        evidence=evidence,
    )

    return RagContext(
        query="Jak przyjД…Д‡ towar?",
        sources=[source],
        context_text=(
            "[S1]\n"
            "Document: Procedura magazynowa\n"
            "Content: Towar naleЕјy przyjД…Д‡ zgodnie z procedurД…."
        ),
    )


def test_build_user_prompt_includes_question_and_context() -> None:
    context = _rag_context()

    prompt = build_user_prompt(context)

    assert "Question:\nJak przyjД…Д‡ towar?" in prompt
    assert "[S1]" in prompt
    assert "Document: Procedura magazynowa" in prompt
    assert (
        "Content: Towar naleЕјy przyjД…Д‡ zgodnie z procedurД…."
        in prompt
    )


def test_generate_grounded_answer_uses_system_prompt_and_user_prompt() -> None:
    provider = FakeAIAnswerProvider()
    context = _rag_context()

    result = generate_grounded_answer(
        provider=provider,
        context=context,
    )

    assert provider.calls == [
        {
            "system_prompt": SYSTEM_PROMPT,
            "user_prompt": build_user_prompt(context),
        }
    ]

    assert result.text == (
        "Towar naleЕјy przyjД…Д‡ zgodnie z procedurД… [S1]."
    )
    assert result.model_name == "fake-answer-model"

    assert result.citation_validation.used_labels == {"S1"}
    assert result.citation_validation.valid_labels == {"S1"}
    assert result.citation_validation.invalid_labels == set()
    assert result.citation_validation.citation_count == 1
    assert result.citation_validation.invalid_citation_count == 0


def test_build_user_prompt_handles_empty_context_text() -> None:
    context = RagContext(
        query="Pytanie bez ЕєrГіdeЕ‚",
        sources=[],
        context_text="",
    )

    prompt = build_user_prompt(context)

    assert "Question:\nPytanie bez ЕєrГіdeЕ‚" in prompt
    assert "Context:\n" in prompt

class InvalidCitationAIAnswerProvider:
    @property
    def model_name(self) -> str:
        return "fake-invalid-citation-model"

    def generate_answer(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> AIAnswerResult:
        return AIAnswerResult(
            text="Niepotwierdzona odpowiedЕє [S99].",
            model_name=self.model_name,
        )

def test_generate_grounded_answer_rejects_empty_evidence() -> None:
    provider = FakeAIAnswerProvider()

    context = RagContext(
        query="Pytanie bez ЕєrГіdeЕ‚",
        sources=[],
        context_text="",
    )

    try:
        generate_grounded_answer(
            provider=provider,
            context=context,
        )
    except ValueError as exc:
        assert str(exc) == (
            "Cannot generate a grounded answer without evidence."
        )
    else:
        raise AssertionError("Expected ValueError.")

    assert provider.calls == []

def test_generate_grounded_answer_allows_reliable_context() -> None:
    provider = FakeAIAnswerProvider()
    context = _rag_context()

    result = generate_grounded_answer(
        provider=provider,
        context=context,
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

    assert result.reliability is not None
    assert result.reliability_policy is not None
    assert result.reliability_policy.decision.value == "degrade"
    assert result.reliability_policy.reasons == (
        "unknown_source_freshness",
    )
    assert len(provider.calls) == 1


def test_generate_grounded_answer_refuses_insufficient_evidence() -> None:
    provider = FakeAIAnswerProvider()
    context = _rag_context()

    try:
        generate_grounded_answer(
            provider=provider,
            context=context,
            evaluated_at=datetime(
                2026,
                9,
                15,
                12,
                0,
                tzinfo=UTC,
            ),
            max_evidence_distance=0.05,
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

    assert provider.calls == []


def test_generate_grounded_answer_refuses_detected_conflict() -> None:
    provider = FakeAIAnswerProvider()
    context = _rag_context()

    try:
        generate_grounded_answer(
            provider=provider,
            context=context,
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
            conflict_count=1,
            conflict_checked=True,
        )
    except ValueError as exc:
        assert str(exc) == (
            "Reliability policy refused answer generation: "
            "conflict_detected"
        )
    else:
        raise AssertionError("Expected ValueError.")

    assert provider.calls == []


def test_generate_grounded_answer_requires_complete_reliability_config() -> None:
    provider = FakeAIAnswerProvider()
    context = _rag_context()

    try:
        generate_grounded_answer(
            provider=provider,
            context=context,
            evaluated_at=datetime(
                2026,
                9,
                15,
                12,
                0,
                tzinfo=UTC,
            ),
        )
    except ValueError as exc:
        assert str(exc) == (
            "Reliability evaluation requires evaluated_at, "
            "max_evidence_distance, and max_source_age."
        )
    else:
        raise AssertionError("Expected ValueError.")

    assert provider.calls == []

class MissingCitationAIAnswerProvider:
    @property
    def model_name(self) -> str:
        return "fake-missing-citation-model"

    def generate_answer(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> AIAnswerResult:
        return AIAnswerResult(
            text="Answer without a source citation.",
            model_name=self.model_name,
        )


def test_generate_grounded_answer_rejects_invalid_citation() -> None:
    provider = InvalidCitationAIAnswerProvider()
    context = _rag_context()

    try:
        generate_grounded_answer(
            provider=provider,
            context=context,
        )
    except ValueError as exc:
        assert str(exc) == (
            "Generated answer contains invalid citations."
        )
    else:
        raise AssertionError("Expected ValueError.")


def test_generate_grounded_answer_rejects_missing_citations() -> None:
    provider = MissingCitationAIAnswerProvider()
    context = _rag_context()

    try:
        generate_grounded_answer(
            provider=provider,
            context=context,
        )
    except ValueError as exc:
        assert str(exc) == (
            "Generated answer does not contain citations."
        )
    else:
        raise AssertionError("Expected ValueError.")

def test_generate_grounded_answer_emits_correlated_ai_trace(
    caplog,
) -> None:
    provider = FakeAIAnswerProvider()
    context = _rag_context()
    trace_context = TraceContext.create()

    with caplog.at_level(
        "INFO",
        logger="enterprise_ai_workspace.ai",
    ):
        result = generate_grounded_answer(
            provider=provider,
            context=context,
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

    matching_records = [
        record
        for record in caplog.records
        if getattr(record, "event_type", None)
        == "ai_generation_completed"
    ]

    assert len(matching_records) == 1

    record = matching_records[0]

    assert record.trace_id == str(trace_context.trace_id)
    assert record.request_id == str(trace_context.request_id)
    assert record.action_id is None
    assert record.model_name == "fake-answer-model"
    assert record.evidence_count == 1
    assert record.citation_count == 1
    assert record.invalid_citation_count == 0
    assert record.reliability_decision == "degrade"
    assert isinstance(record.duration_ms, float)
    assert record.duration_ms >= 0

    assert result.model_name == "fake-answer-model"