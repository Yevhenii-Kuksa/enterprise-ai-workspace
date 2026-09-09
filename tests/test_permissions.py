from app.security.permissions import has_permission


def test_has_permission_returns_true_when_permission_exists() -> None:
    granted_permissions = {
        "knowledge.read",
        "audit.read",
        "approvals.approve",
    }

    assert has_permission(granted_permissions, "audit.read") is True


def test_has_permission_returns_false_when_permission_is_missing() -> None:
    granted_permissions = {
        "knowledge.read",
        "audit.read",
    }

    assert has_permission(granted_permissions, "users.manage") is False