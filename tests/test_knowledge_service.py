import uuid

import pytest
from app.db.session import SessionLocal
from app.knowledge.service import (
    get_document,
    list_document_versions,
    list_documents,
    validate_department_access,
)
from app.models.department import Department
from app.models.document import Document
from app.models.document_version import DocumentVersion
from app.models.organization import Organization
from app.security.current_user import CurrentUser


def _current_user(
    *,
    organization_id: uuid.UUID,
    department_id: uuid.UUID | None,
    is_active: bool = True,
) -> CurrentUser:
    return CurrentUser(
        id=uuid.uuid4(),
        organization_id=organization_id,
        department_id=department_id,
        is_active=is_active,
        permissions=set(),
    )


def test_list_documents_enforces_tenant_and_department_access() -> None:
    organization_id = uuid.uuid4()
    other_organization_id = uuid.uuid4()
    department_id = uuid.uuid4()
    other_department_id = uuid.uuid4()

    with SessionLocal() as db:
        db.add_all(
            [
                Organization(
                    id=organization_id,
                    code=f"KH-{organization_id.hex[:8]}",
                    name="Knowledge Hub Organization",
                ),
                Organization(
                    id=other_organization_id,
                    code=f"KH-{other_organization_id.hex[:8]}",
                    name="Other Organization",
                ),
            ]
        )
        db.flush()

        db.add_all(
            [
                Department(
                    id=department_id,
                    organization_id=organization_id,
                    code="SALES",
                    name="Sales",
                ),
                Department(
                    id=other_department_id,
                    organization_id=organization_id,
                    code="HR",
                    name="HR",
                ),
            ]
        )
        db.flush()

        public_document = Document(
            organization_id=organization_id,
            title="Instrukcja ogólna",
            source_type="upload",
        )
        department_document = Document(
            organization_id=organization_id,
            department_id=department_id,
            title="Procedura sprzedaży",
            source_type="upload",
        )
        inaccessible_document = Document(
            organization_id=organization_id,
            department_id=other_department_id,
            title="Procedura HR",
            source_type="upload",
        )
        foreign_document = Document(
            organization_id=other_organization_id,
            title="Dokument innej organizacji",
            source_type="upload",
        )

        db.add_all(
            [
                public_document,
                department_document,
                inaccessible_document,
                foreign_document,
            ]
        )
        db.flush()

        documents = list_documents(
            db,
            current_user=_current_user(
                organization_id=organization_id,
                department_id=department_id,
            ),
        )

        assert {document.id for document in documents} == {
            public_document.id,
            department_document.id,
        }

        db.rollback()


def test_list_documents_searches_title_and_excludes_inactive() -> None:
    organization_id = uuid.uuid4()

    with SessionLocal() as db:
        db.add(
            Organization(
                id=organization_id,
                code=f"KH-SEARCH-{organization_id.hex[:8]}",
                name="Knowledge Search Organization",
            )
        )
        db.flush()

        matching_document = Document(
            organization_id=organization_id,
            title="Procedura magazynowa",
            source_type="upload",
        )
        unrelated_document = Document(
            organization_id=organization_id,
            title="Regulamin pracy",
            source_type="upload",
        )
        inactive_document = Document(
            organization_id=organization_id,
            title="Stara procedura magazynowa",
            source_type="upload",
            is_active=False,
        )

        db.add_all(
            [
                matching_document,
                unrelated_document,
                inactive_document,
            ]
        )
        db.flush()

        documents = list_documents(
            db,
            current_user=_current_user(
                organization_id=organization_id,
                department_id=None,
            ),
            search="MAGAZYN",
        )

        assert [document.id for document in documents] == [
            matching_document.id
        ]

        db.rollback()


def test_get_document_hides_inaccessible_document() -> None:
    organization_id = uuid.uuid4()
    allowed_department_id = uuid.uuid4()
    blocked_department_id = uuid.uuid4()

    with SessionLocal() as db:
        db.add(
            Organization(
                id=organization_id,
                code=f"KH-GET-{organization_id.hex[:8]}",
                name="Knowledge Get Organization",
            )
        )
        db.flush()

        db.add_all(
            [
                Department(
                    id=allowed_department_id,
                    organization_id=organization_id,
                    code="OFFICE",
                    name="Office",
                ),
                Department(
                    id=blocked_department_id,
                    organization_id=organization_id,
                    code="FINANCE",
                    name="Finance",
                ),
            ]
        )
        db.flush()

        blocked_document = Document(
            organization_id=organization_id,
            department_id=blocked_department_id,
            title="Dokument finansowy",
            source_type="upload",
        )

        db.add(blocked_document)
        db.flush()

        result = get_document(
            db,
            current_user=_current_user(
                organization_id=organization_id,
                department_id=allowed_department_id,
            ),
            document_id=blocked_document.id,
        )

        assert result is None

        db.rollback()


def test_list_document_versions_returns_newest_first() -> None:
    organization_id = uuid.uuid4()

    with SessionLocal() as db:
        db.add(
            Organization(
                id=organization_id,
                code=f"KH-VERSIONS-{organization_id.hex[:8]}",
                name="Knowledge Version Organization",
            )
        )
        db.flush()

        document = Document(
            organization_id=organization_id,
            title="Procedura jakości",
            source_type="upload",
        )
        db.add(document)
        db.flush()

        version_one = DocumentVersion(
            organization_id=organization_id,
            document_id=document.id,
            version_number=1,
            content_sha256="a" * 64,
            mime_type="application/pdf",
            ingestion_status="completed",
        )
        version_two = DocumentVersion(
            organization_id=organization_id,
            document_id=document.id,
            version_number=2,
            content_sha256="b" * 64,
            mime_type="application/pdf",
            ingestion_status="completed",
        )

        db.add_all([version_one, version_two])
        db.flush()

        versions = list_document_versions(
            db,
            current_user=_current_user(
                organization_id=organization_id,
                department_id=None,
            ),
            document_id=document.id,
        )

        assert [
            version.version_number
            for version in versions
        ] == [2, 1]

        db.rollback()


def test_list_document_versions_hides_foreign_tenant() -> None:
    organization_id = uuid.uuid4()
    other_organization_id = uuid.uuid4()

    with SessionLocal() as db:
        db.add_all(
            [
                Organization(
                    id=organization_id,
                    code=f"KH-OWN-{organization_id.hex[:8]}",
                    name="Own Organization",
                ),
                Organization(
                    id=other_organization_id,
                    code=f"KH-OTHER-{other_organization_id.hex[:8]}",
                    name="Other Organization",
                ),
            ]
        )
        db.flush()

        foreign_document = Document(
            organization_id=other_organization_id,
            title="Foreign document",
            source_type="upload",
        )
        db.add(foreign_document)
        db.flush()

        versions = list_document_versions(
            db,
            current_user=_current_user(
                organization_id=organization_id,
                department_id=None,
            ),
            document_id=foreign_document.id,
        )

        assert versions == []

        db.rollback()


def test_inactive_user_cannot_list_documents() -> None:
    with SessionLocal() as db:
        with pytest.raises(
            PermissionError,
            match=(
                "Inactive user cannot access "
                "the Knowledge Hub."
            ),
        ):
            list_documents(
                db,
                current_user=_current_user(
                    organization_id=uuid.uuid4(),
                    department_id=None,
                    is_active=False,
                ),
            )

def test_validate_department_access_accepts_own_department() -> None:
    organization_id = uuid.uuid4()
    department_id = uuid.uuid4()

    with SessionLocal() as db:
        db.add(
            Organization(
                id=organization_id,
                code=f"KH-VALID-{organization_id.hex[:8]}",
                name="Knowledge Validation Organization",
            )
        )
        db.flush()

        db.add(
            Department(
                id=department_id,
                organization_id=organization_id,
                code="SALES",
                name="Sales",
            )
        )
        db.flush()

        validate_department_access(
            db,
            current_user=_current_user(
                organization_id=organization_id,
                department_id=department_id,
            ),
            department_id=department_id,
        )

        db.rollback()


def test_validate_department_access_rejects_other_department() -> None:
    organization_id = uuid.uuid4()
    user_department_id = uuid.uuid4()
    other_department_id = uuid.uuid4()

    with SessionLocal() as db:
        db.add(
            Organization(
                id=organization_id,
                code=f"KH-DEPT-{organization_id.hex[:8]}",
                name="Knowledge Department Organization",
            )
        )
        db.flush()

        db.add_all(
            [
                Department(
                    id=user_department_id,
                    organization_id=organization_id,
                    code="SALES",
                    name="Sales",
                ),
                Department(
                    id=other_department_id,
                    organization_id=organization_id,
                    code="HR",
                    name="HR",
                ),
            ]
        )
        db.flush()

        with pytest.raises(
            PermissionError,
            match="User cannot manage documents for this department.",
        ):
            validate_department_access(
                db,
                current_user=_current_user(
                    organization_id=organization_id,
                    department_id=user_department_id,
                ),
                department_id=other_department_id,
            )

        db.rollback()


def test_validate_department_access_rejects_foreign_tenant_department() -> None:
    organization_id = uuid.uuid4()
    foreign_organization_id = uuid.uuid4()
    foreign_department_id = uuid.uuid4()

    with SessionLocal() as db:
        db.add_all(
            [
                Organization(
                    id=organization_id,
                    code=f"KH-TENANT-{organization_id.hex[:8]}",
                    name="Own Organization",
                ),
                Organization(
                    id=foreign_organization_id,
                    code=f"KH-FOREIGN-{foreign_organization_id.hex[:8]}",
                    name="Foreign Organization",
                ),
            ]
        )
        db.flush()

        db.add(
            Department(
                id=foreign_department_id,
                organization_id=foreign_organization_id,
                code="HR",
                name="Foreign HR",
            )
        )
        db.flush()

        with pytest.raises(
            ValueError,
            match="Department does not belong to the organization.",
        ):
            validate_department_access(
                db,
                current_user=_current_user(
                    organization_id=organization_id,
                    department_id=None,
                ),
                department_id=foreign_department_id,
            )

        db.rollback()


def test_validate_department_access_accepts_public_scope() -> None:
    with SessionLocal() as db:
        validate_department_access(
            db,
            current_user=_current_user(
                organization_id=uuid.uuid4(),
                department_id=uuid.uuid4(),
            ),
            department_id=None,
        )