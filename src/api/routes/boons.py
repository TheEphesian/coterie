"""Boon API routes."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.api.services import BoonService, BoonHistoryService
from src.api.schemas import (
    BoonCreate,
    BoonUpdate,
    BoonResponse,
    BoonListResponse,
    BoonFilter,
    BoonHistoryResponse,
    BoonHistoryListResponse,
    ErrorResponse,
)

router = APIRouter(prefix="/boons", tags=["boons"])


@router.get(
    "",
    response_model=BoonListResponse,
    summary="List boons",
    description="Get a paginated list of boons with optional filtering.",
)
async def list_boons(
    holder_id: Optional[str] = Query(None, description="Filter by holder character ID"),
    other_character_id: Optional[str] = Query(None, description="Filter by other character ID"),
    boon_type: Optional[str] = Query(None, description="Filter by boon type (trivial, minor, major, blood, life)"),
    status: Optional[str] = Query(None, description="Filter by status (active, repaid, defaulted)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    db: AsyncSession = Depends(get_db),
) -> BoonListResponse:
    """List boons with optional filtering."""
    filters = BoonFilter(
        holder_id=holder_id,
        other_character_id=other_character_id,
        boon_type=boon_type,
        status=status,
    )
    
    service = BoonService(db)
    boons, total = await service.list_boons(filters=filters, skip=skip, limit=limit)
    
    return BoonListResponse(
        items=[BoonResponse.model_validate(b) for b in boons],
        total=total,
    )


@router.get(
    "/{boon_id}",
    response_model=BoonResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Get boon",
    description="Get a boon by ID.",
)
async def get_boon(
    boon_id: str,
    db: AsyncSession = Depends(get_db),
) -> BoonResponse:
    """Get a boon by ID."""
    service = BoonService(db)
    boon = await service.get_by_id(boon_id)
    
    if not boon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Boon with ID {boon_id} not found",
        )
    
    return BoonResponse.model_validate(boon)


@router.post(
    "",
    response_model=BoonResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create boon",
    description="Create a new boon (debt/favor between characters).",
)
async def create_boon(
    data: BoonCreate,
    db: AsyncSession = Depends(get_db),
) -> BoonResponse:
    """Create a new boon."""
    service = BoonService(db)
    boon = await service.create(data)
    return BoonResponse.model_validate(boon)


@router.patch(
    "/{boon_id}",
    response_model=BoonResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Update boon",
    description="Update an existing boon.",
)
async def update_boon(
    boon_id: str,
    data: BoonUpdate,
    db: AsyncSession = Depends(get_db),
) -> BoonResponse:
    """Update a boon."""
    service = BoonService(db)
    boon = await service.update(boon_id, data)
    
    if not boon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Boon with ID {boon_id} not found",
        )
    
    return BoonResponse.model_validate(boon)


@router.delete(
    "/{boon_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
    summary="Delete boon",
    description="Delete a boon by ID.",
)
async def delete_boon(
    boon_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a boon."""
    service = BoonService(db)
    deleted = await service.delete(boon_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Boon with ID {boon_id} not found",
        )


@router.post(
    "/{boon_id}/repay",
    response_model=BoonResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Repay boon",
    description="Mark a boon as repaid.",
)
async def repay_boon(
    boon_id: str,
    notes: Optional[str] = Query(None, description="Optional notes about repayment"),
    db: AsyncSession = Depends(get_db),
) -> BoonResponse:
    """Mark a boon as repaid."""
    service = BoonService(db)
    boon = await service.repay_boon(boon_id, notes)
    
    if not boon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Boon with ID {boon_id} not found",
        )
    
    return BoonResponse.model_validate(boon)


@router.post(
    "/{boon_id}/default",
    response_model=BoonResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Default boon",
    description="Mark a boon as defaulted.",
)
async def default_boon(
    boon_id: str,
    notes: Optional[str] = Query(None, description="Optional notes about default"),
    db: AsyncSession = Depends(get_db),
) -> BoonResponse:
    """Mark a boon as defaulted."""
    service = BoonService(db)
    boon = await service.default_boon(boon_id, notes)
    
    if not boon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Boon with ID {boon_id} not found",
        )
    
    return BoonResponse.model_validate(boon)


@router.get(
    "/{boon_id}/history",
    response_model=BoonHistoryListResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Get boon history",
    description="Get the history of changes for a boon.",
)
async def get_boon_history(
    boon_id: str,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    db: AsyncSession = Depends(get_db),
) -> BoonHistoryListResponse:
    """Get history entries for a boon."""
    service = BoonHistoryService(db)
    history, total = await service.list_history(boon_id, skip=skip, limit=limit)
    
    return BoonHistoryListResponse(
        items=[BoonHistoryResponse.model_validate(h) for h in history],
        total=total,
    )


@router.get(
    "/character/{character_id}/held",
    response_model=BoonListResponse,
    summary="Get boons held by character",
    description="Get all boons where the character is the holder.",
)
async def get_character_held_boonds(
    character_id: str,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    db: AsyncSession = Depends(get_db),
) -> BoonListResponse:
    """Get boons held by a character."""
    service = BoonService(db)
    boons, total = await service.get_character_boonds(
        character_id, as_holder=True, skip=skip, limit=limit
    )
    
    return BoonListResponse(
        items=[BoonResponse.model_validate(b) for b in boons],
        total=total,
    )


@router.get(
    "/character/{character_id}/owed",
    response_model=BoonListResponse,
    summary="Get boons owed to character",
    description="Get all boons where the character is owed by others.",
)
async def get_character_owed_boonds(
    character_id: str,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    db: AsyncSession = Depends(get_db),
) -> BoonListResponse:
    """Get boons owed to a character."""
    service = BoonService(db)
    boons, total = await service.get_character_boonds(
        character_id, as_holder=False, skip=skip, limit=limit
    )
    
    return BoonListResponse(
        items=[BoonResponse.model_validate(b) for b in boons],
        total=total,
    )
