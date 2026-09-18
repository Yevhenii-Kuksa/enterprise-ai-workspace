from typing import Annotated

from fastapi import Depends

from app.erp.dependencies import get_erp_service
from app.erp.service import ERPService
from app.executive.service import ExecutiveBriefingService


def get_executive_briefing_service(
    erp_service: Annotated[
        ERPService,
        Depends(get_erp_service),
    ],
) -> ExecutiveBriefingService:
    return ExecutiveBriefingService(erp_service)