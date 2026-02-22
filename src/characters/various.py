"""Generic/Custom character implementation."""

from src.characters.base import RaceCharacter


class VariousCharacter(RaceCharacter):
    """Various/custom character - flexible type."""
    
    race_type = "various"
    
    def get_trait_categories(self) -> list[str]:
        return [
            "physical", "social", "mental",
            "abilities", "backgrounds", "skills",
            "powers", "equipment",
            "merits", "flaws"
        ]
    
    def get_temper_fields(self) -> list[str]:
        return ["willpower"]
    
    def validate(self) -> list[str]:
        return []
