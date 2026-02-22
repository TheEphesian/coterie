"""Boon model for tracking favors between characters."""

from __future__ import annotations

from typing import Optional
from sqlalchemy import String, Integer, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone

from src.core.models.base import Base


class Boon(Base):
    """Boon/favor tracking between characters (primarily for Vampire games).
    
    Boons represent debts and favors owed between characters in the World of Darkness,
    particularly important in Vampire: The Masquerade where social obligations are
    tracked through a system of boons (trivial, minor, major, blood, life).
    """
    
    __tablename__ = "boons"
    
    game_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("games.id"), nullable=True, index=True
    )
    
    # Character Relationships
    # The character who holds the boon (either owes it or is owed it)
    holder_id: Mapped[str] = mapped_column(
        ForeignKey("characters.id"), nullable=False, index=True
    )
    # The character on the other end of the boon
    other_character_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("characters.id"), nullable=True, index=True
    )
    
    # Boon Details
    boon_type: Mapped[str] = mapped_column(
        String(50), 
        nullable=False,
        default="trivial"
    )  # trivial, minor, major, blood, life
    
    # Direction: True = holder is owed by other, False = holder owes other
    is_owed: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Description and Context
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    boon_date: Mapped[datetime] = mapped_column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc)
    )
    
    # Status
    status: Mapped[str] = mapped_column(
        String(50), 
        default="active"
    )  # active, repaid, defaulted
    
    # Relationships
    game: Mapped[Optional["Game"]] = relationship("Game")
    holder: Mapped["Character"] = relationship(
        "Character",
        foreign_keys=[holder_id],
        back_populates="held_boons"
    )
    other_character: Mapped[Optional["Character"]] = relationship(
        "Character",
        foreign_keys=[other_character_id],
        back_populates="owed_boons"
    )


class BoonHistory(Base):
    """History of boon status changes."""
    
    __tablename__ = "boon_history"
    
    boon_id: Mapped[str] = mapped_column(
        ForeignKey("boons.id"), nullable=False, index=True
    )
    
    change_type: Mapped[str] = mapped_column(
        String(50), 
        nullable=False
    )  # created, modified, repaid, defaulted
    
    previous_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    new_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    change_date: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )
    
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    boon: Mapped["Boon"] = relationship("Boon")
