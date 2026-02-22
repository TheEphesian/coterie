"""Service layer for boon operations."""

from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from src.core.models import Boon, BoonHistory, Character
from src.api.schemas import BoonCreate, BoonUpdate, BoonFilter, BoonHistoryCreate


class BoonService:
    """Service for boon CRUD operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, boon_id: str) -> Optional[Boon]:
        """Get boon by ID."""
        result = await self.db.execute(
            select(Boon).where(Boon.id == boon_id)
        )
        return result.scalar_one_or_none()
    
    async def list_boons(
        self,
        filters: Optional[BoonFilter] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Boon], int]:
        """List boons with optional filtering."""
        query = select(Boon)
        
        if filters:
            if filters.holder_id:
                query = query.where(Boon.holder_id == filters.holder_id)
            if filters.other_character_id:
                query = query.where(Boon.other_character_id == filters.other_character_id)
            if filters.boon_type:
                query = query.where(Boon.boon_type == filters.boon_type)
            if filters.status:
                query = query.where(Boon.status == filters.status)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Get paginated results
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        boons = list(result.scalars().all())
        
        return boons, total
    
    async def create(self, data: BoonCreate) -> Boon:
        """Create a new boon."""
        boon = Boon(
            holder_id=data.holder_id,
            other_character_id=data.other_character_id,
            boon_type=data.boon_type,
            is_owed=data.is_owed,
            description=data.description,
            boon_date=data.boon_date or datetime.now(timezone.utc),
            status=data.status,
        )
        
        self.db.add(boon)
        await self.db.flush()
        
        # Create history entry
        history = BoonHistory(
            boon_id=boon.id,
            change_type="created",
            new_status=boon.status,
            notes="Boon created",
        )
        self.db.add(history)
        await self.db.commit()
        
        return boon
    
    async def update(self, boon_id: str, data: BoonUpdate) -> Optional[Boon]:
        """Update an existing boon."""
        boon = await self.get_by_id(boon_id)
        if not boon:
            return None
        
        # Track changes for history
        old_status = boon.status
        
        # Update fields
        if data.holder_id is not None:
            boon.holder_id = data.holder_id
        if data.other_character_id is not None:
            boon.other_character_id = data.other_character_id
        if data.boon_type is not None:
            boon.boon_type = data.boon_type
        if data.is_owed is not None:
            boon.is_owed = data.is_owed
        if data.description is not None:
            boon.description = data.description
        if data.boon_date is not None:
            boon.boon_date = data.boon_date
        if data.status is not None:
            boon.status = data.status
        
        # Create history entry if status changed
        if data.status is not None and data.status != old_status:
            history = BoonHistory(
                boon_id=boon.id,
                change_type="modified",
                previous_status=old_status,
                new_status=boon.status,
                notes=f"Status changed from {old_status} to {boon.status}",
            )
            self.db.add(history)
        
        await self.db.commit()
        return boon
    
    async def delete(self, boon_id: str) -> bool:
        """Delete a boon."""
        boon = await self.get_by_id(boon_id)
        if not boon:
            return False
        
        await self.db.delete(boon)
        await self.db.commit()
        return True
    
    async def repay_boon(self, boon_id: str, notes: Optional[str] = None) -> Optional[Boon]:
        """Mark a boon as repaid."""
        boon = await self.get_by_id(boon_id)
        if not boon:
            return None
        
        old_status = boon.status
        boon.status = "repaid"
        
        history = BoonHistory(
            boon_id=boon.id,
            change_type="repaid",
            previous_status=old_status,
            new_status="repaid",
            notes=notes or "Boon repaid",
        )
        self.db.add(history)
        await self.db.commit()
        
        return boon
    
    async def default_boon(self, boon_id: str, notes: Optional[str] = None) -> Optional[Boon]:
        """Mark a boon as defaulted."""
        boon = await self.get_by_id(boon_id)
        if not boon:
            return None
        
        old_status = boon.status
        boon.status = "defaulted"
        
        history = BoonHistory(
            boon_id=boon.id,
            change_type="defaulted",
            previous_status=old_status,
            new_status="defaulted",
            notes=notes or "Boon defaulted",
        )
        self.db.add(history)
        await self.db.commit()
        
        return boon
    
    async def get_character_boonds(
        self,
        character_id: str,
        as_holder: bool = True,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Boon], int]:
        """Get boons for a specific character.
        
        Args:
            character_id: The character ID
            as_holder: If True, get boons where character is holder, 
                      otherwise where character is other_character
            skip: Pagination skip
            limit: Pagination limit
        """
        if as_holder:
            query = select(Boon).where(Boon.holder_id == character_id)
        else:
            query = select(Boon).where(Boon.other_character_id == character_id)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Get paginated results
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        boons = list(result.scalars().all())
        
        return boons, total


class BoonHistoryService:
    """Service for boon history operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, history_id: str) -> Optional[BoonHistory]:
        """Get history entry by ID."""
        result = await self.db.execute(
            select(BoonHistory).where(BoonHistory.id == history_id)
        )
        return result.scalar_one_or_none()
    
    async def list_history(
        self,
        boon_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[BoonHistory], int]:
        """List history entries for a boon."""
        query = select(BoonHistory).where(BoonHistory.boon_id == boon_id)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Get paginated results ordered by date
        query = query.order_by(BoonHistory.change_date.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        history = list(result.scalars().all())
        
        return history, total
    
    async def create(self, data: BoonHistoryCreate) -> BoonHistory:
        """Create a new history entry."""
        history = BoonHistory(
            boon_id=data.boon_id,
            change_type=data.change_type,
            previous_status=data.previous_status,
            new_status=data.new_status,
            notes=data.notes,
        )
        
        self.db.add(history)
        await self.db.commit()
        return history
