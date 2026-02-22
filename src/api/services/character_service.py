"""Service layer for character operations."""

from datetime import datetime
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.models import Character, Player, Trait
from src.api.schemas import CharacterCreate, CharacterUpdate, CharacterFilter


class CharacterService:
    """Service for character CRUD operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, character_id: int) -> Optional[Character]:
        """Get character by ID."""
        result = await self.db.execute(
            select(Character).where(Character.id == character_id)
        )
        return result.scalar_one_or_none()

    async def list_characters(
        self,
        filters: Optional[CharacterFilter] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Character], int]:
        """List characters with optional filtering."""
        query = select(Character)

        if filters:
            if filters.race_type:
                # race_type is stored in the data JSON field
                query = query.where(
                    Character.data["race_type"].as_string() == filters.race_type
                )
            if filters.player_id:
                query = query.where(Character.player_id == filters.player_id)
            if filters.is_npc is not None:
                query = query.where(Character.is_npc == filters.is_npc)
            if filters.status:
                query = query.where(Character.status == filters.status)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Get paginated results
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        characters = list(result.scalars().all())

        return characters, total

    async def create(self, data: CharacterCreate) -> Character:
        """Create a new character."""
        now = datetime.utcnow()
        # Store race_type in data dict; use 'character' as the polymorphic type
        # to avoid issues with unknown polymorphic identities (werewolf, mage, etc.)
        char_data = dict(data.data or {})
        char_data["race_type"] = data.race_type
        character = Character(
            name=data.name,
            type="character",  # always use base identity to avoid mapper issues
            player_id=data.player_id,
            is_npc=data.is_npc,
            status=data.status,
            xp_unspent=data.xp_unspent,
            xp_earned=data.xp_earned,
            biography=data.biography,
            notes=data.notes,
            narrator=data.narrator,
            data=char_data,
            # Required model fields with defaults for API use
            nature="",
            demeanor="",
            player_name="",
            start_date=now,
            last_modified=now,
        )

        self.db.add(character)
        await self.db.flush()

        # Create traits if provided
        if data.traits:
            for trait_data in data.traits:
                # Convert str value to int (default to 0)
                try:
                    value_int = int(trait_data.value) if trait_data.value else 0
                except (ValueError, TypeError):
                    value_int = 0
                trait = Trait(
                    character_id=character.id,
                    category=trait_data.category,
                    name=trait_data.name,
                    value=value_int,
                    note=trait_data.note,
                    type="trait",  # polymorphic identity
                )
                self.db.add(trait)

        await self.db.commit()
        await self.db.refresh(character)
        return character

    async def update(self, character_id: int, data: CharacterUpdate) -> Optional[Character]:
        """Update a character."""
        character = await self.get_by_id(character_id)
        if not character:
            return None

        # Update fields; store race_type in data dict instead of type column
        update_data = data.model_dump(exclude_unset=True)
        if "race_type" in update_data:
            race_type = update_data.pop("race_type")
            current_data = dict(character.data or {})
            current_data["race_type"] = race_type
            character.data = current_data

        for field, value in update_data.items():
            if hasattr(character, field) and field not in ("type", "id"):
                setattr(character, field, value)

        character.last_modified = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(character)
        return character

    async def delete(self, character_id: int) -> bool:
        """Delete a character."""
        character = await self.get_by_id(character_id)
        if not character:
            return False

        await self.db.delete(character)
        await self.db.commit()
        return True

    async def add_xp(self, character_id: int, amount: int, reason: str) -> Optional[Character]:
        """Add experience points to a character."""
        character = await self.get_by_id(character_id)
        if not character:
            return None

        character.xp_earned += amount
        character.xp_unspent += amount
        character.last_modified = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(character)
        return character

    async def spend_xp(self, character_id: int, amount: int, reason: str) -> Optional[Character]:
        """Spend experience points for a character."""
        character = await self.get_by_id(character_id)
        if not character or character.xp_unspent < amount:
            return None

        character.xp_unspent -= amount
        character.last_modified = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(character)
        return character
