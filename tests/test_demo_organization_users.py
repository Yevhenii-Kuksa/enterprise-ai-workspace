from app.demo.organization import (
    NEXALVORA_DEPARTMENTS,
    NEXALVORA_ORGANIZATION,
)
from app.demo.users import NEXALVORA_USERS


def test_nexalvora_organization_is_defined() -> None:
    assert NEXALVORA_ORGANIZATION.code == "NEXALVORA"
    assert NEXALVORA_ORGANIZATION.name == "Nexalvora Industries Sp. z o.o."


def test_department_codes_are_unique() -> None:
    department_codes = [department.code for department in NEXALVORA_DEPARTMENTS]

    assert len(department_codes) == len(set(department_codes))


def test_all_departments_belong_to_nexalvora() -> None:
    assert all(
        department.organization_id == NEXALVORA_ORGANIZATION.id
        for department in NEXALVORA_DEPARTMENTS
    )


def test_user_ids_are_unique() -> None:
    user_ids = [user.id for user in NEXALVORA_USERS]

    assert len(user_ids) == len(set(user_ids))


def test_employee_codes_are_unique() -> None:
    employee_codes = [user.employee_code for user in NEXALVORA_USERS]

    assert len(employee_codes) == len(set(employee_codes))


def test_user_emails_are_unique() -> None:
    emails = [user.email for user in NEXALVORA_USERS]

    assert len(emails) == len(set(emails))


def test_all_users_belong_to_existing_departments() -> None:
    department_ids = {department.id for department in NEXALVORA_DEPARTMENTS}

    assert all(user.department_id in department_ids for user in NEXALVORA_USERS)


def test_anna_kowalska_has_expected_demo_identity() -> None:
    anna = next(
        user
        for user in NEXALVORA_USERS
        if user.employee_code == "USR-001"
    )

    assert anna.full_name == "Anna Kowalska"
    assert anna.job_title == "Operations Manager"
    assert anna.system_role == "Administrator"