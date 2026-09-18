import pytest
from app.execution.registry import (
    ActionAlreadyRegisteredError,
    ActionNotRegisteredError,
    ActionRegistry,
)
from app.execution.schemas import ActionDefinition


def action_definition(
    action_type: str = "erp.order.release",
) -> ActionDefinition:
    return ActionDefinition(
        action_type=action_type,
        executor_name="demo_executor",
        required_permission="action.execute",
    )


def test_registry_registers_and_returns_action() -> None:
    definition = action_definition()
    registry = ActionRegistry()

    registry.register(definition)

    assert registry.contains(definition.action_type) is True
    assert registry.get(definition.action_type) == definition


def test_registry_initializes_with_definitions() -> None:
    first = action_definition("erp.order.release")
    second = action_definition("document.publish")

    registry = ActionRegistry([first, second])

    assert registry.list_actions() == (first, second)


def test_registry_rejects_duplicate_action_type() -> None:
    definition = action_definition()
    registry = ActionRegistry([definition])

    with pytest.raises(ActionAlreadyRegisteredError):
        registry.register(definition)


def test_registry_rejects_unknown_action() -> None:
    registry = ActionRegistry()

    with pytest.raises(ActionNotRegisteredError):
        registry.get("unknown.action")


def test_registry_reports_missing_action() -> None:
    registry = ActionRegistry()

    assert registry.contains("unknown.action") is False