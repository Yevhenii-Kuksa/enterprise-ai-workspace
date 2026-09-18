from collections.abc import Iterable

from app.integrations.schemas import IntegrationDefinition


class IntegrationRegistryError(Exception):
    pass


class IntegrationAlreadyRegisteredError(IntegrationRegistryError):
    pass


class IntegrationNotRegisteredError(IntegrationRegistryError):
    pass


class IntegrationRegistry:
    def __init__(
        self,
        definitions: Iterable[IntegrationDefinition] = (),
    ) -> None:
        self._definitions: dict[str, IntegrationDefinition] = {}

        for definition in definitions:
            self.register(definition)

    def register(
        self,
        definition: IntegrationDefinition,
    ) -> None:
        if definition.key in self._definitions:
            raise IntegrationAlreadyRegisteredError(
                f"Integration is already registered: "
                f"{definition.key}"
            )

        self._definitions[definition.key] = definition

    def get(
        self,
        key: str,
    ) -> IntegrationDefinition:
        definition = self._definitions.get(key)

        if definition is None:
            raise IntegrationNotRegisteredError(
                f"Integration is not registered: {key}"
            )

        return definition

    def contains(
        self,
        key: str,
    ) -> bool:
        return key in self._definitions

    def list_integrations(
        self,
    ) -> tuple[IntegrationDefinition, ...]:
        return tuple(self._definitions.values())