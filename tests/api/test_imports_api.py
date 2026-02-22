"""API tests for import endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_import_invalid_file_extension(api_client: AsyncClient, api_v1_prefix: str):
    """Test importing a file with wrong extension."""
    response = await api_client.post(
        f"{api_v1_prefix}/imports/legacy",
        files={"file": ("test.txt", b"invalid content", "text/plain")},
    )
    assert response.status_code == 400
    
    data = response.json()
    assert "Invalid file format" in data["detail"]


@pytest.mark.asyncio
async def test_import_empty_gv3_file(api_client: AsyncClient, api_v1_prefix: str):
    """Test importing an invalid GV3 file."""
    # Create a fake .gv3 file with invalid content
    response = await api_client.post(
        f"{api_v1_prefix}/imports/legacy",
        files={"file": ("test.gv3", b"invalid gv3 content", "application/octet-stream")},
    )
    # Should fail because it's not a valid GV3 file
    assert response.status_code == 400
    
    data = response.json()
    assert "Invalid GV3 file" in data["detail"]


@pytest.mark.asyncio
async def test_import_endpoint_exists(api_client: AsyncClient, api_v1_prefix: str):
    """Test that the import endpoint exists and accepts file uploads."""
    # Create a minimal valid GV3 header
    # GV3 format: 2-byte length + "GVBG" magic + version (4 bytes float) + 8 bytes reserved
    import struct
    
    # Build a minimal GV3 file
    magic = b"GVBG"
    version = struct.pack("<f", 3.01)
    reserved = b"\x00" * 8
    
    # Length prefix for header section
    header_length = len(magic) + len(version) + len(reserved)
    length_prefix = struct.pack("<H", header_length)
    
    # Minimal game info (4 empty strings with 2-byte length prefix)
    game_info = b"".join([struct.pack("<H", 0) for _ in range(4)])
    
    # Minimal counts for all entities (each uses 2-byte count)
    empty_counts = b"".join([struct.pack("<H", 0) for _ in range(8)])  # players, chars, items, locations, actions, plots, rumors
    
    gv3_content = (
        length_prefix + magic + version + reserved +
        game_info + empty_counts
    )
    
    response = await api_client.post(
        f"{api_v1_prefix}/imports/legacy",
        files={"file": ("test.gv3", gv3_content, "application/octet-stream")},
    )
    
    # Should succeed with valid structure
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert "stats" in data
    assert data["stats"]["players_imported"] == 0
    assert data["stats"]["characters_imported"] == 0


@pytest.mark.asyncio
async def test_import_with_players(api_client: AsyncClient, api_v1_prefix: str):
    """Test importing a GV3 file with players."""
    import struct
    
    # Build GV3 file with one player
    # Format: 2-byte length prefix + "GVBG" magic + version (4 bytes float) + 8 bytes reserved
    magic = b"GVBG"
    version = struct.pack("<f", 3.01)
    reserved = b"\x00" * 8
    header_length = len(magic) + len(version) + len(reserved)
    length_prefix = struct.pack("<H", header_length)
    
    # Game info (4 empty strings, each with 2-byte length prefix of 0)
    game_info = b"".join([struct.pack("<H", 0) for _ in range(4)])
    
    # Player count = 1 (2-byte count)
    player_count = struct.pack("<H", 1)
    
    # Player data - using 2-byte string lengths
    player_name = b"Test Player"
    player_data = (
        struct.pack("<H", len(player_name)) + player_name +  # name
        struct.pack("<H", 0) +  # id (empty)
        struct.pack("<H", 0) +  # email (empty)
        struct.pack("<H", 0) +  # phone (empty)
        struct.pack("<H", 0) +  # address (empty)
        struct.pack("<H", 0) +  # status (empty)
        struct.pack("<H", 0) +  # position (empty)
        struct.pack("<i", 10) +  # pp_unspent (4-byte int)
        struct.pack("<i", 50)    # pp_earned (4-byte int)
    )
    
    # Empty counts for other entities (6 counts, each 2 bytes)
    empty_counts = b"".join([struct.pack("<H", 0) for _ in range(6)])
    
    gv3_content = (
        length_prefix + magic + version + reserved +
        game_info + player_count + player_data + empty_counts
    )
    
    response = await api_client.post(
        f"{api_v1_prefix}/imports/legacy",
        files={"file": ("test_with_player.gv3", gv3_content, "application/octet-stream")},
    )
    
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert data["stats"]["players_imported"] == 1
