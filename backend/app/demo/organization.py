from dataclasses import dataclass
from uuid import UUID

from app.demo.ids import (
    LOGISTICS_DEPARTMENT_ID,
    NEXALVORA_ORGANIZATION_ID,
    OPERATIONS_DEPARTMENT_ID,
    PROCUREMENT_DEPARTMENT_ID,
    PRODUCTION_DEPARTMENT_ID,
    QUALITY_DEPARTMENT_ID,
    SALES_DEPARTMENT_ID,
)


@dataclass(frozen=True, slots=True)
class DemoOrganization:
    id: UUID
    code: str
    name: str


@dataclass(frozen=True, slots=True)
class DemoDepartment:
    id: UUID
    organization_id: UUID
    code: str
    name: str


NEXALVORA_ORGANIZATION = DemoOrganization(
    id=NEXALVORA_ORGANIZATION_ID,
    code="NEXALVORA",
    name="Nexalvora Industries Sp. z o.o.",
)


NEXALVORA_DEPARTMENTS = (
    DemoDepartment(
        id=OPERATIONS_DEPARTMENT_ID,
        organization_id=NEXALVORA_ORGANIZATION_ID,
        code="OPERATIONS",
        name="Operations",
    ),
    DemoDepartment(
        id=SALES_DEPARTMENT_ID,
        organization_id=NEXALVORA_ORGANIZATION_ID,
        code="SALES",
        name="Sales",
    ),
    DemoDepartment(
        id=PROCUREMENT_DEPARTMENT_ID,
        organization_id=NEXALVORA_ORGANIZATION_ID,
        code="PROCUREMENT",
        name="Procurement",
    ),
    DemoDepartment(
        id=PRODUCTION_DEPARTMENT_ID,
        organization_id=NEXALVORA_ORGANIZATION_ID,
        code="PRODUCTION",
        name="Production",
    ),
    DemoDepartment(
        id=QUALITY_DEPARTMENT_ID,
        organization_id=NEXALVORA_ORGANIZATION_ID,
        code="QUALITY",
        name="Quality",
    ),
    DemoDepartment(
        id=LOGISTICS_DEPARTMENT_ID,
        organization_id=NEXALVORA_ORGANIZATION_ID,
        code="LOGISTICS",
        name="Logistics",
    ),
)