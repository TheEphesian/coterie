"""Tests for database models."""

import pytest
from sqlalchemy import select
from src.core.models import Character, Player, Trait


@pytest.mark.asyncio
async def test_create_player(async_session):
    """Test player creation."""
    player = Player(name="Test Player", email="test@example.com")
    async_session.add(player)
    await async_session.commit()
    
    assert player.id is not None
    assert player.name == "Test Player"


@pytest.mark.asyncio
async def test_create_character(async_session, sample_player_data):
    """Test character creation with player."""
    player = Player(**sample_player_data)
    async_session.add(player)
    await async_session.flush()
    
    character = Character(
        name="Test Vampire",
        race_type="vampire",
        player_id=player.id,
        data={"clan": "Toreador", "generation": 10}
    )
    async_session.add(character)
    await async_session.commit()
    
    assert character.id is not None
    assert character.player.name == "Test Player"


@pytest.mark.asyncio
async def test_character_traits(async_session):
    """Test character traits relationship."""
    character = Character(name="Test", race_type="mortal", data={})
    async_session.add(character)
    await async_session.flush()
    
    trait = Trait(
        character_id=character.id,
        category="abilities",
        name="Athletics",
        value="3"
    )
    async_session.add(trait)
    await async_session.commit()
    
    stmt = select(Character).where(Character.id == character.id)
    result = await async_session.execute(stmt)
    loaded_character = result.scalar_one()
    
    assert len(loaded_character.traits) == 1
    assert loaded_character.traits[0].name == "Athletics"
