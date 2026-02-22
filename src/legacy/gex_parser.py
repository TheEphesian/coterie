"""Parser for Grapevine exchange files (.gex)."""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


class GEXParser:
    """Parse legacy GEX exchange format (XML-based)."""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.data = {}
    
    def parse(self) -> dict[str, Any]:
        """Parse GEX file (XML format)."""
        tree = ET.parse(self.file_path)
        root = tree.getroot()
        
        self.data = {
            "type": root.tag,
            "characters": [],
            "items": [],
            "game_info": {}
        }
        
        # Parse based on root element type
        if root.tag == "grapevine":
            self._parse_grapevine_format(root)
        else:
            self._parse_generic_format(root)
        
        return self.data
    
    def _parse_grapevine_format(self, root: ET.Element) -> None:
        """Parse standard Grapevine GEX format."""
        # Extract game info
        game_elem = root.find("game")
        if game_elem is not None:
            self.data["game_info"] = {
                "name": game_elem.get("name", ""),
                "date": game_elem.get("date", ""),
            }
        
        # Extract characters
        for char_elem in root.findall("character"):
            character = {
                "id": char_elem.get("id", ""),
                "name": char_elem.get("name", ""),
                "race_type": char_elem.get("type", ""),
            }
            self.data["characters"].append(character)
        
        # Extract items
        for item_elem in root.findall("item"):
            item = {
                "id": item_elem.get("id", ""),
                "name": item_elem.get("name", ""),
                "type": item_elem.get("type", ""),
            }
            self.data["items"].append(item)
    
    def _parse_generic_format(self, root: ET.Element) -> None:
        """Parse generic XML format."""
        # Try to extract any character/item references
        for elem in root.iter():
            if elem.tag.lower() in ["character", "char"]:
                self.data["characters"].append({
                    "id": elem.get("id", ""),
                    "name": elem.get("name", elem.text or ""),
                })
            elif elem.tag.lower() in ["item", "equipment"]:
                self.data["items"].append({
                    "id": elem.get("id", ""),
                    "name": elem.get("name", elem.text or ""),
                })
    
    def export(self, data: dict, file_path: Path) -> None:
        """Export data to GEX format."""
        root = ET.Element("grapevine")
        
        # Add game info
        game_info = data.get("game_info", {})
        game_elem = ET.SubElement(root, "game")
        game_elem.set("name", game_info.get("name", ""))
        game_elem.set("date", game_info.get("date", ""))
        
        # Add characters
        for char in data.get("characters", []):
            char_elem = ET.SubElement(root, "character")
            char_elem.set("id", char.get("id", ""))
            char_elem.set("name", char.get("name", ""))
            char_elem.set("type", char.get("race_type", ""))
        
        # Add items
        for item in data.get("items", []):
            item_elem = ET.SubElement(root, "item")
            item_elem.set("id", item.get("id", ""))
            item_elem.set("name", item.get("name", ""))
            item_elem.set("type", item.get("type", ""))
        
        # Write to file
        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")
        tree.write(file_path, encoding="utf-8", xml_declaration=True)
