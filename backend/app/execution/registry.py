from collections.abc import Iterable

from app.execution.schemas import ActionDefinition


class ActionRegistryError(Exception):
    pass


class ActionAlreadyRegisteredError(ActionRegistryError):
    pass


class ActionNotRegisteredError(ActionRegistryError):
    pass


class ActionRegistry:
    def __init__(
        self,
        definitions: Iterable[ActionDefinition] = (),
    ) -> None:
        self._definitions: dict[str, ActionDefinition] = {}

        for definition in definitions:
            self.register(definition)

    def register(
        self,
        definition: ActionDefinition,
    ) -> None:
        if definition.action_type in self._definitions:
            raise ActionAlreadyRegisteredError(
                f"Action is already registered: "
                f"{definition.action_type}"
            )

        self._definitions[definition.action_type] = definition

    def get(
        self,
        action_type: str,
    ) -> ActionDefinition:
        definition = self._definitions.get(action_type)

        if definition is None:
            raise ActionNotRegisteredError(
                f"Action is not registered: {action_type}"
            )

        return definition

    def contains(
        self,
        action_type: str,
    ) -> bool:
        return action_type in self._definitions

    def list_actions(
        self,
    ) -> tuple[ActionDefinition, ...]:
        return tuple(self._definitions.values())