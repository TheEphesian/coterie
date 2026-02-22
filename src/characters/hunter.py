"""Hunter: The Reckoning character implementation."""

from src.characters.base import RaceCharacter


class HunterCharacter(RaceCharacter):
    """Hunter character with Creed, Edges, and Conviction."""
    
    race_type = "hunter"
    
    CREEDS = ["Avenger", "Defender", "Judge", "Martyr", "Redeemer", "Innocent",
              "Hermit", "Penitent", "Survivor", "Visionary"]
    
    EDGES = ["Athletics", "Brawl", "Drive", "Firearms", "Larceny", "Leadership",
             "Medicine", "Melee", "Politics", "Science", "Stealth", "Streetwise",
             "Subterfuge", "Survival", "Theory"]
    
    def get_trait_categories(self) -> list[str]:
        return [
            "physical", "social", "mental",
            "physical_neg", "social_neg", "mental_neg",
            "abilities", "backgrounds", "edges", "equipment",
            "beliefs", "addictions", "vice",
            "merits", "flaws"
        ]
    
    def get_temper_fields(self) -> list[str]:
        return ["conviction", "willpower", "faith"]
    
    def validate(self) -> list[str]:
        errors = []
        
        creed = self.data.get("creed")
        if creed and creed not in self.CREEDS:
            errors.append(f"Invalid creed: {creed}")
        
        return errors
