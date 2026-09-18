from app.integrations.dependencies import get_integration_catalog


def test_integration_catalog_contains_enterprise_sources() -> None:
    catalog = get_integration_catalog()

    integrations = catalog.list_integrations()

    assert {
        integration.key
        for integration in integrations
    } == {
        "gmail",
        "google-drive",
        "sharepoint",
        "google-calendar",
        "erp",
    }