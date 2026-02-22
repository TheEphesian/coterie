"""Changeling: The Dreaming character implementation."""

from src.characters.base import RaceCharacter


class ChangelingCharacter(RaceCharacter):
    """Changeling character with Kith, Seeming, and Arts."""
    
    race_type = "changeling"
    
    SEEMINGS = ["Wilder", "Grump", "Childling"]
    
    KINDS = ["Arcadian", "Common", "Dreaming", "Shadow Court"]
    
    ARTS = ["Chicanery", "Legerdemain", "Primal", "Signer", "Soothsay",
            "Wayfare", "Chronos", "Discord", "Hedge", "Kingdoms"]
    
    def get_trait_categories(self) -> list[str]:
        return [
            "physical", "social", "mental",
            "physical_neg", "social_neg", "mental_neg",
            "abilities", "backgrounds", "realms",
            "arts", "birthright", "glee", "banality",
            "merits", "flaws"
        ]
    
    def get_temper_fields(self) -> list[str]:
        return ["glamour", "willpower", "banality"]
    
    def validate(self) -> list[str]:
        errors = []
        
        seeming = self.data.get("seeming")
        if seeming and seeming not in self.SEEMINGS:
            errors.append(f"Invalid seeming: {seeming}")
        
        kith = self.data.get("kith")
        if not kith:
            errors.append("Kith is required")
        
        return errors
