"""Demon: The Fallen character implementation."""

from src.characters.base import RaceCharacter


class DemonCharacter(RaceCharacter):
    """Demon character with House, Lores, and Torment."""
    
    race_type = "demon"
    
    HOUSES = ["Aleph", "Beth", "Gimel", "Daleth", "He", "Vau", "Zayin",
              "Heth", "Teth", "Yod", "Kaph", "Lamed", "Mem", "Nun",
              "Samekh", "Ayin", "Pe", "Tsade", "Qoph", "Resh", "Shin", "Tau"]
    
    LORES = ["Angelic", "Corporeal", "Demonic", "Ethereal", "Geis"]
    
    def get_trait_categories(self) -> list[str]:
        return [
            "physical", "social", "mental",
            "physical_neg", "social_neg", "mental_neg",
            "abilities", "backgrounds", "lores", "embeds", "edge",
            "faith", "cover", "resources",
            "merits", "flaws"
        ]
    
    def get_temper_fields(self) -> list[str]:
        return ["faith", "willpower", "torment"]
    
    def validate(self) -> list[str]:
        errors = []
        
        house = self.data.get("house")
        if house and house not in self.HOUSES:
            errors.append(f"Invalid house: {house}")
        
        return errors
