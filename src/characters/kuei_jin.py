"""Kindred of the East (Kuei-Jin) character implementation."""

from src.characters.base import RaceCharacter


class KueiJinCharacter(RaceCharacter):
    """Kuei-Jin character with Dharma, Chi, and Cathayan."""
    
    race_type = "kuei_jin"
    
    DHARMAS = ["Drunkard's Dream", "The Hungry Dead", "The Burning Crown",
               "The Celestial Chorus", "The Current of Air", "The Earth Rolls",
               "The Empty Mirror", "The Flowing River", "The Laughing Madman",
               "The Path of ten Thousand Stars", "The Pearl of Great Price",
               "The Rushing River", "The Serpent's Coil", "The Silent Wind",
               "The Standing Body", "The Stone Garden", "The Thunder Strike",
               "The Unerring Arrow", "The Wave", "Yin", "Zazen"]
    
    YIN_YANGS = ["Yin", "Yang"]
    
    def get_trait_categories(self) -> list[str]:
        return [
            "physical", "social", "mental",
            "physical_neg", "social_neg", "mental_neg",
            "abilities", "backgrounds", "disciplines", "kan", "yin_arts",
            "status", "merits", "flaws"
        ]
    
    def get_temper_fields(self) -> list[str]:
        return ["chi", "willpower", "yin"]
    
    def validate(self) -> list[str]:
        errors = []
        
        dharma = self.data.get("dharma")
        if dharma and dharma not in self.DHARMAS:
            errors.append(f"Invalid dharma: {dharma}")
        
        return errors
