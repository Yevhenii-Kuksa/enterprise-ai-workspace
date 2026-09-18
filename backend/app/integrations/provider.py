from collections.abc import Sequence
from typing import Protocol

from app.integrations.schemas import IntegrationRecord


class IntegrationProvider(Protocol):
    def fetch_records(
        self,
    ) -> Sequence[IntegrationRecord]:
        ...