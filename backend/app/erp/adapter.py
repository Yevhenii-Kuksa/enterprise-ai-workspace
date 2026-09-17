import uuid
from abc import ABC, abstractmethod

from app.erp.schemas import (
    ERPCustomer,
    ERPInventoryItem,
    ERPInventoryLocation,
    ERPInventoryReservation,
    ERPOrder,
    ERPProduct,
)


class ERPAdapter(ABC):
    @abstractmethod
    def get_product(
        self,
        *,
        organization_id: uuid.UUID,
        product_id: uuid.UUID,
    ) -> ERPProduct | None:
        pass

    @abstractmethod
    def list_products(
        self,
        *,
        organization_id: uuid.UUID,
    ) -> list[ERPProduct]:
        pass

    @abstractmethod
    def get_customer(
        self,
        *,
        organization_id: uuid.UUID,
        customer_id: uuid.UUID,
    ) -> ERPCustomer | None:
        pass

    @abstractmethod
    def list_inventory_locations(
        self,
        *,
        organization_id: uuid.UUID,
    ) -> list[ERPInventoryLocation]:
        pass

    @abstractmethod
    def list_inventory(
        self,
        *,
        organization_id: uuid.UUID,
        product_id: uuid.UUID | None = None,
        location_id: uuid.UUID | None = None,
    ) -> list[ERPInventoryItem]:
        pass

    @abstractmethod
    def list_inventory_reservations(
        self,
        *,
        organization_id: uuid.UUID,
        product_id: uuid.UUID | None = None,
        location_id: uuid.UUID | None = None,
    ) -> list[ERPInventoryReservation]:
        pass

    @abstractmethod
    def get_order(
        self,
        *,
        organization_id: uuid.UUID,
        order_id: uuid.UUID,
    ) -> ERPOrder | None:
        pass

    @abstractmethod
    def list_orders(
        self,
        *,
        organization_id: uuid.UUID,
    ) -> list[ERPOrder]:
        pass