"""Action, Plot, Rumor models."""

from __future__ import annotations

from typing import Optional
from sqlalchemy import String, Integer, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.models.base import Base


class Action(Base):
    """Character downtime action."""
    
    __tablename__ = "actions"
    
    game_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("games.id"), nullable=True, index=True
    )
    character_id: Mapped[str] = mapped_column(
        ForeignKey("characters.id"), nullable=False, index=True
    )
    
    # Action Details
    action_date: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    action_type: Mapped[str] = mapped_column(String(100), nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=0)
    unused: Mapped[int] = mapped_column(Integer, default=0)
    total: Mapped[int] = mapped_column(Integer, default=0)
    growth: Mapped[int] = mapped_column(Integer, default=0)
    
    # Content
    action_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    result_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Status
    is_done: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    game: Mapped[Optional["Game"]] = relationship("Game", back_populates="actions")
    character: Mapped["Character"] = relationship("Character")


class Plot(Base):
    """Storyline/plot tracking."""
    
    __tablename__ = "plots"
    
    game_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("games.id"), nullable=True, index=True
    )
    
    # Plot Information
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active")
    
    # Relationships
    game: Mapped[Optional["Game"]] = relationship("Game", back_populates="plots")


class Rumor(Base):
    """Information/rumor distribution."""
    
    __tablename__ = "rumors"
    
    game_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("games.id"), nullable=True, index=True
    )
    
    # Rumor Information
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    level: Mapped[int] = mapped_column(Integer, default=1)
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    rumor_date: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    
    # Target Filters
    target_character_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("characters.id"), nullable=True, index=True
    )
    target_race: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    target_group: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    target_influence: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Distribution Tracking (JSON array of character IDs who received this)
    distributed_to: Mapped[dict] = mapped_column(JSON, default=dict)
    
    # Relationships
    game: Mapped[Optional["Game"]] = relationship("Game", back_populates="rumors")
