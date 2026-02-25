"""Power and writeup models for game rules data."""

from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, Boolean, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.models.base import Base

if TYPE_CHECKING:
    from .chronicle import Chronicle


class PowerCategory(Base):
    """Category of power (Discipline, Merit, Flaw, Ritual, etc.)."""
    __tablename__ = "power_categories"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

    powers: Mapped[List["Power"]] = relationship("Power", back_populates="category")

    def __repr__(self) -> str:
        return f"<PowerCategory {self.name}>"


class Power(Base):
    """A game power, trait, merit, flaw, or ability."""
    __tablename__ = "powers"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    category_id: Mapped[int] = mapped_column(ForeignKey("power_categories.id"))
    power_type: Mapped[str] = mapped_column(String(100))
    level_tier: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    level_order: Mapped[int] = mapped_column(Integer, default=1)
    trait_cost: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    prerequisites: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retest_ability: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    clans: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    category: Mapped["PowerCategory"] = relationship("PowerCategory", back_populates="powers")
    writeups: Mapped[List["PowerWriteup"]] = relationship("PowerWriteup", back_populates="power")

    def __repr__(self) -> str:
        return f"<Power {self.name} ({self.power_type})>"


class PowerWriteup(Base):
    """A source book's description of a power."""
    __tablename__ = "power_writeups"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    power_id: Mapped[int] = mapped_column(ForeignKey("powers.id"))
    source_book: Mapped[str] = mapped_column(String(200))
    page_number: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(Text)
    system_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    power: Mapped["Power"] = relationship("Power", back_populates="writeups")

    def __repr__(self) -> str:
        return f"<PowerWriteup {self.power_id} from {self.source_book} p.{self.page_number}>"


class ChronicleWriteupPreference(Base):
    """Per-chronicle override for which writeup to use for a power."""
    __tablename__ = "chronicle_writeup_preferences"
    __table_args__ = {'extend_existing': True}

    chronicle_id: Mapped[int] = mapped_column(ForeignKey("chronicles.id"), primary_key=True)
    power_id: Mapped[int] = mapped_column(ForeignKey("powers.id"), primary_key=True)
    writeup_id: Mapped[int] = mapped_column(ForeignKey("power_writeups.id"))

    writeup: Mapped["PowerWriteup"] = relationship("PowerWriteup")
