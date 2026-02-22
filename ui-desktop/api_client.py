"""API Client for communicating with Grapevine REST API."""

import httpx
from typing import Any, Optional


class APIClient:
    """Client for making API requests to the Grapevine backend."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.Client(base_url=base_url, timeout=30.0)
    
    def get(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """Make a GET request."""
        response = self.client.get(endpoint, params=params)
        response.raise_for_status()
        return response.json()
    
    def post(self, endpoint: str, data: dict) -> dict:
        """Make a POST request."""
        response = self.client.post(endpoint, json=data)
        response.raise_for_status()
        return response.json()
    
    def patch(self, endpoint: str, data: dict) -> dict:
        """Make a PATCH request."""
        response = self.client.patch(endpoint, json=data)
        response.raise_for_status()
        return response.json()
    
    def delete(self, endpoint: str) -> None:
        """Make a DELETE request."""
        response = self.client.delete(endpoint)
        response.raise_for_status()
    
    # Character endpoints
    def get_characters(self, **filters) -> list[dict]:
        """Get list of characters with optional filters."""
        result = self.get("/api/v1/characters", params=filters)
        return result.get("items", [])
    
    def get_character(self, character_id: str) -> dict:
        """Get a single character by ID."""
        return self.get(f"/api/v1/characters/{character_id}")
    
    def create_character(self, data: dict) -> dict:
        """Create a new character."""
        return self.post("/api/v1/characters", data)
    
    def update_character(self, character_id: str, data: dict) -> dict:
        """Update an existing character."""
        return self.patch(f"/api/v1/characters/{character_id}", data)
    
    def delete_character(self, character_id: str) -> None:
        """Delete a character."""
        self.delete(f"/api/v1/characters/{character_id}")
    
    # Player endpoints
    def get_players(self) -> list[dict]:
        """Get list of players."""
        result = self.get("/api/v1/players")
        return result.get("items", [])
    
    def get_player(self, player_id: str) -> dict:
        """Get a single player by ID."""
        return self.get(f"/api/v1/players/{player_id}")
    
    def create_player(self, data: dict) -> dict:
        """Create a new player."""
        return self.post("/api/v1/players", data)
    
    def update_player(self, player_id: str, data: dict) -> dict:
        """Update an existing player."""
        return self.patch(f"/api/v1/players/{player_id}", data)
    
    def delete_player(self, player_id: str) -> None:
        """Delete a player."""
        self.delete(f"/api/v1/players/{player_id}")
    
    # APR endpoints
    def get_actions(self, **filters) -> list[dict]:
        """Get list of actions."""
        result = self.get("/api/v1/apr/actions", params=filters)
        return result.get("items", [])
    
    def create_action(self, data: dict) -> dict:
        """Create a new action."""
        return self.post("/api/v1/apr/actions", data)
    
    def get_plots(self) -> list[dict]:
        """Get list of plots."""
        result = self.get("/api/v1/apr/plots")
        return result.get("items", [])
    
    def create_plot(self, data: dict) -> dict:
        """Create a new plot."""
        return self.post("/api/v1/apr/plots", data)
    
    def get_rumors(self, **filters) -> list[dict]:
        """Get list of rumors."""
        result = self.get("/api/v1/apr/rumors", params=filters)
        return result.get("items", [])
    
    def create_rumor(self, data: dict) -> dict:
        """Create a new rumor."""
        return self.post("/api/v1/apr/rumors", data)
    
    # Boon endpoints
    def get_boonds(self, **filters) -> list[dict]:
        """Get list of boons."""
        result = self.get("/api/v1/boons", params=filters)
        return result.get("items", [])
    
    def get_boon(self, boon_id: str) -> dict:
        """Get a single boon by ID."""
        return self.get(f"/api/v1/boons/{boon_id}")
    
    def create_boon(self, data: dict) -> dict:
        """Create a new boon."""
        return self.post("/api/v1/boons", data)
    
    def update_boon(self, boon_id: str, data: dict) -> dict:
        """Update an existing boon."""
        return self.patch(f"/api/v1/boons/{boon_id}", data)
    
    def delete_boon(self, boon_id: str) -> None:
        """Delete a boon."""
        self.delete(f"/api/v1/boons/{boon_id}")
    
    def repay_boon(self, boon_id: str, reason: str | None = None) -> dict:
        """Mark a boon as repaid."""
        data = {"reason": reason} if reason else {}
        return self.post(f"/api/v1/boons/{boon_id}/repay", data)
    
    def default_boon(self, boon_id: str, reason: str | None = None) -> dict:
        """Mark a boon as defaulted."""
        data = {"reason": reason} if reason else {}
        return self.post(f"/api/v1/boons/{boon_id}/default", data)
    
    def get_character_boonds(self, character_id: str, boon_type: str | None = None) -> dict:
        """Get boons held and owed by a character."""
        params = {"character_id": character_id}
        if boon_type:
            params["boon_type"] = boon_type
        return self.get("/api/v1/boons/character", params=params)
    
    def get_boon_history(self, boon_id: str) -> list[dict]:
        """Get history for a specific boon."""
        result = self.get(f"/api/v1/boons/{boon_id}/history")
        return result.get("items", [])
    
    def health_check(self) -> dict:
        """Check API health."""
        return self.get("/health")
