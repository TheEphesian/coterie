"""Parser for Grapevine 3.x binary game files (.gv3)."""

import struct
from pathlib import Path
from typing import Any, BinaryIO


class GV3Parser:
    """Parse legacy GV3 binary format."""
    
    MAGIC = b"GVBG"
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.version = 0.0
        self.data = {}
    
    def parse(self) -> dict[str, Any]:
        """Parse GV3 file and return structured data."""
        with open(self.file_path, "rb") as f:
            self._read_header(f)
            self._read_game_info(f)
            self._read_players(f)
            self._read_characters(f)
            self._read_items(f)
            self._read_locations(f)
            self._read_actions(f)
            self._read_plots(f)
            self._read_rumors(f)
        
        return self.data
    
    def _read_header(self, f: BinaryIO) -> None:
        """Read file header."""
        # Read 2-byte length prefix first
        length = struct.unpack("<H", f.read(2))[0]
        
        # Read magic bytes
        magic = f.read(4)
        if magic != self.MAGIC:
            raise ValueError(f"Invalid GV3 file: wrong magic bytes {magic}")
        
        # Read version and other header data
        self.version = struct.unpack("<f", f.read(4))[0]
        
        # Read remaining header (8 bytes)
        f.read(8)
    
    def _read_game_info(self, f: BinaryIO) -> None:
        """Read game information section."""
        self.data["game"] = {
            "name": self._read_string(f),
            "description": self._read_string(f),
            "email": self._read_string(f),
            "website": self._read_string(f),
        }
    
    def _read_players(self, f: BinaryIO) -> None:
        """Read player list."""
        try:
            count = self._read_count(f)
            players = []
            
            for _ in range(count):
                try:
                    player = {
                        "name": self._read_string(f),
                        "id": self._read_string(f),
                        "email": self._read_string(f),
                        "phone": self._read_string(f),
                        "address": self._read_string(f),
                        "status": self._read_string(f),
                        "position": self._read_string(f),
                        "pp_unspent": self._read_int(f),
                        "pp_earned": self._read_int(f),
                    }
                    players.append(player)
                except (struct.error, IOError):
                    break
            
            self.data["players"] = players
        except (struct.error, IOError):
            self.data["players"] = []
    
    def _read_characters(self, f: BinaryIO) -> None:
        """Read character list."""
        try:
            count = self._read_count(f)
            characters = []
            
            for _ in range(count):
                try:
                    char = {
                        "name": self._read_string(f),
                        "id": self._read_string(f),
                        "race_type": self._read_string(f),
                        "player_id": self._read_string(f),
                        "is_npc": self._read_bool(f),
                        "status": self._read_string(f),
                        "xp_unspent": self._read_int(f),
                        "xp_earned": self._read_int(f),
                        "narrator": self._read_string(f),
                        "biography": self._read_string(f),
                        "notes": self._read_string(f),
                    }
                    
                    char["data"] = self._read_json_data(f)
                    char["traits"] = self._read_traits(f)
                    char["xp_history"] = self._read_xp_history(f)
                    
                    characters.append(char)
                except (struct.error, IOError):
                    break
            
            self.data["characters"] = characters
        except (struct.error, IOError):
            self.data["characters"] = []
    
    def _read_traits(self, f: BinaryIO) -> list[dict]:
        """Read trait list for a character."""
        try:
            count = self._read_count(f)
            traits = []
            
            for _ in range(count):
                try:
                    trait = {
                        "category": self._read_string(f),
                        "name": self._read_string(f),
                        "value": self._read_string(f),
                        "note": self._read_string(f),
                        "display_type": self._read_string(f),
                    }
                    traits.append(trait)
                except (struct.error, IOError):
                    break
            
            return traits
        except (struct.error, IOError):
            return []
    
    def _read_xp_history(self, f: BinaryIO) -> list[dict]:
        """Read experience history entries."""
        try:
            count = self._read_count(f)
            history = []
            
            for _ in range(count):
                try:
                    entry = {
                        "date": self._read_string(f),
                        "entry_type": self._read_string(f),
                        "change_amount": self._read_int(f),
                        "reason": self._read_string(f),
                        "unspent_after": self._read_int(f),
                        "earned_after": self._read_int(f),
                    }
                    history.append(entry)
                except (struct.error, IOError):
                    break
            
            return history
        except (struct.error, IOError):
            return []
    
    def _read_items(self, f: BinaryIO) -> None:
        """Read item/equipment list."""
        try:
            count = self._read_count(f)
            items = []
            for _ in range(count):
                try:
                    item = {
                        "name": self._read_string(f),
                        "item_type": self._read_string(f),
                        "subtype": self._read_string(f),
                        "level": self._read_int(f),
                        "bonus": self._read_int(f),
                    }
                    items.append(item)
                except (struct.error, IOError):
                    break
            self.data["items"] = items
        except (struct.error, IOError):
            self.data["items"] = []
    
    def _read_locations(self, f: BinaryIO) -> None:
        """Read location list."""
        try:
            count = self._read_count(f)
            locations = []
            for _ in range(count):
                try:
                    location = {
                        "name": self._read_string(f),
                        "location_type": self._read_string(f),
                        "level": self._read_int(f),
                    }
                    locations.append(location)
                except (struct.error, IOError):
                    break
            self.data["locations"] = locations
        except (struct.error, IOError):
            self.data["locations"] = []
    
    def _read_actions(self, f: BinaryIO) -> None:
        """Read action list."""
        try:
            count = self._read_count(f)
            self.data["actions"] = []
            for _ in range(count):
                try:
                    action = {
                        "character_id": self._read_string(f),
                        "action_date": self._read_string(f),
                        "action_type": self._read_string(f),
                    }
                    self.data["actions"].append(action)
                except (struct.error, IOError):
                    break
        except (struct.error, IOError):
            self.data["actions"] = []
    
    def _read_plots(self, f: BinaryIO) -> None:
        """Read plot list."""
        try:
            count = self._read_count(f)
            plots = []
            for _ in range(count):
                try:
                    plot = {
                        "title": self._read_string(f),
                        "description": self._read_string(f),
                        "status": self._read_string(f),
                    }
                    plots.append(plot)
                except (struct.error, IOError):
                    break
            self.data["plots"] = plots
        except (struct.error, IOError):
            self.data["plots"] = []
    
    def _read_rumors(self, f: BinaryIO) -> None:
        """Read rumor list."""
        try:
            count = self._read_count(f)
            rumors = []
            for _ in range(count):
                try:
                    rumor = {
                        "title": self._read_string(f),
                        "content": self._read_string(f),
                        "level": self._read_int(f),
                        "rumor_date": self._read_string(f),
                    }
                    rumors.append(rumor)
                except (struct.error, IOError):
                    break
            self.data["rumors"] = rumors
        except (struct.error, IOError):
            self.data["rumors"] = []
    
    def _read_string(self, f: BinaryIO) -> str:
        """Read length-prefixed string (VB6 format: 2-byte length + string)."""
        length_bytes = f.read(2)
        if len(length_bytes) < 2:
            return ""
        length = struct.unpack("<H", length_bytes)[0]
        if length == 0 or length == 0xFFFF:
            return ""
        return f.read(length).decode("utf-8", errors="replace")
    
    def _read_count(self, f: BinaryIO) -> int:
        """Read count (2-byte integer)."""
        count_bytes = f.read(2)
        if len(count_bytes) < 2:
            return 0
        count = struct.unpack("<H", count_bytes)[0]
        # If count is unreasonable (>10000), try reading as 4 bytes
        if count > 10000:
            # Reset position and try 4-byte read
            remaining = f.read(2)
            if len(remaining) == 2:
                count = struct.unpack("<I", count_bytes + remaining)[0]
        return count
    
    def _read_int(self, f: BinaryIO) -> int:
        """Read 4-byte integer."""
        int_bytes = f.read(4)
        if len(int_bytes) < 4:
            return 0
        return struct.unpack("<i", int_bytes)[0]
    
    def _read_bool(self, f: BinaryIO) -> bool:
        """Read boolean (1 byte)."""
        bool_byte = f.read(1)
        if len(bool_byte) < 1:
            return False
        return struct.unpack("<?", bool_byte)[0]
    
    def _read_json_data(self, f: BinaryIO) -> dict:
        """Read JSON-like data structure."""
        # Placeholder - actual format needs analysis
        return {}
    
    def export(self, data: dict, file_path: Path) -> None:
        """Export data to GV3 format."""
        with open(file_path, "wb") as f:
            self._write_header(f)
            self._write_game_info(f, data.get("game", {}))
            self._write_players(f, data.get("players", []))
            self._write_characters(f, data.get("characters", []))
    
    def _write_header(self, f: BinaryIO) -> None:
        """Write file header."""
        f.write(struct.pack("<H", 4))  # Length prefix
        f.write(self.MAGIC)
        f.write(struct.pack("<f", 3.01))
        f.write(b"\x00" * 8)
    
    def _write_string(self, f: BinaryIO, s: str) -> None:
        """Write length-prefixed string (VB6 format: 2-byte length + string)."""
        encoded = s.encode("utf-8")
        length = len(encoded)
        if length == 0:
            f.write(struct.pack("<H", 0))
        else:
            f.write(struct.pack("<H", length))
            f.write(encoded)
    
    def _write_game_info(self, f: BinaryIO, game: dict) -> None:
        """Write game info."""
        self._write_string(f, game.get("name", ""))
        self._write_string(f, game.get("description", ""))
        self._write_string(f, game.get("email", ""))
        self._write_string(f, game.get("website", ""))
    
    def _write_players(self, f: BinaryIO, players: list) -> None:
        """Write players."""
        f.write(struct.pack("<H", len(players)))
        for player in players:
            self._write_string(f, player.get("name", ""))
            self._write_string(f, player.get("id", ""))
            self._write_string(f, player.get("email", ""))
            self._write_string(f, player.get("phone", ""))
            self._write_string(f, player.get("address", ""))
            self._write_string(f, player.get("status", ""))
            self._write_string(f, player.get("position", ""))
            f.write(struct.pack("<i", player.get("pp_unspent", 0)))
            f.write(struct.pack("<i", player.get("pp_earned", 0)))
    
    def _write_characters(self, f: BinaryIO, characters: list) -> None:
        """Write characters."""
        f.write(struct.pack("<H", len(characters)))
        for char in characters:
            self._write_string(f, char.get("name", ""))
            self._write_string(f, char.get("id", ""))
            self._write_string(f, char.get("race_type", ""))
            self._write_string(f, char.get("player_id", ""))
            f.write(struct.pack("<?", char.get("is_npc", False)))
            self._write_string(f, char.get("status", ""))
            f.write(struct.pack("<i", char.get("xp_unspent", 0)))
            f.write(struct.pack("<i", char.get("xp_earned", 0)))
            self._write_string(f, char.get("narrator", ""))
            self._write_string(f, char.get("biography", ""))
            self._write_string(f, char.get("notes", ""))
