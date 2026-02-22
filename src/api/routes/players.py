"""Player API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.api.services import PlayerService
from src.api.schemas import (
    PlayerCreate,
    PlayerUpdate,
    PlayerResponse,
    PlayerListResponse,
    ErrorResponse,
)

router = APIRouter(prefix="/players", tags=["players"])


@router.get(
    "",
    response_model=PlayerListResponse,
    summary="List players",
    description="Get a paginated list of all players.",
)
async def list_players(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    db: AsyncSession = Depends(get_db),
) -> PlayerListResponse:
    """List all players."""
    service = PlayerService(db)
    players, total = await service.list_players(skip=skip, limit=limit)
    
    return PlayerListResponse(
        items=[PlayerResponse.model_validate(p) for p in players],
        total=total,
    )


@router.get(
    "/{player_id}",
    response_model=PlayerResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Get player",
    description="Get a player by ID.",
)
async def get_player(
    player_id: str,
    db: AsyncSession = Depends(get_db),
) -> PlayerResponse:
    """Get a player by ID."""
    service = PlayerService(db)
    player = await service.get_by_id(player_id)
    
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player with ID {player_id} not found",
        )
    
    # Add character count
    char_count = await service.get_character_count(player_id)
    response = PlayerResponse.model_validate(player)
    response.character_count = char_count
    
    return response


@router.post(
    "",
    response_model=PlayerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create player",
    description="Create a new player.",
)
async def create_player(
    data: PlayerCreate,
    db: AsyncSession = Depends(get_db),
) -> PlayerResponse:
    """Create a new player."""
    service = PlayerService(db)
    player = await service.create(data)
    return PlayerResponse.model_validate(player)


@router.patch(
    "/{player_id}",
    response_model=PlayerResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Update player",
    description="Update an existing player.",
)
async def update_player(
    player_id: str,
    data: PlayerUpdate,
    db: AsyncSession = Depends(get_db),
) -> PlayerResponse:
    """Update a player."""
    service = PlayerService(db)
    player = await service.update(player_id, data)
    
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player with ID {player_id} not found",
        )
    
    return PlayerResponse.model_validate(player)


@router.delete(
    "/{player_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
    summary="Delete player",
    description="Delete a player by ID.",
)
async def delete_player(
    player_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a player."""
    service = PlayerService(db)
    deleted = await service.delete(player_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player with ID {player_id} not found",
        )


@router.post(
    "/{player_id}/pp/add",
    response_model=PlayerResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Add Player Points",
    description="Add player points (PP) to a player.",
)
async def add_pp(
    player_id: str,
    amount: int = Query(..., gt=0, description="Amount of PP to add"),
    db: AsyncSession = Depends(get_db),
) -> PlayerResponse:
    """Add player points to a player."""
    service = PlayerService(db)
    player = await service.add_pp(player_id, amount)
    
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player with ID {player_id} not found",
        )
    
    return PlayerResponse.model_validate(player)
