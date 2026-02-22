"""Parser for Grapevine menu files (.gvm)."""

import struct
from pathlib import Path
from typing import Any, BinaryIO


class GVMParser:
    """Parse legacy GVM binary menu format."""
    
    MAGIC = b"GVBM"
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.menus = []
    
    def parse(self) -> list[dict]:
        """Parse GVM file and return menu structure."""
        with open(self.file_path, "rb") as f:
            self._read_header(f)
            self._read_menus(f)
        
        return self.menus
    
    def _read_header(self, f: BinaryIO) -> None:
        """Read file header."""
        # Read 2-byte length prefix first
        length = struct.unpack("<H", f.read(2))[0]
        
        # Read magic bytes
        magic = f.read(4)
        if magic != self.MAGIC:
            raise ValueError(f"Invalid GVM file: wrong magic bytes {magic}")
        
        version = struct.unpack("<f", f.read(4))[0]
        f.read(8)
    
    def _read_menus(self, f: BinaryIO) -> None:
        """Read menu list."""
        try:
            count = self._read_count(f)
            
            for _ in range(count):
                try:
                    menu = {
                        "name": self._read_string(f),
                        "items": self._read_menu_items(f),
                    }
                    self.menus.append(menu)
                except (struct.error, IOError):
                    break
        except (struct.error, IOError):
            pass
    
    def _read_menu_items(self, f: BinaryIO) -> list[dict]:
        """Read items for a menu."""
        try:
            count = self._read_count(f)
            items = []
            
            for _ in range(count):
                try:
                    item = {
                        "name": self._read_string(f),
                        "tag": self._read_string(f),
                        "is_category": self._read_bool(f),
                        "linked_trait": self._read_string(f),
                        "children": [],
                    }
                    
                    if item["is_category"]:
                        item["children"] = self._read_menu_items(f)
                    
                    items.append(item)
                except (struct.error, IOError):
                    break
            
            return items
        except (struct.error, IOError):
            return []
    
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
            remaining = f.read(2)
            if len(remaining) == 2:
                count = struct.unpack("<I", count_bytes + remaining)[0]
        return count
    
    def _read_bool(self, f: BinaryIO) -> bool:
        """Read boolean (1 byte)."""
        bool_byte = f.read(1)
        if len(bool_byte) < 1:
            return False
        return struct.unpack("<?", bool_byte)[0]
