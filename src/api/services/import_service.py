"""Service for importing legacy Grapevine files."""

from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.models import (
    Player, Character, Trait, ExperienceHistory,
    Action, Plot, Rumor, Item, Location
)
from src.legacy import GV3Parser


class ImportService:
    """Service for importing legacy Grapevine data."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.stats = {
            "players_imported": 0,
            "characters_imported": 0,
            "traits_imported": 0,
            "actions_imported": 0,
            "plots_imported": 0,
            "rumors_imported": 0,
            "items_imported": 0,
            "locations_imported": 0,
            "xp_history_imported": 0,
        }
    
    async def import_gv3(self, file_path: Path) -> dict[str, Any]:
        """Import a GV3 file and return import statistics."""
        parser = GV3Parser(file_path)
        data = parser.parse()
        
        # Import game info (optional, for validation/logging)
        game_info = data.get("game", {})
        
        # Import players first (needed for character relationships)
        await self._import_players(data.get("players", []))
        
        # Import characters with traits and XP history
        await self._import_characters(data.get("characters", []))
        
        # Import items
        await self._import_items(data.get("items", []))
        
        # Import locations
        await self._import_locations(data.get("locations", []))
        
        # Import actions
        await self._import_actions(data.get("actions", []))
        
        # Import plots
        await self._import_plots(data.get("plots", []))
        
        # Import rumors
        await self._import_rumors(data.get("rumors", []))
        
        # Commit all changes
        await self.db.commit()
        
        return {
            "success": True,
            "game_name": game_info.get("name", "Unknown"),
            "stats": self.stats,
        }
    
    async def _import_players(self, players_data: list[dict]) -> None:
        """Import players from legacy data."""
        for player_data in players_data:
            # Check if player already exists by name
            # For now, we'll just create new ones
            player = Player(
                name=player_data.get("name", "Unknown"),
                email=player_data.get("email") or None,
                phone=player_data.get("phone") or None,
                address=player_data.get("address") or None,
                status=player_data.get("status", "active"),
                position=player_data.get("position") or None,
                pp_unspent=player_data.get("pp_unspent", 0),
                pp_earned=player_data.get("pp_earned", 0),
            )
            self.db.add(player)
            self.stats["players_imported"] += 1
    
    async def _import_characters(self, characters_data: list[dict]) -> None:
        """Import characters with traits and XP history."""
        for char_data in characters_data:
            # Map legacy ID to new player if possible
            # For now, we'll leave player_id as None or map by name later
            
            character = Character(
                name=char_data.get("name", "Unknown"),
                race_type=char_data.get("race_type", "various").lower(),
                is_npc=char_data.get("is_npc", False),
                status=char_data.get("status", "active"),
                xp_unspent=char_data.get("xp_unspent", 0),
                xp_earned=char_data.get("xp_earned", 0),
                narrator=char_data.get("narrator") or None,
                biography=char_data.get("biography") or None,
                notes=char_data.get("notes") or None,
                data=char_data.get("data", {}),
            )
            self.db.add(character)
            await self.db.flush()  # Get character ID
            
            self.stats["characters_imported"] += 1
            
            # Import traits
            for trait_data in char_data.get("traits", []):
                trait = Trait(
                    character_id=character.id,
                    category=trait_data.get("category", "unknown"),
                    name=trait_data.get("name", "Unknown"),
                    value=trait_data.get("value") or None,
                    note=trait_data.get("note") or None,
                    display_type=trait_data.get("display_type", "simple"),
                    sort_order=trait_data.get("sort_order", 0),
                )
                self.db.add(trait)
                self.stats["traits_imported"] += 1
            
            # Import XP history
            for xp_data in char_data.get("xp_history", []):
                xp_entry = ExperienceHistory(
                    character_id=character.id,
                    entry_type=xp_data.get("entry_type", "earned"),
                    change_amount=xp_data.get("change_amount", 0),
                    reason=xp_data.get("reason") or None,
                    date=xp_data.get("date", ""),
                    unspent_after=xp_data.get("unspent_after"),
                    earned_after=xp_data.get("earned_after"),
                )
                self.db.add(xp_entry)
                self.stats["xp_history_imported"] += 1
    
    async def _import_items(self, items_data: list[dict]) -> None:
        """Import items from legacy data."""
        for item_data in items_data:
            item = Item(
                name=item_data.get("name", "Unknown Item"),
                item_type=item_data.get("item_type") or None,
                subtype=item_data.get("subtype") or None,
                level=item_data.get("level", 0),
                bonus=item_data.get("bonus", 0),
                damage_type=item_data.get("damage_type") or None,
                damage_amount=item_data.get("damage_amount", 0),
                concealability=item_data.get("concealability") or None,
                appearance=item_data.get("appearance") or None,
                powers=item_data.get("powers") or None,
                data=item_data.get("data", {}),
            )
            self.db.add(item)
            self.stats["items_imported"] += 1
    
    async def _import_locations(self, locations_data: list[dict]) -> None:
        """Import locations from legacy data."""
        for loc_data in locations_data:
            location = Location(
                name=loc_data.get("name", "Unknown Location"),
                location_type=loc_data.get("location_type") or None,
                level=loc_data.get("level", 0),
                access=loc_data.get("access") or None,
                affinity=loc_data.get("affinity") or None,
                totem=loc_data.get("totem") or None,
                security_traits=loc_data.get("security_traits", 0),
                security_retests=loc_data.get("security_retests", 0),
                gauntlet_shroud=loc_data.get("gauntlet_shroud") or None,
                where_description=loc_data.get("where_description") or None,
                appearance=loc_data.get("appearance") or None,
                security_description=loc_data.get("security_description") or None,
                umbra_description=loc_data.get("umbra_description") or None,
                links=loc_data.get("links") or None,
            )
            self.db.add(location)
            self.stats["locations_imported"] += 1
    
    async def _import_actions(self, actions_data: list[dict]) -> None:
        """Import actions from legacy data."""
        for action_data in actions_data:
            action = Action(
                character_id=action_data.get("character_id"),  # May need mapping
                action_date=action_data.get("action_date", ""),
                action_type=action_data.get("action_type", "Unknown"),
                level=action_data.get("level", 0),
                unused=action_data.get("unused", 0),
                total=action_data.get("total", 0),
                growth=action_data.get("growth", 0),
                action_text=action_data.get("action_text") or None,
                result_text=action_data.get("result_text") or None,
            )
            self.db.add(action)
            self.stats["actions_imported"] += 1
    
    async def _import_plots(self, plots_data: list[dict]) -> None:
        """Import plots from legacy data."""
        for plot_data in plots_data:
            plot = Plot(
                title=plot_data.get("title", "Untitled Plot"),
                description=plot_data.get("description") or None,
                status=plot_data.get("status", "active"),
            )
            self.db.add(plot)
            self.stats["plots_imported"] += 1
    
    async def _import_rumors(self, rumors_data: list[dict]) -> None:
        """Import rumors from legacy data."""
        for rumor_data in rumors_data:
            rumor = Rumor(
                title=rumor_data.get("title", "Untitled Rumor"),
                content=rumor_data.get("content") or None,
                level=rumor_data.get("level", 1),
                category=rumor_data.get("category") or None,
                rumor_date=rumor_data.get("rumor_date", ""),
                target_character_id=rumor_data.get("target_character_id"),
                target_race=rumor_data.get("target_race") or None,
                target_group=rumor_data.get("target_group") or None,
                target_influence=rumor_data.get("target_influence") or None,
            )
            self.db.add(rumor)
            self.stats["rumors_imported"] += 1
