from dataclasses import dataclass
from uuid import UUID

from app.demo.ids import (
    ANNA_KOWALSKA_ID,
    EWA_LEWANDOWSKA_ID,
    KAROLINA_WOJCIK_ID,
    KRZYSZTOF_MAZUR_ID,
    LOGISTICS_DEPARTMENT_ID,
    MARTA_ZIELINSKA_ID,
    MICHAL_KAMINSKI_ID,
    OPERATIONS_DEPARTMENT_ID,
    PIOTR_NOWAK_ID,
    PROCUREMENT_DEPARTMENT_ID,
    PRODUCTION_DEPARTMENT_ID,
    QUALITY_DEPARTMENT_ID,
    SALES_DEPARTMENT_ID,
    TOMASZ_WISNIEWSKI_ID,
)


@dataclass(frozen=True, slots=True)
class DemoUser:
    id: UUID
    department_id: UUID
    employee_code: str
    email: str
    full_name: str
    job_title: str
    system_role: str
    is_active: bool = True


NEXALVORA_USERS = (
    DemoUser(
        id=ANNA_KOWALSKA_ID,
        department_id=OPERATIONS_DEPARTMENT_ID,
        employee_code="USR-001",
        email="anna.kowalska@nexalvora.example",
        full_name="Anna Kowalska",
        job_title="Operations Manager",
        system_role="Administrator",
    ),
    DemoUser(
        id=PIOTR_NOWAK_ID,
        department_id=PROCUREMENT_DEPARTMENT_ID,
        employee_code="USR-002",
        email="piotr.nowak@nexalvora.example",
        full_name="Piotr Nowak",
        job_title="Procurement Manager",
        system_role="Manager",
    ),
    DemoUser(
        id=MARTA_ZIELINSKA_ID,
        department_id=QUALITY_DEPARTMENT_ID,
        employee_code="USR-003",
        email="marta.zielinska@nexalvora.example",
        full_name="Marta Zielińska",
        job_title="Quality Manager",
        system_role="Manager",
    ),
    DemoUser(
        id=KRZYSZTOF_MAZUR_ID,
        department_id=PRODUCTION_DEPARTMENT_ID,
        employee_code="USR-004",
        email="krzysztof.mazur@nexalvora.example",
        full_name="Krzysztof Mazur",
        job_title="Production Manager",
        system_role="Manager",
    ),
    DemoUser(
        id=TOMASZ_WISNIEWSKI_ID,
        department_id=SALES_DEPARTMENT_ID,
        employee_code="USR-005",
        email="tomasz.wisniewski@nexalvora.example",
        full_name="Tomasz Wiśniewski",
        job_title="Sales Manager",
        system_role="Manager",
    ),
    DemoUser(
        id=KAROLINA_WOJCIK_ID,
        department_id=SALES_DEPARTMENT_ID,
        employee_code="USR-006",
        email="karolina.wojcik@nexalvora.example",
        full_name="Karolina Wójcik",
        job_title="Key Account Manager",
        system_role="User",
    ),
    DemoUser(
        id=MICHAL_KAMINSKI_ID,
        department_id=SALES_DEPARTMENT_ID,
        employee_code="USR-007",
        email="michal.kaminski@nexalvora.example",
        full_name="Michał Kamiński",
        job_title="Sales Specialist",
        system_role="User",
    ),
    DemoUser(
        id=EWA_LEWANDOWSKA_ID,
        department_id=LOGISTICS_DEPARTMENT_ID,
        employee_code="USR-008",
        email="ewa.lewandowska@nexalvora.example",
        full_name="Ewa Lewandowska",
        job_title="Logistics Coordinator",
        system_role="User",
    ),
)