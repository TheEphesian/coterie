"""Mummy: The Resurrection character implementation."""

from src.characters.base import RaceCharacter


class MummyCharacter(RaceCharacter):
    """Mummy character with Amenti, Hekau, and Tomb."""
    
    race_type = "mummy"
    
    AMENTI = ["Apep", "Aset", "Djed", "Heh", "Heru", "Isis", "Maahes",
              "Mercury", "Neheb", "Nephthys", "Osiris", "Ptah", "Ra",
              "Sebek", "Seker", "Sekhmet", "Set", "Shu", "Tefnut", "Thoth", "Uraeus"]
    
    HEDYAT = ["Ba", "Ka", "Ren", "Sheut"]
    
    def get_trait_categories(self) -> list[str]:
        return [
            "physical", "social", "mental",
            "physical_neg", "social_neg", "mental_neg",
            "abilities", "backgrounds", "hekau", "tomb",
            "atonements", "utterances", "judgments",
            "merits", "flaws"
        ]
    
    def get_temper_fields(self) -> list[str]:
        return ["ba", "ka", "willpower"]
    
    def validate(self) -> list[str]:
        errors = []
        
        amenti = self.data.get("amenti")
        if amenti and amenti not in self.AMENTI:
            errors.append(f"Invalid Amenti: {amenti}")
        
        return errors
