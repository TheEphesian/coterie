"""Changing Breeds (Fera) character implementation."""

from src.characters.base import RaceCharacter


class FeraCharacter(RaceCharacter):
    """Fera (changing breeds) character with Fera type and Gifts."""
    
    race_type = "fera"
    
    FERA_TYPES = ["Ajaba", "Anansi", "Bastet", "Corax", "Grondr", "Kitsune",
                  "Mokole", "Nagah", "Nuwisha", "Ratkin", "Simba", "Wendigo"]
    
    def get_trait_categories(self) -> list[str]:
        return [
            "physical", "social", "mental",
            "physical_neg", "social_neg", "mental_neg",
            "abilities", "backgrounds", "gifts", " rites",
            "breed_aspects", "forms",
            "merits", "flaws"
        ]
    
    def get_temper_fields(self) -> list[str]:
        return ["rage", "gnosis", "willpower"]
    
    def validate(self) -> list[str]:
        errors = []
        
        fera_type = self.data.get("fera_type")
        if fera_type and fera_type not in self.FERA_TYPES:
            errors.append(f"Invalid Fera type: {fera_type}")
        
        return errors
