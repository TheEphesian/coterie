"""Pydantic schemas for API request/response validation."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ============== Base Schemas ==============

class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class IDSchema(BaseSchema):
    """Schema with ID field."""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ============== Player Schemas ==============

class PlayerBase(BaseSchema):
    """Base player schema."""
    name: str = Field(..., min_length=1, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    status: str = Field(default="active", max_length=50)
    position: Optional[str] = Field(None, max_length=255)
    pp_unspent: int = Field(default=0, ge=0)
    pp_earned: int = Field(default=0, ge=0)


class PlayerCreate(PlayerBase):
    """Schema for creating a player."""
    pass


class PlayerUpdate(BaseSchema):
    """Schema for updating a player."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    status: Optional[str] = Field(None, max_length=50)
    position: Optional[str] = Field(None, max_length=255)
    pp_unspent: Optional[int] = Field(None, ge=0)
    pp_earned: Optional[int] = Field(None, ge=0)


class PlayerResponse(PlayerBase, IDSchema):
    """Schema for player response."""
    character_count: Optional[int] = None


class PlayerListResponse(BaseSchema):
    """Schema for player list response."""
    items: list[PlayerResponse]
    total: int


# ============== Trait Schemas ==============

class TraitBase(BaseSchema):
    """Base trait schema."""
    category: str = Field(..., max_length=50)
    name: str = Field(..., max_length=255)
    value: Optional[str] = Field(None, max_length=255)
    note: Optional[str] = None
    display_type: str = Field(default="simple", max_length=50)
    sort_order: int = Field(default=0)

    @field_validator("value", mode="before")
    @classmethod
    def coerce_value_to_str(cls, v: Any) -> Optional[str]:
        """Accept int or other types for value and coerce to str."""
        if v is None:
            return v
        return str(v)


class TraitCreate(TraitBase):
    """Schema for creating a trait."""
    pass


class TraitUpdate(BaseSchema):
    """Schema for updating a trait."""
    category: Optional[str] = Field(None, max_length=50)
    name: Optional[str] = Field(None, max_length=255)
    value: Optional[str] = Field(None, max_length=255)
    note: Optional[str] = None
    display_type: Optional[str] = Field(None, max_length=50)
    sort_order: Optional[int] = None


class TraitResponse(TraitBase, IDSchema):
    """Schema for trait response."""
    character_id: Optional[int] = None


# ============== Experience History Schemas ==============

class ExperienceHistoryBase(BaseSchema):
    """Base experience history schema."""
    entry_type: str = Field(..., max_length=50)  # 'earned' or 'spent'
    change_amount: int
    reason: Optional[str] = None
    date: str = Field(..., max_length=10)  # ISO date
    unspent_after: Optional[int] = None
    earned_after: Optional[int] = None


class ExperienceHistoryCreate(ExperienceHistoryBase):
    """Schema for creating experience history."""
    pass


class ExperienceHistoryResponse(ExperienceHistoryBase, IDSchema):
    """Schema for experience history response."""
    character_id: Optional[int] = None


# ============== Character Schemas ==============

class CharacterBase(BaseSchema):
    """Base character schema."""
    name: str = Field(..., min_length=1, max_length=255)
    race_type: str = Field(..., max_length=50)
    is_npc: bool = False
    status: str = Field(default="active", max_length=50)
    xp_unspent: int = Field(default=0, ge=0)
    xp_earned: int = Field(default=0, ge=0)
    biography: Optional[str] = None
    notes: Optional[str] = None
    narrator: Optional[str] = Field(None, max_length=255)
    data: dict[str, Any] = Field(default_factory=dict)


class CharacterCreate(CharacterBase):
    """Schema for creating a character."""
    player_id: Optional[int] = None
    traits: list[TraitCreate] = Field(default_factory=list)


class CharacterUpdate(BaseSchema):
    """Schema for updating a character."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    race_type: Optional[str] = Field(None, max_length=50)
    player_id: Optional[int] = None
    is_npc: Optional[bool] = None
    status: Optional[str] = Field(None, max_length=50)
    xp_unspent: Optional[int] = Field(None, ge=0)
    xp_earned: Optional[int] = Field(None, ge=0)
    biography: Optional[str] = None
    notes: Optional[str] = None
    narrator: Optional[str] = Field(None, max_length=255)
    data: Optional[dict[str, Any]] = None


class CharacterResponse(CharacterBase, IDSchema):
    """Schema for character response."""
    player_id: Optional[int] = None
    player_name: Optional[str] = None
    traits: list[TraitResponse] = Field(default_factory=list)
    xp_history: list[ExperienceHistoryResponse] = Field(default_factory=list)


class CharacterListResponse(BaseSchema):
    """Schema for character list response."""
    items: list[CharacterResponse]
    total: int


class CharacterFilter(BaseSchema):
    """Schema for character filtering."""
    race_type: Optional[str] = None
    player_id: Optional[int] = None
    is_npc: Optional[bool] = None
    status: Optional[str] = None


# ============== Item Schemas ==============

class ItemBase(BaseSchema):
    """Base item schema."""
    name: str = Field(..., min_length=1, max_length=255)
    item_type: Optional[str] = Field(None, max_length=100)
    subtype: Optional[str] = Field(None, max_length=100)
    level: int = Field(default=0, ge=0)
    bonus: int = Field(default=0)
    damage_type: Optional[str] = Field(None, max_length=50)
    damage_amount: int = Field(default=0)
    concealability: Optional[str] = Field(None, max_length=50)
    appearance: Optional[str] = None
    powers: Optional[str] = None
    data: dict[str, Any] = Field(default_factory=dict)


class ItemCreate(ItemBase):
    """Schema for creating an item."""
    pass


class ItemUpdate(BaseSchema):
    """Schema for updating an item."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    item_type: Optional[str] = Field(None, max_length=100)
    subtype: Optional[str] = Field(None, max_length=100)
    level: Optional[int] = Field(None, ge=0)
    bonus: Optional[int] = None
    damage_type: Optional[str] = Field(None, max_length=50)
    damage_amount: Optional[int] = None
    concealability: Optional[str] = Field(None, max_length=50)
    appearance: Optional[str] = None
    powers: Optional[str] = None
    data: Optional[dict[str, Any]] = None


class ItemResponse(ItemBase, IDSchema):
    """Schema for item response."""
    pass


class ItemListResponse(BaseSchema):
    """Schema for item list response."""
    items: list[ItemResponse]
    total: int


# ============== Location Schemas ==============

class LocationBase(BaseSchema):
    """Base location schema."""
    name: str = Field(..., min_length=1, max_length=255)
    location_type: Optional[str] = Field(None, max_length=100)
    level: int = Field(default=0, ge=0)
    owner_id: Optional[str] = None
    access: Optional[str] = None
    affinity: Optional[str] = Field(None, max_length=100)
    totem: Optional[str] = Field(None, max_length=255)
    security_traits: int = Field(default=0)
    security_retests: int = Field(default=0)
    gauntlet_shroud: Optional[str] = Field(None, max_length=50)
    where_description: Optional[str] = None
    appearance: Optional[str] = None
    security_description: Optional[str] = None
    umbra_description: Optional[str] = None
    links: Optional[str] = None


class LocationCreate(LocationBase):
    """Schema for creating a location."""
    pass


class LocationUpdate(BaseSchema):
    """Schema for updating a location."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    location_type: Optional[str] = Field(None, max_length=100)
    level: Optional[int] = Field(None, ge=0)
    owner_id: Optional[str] = None
    access: Optional[str] = None
    affinity: Optional[str] = Field(None, max_length=100)
    totem: Optional[str] = Field(None, max_length=255)
    security_traits: Optional[int] = None
    security_retests: Optional[int] = None
    gauntlet_shroud: Optional[str] = Field(None, max_length=50)
    where_description: Optional[str] = None
    appearance: Optional[str] = None
    security_description: Optional[str] = None
    umbra_description: Optional[str] = None
    links: Optional[str] = None


class LocationResponse(LocationBase, IDSchema):
    """Schema for location response."""
    owner_name: Optional[str] = None


class LocationListResponse(BaseSchema):
    """Schema for location list response."""
    items: list[LocationResponse]
    total: int


# ============== Action Schemas ==============

class ActionBase(BaseSchema):
    """Base action schema."""
    action_date: str = Field(..., max_length=10)  # ISO date
    action_type: str = Field(..., max_length=100)
    level: int = Field(default=0, ge=0)
    unused: int = Field(default=0, ge=0)
    total: int = Field(default=0, ge=0)
    growth: int = Field(default=0)
    action_text: Optional[str] = None
    result_text: Optional[str] = None


class ActionCreate(ActionBase):
    """Schema for creating an action."""
    character_id: Optional[int] = None


class ActionUpdate(BaseSchema):
    """Schema for updating an action."""
    action_date: Optional[str] = Field(None, max_length=10)
    action_type: Optional[str] = Field(None, max_length=100)
    level: Optional[int] = Field(None, ge=0)
    unused: Optional[int] = Field(None, ge=0)
    total: Optional[int] = Field(None, ge=0)
    growth: Optional[int] = None
    action_text: Optional[str] = None
    result_text: Optional[str] = None


class ActionResponse(ActionBase, IDSchema):
    """Schema for action response."""
    character_id: Optional[int] = None
    character_name: Optional[str] = None


class ActionListResponse(BaseSchema):
    """Schema for action list response."""
    items: list[ActionResponse]
    total: int


# ============== Plot Schemas ==============

class PlotBase(BaseSchema):
    """Base plot schema."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: str = Field(default="active", max_length=50)


class PlotCreate(PlotBase):
    """Schema for creating a plot."""
    pass


class PlotUpdate(BaseSchema):
    """Schema for updating a plot."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = Field(None, max_length=50)


class PlotResponse(PlotBase, IDSchema):
    """Schema for plot response."""
    pass


class PlotListResponse(BaseSchema):
    """Schema for plot list response."""
    items: list[PlotResponse]
    total: int


# ============== Rumor Schemas ==============

class RumorBase(BaseSchema):
    """Base rumor schema."""
    title: str = Field(..., min_length=1, max_length=255)
    content: Optional[str] = None
    level: int = Field(default=1, ge=1)
    category: Optional[str] = Field(None, max_length=50)
    rumor_date: str = Field(..., max_length=10)  # ISO date
    target_character_id: Optional[int] = None
    target_race: Optional[str] = Field(None, max_length=50)
    target_group: Optional[str] = Field(None, max_length=100)
    target_influence: Optional[str] = Field(None, max_length=100)


class RumorCreate(RumorBase):
    """Schema for creating a rumor."""
    pass


class RumorUpdate(BaseSchema):
    """Schema for updating a rumor."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = None
    level: Optional[int] = Field(None, ge=1)
    category: Optional[str] = Field(None, max_length=50)
    rumor_date: Optional[str] = Field(None, max_length=10)
    target_character_id: Optional[int] = None
    target_race: Optional[str] = Field(None, max_length=50)
    target_group: Optional[str] = Field(None, max_length=100)
    target_influence: Optional[str] = Field(None, max_length=100)


class RumorResponse(RumorBase, IDSchema):
    """Schema for rumor response."""
    pass


class RumorListResponse(BaseSchema):
    """Schema for rumor list response."""
    items: list[RumorResponse]
    total: int


# ============== Game Schemas ==============

class GameBase(BaseSchema):
    """Base game schema."""
    name: str = Field(..., min_length=1, max_length=255)
    chronicle: Optional[str] = Field(None, max_length=255)
    website: Optional[str] = Field(None, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None


class GameCreate(GameBase):
    """Schema for creating a game."""
    pass


class GameUpdate(BaseSchema):
    """Schema for updating a game."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    chronicle: Optional[str] = Field(None, max_length=255)
    website: Optional[str] = Field(None, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None


class GameResponse(GameBase, IDSchema):
    """Schema for game response."""
    player_count: Optional[int] = None
    character_count: Optional[int] = None


class GameListResponse(BaseSchema):
    """Schema for game list response."""
    items: list[GameResponse]
    total: int


# ============== Boon Schemas ==============

class BoonBase(BaseSchema):
    """Base boon schema."""
    holder_id: Optional[int] = None
    other_character_id: Optional[int] = None
    boon_type: str = Field(default="trivial", max_length=50)
    is_owed: bool = Field(default=True)
    description: Optional[str] = None
    boon_date: Optional[datetime] = None
    status: str = Field(default="active", max_length=50)


class BoonCreate(BoonBase):
    """Schema for creating a boon."""
    pass


class BoonUpdate(BaseSchema):
    """Schema for updating a boon."""
    holder_id: Optional[int] = None
    other_character_id: Optional[int] = None
    boon_type: Optional[str] = Field(None, max_length=50)
    is_owed: Optional[bool] = None
    description: Optional[str] = None
    boon_date: Optional[datetime] = None
    status: Optional[str] = Field(None, max_length=50)


class BoonResponse(BoonBase, IDSchema):
    """Schema for boon response."""
    pass


class BoonListResponse(BaseSchema):
    """Schema for boon list response."""
    items: list[BoonResponse]
    total: int


class BoonFilter(BaseSchema):
    """Schema for filtering boons."""
    holder_id: Optional[int] = None
    other_character_id: Optional[int] = None
    boon_type: Optional[str] = None
    status: Optional[str] = None


# ============== Boon History Schemas ==============

class BoonHistoryBase(BaseSchema):
    """Base boon history schema."""
    boon_id: int
    change_type: str = Field(..., max_length=50)
    previous_status: Optional[str] = Field(None, max_length=50)
    new_status: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None


class BoonHistoryCreate(BoonHistoryBase):
    """Schema for creating boon history entry."""
    pass


class BoonHistoryResponse(BoonHistoryBase, IDSchema):
    """Schema for boon history response."""
    change_date: datetime


class BoonHistoryListResponse(BaseSchema):
    """Schema for boon history list response."""
    items: list[BoonHistoryResponse]
    total: int


# ============== Error Response Schemas ==============

class ErrorResponse(BaseSchema):
    """Schema for error responses."""
    detail: str
    error_code: Optional[str] = None


class ValidationErrorResponse(BaseSchema):
    """Schema for validation error responses."""
    detail: list[dict[str, Any]]
