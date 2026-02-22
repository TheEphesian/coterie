"""Character API routes."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.api.services import CharacterService
from src.api.schemas import (
    CharacterCreate,
    CharacterUpdate,
    CharacterResponse,
    CharacterListResponse,
    CharacterFilter,
    ErrorResponse,
)

router = APIRouter(prefix="/characters", tags=["characters"])


@router.get(
    "",
    response_model=CharacterListResponse,
    summary="List characters",
    description="Get a paginated list of characters with optional filtering.",
)
async def list_characters(
    race_type: Optional[str] = Query(None, description="Filter by race type"),
    player_id: Optional[str] = Query(None, description="Filter by player ID"),
    is_npc: Optional[bool] = Query(None, description="Filter by NPC status"),
    status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    db: AsyncSession = Depends(get_db),
) -> CharacterListResponse:
    """List characters with optional filtering."""
    filters = CharacterFilter(
        race_type=race_type,
        player_id=player_id,
        is_npc=is_npc,
        status=status,
    )
    
    service = CharacterService(db)
    characters, total = await service.list_characters(filters=filters, skip=skip, limit=limit)
    
    return CharacterListResponse(
        items=[CharacterResponse.model_validate(c) for c in characters],
        total=total,
    )


@router.get(
    "/{character_id}",
    response_model=CharacterResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Get character",
    description="Get a character by ID.",
)
async def get_character(
    character_id: int,
    db: AsyncSession = Depends(get_db),
) -> CharacterResponse:
    """Get a character by ID."""
    service = CharacterService(db)
    character = await service.get_by_id(character_id)
    
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with ID {character_id} not found",
        )
    
    return CharacterResponse.model_validate(character)


@router.post(
    "",
    response_model=CharacterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create character",
    description="Create a new character.",
)
async def create_character(
    data: CharacterCreate,
    db: AsyncSession = Depends(get_db),
) -> CharacterResponse:
    """Create a new character."""
    service = CharacterService(db)
    character = await service.create(data)
    return CharacterResponse.model_validate(character)


@router.patch(
    "/{character_id}",
    response_model=CharacterResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Update character",
    description="Update an existing character.",
)
async def update_character(
    character_id: int,
    data: CharacterUpdate,
    db: AsyncSession = Depends(get_db),
) -> CharacterResponse:
    """Update a character."""
    service = CharacterService(db)
    character = await service.update(character_id, data)
    
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with ID {character_id} not found",
        )
    
    return CharacterResponse.model_validate(character)


@router.delete(
    "/{character_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
    summary="Delete character",
    description="Delete a character by ID.",
)
async def delete_character(
    character_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a character."""
    service = CharacterService(db)
    deleted = await service.delete(character_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with ID {character_id} not found",
        )


@router.post(
    "/{character_id}/xp/add",
    response_model=CharacterResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Add XP",
    description="Add experience points to a character.",
)
async def add_xp(
    character_id: int,
    amount: int = Query(..., gt=0, description="Amount of XP to add"),
    reason: str = Query(..., description="Reason for XP award"),
    db: AsyncSession = Depends(get_db),
) -> CharacterResponse:
    """Add experience points to a character."""
    service = CharacterService(db)
    character = await service.add_xp(character_id, amount, reason)
    
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with ID {character_id} not found",
        )
    
    return CharacterResponse.model_validate(character)


@router.post(
    "/{character_id}/xp/spend",
    response_model=CharacterResponse,
    responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}},
    summary="Spend XP",
    description="Spend experience points for a character.",
)
async def spend_xp(
    character_id: int,
    amount: int = Query(..., gt=0, description="Amount of XP to spend"),
    reason: str = Query(..., description="Reason for XP spend"),
    db: AsyncSession = Depends(get_db),
) -> CharacterResponse:
    """Spend experience points for a character."""
    service = CharacterService(db)
    character = await service.spend_xp(character_id, amount, reason)
    
    if not character:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Character not found or insufficient XP",
        )
    
    return CharacterResponse.model_validate(character)
