"""Pytest fixtures and configuration."""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.core.models import Base
from src.api.main import app
from src.core.database import get_db


@pytest_asyncio.fixture
async def async_engine():
    """Create async test database engine."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest_asyncio.fixture
async def async_session(async_engine):
    """Create async database session."""
    async_session_maker = async_sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture
def sample_vampire_data():
    """Sample vampire character data."""
    return {
        "name": "Test Vampire",
        "race_type": "vampire",
        "data": {
            "clan": "Toreador",
            "sect": "Camarilla",
            "generation": 10,
            "blood": {"permanent": 13, "temporary": 13},
            "path": "Humanity",
            "path_rating": 7
        },
        "traits": [
            {"category": "physical", "name": "Strength", "value": "3"},
            {"category": "disciplines", "name": "Auspex", "value": "2"},
        ]
    }


@pytest.fixture
def sample_player_data():
    """Sample player data."""
    return {
        "name": "Test Player",
        "email": "test@example.com",
        "pp_unspent": 10,
        "pp_earned": 50,
    }


@pytest_asyncio.fixture
async def api_client(async_engine):
    """Create async test client for API with overridden database."""
    # Create async session maker
    async_session_maker = async_sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    # Override the get_db dependency
    async def override_get_db():
        async with async_session_maker() as session:
            yield session
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    
    # Clean up dependency override
    app.dependency_overrides.clear()


@pytest.fixture
def api_v1_prefix():
    """API v1 prefix."""
    return "/api/v1"
