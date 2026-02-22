"""Wraith: The Oblivion character implementation."""

from src.characters.base import RaceCharacter


class WraithCharacter(RaceCharacter):
    """Wraith character with Guild, Arcanoi, and Passions."""
    
    race_type = "wraith"
    
    GUILDS = ["Alchemist", "Bcms", "Charon", "Corpus", "Dust", "Echo",
              "Entropy", "Haunts", "Healers", "Kejakas", "Maerp", "Mnemosyne",
              "Orleans", "Oscur", "Pardoner", "Proctors", "Puppeteers",
              "Recon", "Reliquary", "Remains", "Saw", "Shades", "Slayer",
              "Sojourners", "Specter", "Tomb", "Usurer", "Venator", "Z发生"]
    
    ARCANOI = ["Arcanos", "Aquifer", "Atrocity", "Blade", "Blood", "Boil",
               "Caravan", "Castigate", "Chaos", "Conjure", "Crown", "Darkness",
               "Disassociate", "Embody", "Empower", "Enervation", "Erosion",
               "Fashion", "Flay", "Flow", "Flux", "Fetter", "Ghost Gate",
               "Inhabit", "Innocence", "Insanity", "Invoke", "Knot", "Labyrinth",
               "Leach", "Life", "Marionette", "Mimic", "Mortal", "Muffle",
               "Narcolepsy", "Obscure", "Obfuscate", "Outrage", "Panic",
               "Puppetry", "Rend", "Scare", "Shade", "Shadow", "Soften",
               "Soldier", "Sphinx", "Spite", "Stalk", "Static", "Steel",
               "Store", "Tempest", "Thirst", "Torpor", "Trick", "Ule",
               "Umbra", "Uncanny", "Usurp", "Vigor", "Void", "Weather", "Wither"]
    
    def get_trait_categories(self) -> list[str]:
        return [
            "physical", "social", "mental",
            "corpus", "passions", "arcanoi",
            "guild", "backgrounds", "fetters", "haunts",
            "merits", "flaws"
        ]
    
    def get_temper_fields(self) -> list[str]:
        return ["pathos", "willpower", "corpus"]
    
    def validate(self) -> list[str]:
        errors = []
        
        guild = self.data.get("guild")
        if guild and guild not in self.GUILDS:
            errors.append(f"Invalid guild: {guild}")
        
        return errors
