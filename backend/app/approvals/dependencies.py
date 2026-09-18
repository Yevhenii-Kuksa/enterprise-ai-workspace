from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.approvals.service import ApprovalService
from app.db.dependencies import get_db


def get_approval_service(
    db: Annotated[
        Session,
        Depends(get_db),
    ],
) -> ApprovalService:
    return ApprovalService(db)