from collections.abc import Iterable


def has_permission(
    granted_permissions: Iterable[str],
    required_permission: str,
) -> bool:
    return required_permission in set(granted_permissions)