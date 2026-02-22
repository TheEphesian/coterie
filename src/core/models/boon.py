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

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("games.id"), nullable=True, index=True
    )

    # Character Relationships
    holder_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("characters.id"), nullable=True, index=True
    )
    other_character_id: Mapped[Optional[int]] = mapped_column(
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
    holder: Mapped[Optional["Character"]] = relationship(
        "Character",
        foreign_keys=[holder_id],
    )
    other_character: Mapped[Optional["Character"]] = relationship(
        "Character",
        foreign_keys=[other_character_id],
    )
    history: Mapped[list["BoonHistory"]] = relationship(
        "BoonHistory", back_populates="boon", cascade="all, delete-orphan"
    )


class BoonHistory(Base):
    """History of boon status changes."""

    __tablename__ = "boon_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    boon_id: Mapped[int] = mapped_column(
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
    boon: Mapped["Boon"] = relationship("Boon", back_populates="history")
