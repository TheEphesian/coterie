"""Database models package."""

from src.core.models.base import Base

# Coterie models (primary - used by UI)
from .player import Player
from .character import Character
from .trait import Trait
from .chronicle import Chronicle, GameSession
from .larp_trait import LarpTrait, TraitCategory
from .vampire import Vampire, Discipline, Ritual, Bond
from .menu import MenuCategory, MenuItem
from .staff import Staff

# Grapevine-modern models (secondary - TODO: fix primary keys)
# from .apr import Action, Plot, Rumor
# from .item_location import Item, Location, CharacterItem, CharacterLocation
# from .boon import Boon, BoonHistory

__all__ = [
    "Base",
    "Player",
    "Character",
    "Trait",
    "Chronicle",
    "GameSession",
    "LarpTrait",
    "TraitCategory",
    "Vampire",
    "Discipline",
    "Ritual",
    "Bond",
    "MenuCategory",
    "MenuItem",
    "Staff",
]
