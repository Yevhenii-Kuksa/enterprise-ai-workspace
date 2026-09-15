import uuid

from app.ai.answer_service import (
    SYSTEM_PROMPT,
    build_user_prompt,
    generate_grounded_answer,
)
from app.ai.provider import AIAnswerResult
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
            text="Towar należy przyjąć zgodnie z procedurą [S1].",
            model_name=self.model_name,
        )


def _rag_context() -> RagContext:
    evidence = EvidenceItem(
        chunk_id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        document_version_id=uuid.uuid4(),
        document_title="Procedura magazynowa",
        content="Towar należy przyjąć zgodnie z procedurą.",
        chunk_index=0,
        distance=0.1,
        page_number=3,
        section_title="Przyjęcie towaru",
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
        query="Jak przyjąć towar?",
        sources=[source],
        context_text=(
            "[S1]\n"
            "Document: Procedura magazynowa\n"
            "Content: Towar należy przyjąć zgodnie z procedurą."
        ),
    )


def test_build_user_prompt_includes_question_and_context() -> None:
    context = _rag_context()

    prompt = build_user_prompt(context)

    assert "Question:\nJak przyjąć towar?" in prompt
    assert "[S1]" in prompt
    assert "Document: Procedura magazynowa" in prompt
    assert (
        "Content: Towar należy przyjąć zgodnie z procedurą."
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
        "Towar należy przyjąć zgodnie z procedurą [S1]."
    )
    assert result.model_name == "fake-answer-model"

    assert result.citation_validation.used_labels == {"S1"}
    assert result.citation_validation.valid_labels == {"S1"}
    assert result.citation_validation.invalid_labels == set()
    assert result.citation_validation.citation_count == 1
    assert result.citation_validation.invalid_citation_count == 0


def test_build_user_prompt_handles_empty_context_text() -> None:
    context = RagContext(
        query="Pytanie bez źródeł",
        sources=[],
        context_text="",
    )

    prompt = build_user_prompt(context)

    assert "Question:\nPytanie bez źródeł" in prompt
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
            text="Niepotwierdzona odpowiedź [S99].",
            model_name=self.model_name,
        )


def test_generate_grounded_answer_detects_invalid_citation() -> None:
    provider = InvalidCitationAIAnswerProvider()
    context = _rag_context()

    result = generate_grounded_answer(
        provider=provider,
        context=context,
    )

    assert result.citation_validation.used_labels == {"S99"}
    assert result.citation_validation.valid_labels == set()
    assert result.citation_validation.invalid_labels == {"S99"}
    assert result.citation_validation.citation_count == 1
    assert result.citation_validation.invalid_citation_count == 1

def test_generate_grounded_answer_rejects_empty_evidence() -> None:
    provider = FakeAIAnswerProvider()

    context = RagContext(
        query="Pytanie bez źródeł",
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