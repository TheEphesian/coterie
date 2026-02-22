"""API tests for player endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_players_empty(api_client: AsyncClient, api_v1_prefix: str):
    """Test listing players when database is empty."""
    response = await api_client.get(f"{api_v1_prefix}/players")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_create_player(api_client: AsyncClient, api_v1_prefix: str):
    """Test creating a player."""
    player_data = {
        "name": "Test Player",
        "email": "test@example.com",
        "phone": "555-1234",
        "address": "123 Test St",
        "status": "active",
        "position": "Storyteller",
        "pp_unspent": 10,
        "pp_earned": 50,
    }
    
    response = await api_client.post(f"{api_v1_prefix}/players", json=player_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["name"] == "Test Player"
    assert data["email"] == "test@example.com"
    assert data["pp_unspent"] == 10
    assert data["pp_earned"] == 50


@pytest.mark.asyncio
async def test_get_player(api_client: AsyncClient, api_v1_prefix: str):
    """Test getting a player by ID."""
    # First create a player
    player_data = {
        "name": "Get Test Player",
        "email": "gettest@example.com",
    }
    
    create_response = await api_client.post(f"{api_v1_prefix}/players", json=player_data)
    assert create_response.status_code == 201
    created = create_response.json()
    player_id = created["id"]
    
    # Now get the player
    get_response = await api_client.get(f"{api_v1_prefix}/players/{player_id}")
    assert get_response.status_code == 200
    
    data = get_response.json()
    assert data["id"] == player_id
    assert data["name"] == "Get Test Player"


@pytest.mark.asyncio
async def test_get_player_not_found(api_client: AsyncClient, api_v1_prefix: str):
    """Test getting a non-existent player."""
    response = await api_client.get(f"{api_v1_prefix}/players/99999")
    assert response.status_code == 404
    
    data = response.json()
    assert "not found" in data["detail"].lower()


@pytest.mark.asyncio
async def test_update_player(api_client: AsyncClient, api_v1_prefix: str):
    """Test updating a player."""
    # Create a player first
    player_data = {
        "name": "Original Player Name",
        "email": "original@example.com",
    }
    
    create_response = await api_client.post(f"{api_v1_prefix}/players", json=player_data)
    assert create_response.status_code == 201
    created = create_response.json()
    player_id = created["id"]
    
    # Update the player
    update_data = {"name": "Updated Player Name", "pp_unspent": 20}
    update_response = await api_client.patch(
        f"{api_v1_prefix}/players/{player_id}", json=update_data
    )
    assert update_response.status_code == 200
    
    data = update_response.json()
    assert data["name"] == "Updated Player Name"
    assert data["pp_unspent"] == 20


@pytest.mark.asyncio
async def test_delete_player(api_client: AsyncClient, api_v1_prefix: str):
    """Test deleting a player."""
    # Create a player first
    player_data = {
        "name": "Player to Delete",
        "email": "delete@example.com",
    }
    
    create_response = await api_client.post(f"{api_v1_prefix}/players", json=player_data)
    assert create_response.status_code == 201
    created = create_response.json()
    player_id = created["id"]
    
    # Delete the player
    delete_response = await api_client.delete(f"{api_v1_prefix}/players/{player_id}")
    assert delete_response.status_code == 204
    
    # Verify it's gone
    get_response = await api_client.get(f"{api_v1_prefix}/players/{player_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_add_pp_to_player(api_client: AsyncClient, api_v1_prefix: str):
    """Test adding Player Points to a player."""
    # Create a player
    player_data = {
        "name": "PP Test Player",
        "email": "pptest@example.com",
        "pp_unspent": 10,
        "pp_earned": 50,
    }
    
    create_response = await api_client.post(f"{api_v1_prefix}/players", json=player_data)
    assert create_response.status_code == 201
    created = create_response.json()
    player_id = created["id"]
    
    # Add PP
    pp_response = await api_client.post(
        f"{api_v1_prefix}/players/{player_id}/pp/add?amount=5"
    )
    assert pp_response.status_code == 200
    
    data = pp_response.json()
    assert data["pp_earned"] == 55
    assert data["pp_unspent"] == 15


@pytest.mark.asyncio
async def test_player_character_count(api_client: AsyncClient, api_v1_prefix: str):
    """Test that character count is returned for players."""
    # Create a player
    player_data = {
        "name": "Player with Characters",
        "email": "withchars@example.com",
    }
    
    create_response = await api_client.post(f"{api_v1_prefix}/players", json=player_data)
    assert create_response.status_code == 201
    player_id = create_response.json()["id"]
    
    # Create characters for this player
    for i in range(3):
        await api_client.post(
            f"{api_v1_prefix}/characters",
            json={
                "name": f"Character {i}",
                "race_type": "vampire",
                "player_id": player_id,
                "data": {},
            },
        )
    
    # Get player and check character count
    get_response = await api_client.get(f"{api_v1_prefix}/players/{player_id}")
    assert get_response.status_code == 200
    
    data = get_response.json()
    assert data["character_count"] == 3
