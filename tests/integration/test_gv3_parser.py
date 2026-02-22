"""Integration tests for GV3 parser."""

import pytest
from pathlib import Path

from src.legacy import GV3Parser


def test_gv3_parser_init():
    """Test parser initialization."""
    parser = GV3Parser(Path("dummy.gv3"))
    assert parser.file_path == Path("dummy.gv3")


def test_gv3_magic_bytes():
    """Test GV3 magic bytes are correct."""
    assert GV3Parser.MAGIC == b"GVBG"


def test_gvm_magic_bytes():
    """Test GVM magic bytes are correct."""
    from src.legacy.gvm_parser import GVMParser
    assert GVMParser.MAGIC == b"GVBM"


def test_gex_parser_exists():
    """Test GEX parser can be imported and initialized."""
    from src.legacy.gex_parser import GEXParser
    parser = GEXParser(Path("dummy.gex"))
    assert parser is not None
    assert parser.file_path == Path("dummy.gex")
