import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.approvals.service import ApprovalNotFoundError
from app.core.trace_context import TraceContext
from app.core.trace_dependencies import get_trace_context
from app.execution.dependencies import ExecutionUser
from app.execution.schemas import ActionExecutionResponse
from app.execution.service import (
    ExecutionActionDisabledError,
    ExecutionActionNotAllowedError,
    ExecutionApprovalExpiredError,
    ExecutionError,
    ExecutionExecutorNotAvailableError,
    ExecutionFingerprintError,
    ExecutionInvalidApprovalStateError,
    ExecutionInvalidStateError,
    ExecutionPermissionError,
    ExecutionService,
    ExecutionTenantError,
)
from app.execution.service_dependency import get_execution_service

router = APIRouter(
    prefix="/executions",
    tags=["executions"],
)


@router.post(
    "/approvals/{proposal_id}/execute",
    response_model=ActionExecutionResponse,
)
def execute_approved_proposal(
    proposal_id: uuid.UUID,
    current_user: ExecutionUser,
    service: Annotated[
        ExecutionService,
        Depends(get_execution_service),
    ],
    trace_context: Annotated[
        TraceContext,
        Depends(get_trace_context),
    ],
) -> ActionExecutionResponse:
    try:
        execution = service.execute_approved_proposal(
            organization_id=current_user.organization_id,
            proposal_id=proposal_id,
            current_user=current_user,
            trace_context=trace_context,
        )

    except ApprovalNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval proposal not found.",
        ) from exc

    except ExecutionInvalidApprovalStateError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Proposal is not approved for execution.",
        ) from exc

    except ExecutionApprovalExpiredError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Approval proposal has expired.",
        ) from exc

    except ExecutionFingerprintError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Proposal integrity verification failed.",
        ) from exc

    except ExecutionActionNotAllowedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Action is not allowed for execution.",
        ) from exc

    except ExecutionActionDisabledError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Action is disabled.",
        ) from exc

    except ExecutionPermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Execution permission denied.",
        ) from exc

    except ExecutionTenantError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Execution organization mismatch.",
        ) from exc

    except ExecutionInvalidStateError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Execution is in an invalid state.",
        ) from exc

    except ExecutionExecutorNotAvailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Execution service is temporarily unavailable.",
        ) from exc

    return ActionExecutionResponse.model_validate(
        execution
    )


@router.get(
    "",
    response_model=list[ActionExecutionResponse],
)
def list_executions(
    current_user: ExecutionUser,
    service: Annotated[
        ExecutionService,
        Depends(get_execution_service),
    ],
    limit: Annotated[
        int,
        Query(ge=1, le=100),
    ] = 100,
    offset: Annotated[
        int,
        Query(ge=0),
    ] = 0,
) -> list[ActionExecutionResponse]:
    executions = service.list_executions(
        organization_id=current_user.organization_id,
        limit=limit,
        offset=offset,
    )

    return [
        ActionExecutionResponse.model_validate(execution)
        for execution in executions
    ]


@router.get(
    "/{execution_id}",
    response_model=ActionExecutionResponse,
)
def get_execution(
    execution_id: uuid.UUID,
    current_user: ExecutionUser,
    service: Annotated[
        ExecutionService,
        Depends(get_execution_service),
    ],
) -> ActionExecutionResponse:
    try:
        execution = service.get_execution(
            organization_id=current_user.organization_id,
            execution_id=execution_id,
        )

    except ExecutionError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found.",
        ) from exc

    return ActionExecutionResponse.model_validate(
        execution
    )