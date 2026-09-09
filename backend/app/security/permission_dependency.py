from collections.abc import Callable

from fastapi import Depends, HTTPException, status

from app.security.current_user import CurrentUser
from app.security.dependencies import get_current_user


def require_permission(
    permission_code: str,
) -> Callable[..., CurrentUser]:
    current_user_dependency = Depends(get_current_user)

    def dependency(
        current_user: CurrentUser = current_user_dependency,
    ) -> CurrentUser:
        if permission_code not in current_user.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied.",
            )

        return current_user

    return dependency