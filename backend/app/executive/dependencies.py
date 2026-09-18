from typing import Annotated

from fastapi import Depends

from app.approvals.dependencies import get_approval_service
from app.approvals.service import ApprovalService
from app.erp.dependencies import get_erp_service
from app.erp.service import ERPService
from app.executive.service import ExecutiveBriefingService


def get_executive_briefing_service(
    erp_service: Annotated[
        ERPService,
        Depends(get_erp_service),
    ],
    approval_service: Annotated[
        ApprovalService,
        Depends(get_approval_service),
    ],
) -> ExecutiveBriefingService:
    return ExecutiveBriefingService(
        erp_service=erp_service,
        approval_service=approval_service,
    )