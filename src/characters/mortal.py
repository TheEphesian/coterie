"""Mortal character implementation."""

from src.characters.base import RaceCharacter


class MortalCharacter(RaceCharacter):
    """Mortal character - baseline human."""
    
    race_type = "mortal"
    
    def get_trait_categories(self) -> list[str]:
        return [
            "physical", "social", "mental",
            "abilities", "backgrounds",
            "skills", "contacts",
            "merits", "flaws"
        ]
    
    def get_temper_fields(self) -> list[str]:
        return ["willpower"]
    
    def validate(self) -> list[str]:
        return []
