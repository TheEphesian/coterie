"""APR (Action, Plot, Rumor) API routes."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.api.services import ActionService, PlotService, RumorService
from src.api.schemas import (
    ActionCreate,
    ActionUpdate,
    ActionResponse,
    ActionListResponse,
    PlotCreate,
    PlotUpdate,
    PlotResponse,
    PlotListResponse,
    RumorCreate,
    RumorUpdate,
    RumorResponse,
    RumorListResponse,
    ErrorResponse,
)

router = APIRouter(prefix="/apr", tags=["apr"])


# ============== Action Routes ==============

@router.get(
    "/actions",
    response_model=ActionListResponse,
    summary="List actions",
    description="Get a paginated list of actions.",
)
async def list_actions(
    character_id: Optional[str] = Query(None, description="Filter by character ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    db: AsyncSession = Depends(get_db),
) -> ActionListResponse:
    """List actions with optional filtering."""
    service = ActionService(db)
    actions, total = await service.list_actions(
        character_id=character_id, skip=skip, limit=limit
    )
    
    return ActionListResponse(
        items=[ActionResponse.model_validate(a) for a in actions],
        total=total,
    )


@router.get(
    "/actions/{action_id}",
    response_model=ActionResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Get action",
    description="Get an action by ID.",
)
async def get_action(
    action_id: str,
    db: AsyncSession = Depends(get_db),
) -> ActionResponse:
    """Get an action by ID."""
    service = ActionService(db)
    action = await service.get_by_id(action_id)
    
    if not action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Action with ID {action_id} not found",
        )
    
    return ActionResponse.model_validate(action)


@router.post(
    "/actions",
    response_model=ActionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create action",
    description="Create a new action.",
)
async def create_action(
    data: ActionCreate,
    db: AsyncSession = Depends(get_db),
) -> ActionResponse:
    """Create a new action."""
    service = ActionService(db)
    action = await service.create(data)
    return ActionResponse.model_validate(action)


@router.patch(
    "/actions/{action_id}",
    response_model=ActionResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Update action",
    description="Update an existing action.",
)
async def update_action(
    action_id: str,
    data: ActionUpdate,
    db: AsyncSession = Depends(get_db),
) -> ActionResponse:
    """Update an action."""
    service = ActionService(db)
    action = await service.update(action_id, data)
    
    if not action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Action with ID {action_id} not found",
        )
    
    return ActionResponse.model_validate(action)


@router.delete(
    "/actions/{action_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
    summary="Delete action",
    description="Delete an action by ID.",
)
async def delete_action(
    action_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete an action."""
    service = ActionService(db)
    deleted = await service.delete(action_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Action with ID {action_id} not found",
        )


# ============== Plot Routes ==============

@router.get(
    "/plots",
    response_model=PlotListResponse,
    summary="List plots",
    description="Get a paginated list of plots.",
)
async def list_plots(
    status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    db: AsyncSession = Depends(get_db),
) -> PlotListResponse:
    """List plots with optional filtering."""
    service = PlotService(db)
    plots, total = await service.list_plots(status=status, skip=skip, limit=limit)
    
    return PlotListResponse(
        items=[PlotResponse.model_validate(p) for p in plots],
        total=total,
    )


@router.get(
    "/plots/{plot_id}",
    response_model=PlotResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Get plot",
    description="Get a plot by ID.",
)
async def get_plot(
    plot_id: str,
    db: AsyncSession = Depends(get_db),
) -> PlotResponse:
    """Get a plot by ID."""
    service = PlotService(db)
    plot = await service.get_by_id(plot_id)
    
    if not plot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plot with ID {plot_id} not found",
        )
    
    return PlotResponse.model_validate(plot)


@router.post(
    "/plots",
    response_model=PlotResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create plot",
    description="Create a new plot.",
)
async def create_plot(
    data: PlotCreate,
    db: AsyncSession = Depends(get_db),
) -> PlotResponse:
    """Create a new plot."""
    service = PlotService(db)
    plot = await service.create(data)
    return PlotResponse.model_validate(plot)


@router.patch(
    "/plots/{plot_id}",
    response_model=PlotResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Update plot",
    description="Update an existing plot.",
)
async def update_plot(
    plot_id: str,
    data: PlotUpdate,
    db: AsyncSession = Depends(get_db),
) -> PlotResponse:
    """Update a plot."""
    service = PlotService(db)
    plot = await service.update(plot_id, data)
    
    if not plot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plot with ID {plot_id} not found",
        )
    
    return PlotResponse.model_validate(plot)


@router.delete(
    "/plots/{plot_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
    summary="Delete plot",
    description="Delete a plot by ID.",
)
async def delete_plot(
    plot_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a plot."""
    service = PlotService(db)
    deleted = await service.delete(plot_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plot with ID {plot_id} not found",
        )


# ============== Rumor Routes ==============

@router.get(
    "/rumors",
    response_model=RumorListResponse,
    summary="List rumors",
    description="Get a paginated list of rumors.",
)
async def list_rumors(
    category: Optional[str] = Query(None, description="Filter by category"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    db: AsyncSession = Depends(get_db),
) -> RumorListResponse:
    """List rumors with optional filtering."""
    service = RumorService(db)
    rumors, total = await service.list_rumors(category=category, skip=skip, limit=limit)
    
    return RumorListResponse(
        items=[RumorResponse.model_validate(r) for r in rumors],
        total=total,
    )


@router.get(
    "/rumors/{rumor_id}",
    response_model=RumorResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Get rumor",
    description="Get a rumor by ID.",
)
async def get_rumor(
    rumor_id: str,
    db: AsyncSession = Depends(get_db),
) -> RumorResponse:
    """Get a rumor by ID."""
    service = RumorService(db)
    rumor = await service.get_by_id(rumor_id)
    
    if not rumor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rumor with ID {rumor_id} not found",
        )
    
    return RumorResponse.model_validate(rumor)


@router.post(
    "/rumors",
    response_model=RumorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create rumor",
    description="Create a new rumor.",
)
async def create_rumor(
    data: RumorCreate,
    db: AsyncSession = Depends(get_db),
) -> RumorResponse:
    """Create a new rumor."""
    service = RumorService(db)
    rumor = await service.create(data)
    return RumorResponse.model_validate(rumor)


@router.patch(
    "/rumors/{rumor_id}",
    response_model=RumorResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Update rumor",
    description="Update an existing rumor.",
)
async def update_rumor(
    rumor_id: str,
    data: RumorUpdate,
    db: AsyncSession = Depends(get_db),
) -> RumorResponse:
    """Update a rumor."""
    service = RumorService(db)
    rumor = await service.update(rumor_id, data)
    
    if not rumor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rumor with ID {rumor_id} not found",
        )
    
    return RumorResponse.model_validate(rumor)


@router.delete(
    "/rumors/{rumor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
    summary="Delete rumor",
    description="Delete a rumor by ID.",
)
async def delete_rumor(
    rumor_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a rumor."""
    service = RumorService(db)
    deleted = await service.delete(rumor_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rumor with ID {rumor_id} not found",
        )
