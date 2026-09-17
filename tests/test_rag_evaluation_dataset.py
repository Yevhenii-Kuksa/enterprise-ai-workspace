import json
import uuid
from pathlib import Path

import pytest
from app.ai.evaluation.dataset import load_golden_dataset
from app.ai.evaluation.schemas import EvaluationCaseType
from app.ai.reliability.policy import ReliabilityDecision
from pydantic import ValidationError


def _valid_case(
    *,
    case_id: str = "case-001",
) -> dict[str, object]:
    return {
        "case_id": case_id,
        "case_type": "grounded_answer",
        "organization_id": str(uuid.uuid4()),
        "user_id": str(uuid.uuid4()),
        "query": "Jaka jest procedura reklamacji?",
        "expected_evidence": [
            {
                "document_id": str(uuid.uuid4()),
                "chunk_ids": [
                    str(uuid.uuid4()),
                ],
            }
        ],
        "expected_reliability_decision": "allow",
        "require_citations": True,
        "security_case": False,
    }


def _write_dataset(
    path: Path,
    cases: list[dict[str, object]],
) -> None:
    path.write_text(
        json.dumps(cases),
        encoding="utf-8",
    )


def test_load_golden_dataset_returns_validated_cases(
    tmp_path: Path,
) -> None:
    dataset_path = tmp_path / "rag_cases.json"

    _write_dataset(
        dataset_path,
        [
            _valid_case(case_id="case-001"),
            _valid_case(case_id="case-002"),
        ],
    )

    cases = load_golden_dataset(dataset_path)

    assert len(cases) == 2
    assert cases[0].case_id == "case-001"
    assert cases[0].case_type == EvaluationCaseType.GROUNDED_ANSWER
    assert (
        cases[0].expected_reliability_decision
        == ReliabilityDecision.ALLOW
    )


def test_load_golden_dataset_accepts_string_path(
    tmp_path: Path,
) -> None:
    dataset_path = tmp_path / "rag_cases.json"

    _write_dataset(
        dataset_path,
        [_valid_case()],
    )

    cases = load_golden_dataset(str(dataset_path))

    assert len(cases) == 1


def test_load_golden_dataset_rejects_missing_file(
    tmp_path: Path,
) -> None:
    dataset_path = tmp_path / "missing.json"

    with pytest.raises(
        FileNotFoundError,
        match="Golden dataset not found",
    ):
        load_golden_dataset(dataset_path)


def test_load_golden_dataset_rejects_invalid_json(
    tmp_path: Path,
) -> None:
    dataset_path = tmp_path / "rag_cases.json"
    dataset_path.write_text(
        "{invalid-json",
        encoding="utf-8",
    )

    with pytest.raises(json.JSONDecodeError):
        load_golden_dataset(dataset_path)


def test_load_golden_dataset_rejects_invalid_case(
    tmp_path: Path,
) -> None:
    dataset_path = tmp_path / "rag_cases.json"

    invalid_case = _valid_case()
    invalid_case["query"] = ""

    _write_dataset(
        dataset_path,
        [invalid_case],
    )

    with pytest.raises(ValidationError):
        load_golden_dataset(dataset_path)


def test_load_golden_dataset_rejects_duplicate_case_ids(
    tmp_path: Path,
) -> None:
    dataset_path = tmp_path / "rag_cases.json"

    _write_dataset(
        dataset_path,
        [
            _valid_case(case_id="duplicate-case"),
            _valid_case(case_id="duplicate-case"),
        ],
    )

    with pytest.raises(
        ValueError,
        match="duplicate case_id",
    ):
        load_golden_dataset(dataset_path)