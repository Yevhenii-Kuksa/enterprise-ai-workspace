import uuid
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TraceContext:
    trace_id: uuid.UUID
    request_id: uuid.UUID
    action_id: uuid.UUID | None = None

    @classmethod
    def create(
        cls,
        *,
        trace_id: uuid.UUID | None = None,
        request_id: uuid.UUID | None = None,
        action_id: uuid.UUID | None = None,
    ) -> "TraceContext":
        return cls(
            trace_id=(
                trace_id
                if trace_id is not None
                else uuid.uuid4()
            ),
            request_id=(
                request_id
                if request_id is not None
                else uuid.uuid4()
            ),
            action_id=action_id,
        )