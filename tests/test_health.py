from app.db.dependencies import get_db
from app.main import app
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

client = TestClient(app)


class HealthyDb:
    def __init__(self) -> None:
        self.execute_called = False

    def execute(
        self,
        statement: object,
    ) -> None:
        self.execute_called = True


class FailingDb:
    def execute(
        self,
        statement: object,
    ) -> None:
        raise SQLAlchemyError(
            "Synthetic database readiness failure."
        )


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "enterprise-ai-workspace-api",
    }


def test_readiness_check_returns_200_when_database_is_available() -> None:
    database = HealthyDb()

    app.dependency_overrides[get_db] = lambda: database

    try:
        response = client.get("/ready")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "service": "enterprise-ai-workspace-api",
        "database": "ok",
    }
    assert database.execute_called is True


def test_readiness_check_returns_safe_503_when_database_is_unavailable() -> None:
    app.dependency_overrides[get_db] = lambda: FailingDb()

    try:
        response = client.get("/ready")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Service is not ready."
    }

    assert (
        "Synthetic database readiness failure."
        not in response.text
    )