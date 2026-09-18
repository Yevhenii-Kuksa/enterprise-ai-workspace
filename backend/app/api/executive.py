from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends

from app.executive.dependencies import get_executive_briefing_service
from app.executive.schemas import ExecutiveBriefing
from app.executive.service import ExecutiveBriefingService
from app.security.current_user import CurrentUser
from app.security.permission_dependency import require_permission

router = APIRouter(
    prefix="/api/executive",
    tags=["executive"],
)


ExecutiveReadUser = Annotated[
    CurrentUser,
    Depends(require_permission("executive.read")),
]

ExecutiveBriefingServiceDependency = Annotated[
    ExecutiveBriefingService,
    Depends(get_executive_briefing_service),
]


@router.get(
    "/briefing",
    response_model=ExecutiveBriefing,
)
def get_executive_briefing(
    current_user: ExecutiveReadUser,
    briefing_service: ExecutiveBriefingServiceDependency,
) -> ExecutiveBriefing:
    return briefing_service.generate_briefing(
        organization_id=current_user.organization_id,
        now=datetime.now(UTC),
    )