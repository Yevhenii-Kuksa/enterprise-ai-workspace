import pytest
from app.integrations.registry import (
    IntegrationAlreadyRegisteredError,
    IntegrationNotRegisteredError,
    IntegrationRegistry,
)
from app.integrations.schemas import (
    IntegrationCapability,
    IntegrationDefinition,
    IntegrationKind,
)


def integration_definition(
    key: str = "google-drive",
) -> IntegrationDefinition:
    return IntegrationDefinition(
        key=key,
        kind=IntegrationKind.FILE_STORAGE,
        provider="google",
        capabilities=(
            IntegrationCapability.READ_FILES,
        ),
    )


def test_registry_registers_and_returns_integration() -> None:
    definition = integration_definition()
    registry = IntegrationRegistry()

    registry.register(definition)

    assert registry.contains(definition.key) is True
    assert registry.get(definition.key) == definition


def test_registry_initializes_with_definitions() -> None:
    first = integration_definition("google-drive")
    second = integration_definition("sharepoint")

    registry = IntegrationRegistry(
        [
            first,
            second,
        ]
    )

    assert registry.list_integrations() == (
        first,
        second,
    )


def test_registry_rejects_duplicate_key() -> None:
    definition = integration_definition()
    registry = IntegrationRegistry(
        [definition]
    )

    with pytest.raises(
        IntegrationAlreadyRegisteredError
    ):
        registry.register(definition)


def test_registry_rejects_unknown_integration() -> None:
    registry = IntegrationRegistry()

    with pytest.raises(
        IntegrationNotRegisteredError
    ):
        registry.get("missing")


def test_registry_reports_missing_integration() -> None:
    registry = IntegrationRegistry()

    assert registry.contains("missing") is False