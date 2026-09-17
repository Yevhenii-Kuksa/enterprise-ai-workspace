from app.core.error_taxonomy import ErrorCategory, classify_error


def test_error_category_values_are_stable() -> None:
    assert ErrorCategory.VALIDATION.value == "validation"
    assert ErrorCategory.AUTHORIZATION.value == "authorization"
    assert ErrorCategory.DEPENDENCY.value == "dependency"
    assert ErrorCategory.AI_PROVIDER.value == "ai_provider"
    assert ErrorCategory.DATABASE.value == "database"
    assert ErrorCategory.INTERNAL.value == "internal"

def test_classify_error_maps_common_exceptions() -> None:
    assert classify_error(ValueError()) is ErrorCategory.VALIDATION
    assert (
        classify_error(PermissionError())
        is ErrorCategory.AUTHORIZATION
    )
    assert (
        classify_error(ConnectionError())
        is ErrorCategory.DEPENDENCY
    )
    assert (
        classify_error(TimeoutError())
        is ErrorCategory.DEPENDENCY
    )
    assert classify_error(RuntimeError()) is ErrorCategory.INTERNAL