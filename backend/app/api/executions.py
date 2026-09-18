import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.trace_context import TraceContext
from app.execution.dependencies import ExecutionUser
from app.execution.schemas import ActionExecutionResponse
from app.execution.service import (
    ExecutionError,
    ExecutionInvalidApprovalStateError,
    ExecutionService,
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
) -> ActionExecutionResponse:
    try:
        execution = service.execute_approved_proposal(
            organization_id=current_user.organization_id,
            proposal_id=proposal_id,
            current_user=current_user,
            trace_context=TraceContext.create(),
        )
    except ExecutionInvalidApprovalStateError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Proposal is not approved for execution.",
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