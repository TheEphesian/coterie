"""Character model for Coterie."""

from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.models.base import Base
from src.core.models.chronicle import session_attendance

if TYPE_CHECKING:
    from src.core.models.chronicle import Chronicle, GameSession
    from .player import Player
    from .larp_trait import LarpTrait
    from .trait import Trait

class Character(Base):
    """Base character class for all World of Darkness characters."""
    __tablename__ = "characters"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    nature: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, default="")
    demeanor: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, default="")
    player_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, default="")
    status: Mapped[str] = mapped_column(String(50), default="active")
    narrator: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_npc: Mapped[bool] = mapped_column(Boolean, default=False)
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_modified: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    biography: Mapped[Optional[str]] = mapped_column(String)
    notes: Mapped[Optional[str]] = mapped_column(String(2000))
    
    # Chronicle relationship
    chronicle_id: Mapped[Optional[int]] = mapped_column(ForeignKey("chronicles.id"), nullable=True)
    
    # Player relationship
    player_id: Mapped[Optional[int]] = mapped_column(ForeignKey("players.id"), nullable=True)
    
    # Common attributes
    willpower: Mapped[int] = mapped_column(Integer, default=0)
    temp_willpower: Mapped[int] = mapped_column(Integer, default=0)
    
    # Experience points
    xp_earned: Mapped[int] = mapped_column(Integer, default=0)
    xp_unspent: Mapped[int] = mapped_column(Integer, default=0)

    # Race-specific data stored as JSON (used by API)
    data: Mapped[dict] = mapped_column(JSON, default=dict)

    # Discriminator column for polymorphic identity
    type: Mapped[str] = mapped_column(String(50))

    # Relationships
    chronicle: Mapped[Optional["Chronicle"]] = relationship(back_populates="characters")
    player: Mapped[Optional["Player"]] = relationship(back_populates="characters")
    larp_traits: Mapped[List["LarpTrait"]] = relationship(
        back_populates="character", lazy="selectin"
    )
    traits: Mapped[List["Trait"]] = relationship(
        back_populates="character", lazy="selectin"
    )
    attended_sessions: Mapped[List["GameSession"]] = relationship(
        secondary=session_attendance,
        back_populates="attending_characters"
    )

    __mapper_args__ = {
        "polymorphic_identity": "character",
        "polymorphic_on": "type",
    }

    @property
    def race_type(self) -> str:
        """API compatibility: returns race_type from data dict or type discriminator."""
        if self.data and "race_type" in self.data:
            return self.data["race_type"]
        return self.type

    @race_type.setter
    def race_type(self, value: str) -> None:
        """Store race_type in the data dict."""
        if self.data is None:
            self.data = {}
        data = dict(self.data)
        data["race_type"] = value
        self.data = data

    @property
    def created_at(self) -> Optional[datetime]:
        """API compatibility alias for start_date."""
        return self.start_date

    @property
    def updated_at(self) -> Optional[datetime]:
        """API compatibility alias for last_modified."""
        return self.last_modified

    def __repr__(self) -> str:
        return f"<Character {self.name} ({self.player_name})>" 