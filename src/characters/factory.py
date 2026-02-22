"""Factory for creating race-specific character instances."""

from typing import Type

from src.characters.base import RaceCharacter
from src.characters.vampire import VampireCharacter
from src.characters.werewolf import WerewolfCharacter
from src.characters.mage import MageCharacter
from src.characters.changeling import ChangelingCharacter
from src.characters.wraith import WraithCharacter
from src.characters.mummy import MummyCharacter
from src.characters.kuei_jin import KueiJinCharacter
from src.characters.fera import FeraCharacter
from src.characters.hunter import HunterCharacter
from src.characters.demon import DemonCharacter
from src.characters.mortal import MortalCharacter
from src.characters.various import VariousCharacter

CHARACTER_REGISTRY: dict[str, Type[RaceCharacter]] = {
    "vampire": VampireCharacter,
    "werewolf": WerewolfCharacter,
    "mage": MageCharacter,
    "changeling": ChangelingCharacter,
    "wraith": WraithCharacter,
    "mummy": MummyCharacter,
    "kuei_jin": KueiJinCharacter,
    "fera": FeraCharacter,
    "hunter": HunterCharacter,
    "demon": DemonCharacter,
    "mortal": MortalCharacter,
    "various": VariousCharacter,
}


def get_character_class(race_type: str) -> Type[RaceCharacter]:
    """Get character class for race type."""
    race_type = race_type.lower().replace("-", "_").replace(" ", "_")
    if race_type not in CHARACTER_REGISTRY:
        raise ValueError(f"Unknown race type: {race_type}")
    return CHARACTER_REGISTRY[race_type]


def create_character(race_type: str, data: dict) -> RaceCharacter:
    """Create character instance for race type."""
    char_class = get_character_class(race_type)
    return char_class(data)


def list_races() -> list[str]:
    """List all supported race types."""
    return list(CHARACTER_REGISTRY.keys())
