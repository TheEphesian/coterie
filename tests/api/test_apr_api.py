"""API tests for APR (Action, Plot, Rumor) endpoints."""

import pytest
from httpx import AsyncClient


# ============== Action Tests ==============

@pytest.mark.asyncio
async def test_list_actions_empty(api_client: AsyncClient, api_v1_prefix: str):
    """Test listing actions when database is empty."""
    response = await api_client.get(f"{api_v1_prefix}/apr/actions")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_create_action(api_client: AsyncClient, api_v1_prefix: str):
    """Test creating an action."""
    # First create a character
    char_response = await api_client.post(
        f"{api_v1_prefix}/characters",
        json={"name": "Action Test Char", "race_type": "vampire", "data": {}},
    )
    assert char_response.status_code == 201
    character_id = char_response.json()["id"]
    
    # Create action
    action_data = {
        "character_id": character_id,
        "action_date": "2026-02-13",
        "action_type": "Downtime",
        "level": 3,
        "action_text": "Test action description",
        "result_text": "Test result",
    }
    
    response = await api_client.post(f"{api_v1_prefix}/apr/actions", json=action_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["action_type"] == "Downtime"
    assert data["level"] == 3
    assert data["character_id"] == character_id


@pytest.mark.asyncio
async def test_get_action(api_client: AsyncClient, api_v1_prefix: str):
    """Test getting an action by ID."""
    # Create character and action
    char_response = await api_client.post(
        f"{api_v1_prefix}/characters",
        json={"name": "Get Action Char", "race_type": "vampire", "data": {}},
    )
    character_id = char_response.json()["id"]
    
    action_data = {
        "character_id": character_id,
        "action_date": "2026-02-13",
        "action_type": "Investigation",
        "level": 2,
    }
    
    create_response = await api_client.post(f"{api_v1_prefix}/apr/actions", json=action_data)
    assert create_response.status_code == 201
    action_id = create_response.json()["id"]
    
    # Get the action
    get_response = await api_client.get(f"{api_v1_prefix}/apr/actions/{action_id}")
    assert get_response.status_code == 200
    
    data = get_response.json()
    assert data["id"] == action_id
    assert data["action_type"] == "Investigation"


@pytest.mark.asyncio
async def test_get_action_not_found(api_client: AsyncClient, api_v1_prefix: str):
    """Test getting a non-existent action."""
    response = await api_client.get(f"{api_v1_prefix}/apr/actions/non-existent-id")
    assert response.status_code == 404
    
    data = response.json()
    assert "not found" in data["detail"].lower()


@pytest.mark.asyncio
async def test_update_action(api_client: AsyncClient, api_v1_prefix: str):
    """Test updating an action."""
    # Create character and action
    char_response = await api_client.post(
        f"{api_v1_prefix}/characters",
        json={"name": "Update Action Char", "race_type": "vampire", "data": {}},
    )
    character_id = char_response.json()["id"]
    
    action_data = {
        "character_id": character_id,
        "action_date": "2026-02-13",
        "action_type": "Original Type",
        "level": 1,
    }
    
    create_response = await api_client.post(f"{api_v1_prefix}/apr/actions", json=action_data)
    action_id = create_response.json()["id"]
    
    # Update the action
    update_data = {"action_type": "Updated Type", "level": 5}
    update_response = await api_client.patch(
        f"{api_v1_prefix}/apr/actions/{action_id}", json=update_data
    )
    assert update_response.status_code == 200
    
    data = update_response.json()
    assert data["action_type"] == "Updated Type"
    assert data["level"] == 5


@pytest.mark.asyncio
async def test_delete_action(api_client: AsyncClient, api_v1_prefix: str):
    """Test deleting an action."""
    # Create character and action
    char_response = await api_client.post(
        f"{api_v1_prefix}/characters",
        json={"name": "Delete Action Char", "race_type": "vampire", "data": {}},
    )
    character_id = char_response.json()["id"]
    
    action_data = {
        "character_id": character_id,
        "action_date": "2026-02-13",
        "action_type": "To Delete",
        "level": 1,
    }
    
    create_response = await api_client.post(f"{api_v1_prefix}/apr/actions", json=action_data)
    action_id = create_response.json()["id"]
    
    # Delete the action
    delete_response = await api_client.delete(f"{api_v1_prefix}/apr/actions/{action_id}")
    assert delete_response.status_code == 204
    
    # Verify it's gone
    get_response = await api_client.get(f"{api_v1_prefix}/apr/actions/{action_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_filter_actions_by_character(api_client: AsyncClient, api_v1_prefix: str):
    """Test filtering actions by character ID."""
    # Create two characters
    char1_response = await api_client.post(
        f"{api_v1_prefix}/characters",
        json={"name": "Char 1", "race_type": "vampire", "data": {}},
    )
    char1_id = char1_response.json()["id"]
    
    char2_response = await api_client.post(
        f"{api_v1_prefix}/characters",
        json={"name": "Char 2", "race_type": "vampire", "data": {}},
    )
    char2_id = char2_response.json()["id"]
    
    # Create actions for each character
    for i in range(2):
        await api_client.post(
            f"{api_v1_prefix}/apr/actions",
            json={
                "character_id": char1_id,
                "action_date": "2026-02-13",
                "action_type": f"Action {i}",
                "level": 1,
            },
        )
    
    await api_client.post(
        f"{api_v1_prefix}/apr/actions",
        json={
            "character_id": char2_id,
            "action_date": "2026-02-13",
            "action_type": "Other Action",
            "level": 1,
        },
    )
    
    # Filter by char1
    response = await api_client.get(f"{api_v1_prefix}/apr/actions?character_id={char1_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total"] == 2
    assert all(a["character_id"] == char1_id for a in data["items"])


# ============== Plot Tests ==============

@pytest.mark.asyncio
async def test_list_plots_empty(api_client: AsyncClient, api_v1_prefix: str):
    """Test listing plots when database is empty."""
    response = await api_client.get(f"{api_v1_prefix}/apr/plots")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_create_plot(api_client: AsyncClient, api_v1_prefix: str):
    """Test creating a plot."""
    plot_data = {
        "title": "Test Plot",
        "description": "A test plot description",
        "status": "active",
    }
    
    response = await api_client.post(f"{api_v1_prefix}/apr/plots", json=plot_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["title"] == "Test Plot"
    assert data["description"] == "A test plot description"
    assert data["status"] == "active"


@pytest.mark.asyncio
async def test_get_plot(api_client: AsyncClient, api_v1_prefix: str):
    """Test getting a plot by ID."""
    plot_data = {"title": "Get Test Plot", "status": "active"}
    
    create_response = await api_client.post(f"{api_v1_prefix}/apr/plots", json=plot_data)
    plot_id = create_response.json()["id"]
    
    get_response = await api_client.get(f"{api_v1_prefix}/apr/plots/{plot_id}")
    assert get_response.status_code == 200
    
    data = get_response.json()
    assert data["id"] == plot_id
    assert data["title"] == "Get Test Plot"


@pytest.mark.asyncio
async def test_update_plot(api_client: AsyncClient, api_v1_prefix: str):
    """Test updating a plot."""
    plot_data = {"title": "Original Title", "status": "active"}
    
    create_response = await api_client.post(f"{api_v1_prefix}/apr/plots", json=plot_data)
    plot_id = create_response.json()["id"]
    
    update_data = {"title": "Updated Title", "status": "completed"}
    update_response = await api_client.patch(
        f"{api_v1_prefix}/apr/plots/{plot_id}", json=update_data
    )
    assert update_response.status_code == 200
    
    data = update_response.json()
    assert data["title"] == "Updated Title"
    assert data["status"] == "completed"


@pytest.mark.asyncio
async def test_delete_plot(api_client: AsyncClient, api_v1_prefix: str):
    """Test deleting a plot."""
    plot_data = {"title": "Plot to Delete", "status": "active"}
    
    create_response = await api_client.post(f"{api_v1_prefix}/apr/plots", json=plot_data)
    plot_id = create_response.json()["id"]
    
    delete_response = await api_client.delete(f"{api_v1_prefix}/apr/plots/{plot_id}")
    assert delete_response.status_code == 204
    
    get_response = await api_client.get(f"{api_v1_prefix}/apr/plots/{plot_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_filter_plots_by_status(api_client: AsyncClient, api_v1_prefix: str):
    """Test filtering plots by status."""
    # Create plots with different statuses
    statuses = ["active", "active", "completed"]
    for status in statuses:
        await api_client.post(
            f"{api_v1_prefix}/apr/plots",
            json={"title": f"Plot {status}", "status": status},
        )
    
    # Filter by active status
    response = await api_client.get(f"{api_v1_prefix}/apr/plots?status=active")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total"] == 2
    assert all(p["status"] == "active" for p in data["items"])


# ============== Rumor Tests ==============

@pytest.mark.asyncio
async def test_list_rumors_empty(api_client: AsyncClient, api_v1_prefix: str):
    """Test listing rumors when database is empty."""
    response = await api_client.get(f"{api_v1_prefix}/apr/rumors")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_create_rumor(api_client: AsyncClient, api_v1_prefix: str):
    """Test creating a rumor."""
    rumor_data = {
        "title": "Test Rumor",
        "content": "A test rumor content",
        "level": 2,
        "category": "General",
        "rumor_date": "2026-02-13",
    }
    
    response = await api_client.post(f"{api_v1_prefix}/apr/rumors", json=rumor_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["title"] == "Test Rumor"
    assert data["content"] == "A test rumor content"
    assert data["level"] == 2
    assert data["category"] == "General"


@pytest.mark.asyncio
async def test_get_rumor(api_client: AsyncClient, api_v1_prefix: str):
    """Test getting a rumor by ID."""
    rumor_data = {
        "title": "Get Test Rumor",
        "content": "Test content",
        "level": 1,
        "rumor_date": "2026-02-13",
    }
    
    create_response = await api_client.post(f"{api_v1_prefix}/apr/rumors", json=rumor_data)
    rumor_id = create_response.json()["id"]
    
    get_response = await api_client.get(f"{api_v1_prefix}/apr/rumors/{rumor_id}")
    assert get_response.status_code == 200
    
    data = get_response.json()
    assert data["id"] == rumor_id
    assert data["title"] == "Get Test Rumor"


@pytest.mark.asyncio
async def test_update_rumor(api_client: AsyncClient, api_v1_prefix: str):
    """Test updating a rumor."""
    rumor_data = {
        "title": "Original Rumor",
        "content": "Original content",
        "level": 1,
        "rumor_date": "2026-02-13",
    }
    
    create_response = await api_client.post(f"{api_v1_prefix}/apr/rumors", json=rumor_data)
    rumor_id = create_response.json()["id"]
    
    update_data = {"title": "Updated Rumor", "level": 3}
    update_response = await api_client.patch(
        f"{api_v1_prefix}/apr/rumors/{rumor_id}", json=update_data
    )
    assert update_response.status_code == 200
    
    data = update_response.json()
    assert data["title"] == "Updated Rumor"
    assert data["level"] == 3


@pytest.mark.asyncio
async def test_delete_rumor(api_client: AsyncClient, api_v1_prefix: str):
    """Test deleting a rumor."""
    rumor_data = {
        "title": "Rumor to Delete",
        "content": "Delete me",
        "level": 1,
        "rumor_date": "2026-02-13",
    }
    
    create_response = await api_client.post(f"{api_v1_prefix}/apr/rumors", json=rumor_data)
    rumor_id = create_response.json()["id"]
    
    delete_response = await api_client.delete(f"{api_v1_prefix}/apr/rumors/{rumor_id}")
    assert delete_response.status_code == 204
    
    get_response = await api_client.get(f"{api_v1_prefix}/apr/rumors/{rumor_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_filter_rumors_by_category(api_client: AsyncClient, api_v1_prefix: str):
    """Test filtering rumors by category."""
    # Create rumors with different categories
    categories = ["General", "General", "Secret"]
    for category in categories:
        await api_client.post(
            f"{api_v1_prefix}/apr/rumors",
            json={
                "title": f"Rumor {category}",
                "content": "Test",
                "level": 1,
                "category": category,
                "rumor_date": "2026-02-13",
            },
        )
    
    # Filter by General category
    response = await api_client.get(f"{api_v1_prefix}/apr/rumors?category=General")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total"] == 2
    assert all(r["category"] == "General" for r in data["items"])
