import uuid

from app.erp.service import ERPService
from app.integrations.erp_adapter import ErpRecordAdapter
from app.integrations.schemas import IntegrationRecord


class ERPIntegrationProvider:
    def __init__(
        self,
        *,
        service: ERPService,
        organization_id: uuid.UUID,
        source_system: str = "erp",
    ) -> None:
        self.service = service
        self.organization_id = organization_id
        self.source_system = source_system

    def fetch_records(
        self,
    ) -> list[IntegrationRecord]:
        records: list[IntegrationRecord] = []

        for product in self.service.list_products(
            organization_id=self.organization_id,
        ):
            records.append(
                ErpRecordAdapter.from_record(
                    source_system=self.source_system,
                    record_type="product",
                    external_id=product.source.source_record_id,
                    payload=product.model_dump(
                        mode="json",
                    ),
                    occurred_at=product.source.last_synced_at,
                )
            )

        for item in self.service.list_inventory(
            organization_id=self.organization_id,
        ):
            records.append(
                ErpRecordAdapter.from_record(
                    source_system=self.source_system,
                    record_type="inventory_item",
                    external_id=item.source.source_record_id,
                    payload=item.model_dump(
                        mode="json",
                    ),
                    occurred_at=item.source.last_synced_at,
                )
            )

        for order in self.service.list_orders(
            organization_id=self.organization_id,
        ):
            records.append(
                ErpRecordAdapter.from_record(
                    source_system=self.source_system,
                    record_type="order",
                    external_id=order.source.source_record_id,
                    payload=order.model_dump(
                        mode="json",
                    ),
                    occurred_at=order.source.last_synced_at,
                )
            )

        return records