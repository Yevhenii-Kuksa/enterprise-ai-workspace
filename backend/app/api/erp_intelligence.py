import uuid
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.erp.dependencies import get_erp_service
from app.erp.intelligence import InventoryAvailability, OrderDelayState
from app.erp.service import ERPService
from app.security.current_user import CurrentUser
from app.security.permission_dependency import require_permission

router = APIRouter(
    prefix="/api/erp/intelligence",
    tags=["erp-intelligence"],
)


ERPReadUser = Annotated[
    CurrentUser,
    Depends(require_permission("erp.read")),
]

ERPServiceDependency = Annotated[
    ERPService,
    Depends(get_erp_service),
]


@router.get(
    "/inventory/availability",
    response_model=list[InventoryAvailability],
)
def get_inventory_availability(
    current_user: ERPReadUser,
    erp_service: ERPServiceDependency,
    product_id: Annotated[uuid.UUID | None, Query()] = None,
    location_id: Annotated[uuid.UUID | None, Query()] = None,
) -> list[InventoryAvailability]:
    return erp_service.get_inventory_availability(
        organization_id=current_user.organization_id,
        product_id=product_id,
        location_id=location_id,
        now=datetime.now(UTC),
    )


@router.get(
    "/orders/{order_id}/delay-state",
    response_model=OrderDelayState,
)
def get_order_delay_state(
    order_id: uuid.UUID,
    current_user: ERPReadUser,
    erp_service: ERPServiceDependency,
) -> OrderDelayState:
    delay_state = erp_service.get_order_delay_state(
        organization_id=current_user.organization_id,
        order_id=order_id,
        now=datetime.now(UTC),
    )

    if delay_state is None:
        raise HTTPException(
            status_code=404,
            detail="ERP order not found.",
        )

    return delay_state