from app.integrations.provider import IntegrationProvider


class ProviderRegistryError(Exception):
    pass


class ProviderAlreadyRegisteredError(ProviderRegistryError):
    pass


class ProviderNotRegisteredError(ProviderRegistryError):
    pass


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, IntegrationProvider] = {}

    def register(
        self,
        key: str,
        provider: IntegrationProvider,
    ) -> None:
        normalized_key = key.strip()

        if not normalized_key:
            raise ValueError(
                "Provider key must not be empty."
            )

        if normalized_key in self._providers:
            raise ProviderAlreadyRegisteredError(
                f"Provider is already registered: "
                f"{normalized_key}"
            )

        self._providers[normalized_key] = provider

    def get(
        self,
        key: str,
    ) -> IntegrationProvider:
        provider = self._providers.get(key)

        if provider is None:
            raise ProviderNotRegisteredError(
                f"Provider is not registered: {key}"
            )

        return provider

    def contains(
        self,
        key: str,
    ) -> bool:
        return key in self._providers