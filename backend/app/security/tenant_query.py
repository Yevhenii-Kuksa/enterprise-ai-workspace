import uuid

from sqlalchemy import Select
from sqlalchemy.orm.attributes import InstrumentedAttribute


def apply_tenant_filter[ModelT](
    statement: Select[tuple[ModelT]],
    organization_id_column: InstrumentedAttribute[uuid.UUID],
    organization_id: uuid.UUID,
) -> Select[tuple[ModelT]]:
    return statement.where(organization_id_column == organization_id)