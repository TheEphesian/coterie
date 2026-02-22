"""Mage: The Ascension character implementation."""

from src.characters.base import RaceCharacter


class MageCharacter(RaceCharacter):
    """Mage character with Traditions, Spheres, and Arete."""
    
    race_type = "mage"
    
    TRADITIONS = ["Tradition", "Cult of Ecstasy", "Dreamspeakers", "Euthanatos",
                  "Hermetic", "Orphans", "Verbena", "Virtual Adepts", "Akashic Brotherhood",
                  "Brotherhood of the Common Room", "Celestial Chorus", "Crafts",
                  "Order of Hermes", "Society of Ether", "Verbena"]
    
    SPHERES = ["Correspondence", "Entropy", "Forces", "Life", "Matter",
               "Mind", "Prime", "Spirit", "Time"]
    
    PARADIGMS = ["Dynamic", "Static", "Initiative", "Acropolitan"]
    
    def get_trait_categories(self) -> list[str]:
        return [
            "physical", "social", "mental",
            "physical_neg", "social_neg", "mental_neg",
            "abilities", "backgrounds", "spheres",
            "arts", "paradigm", "practice", "instruments",
            "merits", "flaws"
        ]
    
    def get_temper_fields(self) -> list[str]:
        return ["arete", "willpower", "quintessence"]
    
    def validate(self) -> list[str]:
        errors = []
        
        tradition = self.data.get("tradition")
        if tradition and tradition not in self.TRADITIONS:
            errors.append(f"Invalid tradition: {tradition}")
        
        arete = self.data.get("arete")
        if arete and not (1 <= arete <= 10):
            errors.append(f"Invalid arete: {arete}")
        
        return errors
