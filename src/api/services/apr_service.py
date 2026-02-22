"""Service layer for APR (Action, Plot, Rumor) operations."""

from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.models import Action, Plot, Rumor
from src.api.schemas import ActionCreate, ActionUpdate, PlotCreate, PlotUpdate, RumorCreate, RumorUpdate


class ActionService:
    """Service for action CRUD operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, action_id: str) -> Optional[Action]:
        """Get action by ID."""
        result = await self.db.execute(
            select(Action).where(Action.id == action_id)
        )
        return result.scalar_one_or_none()
    
    async def list_actions(
        self,
        character_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Action], int]:
        """List actions with optional filtering."""
        query = select(Action)
        
        if character_id:
            query = query.where(Action.character_id == character_id)
        
        # Get total count
        count_result = await self.db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar() or 0
        
        # Get paginated results
        result = await self.db.execute(query.offset(skip).limit(limit))
        actions = list(result.scalars().all())
        
        return actions, total
    
    async def create(self, data: ActionCreate) -> Action:
        """Create a new action."""
        action = Action(
            character_id=data.character_id,
            action_date=data.action_date,
            action_type=data.action_type,
            level=data.level,
            unused=data.unused,
            total=data.total,
            growth=data.growth,
            action_text=data.action_text,
            result_text=data.result_text,
        )
        
        self.db.add(action)
        await self.db.commit()
        await self.db.refresh(action)
        return action
    
    async def update(self, action_id: str, data: ActionUpdate) -> Optional[Action]:
        """Update an action."""
        action = await self.get_by_id(action_id)
        if not action:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(action, field, value)
        
        await self.db.commit()
        await self.db.refresh(action)
        return action
    
    async def delete(self, action_id: str) -> bool:
        """Delete an action."""
        action = await self.get_by_id(action_id)
        if not action:
            return False
        
        await self.db.delete(action)
        await self.db.commit()
        return True


class PlotService:
    """Service for plot CRUD operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, plot_id: str) -> Optional[Plot]:
        """Get plot by ID."""
        result = await self.db.execute(
            select(Plot).where(Plot.id == plot_id)
        )
        return result.scalar_one_or_none()
    
    async def list_plots(
        self,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Plot], int]:
        """List plots with optional filtering."""
        query = select(Plot)
        
        if status:
            query = query.where(Plot.status == status)
        
        # Get total count
        count_result = await self.db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar() or 0
        
        # Get paginated results
        result = await self.db.execute(query.offset(skip).limit(limit))
        plots = list(result.scalars().all())
        
        return plots, total
    
    async def create(self, data: PlotCreate) -> Plot:
        """Create a new plot."""
        plot = Plot(
            title=data.title,
            description=data.description,
            status=data.status,
        )
        
        self.db.add(plot)
        await self.db.commit()
        await self.db.refresh(plot)
        return plot
    
    async def update(self, plot_id: str, data: PlotUpdate) -> Optional[Plot]:
        """Update a plot."""
        plot = await self.get_by_id(plot_id)
        if not plot:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(plot, field, value)
        
        await self.db.commit()
        await self.db.refresh(plot)
        return plot
    
    async def delete(self, plot_id: str) -> bool:
        """Delete a plot."""
        plot = await self.get_by_id(plot_id)
        if not plot:
            return False
        
        await self.db.delete(plot)
        await self.db.commit()
        return True


class RumorService:
    """Service for rumor CRUD operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, rumor_id: str) -> Optional[Rumor]:
        """Get rumor by ID."""
        result = await self.db.execute(
            select(Rumor).where(Rumor.id == rumor_id)
        )
        return result.scalar_one_or_none()
    
    async def list_rumors(
        self,
        category: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Rumor], int]:
        """List rumors with optional filtering."""
        query = select(Rumor)
        
        if category:
            query = query.where(Rumor.category == category)
        
        # Get total count
        count_result = await self.db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar() or 0
        
        # Get paginated results
        result = await self.db.execute(query.offset(skip).limit(limit))
        rumors = list(result.scalars().all())
        
        return rumors, total
    
    async def create(self, data: RumorCreate) -> Rumor:
        """Create a new rumor."""
        rumor = Rumor(
            title=data.title,
            content=data.content,
            level=data.level,
            category=data.category,
            rumor_date=data.rumor_date,
            target_character_id=data.target_character_id,
            target_race=data.target_race,
            target_group=data.target_group,
            target_influence=data.target_influence,
        )
        
        self.db.add(rumor)
        await self.db.commit()
        await self.db.refresh(rumor)
        return rumor
    
    async def update(self, rumor_id: str, data: RumorUpdate) -> Optional[Rumor]:
        """Update a rumor."""
        rumor = await self.get_by_id(rumor_id)
        if not rumor:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(rumor, field, value)
        
        await self.db.commit()
        await self.db.refresh(rumor)
        return rumor
    
    async def delete(self, rumor_id: str) -> bool:
        """Delete a rumor."""
        rumor = await self.get_by_id(rumor_id)
        if not rumor:
            return False
        
        await self.db.delete(rumor)
        await self.db.commit()
        return True
