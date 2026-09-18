import uuid
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel

from app.erp.schemas import (
    ERPInventoryItem,
    ERPInventoryReservation,
    ERPOrder,
    ERPSourceMetadata,
)


class InventoryAvailabilityState(StrEnum):
    AVAILABLE = "available"
    LIMITED = "limited"
    UNAVAILABLE = "unavailable"


class OrderDelayState(StrEnum):
    ON_TIME = "on_time"
    AT_RISK = "at_risk"
    DELAYED = "delayed"


class InventoryAvailability(BaseModel):
    organization_id: uuid.UUID
    product_id: uuid.UUID
    location_id: uuid.UUID
    on_hand: Decimal
    reserved: Decimal
    available: Decimal
    state: InventoryAvailabilityState
    source: ERPSourceMetadata


def calculate_available(
    *,
    on_hand: Decimal,
    reserved: Decimal,
) -> Decimal:
    return max(
        on_hand - reserved,
        Decimal("0"),
    )


def calculate_inventory_state(
    *,
    available: Decimal,
    on_hand: Decimal,
) -> InventoryAvailabilityState:
    if available <= 0:
        return InventoryAvailabilityState.UNAVAILABLE

    if on_hand > 0 and available < on_hand:
        return InventoryAvailabilityState.LIMITED

    return InventoryAvailabilityState.AVAILABLE


def is_reservation_active(
    reservation: ERPInventoryReservation,
    *,
    now: datetime,
) -> bool:
    if reservation.expires_at is None:
        return True

    return reservation.expires_at > now


def calculate_inventory_availability(
    item: ERPInventoryItem,
    reservations: list[ERPInventoryReservation],
    *,
    now: datetime | None = None,
) -> InventoryAvailability:
    matching_reservations = [
        reservation
        for reservation in reservations
        if reservation.organization_id == item.organization_id
        and reservation.product_id == item.product_id
        and reservation.location_id == item.location_id
    ]

    if now is not None:
        matching_reservations = [
            reservation
            for reservation in matching_reservations
            if is_reservation_active(
                reservation,
                now=now,
            )
        ]

    active_reserved = sum(
        (
            reservation.quantity
            for reservation in matching_reservations
        ),
        Decimal("0"),
    )

    reserved = max(
        item.reserved,
        active_reserved,
    )

    available = calculate_available(
        on_hand=item.on_hand,
        reserved=reserved,
    )

    state = calculate_inventory_state(
        available=available,
        on_hand=item.on_hand,
    )

    return InventoryAvailability(
        organization_id=item.organization_id,
        product_id=item.product_id,
        location_id=item.location_id,
        on_hand=item.on_hand,
        reserved=reserved,
        available=available,
        state=state,
        source=item.source,
    )


def calculate_order_delay_state(
    order: ERPOrder,
    *,
    now: datetime,
    at_risk_window_hours: int = 24,
) -> OrderDelayState:
    if order.completed_at is not None:
        return OrderDelayState.ON_TIME

    delivery_at = (
        order.confirmed_delivery_at
        or order.requested_delivery_at
    )

    if delivery_at is None:
        return OrderDelayState.ON_TIME

    if now > delivery_at:
        return OrderDelayState.DELAYED

    seconds_until_delivery = (
        delivery_at - now
    ).total_seconds()

    if seconds_until_delivery <= at_risk_window_hours * 3600:
        return OrderDelayState.AT_RISK

    return OrderDelayState.ON_TIME