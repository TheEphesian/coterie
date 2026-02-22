"""Game model for game-level settings and configuration."""

from __future__ import annotations

from typing import Optional
from sqlalchemy import String, Integer, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone

from src.core.models.base import Base


class Game(Base):
    """Game/Chronicle entity containing global settings."""
    
    __tablename__ = "games"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Basic Information
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    chronicle_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Contact Information
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Game Details
    usual_place: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    usual_time: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Configuration Flags
    extended_health: Mapped[bool] = mapped_column(Boolean, default=True)
    enforce_history: Mapped[bool] = mapped_column(Boolean, default=True)
    link_trait_maxes: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Random Trait Configuration
    random_traits: Mapped[str] = mapped_column(
        String(255), 
        default="7,5,3,5,5,5,5",
        nullable=False
    )
    
    # ST Comment Markup
    st_comment_start: Mapped[str] = mapped_column(String(50), default="[ST]")
    st_comment_end: Mapped[str] = mapped_column(String(50), default="[/ST]")
    
    # File Format Version for compatibility
    file_format_version: Mapped[str] = mapped_column(String(10), default="3.01")
    
    # Relationships (viewonly to avoid back_populates conflicts with Coterie models)
    actions: Mapped[list["Action"]] = relationship(
        "Action", back_populates="game", lazy="selectin"
    )
    plots: Mapped[list["Plot"]] = relationship(
        "Plot", back_populates="game", lazy="selectin"
    )
    rumors: Mapped[list["Rumor"]] = relationship(
        "Rumor", back_populates="game", lazy="selectin"
    )
    calendar_entries: Mapped[list["Calendar"]] = relationship(
        "Calendar", back_populates="game", lazy="selectin"
    )
    xp_awards: Mapped[list["XPAward"]] = relationship(
        "XPAward", back_populates="game", lazy="selectin"
    )
    output_templates: Mapped[list["OutputTemplate"]] = relationship(
        "OutputTemplate", back_populates="game", lazy="selectin"
    )


class Calendar(Base):
    """Game date entries for the chronicle."""

    __tablename__ = "calendar"

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("games.id"), nullable=True, index=True
    )
    entry_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    game: Mapped[Game] = relationship("Game", back_populates="calendar_entries")


class XPAward(Base):
    """Standard XP and PP award templates."""

    __tablename__ = "xp_awards"

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("games.id"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    xp_amount: Mapped[int] = mapped_column(Integer, default=0)
    pp_amount: Mapped[int] = mapped_column(Integer, default=0)
    is_standard: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    game: Mapped[Game] = relationship("Game", back_populates="xp_awards")


class OutputTemplate(Base):
    """Templates for generating reports and character sheets."""

    __tablename__ = "output_templates"

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("games.id"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    template_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # 'character_sheet', 'roster', 'rumor_report', etc.
    format: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # 'html', 'text', 'rtf', 'pdf'
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    game: Mapped[Game] = relationship("Game", back_populates="output_templates")


class HealthLevel(Base):
    """Health level configuration for games."""

    __tablename__ = "health_levels"

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("games.id"), nullable=True, index=True
    )
    level_order: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    penalty: Mapped[int] = mapped_column(Integer, default=0)
    is_abbreviated: Mapped[bool] = mapped_column(
        Boolean, default=False
    )  # Whether this is for abbreviated health system
    
    # Relationships
    game: Mapped[Game] = relationship("Game")


class Rote(Base):
    """Mage rotes (prepared spells)."""

    __tablename__ = "rotes"

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("games.id"), nullable=True, index=True
    )
    character_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("characters.id"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    spheres: Mapped[str] = mapped_column(
        String(255), nullable=True
    )  # JSON array of required spheres
    level: Mapped[int] = mapped_column(Integer, default=1)
    
    # Relationships
    game: Mapped[Optional[Game]] = relationship("Game")
    character: Mapped[Optional["Character"]] = relationship("Character")


class SavedQuery(Base):
    """Saved queries for searching characters."""

    __tablename__ = "saved_queries"

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("games.id"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    query_data: Mapped[str] = mapped_column(
        Text, nullable=False
    )  # JSON representation of query clauses
    sort_field: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    sort_ascending: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    game: Mapped[Game] = relationship("Game")
