from typing import Literal

from pydantic import BaseModel, Field


class RagQueryRequest(BaseModel):
    query: str = Field(
        min_length=1,
        max_length=4000,
    )


class RagCitationResponse(BaseModel):
    label: str
    document_title: str
    page_number: int | None
    section_title: str | None
    source_system: str | None
    source_uri: str | None


class RagReliabilityResponse(BaseModel):
    decision: Literal["allow", "degrade"]
    reasons: list[str]


class RagQueryResponse(BaseModel):
    answer: str
    model_name: str
    citations: list[RagCitationResponse]
    reliability: RagReliabilityResponse