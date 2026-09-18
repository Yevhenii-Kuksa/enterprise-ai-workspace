from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.integrations.api_schemas import (
    IntegrationRecordResponse,
    IntegrationSummaryResponse,
)
from app.integrations.catalog import IntegrationCatalog
from app.integrations.dependencies import (
    get_integration_catalog,
    get_integration_service,
)
from app.integrations.service import (
    IntegrationProviderUnavailableError,
    IntegrationService,
    IntegrationSourceMismatchError,
    IntegrationUnavailableError,
)
from app.security.current_user import CurrentUser
from app.security.permission_dependency import require_permission

router = APIRouter(
    prefix="/api/integrations",
    tags=["integrations"],
)

integration_read_dependency = require_permission(
    "integration.read"
)


@router.get(
    "",
    response_model=list[IntegrationSummaryResponse],
)
def list_integrations(
    _: Annotated[
        CurrentUser,
        Depends(integration_read_dependency),
    ],
    catalog: Annotated[
        IntegrationCatalog,
        Depends(get_integration_catalog),
    ],
) -> list[IntegrationSummaryResponse]:
    return catalog.list_integrations()


@router.get(
    "/{integration_key}/records",
    response_model=list[IntegrationRecordResponse],
)
def list_integration_records(
    integration_key: str,
    _: Annotated[
        CurrentUser,
        Depends(integration_read_dependency),
    ],
    service: Annotated[
        IntegrationService,
        Depends(get_integration_service),
    ],
) -> list[IntegrationRecordResponse]:
    try:
        records = service.fetch_records(
            integration_key=integration_key,
        )
    except IntegrationUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except IntegrationProviderUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except IntegrationSourceMismatchError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    return [
        IntegrationRecordResponse.from_record(record)
        for record in records
    ]