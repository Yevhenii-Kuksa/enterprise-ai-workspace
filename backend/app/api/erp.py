import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.erp.dependencies import get_erp_service
from app.erp.schemas import (
    ERPCustomer,
    ERPInventoryItem,
    ERPInventoryLocation,
    ERPInventoryReservation,
    ERPOrder,
    ERPProduct,
)
from app.erp.service import ERPService
from app.security.current_user import CurrentUser
from app.security.permission_dependency import require_permission

router = APIRouter(
    prefix="/api/erp",
    tags=["erp"],
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
    "/products",
    response_model=list[ERPProduct],
)
def list_products(
    current_user: ERPReadUser,
    service: ERPServiceDependency,
) -> list[ERPProduct]:
    return service.list_products(
        organization_id=current_user.organization_id,
    )


@router.get(
    "/products/{product_id}",
    response_model=ERPProduct,
)
def get_product(
    product_id: uuid.UUID,
    current_user: ERPReadUser,
    service: ERPServiceDependency,
) -> ERPProduct:
    product = service.get_product(
        organization_id=current_user.organization_id,
        product_id=product_id,
    )

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="ERP product not found.",
        )

    return product


@router.get(
    "/customers/{customer_id}",
    response_model=ERPCustomer,
)
def get_customer(
    customer_id: uuid.UUID,
    current_user: ERPReadUser,
    service: ERPServiceDependency,
) -> ERPCustomer:
    customer = service.get_customer(
        organization_id=current_user.organization_id,
        customer_id=customer_id,
    )

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="ERP customer not found.",
        )

    return customer


@router.get(
    "/inventory/locations",
    response_model=list[ERPInventoryLocation],
)
def list_inventory_locations(
    current_user: ERPReadUser,
    service: ERPServiceDependency,
) -> list[ERPInventoryLocation]:
    return service.list_inventory_locations(
        organization_id=current_user.organization_id,
    )


@router.get(
    "/inventory",
    response_model=list[ERPInventoryItem],
)
def list_inventory(
    current_user: ERPReadUser,
    service: ERPServiceDependency,
    product_id: Annotated[
        uuid.UUID | None,
        Query(),
    ] = None,
    location_id: Annotated[
        uuid.UUID | None,
        Query(),
    ] = None,
) -> list[ERPInventoryItem]:
    return service.list_inventory(
        organization_id=current_user.organization_id,
        product_id=product_id,
        location_id=location_id,
    )


@router.get(
    "/inventory/reservations",
    response_model=list[ERPInventoryReservation],
)
def list_inventory_reservations(
    current_user: ERPReadUser,
    service: ERPServiceDependency,
    product_id: Annotated[
        uuid.UUID | None,
        Query(),
    ] = None,
    location_id: Annotated[
        uuid.UUID | None,
        Query(),
    ] = None,
) -> list[ERPInventoryReservation]:
    return service.list_inventory_reservations(
        organization_id=current_user.organization_id,
        product_id=product_id,
        location_id=location_id,
    )


@router.get(
    "/orders",
    response_model=list[ERPOrder],
)
def list_orders(
    current_user: ERPReadUser,
    service: ERPServiceDependency,
) -> list[ERPOrder]:
    return service.list_orders(
        organization_id=current_user.organization_id,
    )


@router.get(
    "/orders/{order_id}",
    response_model=ERPOrder,
)
def get_order(
    order_id: uuid.UUID,
    current_user: ERPReadUser,
    service: ERPServiceDependency,
) -> ERPOrder:
    order = service.get_order(
        organization_id=current_user.organization_id,
        order_id=order_id,
    )

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="ERP order not found.",
        )

    return order