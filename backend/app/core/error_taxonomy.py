from enum import StrEnum


class ErrorCategory(StrEnum):
    VALIDATION = "validation"
    AUTHORIZATION = "authorization"
    DEPENDENCY = "dependency"
    AI_PROVIDER = "ai_provider"
    DATABASE = "database"
    INTERNAL = "internal"

def classify_error(exc: Exception) -> ErrorCategory:
    if isinstance(exc, ValueError):
        return ErrorCategory.VALIDATION

    if isinstance(exc, PermissionError):
        return ErrorCategory.AUTHORIZATION

    if isinstance(exc, (ConnectionError, TimeoutError)):
        return ErrorCategory.DEPENDENCY

    return ErrorCategory.INTERNAL