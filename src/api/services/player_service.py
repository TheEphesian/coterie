"""Service layer for player operations."""

from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.models import Player, Character
from src.api.schemas import PlayerCreate, PlayerUpdate


class PlayerService:
    """Service for player CRUD operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, player_id: str) -> Optional[Player]:
        """Get player by ID."""
        result = await self.db.execute(
            select(Player).where(Player.id == player_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[Player]:
        """Get player by email."""
        result = await self.db.execute(
            select(Player).where(Player.email == email)
        )
        return result.scalar_one_or_none()
    
    async def list_players(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Player], int]:
        """List all players."""
        # Get total count
        count_result = await self.db.execute(select(func.count()).select_from(Player))
        total = count_result.scalar() or 0
        
        # Get paginated results
        result = await self.db.execute(
            select(Player).offset(skip).limit(limit)
        )
        players = list(result.scalars().all())
        
        return players, total
    
    async def create(self, data: PlayerCreate) -> Player:
        """Create a new player."""
        player = Player(
            name=data.name,
            email=data.email,
            phone=data.phone,
            address=data.address,
            status=data.status,
            position=data.position,
            pp_unspent=data.pp_unspent,
            pp_earned=data.pp_earned,
        )
        
        self.db.add(player)
        await self.db.commit()
        await self.db.refresh(player)
        return player
    
    async def update(self, player_id: str, data: PlayerUpdate) -> Optional[Player]:
        """Update a player."""
        player = await self.get_by_id(player_id)
        if not player:
            return None
        
        # Update fields
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(player, field, value)
        
        await self.db.commit()
        await self.db.refresh(player)
        return player
    
    async def delete(self, player_id: str) -> bool:
        """Delete a player."""
        player = await self.get_by_id(player_id)
        if not player:
            return False
        
        await self.db.delete(player)
        await self.db.commit()
        return True
    
    async def add_pp(self, player_id: str, amount: int) -> Optional[Player]:
        """Add player points."""
        player = await self.get_by_id(player_id)
        if not player:
            return None
        
        player.pp_earned += amount
        player.pp_unspent += amount
        
        await self.db.commit()
        await self.db.refresh(player)
        return player
    
    async def get_character_count(self, player_id: str) -> int:
        """Get character count for a player."""
        result = await self.db.execute(
            select(func.count())
            .select_from(Character)
            .where(Character.player_id == player_id)
        )
        return result.scalar() or 0
