"""API tests for boon endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_boonds_empty(api_client: AsyncClient, api_v1_prefix: str):
    """Test listing boons when database is empty."""
    response = await api_client.get(f"{api_v1_prefix}/boons")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_create_boon(api_client: AsyncClient, api_v1_prefix: str):
    """Test creating a boon."""
    # First create a character to be the holder
    character_data = {
        "name": "Boon Holder",
        "race_type": "vampire",
        "data": {},
    }
    
    char_response = await api_client.post(f"{api_v1_prefix}/characters", json=character_data)
    assert char_response.status_code == 201
    holder_id = char_response.json()["id"]
    
    # Create another character for other end
    other_data = {
        "name": "Boon Other",
        "race_type": "vampire",
        "data": {},
    }
    other_response = await api_client.post(f"{api_v1_prefix}/characters", json=other_data)
    assert other_response.status_code == 201
    other_id = other_response.json()["id"]
    
    # Create a boon
    boon_data = {
        "holder_id": holder_id,
        "other_character_id": other_id,
        "boon_type": "major",
        "is_owed": True,
        "description": "Saved from werewolf attack",
        "status": "active",
    }
    
    response = await api_client.post(f"{api_v1_prefix}/boons", json=boon_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["holder_id"] == holder_id
    assert data["other_character_id"] == other_id
    assert data["boon_type"] == "major"
    assert data["is_owed"] is True
    assert data["status"] == "active"


@pytest.mark.asyncio
async def test_get_boon(api_client: AsyncClient, api_v1_prefix: str):
    """Test getting a boon by ID."""
    # Create a character first
    character_data = {"name": "Holder 2", "race_type": "vampire", "data": {}}
    char_response = await api_client.post(f"{api_v1_prefix}/characters", json=character_data)
    holder_id = char_response.json()["id"]
    
    # Create a boon
    boon_data = {
        "holder_id": holder_id,
        "boon_type": "minor",
        "is_owed": True,
        "description": "Test boon",
    }
    
    create_response = await api_client.post(f"{api_v1_prefix}/boons", json=boon_data)
    assert create_response.status_code == 201
    boon_id = create_response.json()["id"]
    
    # Get the boon
    get_response = await api_client.get(f"{api_v1_prefix}/boons/{boon_id}")
    assert get_response.status_code == 200
    
    data = get_response.json()
    assert data["id"] == boon_id
    assert data["boon_type"] == "minor"


@pytest.mark.asyncio
async def test_get_boon_not_found(api_client: AsyncClient, api_v1_prefix: str):
    """Test getting a non-existent boon."""
    response = await api_client.get(f"{api_v1_prefix}/boons/non-existent-id")
    assert response.status_code == 404
    
    data = response.json()
    assert "not found" in data["detail"].lower()


@pytest.mark.asyncio
async def test_update_boon(api_client: AsyncClient, api_v1_prefix: str):
    """Test updating a boon."""
    # Create a character and boon
    character_data = {"name": "Holder 3", "race_type": "vampire", "data": {}}
    char_response = await api_client.post(f"{api_v1_prefix}/characters", json=character_data)
    holder_id = char_response.json()["id"]
    
    boon_data = {
        "holder_id": holder_id,
        "boon_type": "trivial",
        "is_owed": True,
        "description": "Original description",
    }
    
    create_response = await api_client.post(f"{api_v1_prefix}/boons", json=boon_data)
    assert create_response.status_code == 201
    boon_id = create_response.json()["id"]
    
    # Update the boon
    update_data = {"boon_type": "major", "description": "Updated description"}
    update_response = await api_client.patch(
        f"{api_v1_prefix}/boons/{boon_id}", json=update_data
    )
    assert update_response.status_code == 200
    
    data = update_response.json()
    assert data["boon_type"] == "major"
    assert data["description"] == "Updated description"


@pytest.mark.asyncio
async def test_delete_boon(api_client: AsyncClient, api_v1_prefix: str):
    """Test deleting a boon."""
    # Create a character and boon
    character_data = {"name": "Holder 4", "race_type": "vampire", "data": {}}
    char_response = await api_client.post(f"{api_v1_prefix}/characters", json=character_data)
    holder_id = char_response.json()["id"]
    
    boon_data = {
        "holder_id": holder_id,
        "boon_type": "trivial",
        "is_owed": True,
    }
    
    create_response = await api_client.post(f"{api_v1_prefix}/boons", json=boon_data)
    assert create_response.status_code == 201
    boon_id = create_response.json()["id"]
    
    # Delete the boon
    delete_response = await api_client.delete(f"{api_v1_prefix}/boons/{boon_id}")
    assert delete_response.status_code == 204
    
    # Verify it's gone
    get_response = await api_client.get(f"{api_v1_prefix}/boons/{boon_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_repay_boon(api_client: AsyncClient, api_v1_prefix: str):
    """Test repaying a boon."""
    # Create a character and boon
    character_data = {"name": "Holder 5", "race_type": "vampire", "data": {}}
    char_response = await api_client.post(f"{api_v1_prefix}/characters", json=character_data)
    holder_id = char_response.json()["id"]
    
    boon_data = {
        "holder_id": holder_id,
        "boon_type": "minor",
        "is_owed": True,
        "status": "active",
    }
    
    create_response = await api_client.post(f"{api_v1_prefix}/boons", json=boon_data)
    assert create_response.status_code == 201
    boon_id = create_response.json()["id"]
    
    # Repay the boon
    repay_response = await api_client.post(
        f"{api_v1_prefix}/boons/{boon_id}/repay?notes=Boon repaid with interest"
    )
    assert repay_response.status_code == 200
    
    data = repay_response.json()
    assert data["status"] == "repaid"


@pytest.mark.asyncio
async def test_default_boon(api_client: AsyncClient, api_v1_prefix: str):
    """Test defaulting a boon."""
    # Create a character and boon
    character_data = {"name": "Holder 6", "race_type": "vampire", "data": {}}
    char_response = await api_client.post(f"{api_v1_prefix}/characters", json=character_data)
    holder_id = char_response.json()["id"]
    
    boon_data = {
        "holder_id": holder_id,
        "boon_type": "life",
        "is_owed": True,
        "status": "active",
    }
    
    create_response = await api_client.post(f"{api_v1_prefix}/boons", json=boon_data)
    assert create_response.status_code == 201
    boon_id = create_response.json()["id"]
    
    # Default the boon
    default_response = await api_client.post(
        f"{api_v1_prefix}/boons/{boon_id}/default?notes=Character failed to repay"
    )
    assert default_response.status_code == 200
    
    data = default_response.json()
    assert data["status"] == "defaulted"


@pytest.mark.asyncio
async def test_filter_boonds_by_type(api_client: AsyncClient, api_v1_prefix: str):
    """Test filtering boons by type."""
    # Create a character
    character_data = {"name": "Holder 7", "race_type": "vampire", "data": {}}
    char_response = await api_client.post(f"{api_v1_prefix}/characters", json=character_data)
    holder_id = char_response.json()["id"]
    
    # Create boons of different types
    for boon_type in ["trivial", "minor", "major"]:
        boon_data = {
            "holder_id": holder_id,
            "boon_type": boon_type,
            "is_owed": True,
        }
        await api_client.post(f"{api_v1_prefix}/boons", json=boon_data)
    
    # Filter by type
    response = await api_client.get(f"{api_v1_prefix}/boons?boon_type=major")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["boon_type"] == "major"


@pytest.mark.asyncio
async def test_get_character_boonds(api_client: AsyncClient, api_v1_prefix: str):
    """Test getting boons for a specific character."""
    # Create holder character
    holder_data = {"name": "Holder Character", "race_type": "vampire", "data": {}}
    holder_response = await api_client.post(f"{api_v1_prefix}/characters", json=holder_data)
    holder_id = holder_response.json()["id"]
    
    # Create other character
    other_data = {"name": "Other Character", "race_type": "vampire", "data": {}}
    other_response = await api_client.post(f"{api_v1_prefix}/characters", json=other_data)
    other_id = other_response.json()["id"]
    
    # Create boons for holder
    for i in range(2):
        boon_data = {
            "holder_id": holder_id,
            "other_character_id": other_id,
            "boon_type": "minor",
            "is_owed": True,
        }
        await api_client.post(f"{api_v1_prefix}/boons", json=boon_data)
    
    # Get boons held by character
    held_response = await api_client.get(f"{api_v1_prefix}/boons/character/{holder_id}/held")
    assert held_response.status_code == 200
    
    held_data = held_response.json()
    assert held_data["total"] == 2
    
    # Get boons owed to character
    owed_response = await api_client.get(f"{api_v1_prefix}/boons/character/{holder_id}/owed")
    assert owed_response.status_code == 200
    
    owed_data = owed_response.json()
    assert owed_data["total"] == 0  # No boons where holder is the one owed


@pytest.mark.asyncio
async def test_get_boon_history(api_client: AsyncClient, api_v1_prefix: str):
    """Test getting boon history."""
    # Create a character and boon
    character_data = {"name": "Holder 8", "race_type": "vampire", "data": {}}
    char_response = await api_client.post(f"{api_v1_prefix}/characters", json=character_data)
    holder_id = char_response.json()["id"]
    
    boon_data = {
        "holder_id": holder_id,
        "boon_type": "minor",
        "is_owed": True,
        "status": "active",
    }
    
    create_response = await api_client.post(f"{api_v1_prefix}/boons", json=boon_data)
    assert create_response.status_code == 201
    boon_id = create_response.json()["id"]
    
    # Repay the boon to create history
    await api_client.post(f"{api_v1_prefix}/boons/{boon_id}/repay")
    
    # Get history
    history_response = await api_client.get(f"{api_v1_prefix}/boons/{boon_id}/history")
    assert history_response.status_code == 200
    
    history_data = history_response.json()
    assert history_data["total"] >= 2  # Created + repaid entries
