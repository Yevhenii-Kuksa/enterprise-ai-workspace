import uuid
from datetime import datetime

from app.approvals.schemas import ApprovalStatus
from app.approvals.service import ApprovalService
from app.erp.facts import FactType
from app.erp.intelligence import (
    InventoryAvailability,
    InventoryAvailabilityState,
    OrderDelayState,
    calculate_order_delay_state,
)
from app.erp.schemas import ERPOrder, ERPOrderStatus
from app.erp.service import ERPService
from app.executive.schemas import (
    ExecutiveApprovalSummary,
    ExecutiveBriefing,
    ExecutiveBriefingSummary,
    ExecutiveEvidence,
    ExecutiveInventoryRisk,
    ExecutiveOrderException,
    ExecutiveRiskLevel,
)

ACTIVE_ORDER_STATUSES = {
    ERPOrderStatus.CONFIRMED,
    ERPOrderStatus.PROCESSING,
    ERPOrderStatus.READY,
    ERPOrderStatus.SHIPPED,
}


class ExecutiveBriefingService:
    def __init__(
        self,
        erp_service: ERPService,
        approval_service: ApprovalService,
    ) -> None:
        self._erp_service = erp_service
        self._approval_service = approval_service

    def generate_briefing(
        self,
        *,
        organization_id: uuid.UUID,
        now: datetime,
    ) -> ExecutiveBriefing:
        inventory = self._erp_service.get_inventory_availability(
            organization_id=organization_id,
            now=now,
        )

        orders = self._erp_service.list_orders(
            organization_id=organization_id,
        )

        inventory_risks = [
            risk
            for item in inventory
            if (risk := self._build_inventory_risk(item)) is not None
        ]

        order_exceptions = [
            exception
            for order in orders
            if (
                exception := self._build_order_exception(
                    order,
                    now=now,
                )
            )
            is not None
        ]

        active_orders = [
            order
            for order in orders
            if order.status in ACTIVE_ORDER_STATUSES
        ]

        summary = ExecutiveBriefingSummary(
            inventory_items=len(inventory),
            unavailable_inventory_items=sum(
                item.state == InventoryAvailabilityState.UNAVAILABLE
                for item in inventory
            ),
            limited_inventory_items=sum(
                item.state == InventoryAvailabilityState.LIMITED
                for item in inventory
            ),
            active_orders=len(active_orders),
            delayed_orders=sum(
                exception.delay_state == OrderDelayState.DELAYED
                for exception in order_exceptions
            ),
            at_risk_orders=sum(
                exception.delay_state == OrderDelayState.AT_RISK
                for exception in order_exceptions
            ),
        )

        evidence = self._collect_evidence(
            inventory_risks=inventory_risks,
            order_exceptions=order_exceptions,
        )

        approvals = ExecutiveApprovalSummary(
            pending=self._approval_service.count_by_status(
                organization_id=organization_id,
                status=ApprovalStatus.PENDING,
            ),
            approved=self._approval_service.count_by_status(
                organization_id=organization_id,
                status=ApprovalStatus.APPROVED,
            ),
            rejected=self._approval_service.count_by_status(
                organization_id=organization_id,
                status=ApprovalStatus.REJECTED,
            ),
        )

        return ExecutiveBriefing(
            organization_id=organization_id,
            generated_at=now,
            summary=summary,
            inventory_risks=inventory_risks,
            order_exceptions=order_exceptions,
            approvals=approvals,
            evidence=evidence,
        )

    def _build_inventory_risk(
        self,
        item: InventoryAvailability,
    ) -> ExecutiveInventoryRisk | None:
        if item.state == InventoryAvailabilityState.AVAILABLE:
            return None

        if item.state == InventoryAvailabilityState.UNAVAILABLE:
            risk_level = ExecutiveRiskLevel.CRITICAL
            message_pl = "Brak dostępnego zapasu."
        else:
            risk_level = ExecutiveRiskLevel.WARNING
            message_pl = "Ograniczona dostępność zapasu."

        evidence = self._build_system_evidence(
            entity_type="inventory",
            entity_id=f"{item.product_id}:{item.location_id}",
            source_system=item.source.source_system,
            source_record_id=item.source.source_record_id,
            last_synced_at=item.source.last_synced_at,
        )

        return ExecutiveInventoryRisk(
            product_id=item.product_id,
            location_id=item.location_id,
            on_hand=item.on_hand,
            reserved=item.reserved,
            available=item.available,
            availability_state=item.state,
            risk_level=risk_level,
            message_pl=message_pl,
            evidence=[evidence],
        )

    def _build_order_exception(
        self,
        order: ERPOrder,
        *,
        now: datetime,
    ) -> ExecutiveOrderException | None:
        if order.status not in ACTIVE_ORDER_STATUSES:
            return None

        delay_state = calculate_order_delay_state(
            order,
            now=now,
        )

        if delay_state == OrderDelayState.ON_TIME:
            return None

        if delay_state == OrderDelayState.DELAYED:
            risk_level = ExecutiveRiskLevel.CRITICAL
            message_pl = "Zamówienie jest opóźnione."
        else:
            risk_level = ExecutiveRiskLevel.WARNING
            message_pl = "Zamówienie jest zagrożone opóźnieniem."

        evidence = self._build_system_evidence(
            entity_type="order",
            entity_id=str(order.id),
            source_system=order.source.source_system,
            source_record_id=order.source.source_record_id,
            last_synced_at=order.source.last_synced_at,
        )

        return ExecutiveOrderException(
            order_id=order.id,
            order_number=order.order_number,
            lifecycle_status=order.status,
            delay_state=delay_state,
            risk_level=risk_level,
            message_pl=message_pl,
            evidence=[evidence],
        )

    def _build_system_evidence(
        self,
        *,
        entity_type: str,
        entity_id: str,
        source_system: str,
        source_record_id: str,
        last_synced_at: datetime,
    ) -> ExecutiveEvidence:
        return ExecutiveEvidence(
            fact_type=FactType.SYSTEM_FACT,
            entity_type=entity_type,
            entity_id=entity_id,
            source_system=source_system,
            source_record_id=source_record_id,
            last_synced_at=last_synced_at,
        )

    def _collect_evidence(
        self,
        *,
        inventory_risks: list[ExecutiveInventoryRisk],
        order_exceptions: list[ExecutiveOrderException],
    ) -> list[ExecutiveEvidence]:
        evidence: list[ExecutiveEvidence] = []

        for risk in inventory_risks:
            evidence.extend(risk.evidence)

        for exception in order_exceptions:
            evidence.extend(exception.evidence)

        return evidence