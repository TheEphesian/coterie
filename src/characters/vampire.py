"""Vampire: The Masquerade character implementation."""

from src.characters.base import RaceCharacter


class VampireCharacter(RaceCharacter):
    """Vampire character with Camarilla/Sabbat/Anarch support."""
    
    race_type = "vampire"
    
    CLANS = [
        "Assamite", "Brujah", "Followers of Set", "Gangrel", "Giovanni",
        "Lasombra", "Malkavian", "Nosferatu", "Ravnos", "Toreador",
        "Tremere", "Tzimisce", "Ventru", "Caitiff", "Blood Brothers",
        "Gargoyles", "Harbingers of Skulls", "Kiasyd", "Nagaraja", "Salubri",
        "Samedi", "True Brujah", "Ahrimanes", "Anda", "Baali", "Bonsam",
        "Brujah antitribu", "City Gangrel", "Country Gangrel", "Daughters of Cacophony",
        "Gangrel antitribu", "Harbingers of Skulls", "Koldun", "Lamia", "Lhiannan",
        "Malkavian antitribu", "Nosferatu antitribu", "Pander", "Ravnos antitribu",
        "Serpents of the Light", "Toreador antitribu", "Tremere antitribu",
        "Ventru antitribu", "Angellis Ater", "Noiad"
    ]
    
    SECTS = ["Camarilla", "Sabbat", "Anarch", "Independent", "Inconnu"]
    
    PATHS = ["Humanity", "Path of the Beast", "Path of Blood", "Path of Bones",
             "Path of Metamorphosis", "Path of Night", "Path of Paradox",
             "Path of Power and the Inner Voice", "Path of Typhon", "Path of Lilith"]
    
    def get_trait_categories(self) -> list[str]:
        return [
            "physical", "social", "mental",
            "physical_neg", "social_neg", "mental_neg",
            "abilities", "backgrounds", "influences",
            "disciplines", "rituals", "status", "merits", "flaws"
        ]
    
    def get_temper_fields(self) -> list[str]:
        return ["blood", "willpower"]
    
    def validate(self) -> list[str]:
        errors = []
        
        clan = self.data.get("clan")
        if clan and clan not in self.CLANS:
            errors.append(f"Invalid clan: {clan}")
        
        sect = self.data.get("sect")
        if sect and sect not in self.SECTS:
            errors.append(f"Invalid sect: {sect}")
        
        generation = self.data.get("generation")
        if generation and not (4 <= generation <= 16):
            errors.append(f"Invalid generation: {generation}")
        
        return errors
