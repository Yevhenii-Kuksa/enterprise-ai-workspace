import uuid
from enum import StrEnum

from pydantic import BaseModel, Field

from app.ai.reliability.policy import ReliabilityDecision


class EvaluationCaseType(StrEnum):
    RETRIEVAL = "retrieval"
    GROUNDED_ANSWER = "grounded_answer"
    RELIABILITY = "reliability"
    SECURITY = "security"


class ExpectedEvidence(BaseModel):
    document_id: uuid.UUID
    chunk_ids: set[uuid.UUID] = Field(default_factory=set)


class RagEvaluationCase(BaseModel):
    case_id: str = Field(min_length=1, max_length=100)
    case_type: EvaluationCaseType

    organization_id: uuid.UUID
    user_id: uuid.UUID

    query: str = Field(min_length=1)

    expected_evidence: list[ExpectedEvidence] = Field(
        default_factory=list
    )
    expected_reliability_decision: ReliabilityDecision | None = None

    require_citations: bool = True
    security_case: bool = False


class RetrievalEvaluationResult(BaseModel):
    hit: bool
    expected_evidence_count: int
    retrieved_expected_evidence_count: int
    recall_at_k: float


class CitationEvaluationResult(BaseModel):
    citation_count: int
    invalid_citation_count: int
    citation_correctness: float
    passed: bool


class GroundednessEvaluationResult(BaseModel):
    claim_count: int
    grounded_claim_count: int
    groundedness: float
    passed: bool


class ReliabilityEvaluationResult(BaseModel):
    expected_decision: ReliabilityDecision | None
    actual_decision: ReliabilityDecision | None
    passed: bool


class SecurityEvaluationResult(BaseModel):
    passed: bool
    violation_count: int = 0
    reasons: list[str] = Field(default_factory=list)


class RagEvaluationResult(BaseModel):
    case_id: str
    case_type: EvaluationCaseType

    retrieval: RetrievalEvaluationResult | None = None
    citations: CitationEvaluationResult | None = None
    groundedness: GroundednessEvaluationResult | None = None
    reliability: ReliabilityEvaluationResult | None = None
    security: SecurityEvaluationResult | None = None

    passed: bool


class RagEvaluationSummary(BaseModel):
    total_cases: int
    passed_cases: int
    failed_cases: int

    retrieval_hit_rate: float
    retrieval_recall_at_k: float
    citation_correctness: float
    groundedness: float
    reliability_accuracy: float

    security_violations: int

    passed: bool