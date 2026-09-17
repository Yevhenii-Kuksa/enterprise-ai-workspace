import json
from pathlib import Path

from pydantic import TypeAdapter

from app.ai.evaluation.schemas import RagEvaluationCase

_CASES_ADAPTER = TypeAdapter(list[RagEvaluationCase])


def load_golden_dataset(
    path: str | Path,
) -> list[RagEvaluationCase]:
    dataset_path = Path(path)

    if not dataset_path.is_file():
        raise FileNotFoundError(
            f"Golden dataset not found: {dataset_path}"
        )

    raw_data = json.loads(
        dataset_path.read_text(encoding="utf-8")
    )

    cases = _CASES_ADAPTER.validate_python(raw_data)

    case_ids = [
        case.case_id
        for case in cases
    ]

    if len(case_ids) != len(set(case_ids)):
        raise ValueError(
            "Golden dataset contains duplicate case_id values."
        )

    return cases