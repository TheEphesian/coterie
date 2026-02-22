"""API tests for character endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_characters_empty(api_client: AsyncClient, api_v1_prefix: str):
    """Test listing characters when database is empty."""
    response = await api_client.get(f"{api_v1_prefix}/characters")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_create_character(api_client: AsyncClient, api_v1_prefix: str):
    """Test creating a character."""
    character_data = {
        "name": "Test Vampire",
        "race_type": "vampire",
        "is_npc": False,
        "status": "active",
        "xp_unspent": 10,
        "xp_earned": 50,
        "biography": "Test biography",
        "notes": "Test notes",
        "data": {"clan": "Toreador", "generation": 10},
        "traits": [
            {"category": "physical", "name": "Strength", "value": "3"},
            {"category": "disciplines", "name": "Auspex", "value": "2"},
        ],
    }
    
    response = await api_client.post(f"{api_v1_prefix}/characters", json=character_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["name"] == "Test Vampire"
    assert data["race_type"] == "vampire"
    assert data["xp_unspent"] == 10
    assert data["xp_earned"] == 50
    assert len(data["traits"]) == 2


@pytest.mark.asyncio
async def test_get_character(api_client: AsyncClient, api_v1_prefix: str):
    """Test getting a character by ID."""
    # First create a character
    character_data = {
        "name": "Test Werewolf",
        "race_type": "werewolf",
        "data": {"tribe": "Glass Walkers"},
    }
    
    create_response = await api_client.post(f"{api_v1_prefix}/characters", json=character_data)
    assert create_response.status_code == 201
    created = create_response.json()
    character_id = created["id"]
    
    # Now get the character
    get_response = await api_client.get(f"{api_v1_prefix}/characters/{character_id}")
    assert get_response.status_code == 200
    
    data = get_response.json()
    assert data["id"] == character_id
    assert data["name"] == "Test Werewolf"
    assert data["race_type"] == "werewolf"


@pytest.mark.asyncio
async def test_get_character_not_found(api_client: AsyncClient, api_v1_prefix: str):
    """Test getting a non-existent character."""
    response = await api_client.get(f"{api_v1_prefix}/characters/99999")
    assert response.status_code == 404
    
    data = response.json()
    assert "not found" in data["detail"].lower()


@pytest.mark.asyncio
async def test_update_character(api_client: AsyncClient, api_v1_prefix: str):
    """Test updating a character."""
    # Create a character first
    character_data = {
        "name": "Original Name",
        "race_type": "mage",
        "data": {},
    }
    
    create_response = await api_client.post(f"{api_v1_prefix}/characters", json=character_data)
    assert create_response.status_code == 201
    created = create_response.json()
    character_id = created["id"]
    
    # Update the character
    update_data = {"name": "Updated Name", "xp_unspent": 20}
    update_response = await api_client.patch(
        f"{api_v1_prefix}/characters/{character_id}", json=update_data
    )
    assert update_response.status_code == 200
    
    data = update_response.json()
    assert data["name"] == "Updated Name"
    assert data["xp_unspent"] == 20


@pytest.mark.asyncio
async def test_delete_character(api_client: AsyncClient, api_v1_prefix: str):
    """Test deleting a character."""
    # Create a character first
    character_data = {
        "name": "Character to Delete",
        "race_type": "mortal",
        "data": {},
    }
    
    create_response = await api_client.post(f"{api_v1_prefix}/characters", json=character_data)
    assert create_response.status_code == 201
    created = create_response.json()
    character_id = created["id"]
    
    # Delete the character
    delete_response = await api_client.delete(f"{api_v1_prefix}/characters/{character_id}")
    assert delete_response.status_code == 204
    
    # Verify it's gone
    get_response = await api_client.get(f"{api_v1_prefix}/characters/{character_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_filter_characters_by_race(api_client: AsyncClient, api_v1_prefix: str):
    """Test filtering characters by race type."""
    # Create characters of different races
    races = ["vampire", "werewolf", "mage"]
    
    for race in races:
        await api_client.post(
            f"{api_v1_prefix}/characters",
            json={"name": f"Test {race}", "race_type": race, "data": {}},
        )
    
    # Filter by vampire
    response = await api_client.get(f"{api_v1_prefix}/characters?race_type=vampire")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total"] >= 1
    assert all(c["race_type"] == "vampire" for c in data["items"])


@pytest.mark.asyncio
async def test_add_xp_to_character(api_client: AsyncClient, api_v1_prefix: str):
    """Test adding XP to a character."""
    # Create a character
    character_data = {
        "name": "XP Test Character",
        "race_type": "vampire",
        "xp_unspent": 10,
        "xp_earned": 50,
        "data": {},
    }
    
    create_response = await api_client.post(f"{api_v1_prefix}/characters", json=character_data)
    assert create_response.status_code == 201
    created = create_response.json()
    character_id = created["id"]
    
    # Add XP
    xp_response = await api_client.post(
        f"{api_v1_prefix}/characters/{character_id}/xp/add?amount=5&reason=Session+reward"
    )
    assert xp_response.status_code == 200
    
    data = xp_response.json()
    assert data["xp_earned"] == 55
    assert data["xp_unspent"] == 15


@pytest.mark.asyncio
async def test_spend_xp_for_character(api_client: AsyncClient, api_v1_prefix: str):
    """Test spending XP for a character."""
    # Create a character with XP
    character_data = {
        "name": "XP Spend Test",
        "race_type": "vampire",
        "xp_unspent": 10,
        "xp_earned": 50,
        "data": {},
    }
    
    create_response = await api_client.post(f"{api_v1_prefix}/characters", json=character_data)
    assert create_response.status_code == 201
    created = create_response.json()
    character_id = created["id"]
    
    # Spend XP
    xp_response = await api_client.post(
        f"{api_v1_prefix}/characters/{character_id}/xp/spend?amount=5&reason=Buy+new+trait"
    )
    assert xp_response.status_code == 200
    
    data = xp_response.json()
    assert data["xp_unspent"] == 5
    assert data["xp_earned"] == 50  # Unchanged
