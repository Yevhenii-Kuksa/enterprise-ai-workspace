import uuid
from collections.abc import Iterable

from app.erp.adapter import ERPAdapter
from app.erp.schemas import (
    ERPCustomer,
    ERPInventoryItem,
    ERPInventoryLocation,
    ERPInventoryReservation,
    ERPOrder,
    ERPProduct,
)


class DemoERPAdapter(ERPAdapter):
    def __init__(
        self,
        *,
        products: Iterable[ERPProduct] = (),
        customers: Iterable[ERPCustomer] = (),
        inventory_locations: Iterable[ERPInventoryLocation] = (),
        inventory_items: Iterable[ERPInventoryItem] = (),
        inventory_reservations: Iterable[ERPInventoryReservation] = (),
        orders: Iterable[ERPOrder] = (),
    ) -> None:
        self._products = list(products)
        self._customers = list(customers)
        self._inventory_locations = list(inventory_locations)
        self._inventory_items = list(inventory_items)
        self._inventory_reservations = list(inventory_reservations)
        self._orders = list(orders)

    def get_product(
        self,
        *,
        organization_id: uuid.UUID,
        product_id: uuid.UUID,
    ) -> ERPProduct | None:
        return next(
            (
                product
                for product in self._products
                if product.organization_id == organization_id
                and product.id == product_id
            ),
            None,
        )

    def list_products(
        self,
        *,
        organization_id: uuid.UUID,
    ) -> list[ERPProduct]:
        return [
            product
            for product in self._products
            if product.organization_id == organization_id
        ]

    def get_customer(
        self,
        *,
        organization_id: uuid.UUID,
        customer_id: uuid.UUID,
    ) -> ERPCustomer | None:
        return next(
            (
                customer
                for customer in self._customers
                if customer.organization_id == organization_id
                and customer.id == customer_id
            ),
            None,
        )

    def list_inventory_locations(
        self,
        *,
        organization_id: uuid.UUID,
    ) -> list[ERPInventoryLocation]:
        return [
            location
            for location in self._inventory_locations
            if location.organization_id == organization_id
        ]

    def list_inventory(
        self,
        *,
        organization_id: uuid.UUID,
        product_id: uuid.UUID | None = None,
        location_id: uuid.UUID | None = None,
    ) -> list[ERPInventoryItem]:
        return [
            item
            for item in self._inventory_items
            if item.organization_id == organization_id
            and (product_id is None or item.product_id == product_id)
            and (location_id is None or item.location_id == location_id)
        ]

    def list_inventory_reservations(
        self,
        *,
        organization_id: uuid.UUID,
        product_id: uuid.UUID | None = None,
        location_id: uuid.UUID | None = None,
    ) -> list[ERPInventoryReservation]:
        return [
            reservation
            for reservation in self._inventory_reservations
            if reservation.organization_id == organization_id
            and (
                product_id is None
                or reservation.product_id == product_id
            )
            and (
                location_id is None
                or reservation.location_id == location_id
            )
        ]

    def get_order(
        self,
        *,
        organization_id: uuid.UUID,
        order_id: uuid.UUID,
    ) -> ERPOrder | None:
        return next(
            (
                order
                for order in self._orders
                if order.organization_id == organization_id
                and order.id == order_id
            ),
            None,
        )

    def list_orders(
        self,
        *,
        organization_id: uuid.UUID,
    ) -> list[ERPOrder]:
        return [
            order
            for order in self._orders
            if order.organization_id == organization_id
        ]