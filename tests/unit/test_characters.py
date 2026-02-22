"""Tests for race-specific character classes."""

import pytest
from src.characters import create_character, list_races
from src.characters.vampire import VampireCharacter


def test_list_races():
    """Test that all races are registered."""
    races = list_races()
    assert len(races) == 12
    assert "vampire" in races
    assert "werewolf" in races


def test_create_vampire():
    """Test vampire character creation."""
    data = {"clan": "Toreador", "generation": 10}
    vampire = create_character("vampire", data)
    
    assert isinstance(vampire, VampireCharacter)
    assert vampire.data["clan"] == "Toreador"


def test_vampire_validation():
    """Test vampire validation."""
    data = {"clan": "InvalidClan", "generation": 20}
    vampire = create_character("vampire", data)
    
    errors = vampire.validate()
    assert len(errors) == 2


def test_vampire_valid():
    """Test vampire validation with valid data."""
    data = {"clan": "Toreador", "generation": 10, "sect": "Camarilla"}
    vampire = create_character("vampire", data)
    
    errors = vampire.validate()
    assert len(errors) == 0


def test_werewolf():
    """Test werewolf character creation."""
    data = {"tribe": "Black Furies", "breed": "Homid", "auspice": "Galliard"}
    werewolf = create_character("werewolf", data)
    
    assert werewolf.data["tribe"] == "Black Furies"
    assert werewolf.validate() == []


def test_mage():
    """Test mage character creation."""
    data = {"tradition": "Hermetic", "arete": 5}
    mage = create_character("mage", data)
    
    assert mage.data["tradition"] == "Hermetic"


def test_mortal():
    """Test mortal character creation."""
    data = {}
    mortal = create_character("mortal", data)
    
    assert mortal.validate() == []


def test_unknown_race():
    """Test that unknown race raises ValueError."""
    with pytest.raises(ValueError):
        create_character("unknown", {})
