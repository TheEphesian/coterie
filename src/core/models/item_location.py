"""Items and Locations models."""

from __future__ import annotations

from typing import Optional
from sqlalchemy import String, Integer, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.models.base import Base


class Item(Base):
    """Equipment item."""
    
    __tablename__ = "items"
    
    game_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("games.id"), nullable=True, index=True
    )
    
    # Item Information
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    item_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    subtype: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    level: Mapped[int] = mapped_column(Integer, default=0)
    bonus: Mapped[int] = mapped_column(Integer, default=0)
    damage_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    damage_amount: Mapped[int] = mapped_column(Integer, default=0)
    concealability: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    appearance: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    powers: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    data: Mapped[dict] = mapped_column(JSON, default=dict)
    
    # Relationships
    game: Mapped[Optional["Game"]] = relationship("Game", back_populates="items")


class Location(Base):
    """Game location (haven, caern, etc.)."""
    
    __tablename__ = "locations"
    
    game_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("games.id"), nullable=True, index=True
    )
    
    # Location Information
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    location_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    level: Mapped[int] = mapped_column(Integer, default=0)
    owner_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("characters.id"), nullable=True, index=True
    )
    
    # Access and Security
    access: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    affinity: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    totem: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    security_traits: Mapped[int] = mapped_column(Integer, default=0)
    security_retests: Mapped[int] = mapped_column(Integer, default=0)
    
    # Descriptions
    gauntlet_shroud: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    where_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    appearance: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    security_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    umbra_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    links: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    game: Mapped[Optional["Game"]] = relationship("Game", back_populates="locations")


class CharacterItem(Base):
    """Association between character and item."""
    
    __tablename__ = "character_items"
    
    character_id: Mapped[str] = mapped_column(
        ForeignKey("characters.id"), nullable=False, index=True
    )
    item_id: Mapped[str] = mapped_column(
        ForeignKey("items.id"), nullable=False, index=True
    )
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    character: Mapped["Character"] = relationship("Character", back_populates="equipment")
    item: Mapped["Item"] = relationship("Item")


class CharacterLocation(Base):
    """Association between character and location."""
    
    __tablename__ = "character_locations"
    
    character_id: Mapped[str] = mapped_column(
        ForeignKey("characters.id"), nullable=False, index=True
    )
    location_id: Mapped[str] = mapped_column(
        ForeignKey("locations.id"), nullable=False, index=True
    )
    relationship_type: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )
    
    character: Mapped["Character"] = relationship("Character", back_populates="locations")
    location: Mapped["Location"] = relationship("Location")
