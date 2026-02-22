"""Werewolf: The Apocalypse character implementation."""

from src.characters.base import RaceCharacter


class WerewolfCharacter(RaceCharacter):
    """Garou character with tribe, auspice, and breed."""
    
    race_type = "werewolf"
    
    TRIBES = ["Black Furies", "Bone Gnawers", "Children of Gaia", "Fianna",
              "Get of Fenris", "Glass Walkers", "Red Talons", "Shadow Lords",
              "Silent Striders", "Silver Fangs", "Uktena", "Wendigo", "Stargazers",
              "Black Spiral Dancers", "Bane Tender", "Blooded"]
    
    BREEDS = ["Homid", "Lupus", "Metis"]
    AUSPICES = ["Ragabash", "Theurge", "Philodox", "Galliard", "Ahroun"]
    RANKS = ["Cliath", "Fostern", "Adren", "Athro", "Elder"]
    
    def get_trait_categories(self) -> list[str]:
        return [
            "physical", "social", "mental",
            "physical_neg", "social_neg", "mental_neg",
            "abilities", "backgrounds", "gifts", "rites",
            "honor_traits", "glory_traits", "wisdom_traits",
            "features", "merits", "flaws"
        ]
    
    def get_temper_fields(self) -> list[str]:
        return ["rage", "gnosis", "willpower"]
    
    def validate(self) -> list[str]:
        errors = []
        
        if self.data.get("tribe") not in self.TRIBES:
            errors.append(f"Invalid tribe: {self.data.get('tribe')}")
        
        if self.data.get("breed") not in self.BREEDS:
            errors.append(f"Invalid breed: {self.data.get('breed')}")
        
        if self.data.get("auspice") not in self.AUSPICES:
            errors.append(f"Invalid auspice: {self.data.get('auspice')}")
        
        return errors
