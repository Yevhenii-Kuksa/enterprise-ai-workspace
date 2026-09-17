import uuid

from app.erp.adapter import ERPAdapter
from app.erp.schemas import (
    ERPCustomer,
    ERPInventoryItem,
    ERPInventoryLocation,
    ERPInventoryReservation,
    ERPOrder,
    ERPProduct,
)


class ERPService:
    def __init__(self, adapter: ERPAdapter) -> None:
        self._adapter = adapter

    def get_product(
        self,
        *,
        organization_id: uuid.UUID,
        product_id: uuid.UUID,
    ) -> ERPProduct | None:
        return self._adapter.get_product(
            organization_id=organization_id,
            product_id=product_id,
        )

    def list_products(
        self,
        *,
        organization_id: uuid.UUID,
    ) -> list[ERPProduct]:
        return self._adapter.list_products(
            organization_id=organization_id,
        )

    def get_customer(
        self,
        *,
        organization_id: uuid.UUID,
        customer_id: uuid.UUID,
    ) -> ERPCustomer | None:
        return self._adapter.get_customer(
            organization_id=organization_id,
            customer_id=customer_id,
        )

    def list_inventory_locations(
        self,
        *,
        organization_id: uuid.UUID,
    ) -> list[ERPInventoryLocation]:
        return self._adapter.list_inventory_locations(
            organization_id=organization_id,
        )

    def list_inventory(
        self,
        *,
        organization_id: uuid.UUID,
        product_id: uuid.UUID | None = None,
        location_id: uuid.UUID | None = None,
    ) -> list[ERPInventoryItem]:
        return self._adapter.list_inventory(
            organization_id=organization_id,
            product_id=product_id,
            location_id=location_id,
        )

    def list_inventory_reservations(
        self,
        *,
        organization_id: uuid.UUID,
        product_id: uuid.UUID | None = None,
        location_id: uuid.UUID | None = None,
    ) -> list[ERPInventoryReservation]:
        return self._adapter.list_inventory_reservations(
            organization_id=organization_id,
            product_id=product_id,
            location_id=location_id,
        )

    def get_order(
        self,
        *,
        organization_id: uuid.UUID,
        order_id: uuid.UUID,
    ) -> ERPOrder | None:
        return self._adapter.get_order(
            organization_id=organization_id,
            order_id=order_id,
        )

    def list_orders(
        self,
        *,
        organization_id: uuid.UUID,
    ) -> list[ERPOrder]:
        return self._adapter.list_orders(
            organization_id=organization_id,
        )