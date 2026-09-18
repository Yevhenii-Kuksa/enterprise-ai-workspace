from typing import Annotated

from fastapi import Depends

from app.security.current_user import CurrentUser
from app.security.permission_dependency import require_permission

execution_permission_dependency = require_permission(
    "action.execute"
)

ExecutionUser = Annotated[
    CurrentUser,
    Depends(execution_permission_dependency),
]