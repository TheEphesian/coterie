# AGENTS.md - Grapevine Migration Build Commands

> For use with ralph-wiggum loop (opencode/claude-code/codex)

## Project Context

**Goal:** Migrate VB6 Grapevine LARP character manager to Python with modern architecture  
**Source:** Legacy VB6 code in `VB-Grapevine-SourceCode/`  
**PRD:** `Grapevine-Migration-PRD.md` (comprehensive requirements document)  
**Target:** `grapevine-modern/` directory  

---

## Pre-Flight Checklist (Run Once)

Before starting the ralph loop, ensure:

```bash
# 1. Check Python version (must be 3.12+)
python --version

# 2. Verify PRD exists and is readable
cat Grapevine-Migration-PRD.md | head -100

# 3. Check available disk space (need ~500MB)
df -h .

# 4. Verify legacy source files exist
ls -la VB-Grapevine-SourceCode/

# 5. Create working directory
mkdir -p grapevine-modern
cd grapevine-modern
```

---

## Phase 1: Foundation & Project Structure

**Goal:** Create complete project scaffolding

### Step 1.1: Initialize Project Structure

```bash
# Create directory tree
mkdir -p src/{api/routes,core/{models,schemas,services,repositories},characters,legacy,templates/{html,text,rtf},plugins,utils}
mkdir -p tests/{unit,integration,fixtures}
mkdir -p docs/{api,user,developer}
mkdir -p migrations
mkdir -p scripts
mkdir -p ui-desktop
mkdir -p ui-web

# Create initial files
touch src/__init__.py
touch src/api/__init__.py
touch src/core/__init__.py
touch src/characters/__init__.py
touch src/legacy/__init__.py
touch tests/__init__.py
```

### Step 1.2: Python Environment Setup

```bash
# Create virtual environment
python -m venv .venv

# Activation scripts
echo 'source .venv/bin/activate' > scripts/activate.sh
echo '.venv\Scripts\activate' > scripts/activate.bat

# Create requirements.txt
cat > requirements.txt << 'EOF'
# Web Framework
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
python-multipart>=0.0.6

# Database
sqlalchemy>=2.0.0
alembic>=1.12.0
aiosqlite>=0.19.0

# Data Validation
pydantic>=2.5.0
pydantic-settings>=2.1.0

# Authentication
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6

# Templating & Reports
jinja2>=3.1.0
reportlab>=4.0.0
openpyxl>=3.1.0
weasyprint>=60.0

# Utilities
structlog>=23.0.0
python-dotenv>=1.0.0
click>=8.1.0
rich>=13.0.0
httpx>=0.25.0

# Development
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
pytest-xdist>=3.3.0
mypy>=1.7.0
ruff>=0.1.0
black>=23.0.0
pre-commit>=3.5.0

# Legacy File Parsing
struct>=0.2
EOF

# Install dependencies
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 1.3: Core Configuration Files

```bash
# Create pyproject.toml
cat > pyproject.toml << 'EOF'
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "grapevine-modern"
version = "0.1.0"
description = "Modern Python implementation of Grapevine LARP manager"
requires-python = ">=3.12"
license = "MIT"
authors = [
    {name = "Grapevine Migration Team"}
]

[tool.black]
line-length = 100
target-version = ['py312']

[tool.ruff]
line-length = 100
target-version = "py312"
select = ["E", "F", "I", "N", "W", "UP", "B", "C4", "SIM"]

[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-ra -q --strict-markers --strict-config"
testpaths = ["tests"]
asyncio_mode = "auto"
EOF

# Create .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
env/
venv/
*.egg-info/
dist/
build/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Testing
.coverage
htmlcov/
.pytest_cache/
.mypy_cache/
.ruff_cache/

# Database
*.db
*.sqlite
*.sqlite3

# Legacy files (keep structure but not binary)
*.gv3
*.gvm
*.gex
!tests/fixtures/**/*.gv3

# Environment
.env
.env.local

# OS
.DS_Store
Thumbs.db
EOF

# Create .env.example
cat > .env.example << 'EOF'
# Database
DATABASE_URL=sqlite:///./grapevine.db
# DATABASE_URL=postgresql://user:pass@localhost/grapevine

# API
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true
SECRET_KEY=your-secret-key-change-in-production

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Legacy Import
LEGACY_IMPORT_PATH=./legacy-imports
EOF
```

---

## Phase 2: Core Data Models

**Goal:** Implement SQLAlchemy models for all entities

### Step 2.1: Base Model & Mixins

Create `src/core/models/base.py`:

```python
"""Base SQLAlchemy model with common functionality."""

from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import MetaData, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import DateTime, TypeDecorator
import uuid

# Naming convention for constraints
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Base class for all models."""
    
    metadata = MetaData(naming_convention=convention)
    
    # Common columns for all tables
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class UUIDType(TypeDecorator[str]):
    """UUID type decorator for SQLite compatibility."""
    
    impl = String(36)
    cache_ok = True
    
    def process_bind_param(self, value: Any | None, dialect: Any) -> str | None:
        if value is None:
            return None
        return str(value)
    
    def process_result_value(self, value: str | None, dialect: Any) -> uuid.UUID | None:
        if value is None:
            return None
        return uuid.UUID(value)
```

### Step 2.2: Player Model

Create `src/core/models/player.py`:

```python
"""Player model for storing player information."""

from sqlalchemy import String, Integer, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.models.base import Base


class Player(Base):
    """Player (user) entity."""
    
    __tablename__ = "players"
    
    # Basic info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Player Points (staff experience)
    pp_unspent: Mapped[int] = mapped_column(Integer, default=0)
    pp_earned: Mapped[int] = mapped_column(Integer, default=0)
    
    # Status
    status: Mapped[str] = mapped_column(String(50), default="active")
    position: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    # Relationships
    characters: Mapped[list["Character"]] = relationship(
        "Character", back_populates="player", lazy="selectin"
    )
    pp_history: Mapped[list["PlayerPointHistory"]] = relationship(
        "PlayerPointHistory", back_populates="player", lazy="selectin"
    )


class PlayerPointHistory(Base):
    """History of Player Point changes."""
    
    __tablename__ = "player_point_history"
    
    player_id: Mapped[str] = mapped_column(ForeignKey("players.id"), nullable=False)
    change_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    unspent_after: Mapped[int | None] = mapped_column(Integer, nullable=True)
    earned_after: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    # Relationships
    player: Mapped[Player] = relationship(Player, back_populates="pp_history")
```

### Step 2.3: Character Base Model

Create `src/core/models/character.py`:

```python
"""Character base model and shared functionality."""

from sqlalchemy import String, Integer, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.models.base import Base


class Character(Base):
    """Base character model - all races use this with JSON data."""
    
    __tablename__ = "characters"
    
    # Core info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    race_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Player relationship
    player_id: Mapped[str | None] = mapped_column(
        ForeignKey("players.id"), nullable=True, index=True
    )
    
    # Status
    is_npc: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(50), default="active")
    
    # Experience
    xp_unspent: Mapped[int] = mapped_column(Integer, default=0)
    xp_earned: Mapped[int] = mapped_column(Integer, default=0)
    
    # Narrative
    biography: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Metadata
    narrator: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    # Race-specific data stored as JSON
    data: Mapped[dict] = mapped_column(JSON, default=dict)
    
    # Relationships
    player: Mapped["Player" | None] = relationship(
        "Player", back_populates="characters"
    )
    traits: Mapped[list["Trait"]] = relationship(
        "Trait", back_populates="character", lazy="selectin", cascade="all, delete-orphan"
    )
    xp_history: Mapped[list["ExperienceHistory"]] = relationship(
        "ExperienceHistory", back_populates="character", lazy="selectin"
    )
    equipment: Mapped[list["CharacterItem"]] = relationship(
        "CharacterItem", back_populates="character", lazy="selectin"
    )
    locations: Mapped[list["CharacterLocation"]] = relationship(
        "CharacterLocation", back_populates="character", lazy="selectin"
    )


class Trait(Base):
    """Individual trait (attribute, ability, discipline, etc.)."""
    
    __tablename__ = "traits"
    
    character_id: Mapped[str] = mapped_column(
        ForeignKey("characters.id"), nullable=False, index=True
    )
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[str | None] = mapped_column(String(255), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    display_type: Mapped[str] = mapped_column(String(50), default="simple")
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships
    character: Mapped[Character] = relationship(Character, back_populates="traits")


class ExperienceHistory(Base):
    """Experience point transaction history."""
    
    __tablename__ = "experience_history"
    
    character_id: Mapped[str] = mapped_column(
        ForeignKey("characters.id"), nullable=False, index=True
    )
    entry_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'earned' or 'spent'
    change_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    date: Mapped[str] = mapped_column(String(10), nullable=False)  # ISO date
    unspent_after: Mapped[int | None] = mapped_column(Integer, nullable=True)
    earned_after: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    # Relationships
    character: Mapped[Character] = relationship(Character, back_populates="xp_history")
```

### Step 2.4: APR Models

Create `src/core/models/apr.py`:

```python
"""Action, Plot, Rumor models."""

from sqlalchemy import String, Integer, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.models.base import Base


class Action(Base):
    """Character downtime action."""
    
    __tablename__ = "actions"
    
    character_id: Mapped[str] = mapped_column(
        ForeignKey("characters.id"), nullable=False, index=True
    )
    action_date: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    action_type: Mapped[str] = mapped_column(String(100), nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=0)
    unused: Mapped[int] = mapped_column(Integer, default=0)
    total: Mapped[int] = mapped_column(Integer, default=0)
    growth: Mapped[int] = mapped_column(Integer, default=0)
    action_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Relationships
    character: Mapped["Character"] = relationship("Character")


class Plot(Base):
    """Storyline/plot tracking."""
    
    __tablename__ = "plots"
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active")


class Rumor(Base):
    """Information/rumor distribution."""
    
    __tablename__ = "rumors"
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    level: Mapped[int] = mapped_column(Integer, default=1)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    rumor_date: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    
    # Target filters (optional)
    target_character_id: Mapped[str | None] = mapped_column(
        ForeignKey("characters.id"), nullable=True, index=True
    )
    target_race: Mapped[str | None] = mapped_column(String(50), nullable=True)
    target_group: Mapped[str | None] = mapped_column(String(100), nullable=True)
    target_influence: Mapped[str | None] = mapped_column(String(100), nullable=True)
```

### Step 2.5: Item & Location Models

Create `src/core/models/item_location.py`:

```python
"""Items and Locations models."""

from sqlalchemy import String, Integer, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.models.base import Base


class Item(Base):
    """Equipment item."""
    
    __tablename__ = "items"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    item_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    subtype: Mapped[str | None] = mapped_column(String(100), nullable=True)
    level: Mapped[int] = mapped_column(Integer, default=0)
    bonus: Mapped[int] = mapped_column(Integer, default=0)
    damage_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    damage_amount: Mapped[int] = mapped_column(Integer, default=0)
    concealability: Mapped[str | None] = mapped_column(String(50), nullable=True)
    appearance: Mapped[str | None] = mapped_column(Text, nullable=True)
    powers: Mapped[str | None] = mapped_column(Text, nullable=True)
    data: Mapped[dict] = mapped_column(JSON, default=dict)


class Location(Base):
    """Game location (haven, caern, etc.)."""
    
    __tablename__ = "locations"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    location_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    level: Mapped[int] = mapped_column(Integer, default=0)
    owner_id: Mapped[str | None] = mapped_column(
        ForeignKey("characters.id"), nullable=True, index=True
    )
    access: Mapped[str | None] = mapped_column(Text, nullable=True)
    affinity: Mapped[str | None] = mapped_column(String(100), nullable=True)
    totem: Mapped[str | None] = mapped_column(String(255), nullable=True)
    security_traits: Mapped[int] = mapped_column(Integer, default=0)
    security_retests: Mapped[int] = mapped_column(Integer, default=0)
    gauntlet_shroud: Mapped[str | None] = mapped_column(String(50), nullable=True)
    where_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    appearance: Mapped[str | None] = mapped_column(Text, nullable=True)
    security_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    umbra_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    links: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array as string


class CharacterItem(Base):
    """Association between character and item."""
    
    __tablename__ = "character_items"
    
    character_id: Mapped[str] = mapped_column(
        ForeignKey("characters.id"), nullable=False, index=True
    )
    item_id: Mapped[str] = mapped_column(
        ForeignKey("items.id"), nullable=False, index=True
    )
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Relationships
    character: Mapped["Character"] = relationship("Character", back_populates="equipment")
    item: Mapped[Item] = relationship(Item)


class CharacterLocation(Base):
    """Association between character and location."""
    
    __tablename__ = "character_locations"
    
    character_id: Mapped[str] = mapped_column(
        ForeignKey("characters.id"), nullable=False, index=True
    )
    location_id: Mapped[str] = mapped_column(
        ForeignKey("locations.id"), nullable=False, index=True
    )
    relationship_type: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # 'owner', 'resident', 'frequent'
    
    # Relationships
    character: Mapped["Character"] = relationship("Character", back_populates="locations")
    location: Mapped[Location] = relationship(Location)
```

### Step 2.6: Create Model Init

Create `src/core/models/__init__.py`:

```python
"""Database models package."""

from src.core.models.base import Base
from src.core.models.player import Player, PlayerPointHistory
from src.core.models.character import Character, Trait, ExperienceHistory
from src.core.models.apr import Action, Plot, Rumor
from src.core.models.item_location import Item, Location, CharacterItem, CharacterLocation

__all__ = [
    "Base",
    "Player",
    "PlayerPointHistory",
    "Character",
    "Trait",
    "ExperienceHistory",
    "Action",
    "Plot",
    "Rumor",
    "Item",
    "Location",
    "CharacterItem",
    "CharacterLocation",
]
```

### Step 2.7: Test Model Creation

```bash
# Create test script
cat > scripts/test_models.py << 'EOF'
"""Test database model creation."""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.core.models import Base, Character, Player, Trait

async def test_models():
    # Create in-memory database
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=True)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Create player
        player = Player(name="Test Player", email="test@example.com")
        session.add(player)
        await session.flush()
        
        # Create character
        character = Character(
            name="Test Vampire",
            race_type="vampire",
            player_id=player.id,
            data={"clan": "Toreador", "generation": 10}
        )
        session.add(character)
        await session.flush()
        
        # Add traits
        traits = [
            Trait(character_id=character.id, category="physical", name="Strength", value="3"),
            Trait(character_id=character.id, category="disciplines", name="Auspex", value="2"),
        ]
        session.add_all(traits)
        
        await session.commit()
        
        # Query back
        result = await session.get(Character, character.id)
        print(f"Created character: {result.name}")
        print(f"Race: {result.race_type}")
        print(f"Player: {result.player.name}")
        print(f"Traits: {[t.name for t in result.traits]}")
    
    await engine.dispose()
    print("\n✓ Model tests passed!")

if __name__ == "__main__":
    asyncio.run(test_models())
EOF

# Run test
cd grapevine-modern
source .venv/bin/activate
python scripts/test_models.py
```

**Checkpoint:** If models test passes, commit: `git add -A && git commit -m "Phase 2: Core data models"`

---

## Phase 3: Race-Specific Character Classes

**Goal:** Implement 12 race-specific character types

### Step 3.1: Create Race Classes

Create `src/characters/base.py`:

```python
"""Base character class with common functionality."""

from abc import ABC, abstractmethod
from typing import Any


class RaceCharacter(ABC):
    """Abstract base for all race-specific character types."""
    
    race_type: str = ""
    
    def __init__(self, character_data: dict[str, Any]):
        self.data = character_data
    
    @abstractmethod
    def get_trait_categories(self) -> list[str]:
        """Return list of trait categories for this race."""
        pass
    
    @abstractmethod
    def get_temper_fields(self) -> list[str]:
        """Return list of temper fields (willpower, blood, etc.)."""
        pass
    
    @abstractmethod
    def validate(self) -> list[str]:
        """Validate character data, return list of errors."""
        pass
```

Create `src/characters/vampire.py`:

```python
"""Vampire: The Masquerade character implementation."""

from src.characters.base import RaceCharacter


class VampireCharacter(RaceCharacter):
    """Vampire character with Camarilla/Sabbat/Anarch support."""
    
    race_type = "vampire"
    
    # Valid options
    CLANS = [
        "Assamite", "Brujah", "Followers of Set", "Gangrel", "Giovanni",
        "Lasombra", "Malkavian", "Nosferatu", "Ravnos", "Toreador",
        "Tremere", "Tzimisce", "Ventru", "Caitiff", "Blood Brothers",
        "Gargoyles", "Harbingers of Skulls", "Kiasyd", "Nagaraja", "Salubri",
        "Samedi", "True Brujah", "Ahrimanes", "Anda", "Baali", "Bonsam",
        "Brujah antitribu", "City Gangrel", "Country Gangrel", "Daughters of Cacophony",
        "Gangrel antitribu", "Harbingers of Skulls", "Koldun", "Lamia", "Lhiannan",
        "Malkavian antitribu", "Nosferatu antitribu", "Pander", "Ravnos antitribu",
        "Serpents of the Light", "Toreador antitribu", "Tremere antitribu",
        "Ventru antitribu", "Angellis Ater", "Noiad"
    ]
    
    SECTS = ["Camarilla", "Sabbat", "Anarch", "Independent", "Inconnu"]
    
    PATHS = ["Humanity", "Path of the Beast", "Path of Blood", "Path of Bones",
             "Path of Metamorphosis", "Path of Night", "Path of Paradox",
             "Path of Power and the Inner Voice", "Path of Typhon", "Path of Lilith"]
    
    def get_trait_categories(self) -> list[str]:
        return [
            "physical", "social", "mental",
            "physical_neg", "social_neg", "mental_neg",
            "abilities", "backgrounds", "influences",
            "disciplines", "rituals", "status", "merits", "flaws"
        ]
    
    def get_temper_fields(self) -> list[str]:
        return ["blood", "willpower"]
    
    def validate(self) -> list[str]:
        errors = []
        
        # Validate clan
        clan = self.data.get("clan")
        if clan and clan not in self.CLANS:
            errors.append(f"Invalid clan: {clan}")
        
        # Validate sect
        sect = self.data.get("sect")
        if sect and sect not in self.SECTS:
            errors.append(f"Invalid sect: {sect}")
        
        # Validate generation
        generation = self.data.get("generation")
        if generation and not (4 <= generation <= 16):
            errors.append(f"Invalid generation: {generation}")
        
        return errors
```

Create `src/characters/werewolf.py`:

```python
"""Werewolf: The Apocalypse character implementation."""

from src.characters.base import RaceCharacter


class WerewolfCharacter(RaceCharacter):
    """Garou character with tribe, auspice, and breed."""
    
    race_type = "werewolf"
    
    TRIBES = ["Black Furies", "Bone Gnawers", "Children of Gaia", "Fianna",
              "Get of Fenris", "Glass Walkers", "Red Talons", "Shadow Lords",
              "Silent Striders", "Silver Fangs", "Uktena", "Wendigo", "Stargazers",
              "Black Spiral Dancers", "Bane Tender", "Blooded"]
    
    BREEDS = ["Homid", "Lupus", "Metis"]
    AUSPICES = ["Ragabash", "Theurge", "Philodox", "Galliard", "Ahroun"]
    RANKS = ["Cliath", "Fostern", "Adren", "Athro", "Elder"]
    
    def get_trait_categories(self) -> list[str]:
        return [
            "physical", "social", "mental",
            "physical_neg", "social_neg", "mental_neg",
            "abilities", "backgrounds", "gifts", "rites",
            "honor_traits", "glory_traits", "wisdom_traits",
            "features", "merits", "flaws"
        ]
    
    def get_temper_fields(self) -> list[str]:
        return ["rage", "gnosis", "willpower"]
    
    def validate(self) -> list[str]:
        errors = []
        
        if self.data.get("tribe") not in self.TRIBES:
            errors.append(f"Invalid tribe: {self.data.get('tribe')}")
        
        if self.data.get("breed") not in self.BREEDS:
            errors.append(f"Invalid breed: {self.data.get('breed')}")
        
        if self.data.get("auspice") not in self.AUSPICES:
            errors.append(f"Invalid auspice: {self.data.get('auspice')}")
        
        return errors
```

Create remaining race files following the same pattern:
- `mage.py` - Mage: The Ascension (Traditions, Spheres, Arete)
- `changeling.py` - Changeling: The Dreaming (Kith, Seeming, Arts)
- `wraith.py` - Wraith: The Oblivion (Guild, Arcanoi, Passions)
- `mummy.py` - Mummy: The Resurrection (Amenti, Hekau)
- `kuei_jin.py` - Kindred of the East (Dharma, Chi)
- `fera.py` - Changing Breeds (Fera type, Gifts)
- `hunter.py` - Hunter: The Reckoning (Creed, Edges)
- `demon.py` - Demon: The Fallen (House, Lores)
- `various.py` - Generic/Custom characters
- `mortal.py` - Mortal characters

### Step 3.2: Create Character Factory

Create `src/characters/factory.py`:

```python
"""Factory for creating race-specific character instances."""

from typing import Type

from src.characters.base import RaceCharacter
from src.characters.vampire import VampireCharacter
from src.characters.werewolf import WerewolfCharacter
from src.characters.mage import MageCharacter
from src.characters.changeling import ChangelingCharacter
from src.characters.wraith import WraithCharacter
from src.characters.mummy import MummyCharacter
from src.characters.kuei_jin import KueiJinCharacter
from src.characters.fera import FeraCharacter
from src.characters.hunter import HunterCharacter
from src.characters.demon import DemonCharacter
from src.characters.mortal import MortalCharacter
from src.characters.various import VariousCharacter

# Registry of character types
CHARACTER_REGISTRY: dict[str, Type[RaceCharacter]] = {
    "vampire": VampireCharacter,
    "werewolf": WerewolfCharacter,
    "mage": MageCharacter,
    "changeling": ChangelingCharacter,
    "wraith": WraithCharacter,
    "mummy": MummyCharacter,
    "kuei_jin": KueiJinCharacter,
    "fera": FeraCharacter,
    "hunter": HunterCharacter,
    "demon": DemonCharacter,
    "mortal": MortalCharacter,
    "various": VariousCharacter,
}


def get_character_class(race_type: str) -> Type[RaceCharacter]:
    """Get character class for race type."""
    race_type = race_type.lower().replace("-", "_").replace(" ", "_")
    if race_type not in CHARACTER_REGISTRY:
        raise ValueError(f"Unknown race type: {race_type}")
    return CHARACTER_REGISTRY[race_type]


def create_character(race_type: str, data: dict) -> RaceCharacter:
    """Create character instance for race type."""
    char_class = get_character_class(race_type)
    return char_class(data)


def list_races() -> list[str]:
    """List all supported race types."""
    return list(CHARACTER_REGISTRY.keys())
```

### Step 3.3: Create Init File

Create `src/characters/__init__.py`:

```python
"""Character race implementations."""

from src.characters.base import RaceCharacter
from src.characters.factory import (
    get_character_class,
    create_character,
    list_races,
    CHARACTER_REGISTRY,
)

__all__ = [
    "RaceCharacter",
    "get_character_class",
    "create_character",
    "list_races",
    "CHARACTER_REGISTRY",
]
```

**Checkpoint:** Test factory works with all 12 races, then commit.

---

## Phase 4: Legacy File Parsers

**Goal:** Implement parsers for .gv3, .gvm, .gex files

### Step 4.1: GV3 Parser

Create `src/legacy/gv3_parser.py`:

```python
"""Parser for Grapevine 3.x binary game files (.gv3)."""

import struct
from pathlib import Path
from typing import Any, BinaryIO


class GV3Parser:
    """Parse legacy GV3 binary format."""
    
    MAGIC = b"GVBG"
    SUPPORTED_VERSIONS = [3.0, 3.01]
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.version = 0.0
        self.data = {}
    
    def parse(self) -> dict[str, Any]:
        """Parse GV3 file and return structured data."""
        with open(self.file_path, "rb") as f:
            self._read_header(f)
            self._read_game_info(f)
            self._read_players(f)
            self._read_characters(f)
            self._read_items(f)
            self._read_locations(f)
            self._read_actions(f)
            self._read_plots(f)
            self._read_rumors(f)
        
        return self.data
    
    def _read_header(self, f: BinaryIO) -> None:
        """Read file header."""
        magic = f.read(4)
        if magic != self.MAGIC:
            raise ValueError(f"Invalid GV3 file: wrong magic bytes {magic}")
        
        self.version = struct.unpack("<f", f.read(4))[0]
        if self.version not in self.SUPPORTED_VERSIONS:
            print(f"Warning: Untested version {self.version}")
        
        # Skip reserved bytes
        f.read(8)
    
    def _read_game_info(self, f: BinaryIO) -> None:
        """Read game information section."""
        # Implementation based on VB6 structure
        # This is a placeholder - actual structure needs analysis of binary format
        self.data["game"] = {
            "name": self._read_string(f),
            "description": self._read_string(f),
            "email": self._read_string(f),
            "website": self._read_string(f),
        }
    
    def _read_players(self, f: BinaryIO) -> None:
        """Read player list."""
        count = struct.unpack("<i", f.read(4))[0]
        players = []
        
        for _ in range(count):
            player = {
                "name": self._read_string(f),
                "id": self._read_string(f),
                "email": self._read_string(f),
                "phone": self._read_string(f),
                "address": self._read_string(f),
                "status": self._read_string(f),
                "position": self._read_string(f),
                "pp_unspent": struct.unpack("<i", f.read(4))[0],
                "pp_earned": struct.unpack("<i", f.read(4))[0],
            }
            players.append(player)
        
        self.data["players"] = players
    
    def _read_characters(self, f: BinaryIO) -> None:
        """Read character list."""
        count = struct.unpack("<i", f.read(4))[0]
        characters = []
        
        for _ in range(count):
            char = {
                "name": self._read_string(f),
                "id": self._read_string(f),
                "race_type": self._read_string(f),
                "player_id": self._read_string(f),
                "is_npc": struct.unpack("<?", f.read(1))[0],
                "status": self._read_string(f),
                "xp_unspent": struct.unpack("<i", f.read(4))[0],
                "xp_earned": struct.unpack("<i", f.read(4))[0],
                "narrator": self._read_string(f),
                "biography": self._read_string(f),
                "notes": self._read_string(f),
            }
            
            # Read race-specific data as JSON-like dict
            char["data"] = self._read_json_data(f)
            
            # Read traits
            char["traits"] = self._read_traits(f)
            
            # Read experience history
            char["xp_history"] = self._read_xp_history(f)
            
            characters.append(char)
        
        self.data["characters"] = characters
    
    def _read_traits(self, f: BinaryIO) -> list[dict]:
        """Read trait list for a character."""
        count = struct.unpack("<i", f.read(4))[0]
        traits = []
        
        for _ in range(count):
            trait = {
                "category": self._read_string(f),
                "name": self._read_string(f),
                "value": self._read_string(f),
                "note": self._read_string(f),
                "display_type": self._read_string(f),
            }
            traits.append(trait)
        
        return traits
    
    def _read_xp_history(self, f: BinaryIO) -> list[dict]:
        """Read experience history entries."""
        count = struct.unpack("<i", f.read(4))[0]
        history = []
        
        for _ in range(count):
            entry = {
                "date": self._read_string(f),
                "entry_type": self._read_string(f),
                "change_amount": struct.unpack("<i", f.read(4))[0],
                "reason": self._read_string(f),
                "unspent_after": struct.unpack("<i", f.read(4))[0],
                "earned_after": struct.unpack("<i", f.read(4))[0],
            }
            history.append(entry)
        
        return history
    
    def _read_items(self, f: BinaryIO) -> None:
        """Read item/equipment list."""
        # Implementation placeholder
        pass
    
    def _read_locations(self, f: BinaryIO) -> None:
        """Read location list."""
        # Implementation placeholder
        pass
    
    def _read_actions(self, f: BinaryIO) -> None:
        """Read action list."""
        # Implementation placeholder
        pass
    
    def _read_plots(self, f: BinaryIO) -> None:
        """Read plot list."""
        # Implementation placeholder
        pass
    
    def _read_rumors(self, f: BinaryIO) -> None:
        """Read rumor list."""
        # Implementation placeholder
        pass
    
    def _read_string(self, f: BinaryIO) -> str:
        """Read length-prefixed string."""
        length = struct.unpack("<i", f.read(4))[0]
        if length == 0:
            return ""
        return f.read(length).decode("utf-8", errors="replace")
    
    def _read_json_data(self, f: BinaryIO) -> dict:
        """Read JSON-like data structure."""
        # Placeholder - actual format needs analysis
        return {}
    
    def export(self, data: dict, file_path: Path) -> None:
        """Export data to GV3 format."""
        with open(file_path, "wb") as f:
            self._write_header(f)
            self._write_game_info(f, data.get("game", {}))
            self._write_players(f, data.get("players", []))
            self._write_characters(f, data.get("characters", []))
    
    def _write_header(self, f: BinaryIO) -> None:
        """Write file header."""
        f.write(self.MAGIC)
        f.write(struct.pack("<f", 3.01))
        f.write(b"\x00" * 8)  # Reserved
    
    def _write_string(self, f: BinaryIO, s: str) -> None:
        """Write length-prefixed string."""
        encoded = s.encode("utf-8")
        f.write(struct.pack("<i", len(encoded)))
        f.write(encoded)
```

### Step 4.2: GVM Parser (Menus)

Create `src/legacy/gvm_parser.py`:

```python
"""Parser for Grapevine menu files (.gvm)."""

import struct
from pathlib import Path
from typing import Any, BinaryIO


class GVMParser:
    """Parse legacy GVM binary menu format."""
    
    MAGIC = b"GVBM"
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.menus = []
    
    def parse(self) -> list[dict]:
        """Parse GVM file and return menu structure."""
        with open(self.file_path, "rb") as f:
            self._read_header(f)
            self._read_menus(f)
        
        return self.menus
    
    def _read_header(self, f: BinaryIO) -> None:
        """Read file header."""
        magic = f.read(4)
        if magic != self.MAGIC:
            raise ValueError(f"Invalid GVM file: wrong magic bytes {magic}")
        
        version = struct.unpack("<f", f.read(4))[0]
        # Skip reserved
        f.read(8)
    
    def _read_menus(self, f: BinaryIO) -> None:
        """Read menu list."""
        count = struct.unpack("<i", f.read(4))[0]
        
        for _ in range(count):
            menu = {
                "name": self._read_string(f),
                "items": self._read_menu_items(f),
            }
            self.menus.append(menu)
    
    def _read_menu_items(self, f: BinaryIO) -> list[dict]:
        """Read items for a menu."""
        count = struct.unpack("<i", f.read(4))[0]
        items = []
        
        for _ in range(count):
            item = {
                "name": self._read_string(f),
                "tag": self._read_string(f),
                "is_category": struct.unpack("<?", f.read(1))[0],
                "linked_trait": self._read_string(f),
                "children": [],
            }
            
            # Recursively read children if category
            if item["is_category"]:
                item["children"] = self._read_menu_items(f)
            
            items.append(item)
        
        return items
    
    def _read_string(self, f: BinaryIO) -> str:
        """Read length-prefixed string."""
        length = struct.unpack("<i", f.read(4))[0]
        if length == 0:
            return ""
        return f.read(length).decode("utf-8", errors="replace")
```

### Step 4.3: GEX Parser (Exchange)

Create `src/legacy/gex_parser.py`:

```python
"""Parser for Grapevine exchange files (.gex)."""

import struct
from pathlib import Path
from typing import Any, BinaryIO


class GEXParser:
    """Parse legacy GEX exchange format."""
    
    MAGIC = b"GVBE"
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.data = {}
    
    def parse(self) -> dict[str, Any]:
        """Parse GEX file."""
        with open(self.file_path, "rb") as f:
            self._read_header(f)
            self._read_exchange_data(f)
        
        return self.data
    
    def _read_header(self, f: BinaryIO) -> None:
        """Read file header."""
        magic = f.read(4)
        if magic != self.MAGIC:
            raise ValueError(f"Invalid GEX file: wrong magic bytes {magic}")
        
        version = struct.unpack("<f", f.read(4))[0]
        f.read(8)  # Reserved
    
    def _read_exchange_data(self, f: BinaryIO) -> None:
        """Read exchange data sections."""
        # Implementation based on actual binary structure
        self.data["type"] = self._read_string(f)
        self.data["characters"] = self._read_character_refs(f)
        self.data["items"] = self._read_item_refs(f)
    
    def _read_string(self, f: BinaryIO) -> str:
        """Read length-prefixed string."""
        length = struct.unpack("<i", f.read(4))[0]
        if length == 0:
            return ""
        return f.read(length).decode("utf-8", errors="replace")
    
    def _read_character_refs(self, f: BinaryIO) -> list[str]:
        """Read character ID references."""
        count = struct.unpack("<i", f.read(4))[0]
        return [self._read_string(f) for _ in range(count)]
    
    def _read_item_refs(self, f: BinaryIO) -> list[str]:
        """Read item ID references."""
        count = struct.unpack("<i", f.read(4))[0]
        return [self._read_string(f) for _ in range(count)]
```

### Step 4.4: Create Legacy Init

Create `src/legacy/__init__.py`:

```python
"""Legacy file format support."""

from src.legacy.gv3_parser import GV3Parser
from src.legacy.gvm_parser import GVMParser
from src.legacy.gex_parser import GEXParser

__all__ = ["GV3Parser", "GVMParser", "GEXParser"]
```

**Checkpoint:** Test parsers with sample files, then commit.

---

## Phase 5: Alembic Migrations

**Goal:** Set up database migration system

### Step 5.1: Initialize Alembic

```bash
cd grapevine-modern
source .venv/bin/activate

# Initialize alembic
alembic init migrations

# Configure alembic.ini
cat > alembic.ini << 'EOF'
# Alembic configuration
[alembic]
script_location = migrations
prepend_sys_path = .
version_path_separator = os

# Database URL (override with env var)
sqlalchemy.url = sqlite:///./grapevine.db

[post_write_hooks]
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
EOF

# Update migrations/env.py
cat > migrations/env.py << 'EOF'
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
import os
import sys

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.core.models import Base

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Model metadata
target_metadata = Base.metadata

# Get database URL from env or use default
database_url = os.getenv("DATABASE_URL", "sqlite:///./grapevine.db")
config.set_main_option("sqlalchemy.url", database_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
EOF
```

### Step 5.2: Create Initial Migration

```bash
# Create initial migration
alembic revision --autogenerate -m "Initial migration - core models"

# Verify migration was created
ls -la migrations/versions/

# Run migration
alembic upgrade head
```

**Checkpoint:** Migration runs successfully, database created.

---

## Phase 6: Testing Infrastructure

**Goal:** Set up pytest with fixtures

### Step 6.1: Test Configuration

Create `tests/conftest.py`:

```python
"""Pytest fixtures and configuration."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.core.models import Base


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
    async_session_maker = sessionmaker(
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
```

### Step 6.2: Unit Tests

Create `tests/unit/test_models.py`:

```python
"""Tests for database models."""

import pytest
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
    # Create player first
    player = Player(**sample_player_data)
    async_session.add(player)
    await async_session.flush()
    
    # Create character
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
    
    assert len(character.traits) == 1
    assert character.traits[0].name == "Athletics"
```

Create `tests/unit/test_characters.py`:

```python
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
    assert len(errors) == 2  # Invalid clan and generation
```

### Step 6.3: Integration Tests

Create `tests/integration/test_gv3_parser.py`:

```python
"""Integration tests for GV3 parser."""

import pytest
from pathlib import Path

from src.legacy import GV3Parser


@pytest.fixture
def sample_gv3_path():
    """Path to sample GV3 file for testing."""
    # Placeholder - create test fixtures
    return Path("tests/fixtures/sample.gv3")


def test_gv3_parser_init():
    """Test parser initialization."""
    parser = GV3Parser(Path("dummy.gv3"))
    assert parser.file_path == Path("dummy.gv3")


# def test_gv3_parse_real_file(sample_gv3_path):
#     """Test parsing a real GV3 file (requires fixture)."""
#     if not sample_gv3_path.exists():
#         pytest.skip("Sample GV3 file not found")
#     
#     parser = GV3Parser(sample_gv3_path)
#     data = parser.parse()
#     
#     assert "game" in data
#     assert "characters" in data
```

### Step 6.4: Run Tests

```bash
# Run all tests
cd grapevine-modern
source .venv/bin/activate
pytest -v

# Run with coverage
pytest --cov=src --cov-report=html --cov-report=term

# Run specific test file
pytest tests/unit/test_models.py -v
```

**Checkpoint:** All tests pass, commit: `git add -A && git commit -m "Phase 6: Testing infrastructure"`

---

## Phase 7: Documentation & Completion

### Step 7.1: Create README

Create `README.md`:

```markdown
# Grapevine Modern

A modern Python implementation of the Grapevine LARP character management system.

## Features

- **12 Character Types:** Full support for Vampire, Werewolf, Mage, Changeling, Wraith, Mummy, Kuei-Jin, Fera, Hunter, Demon, Mortal, and Various
- **Legacy Compatibility:** Import/Export .gv3, .gvm, and .gex files
- **Modern Architecture:** FastAPI backend with SQLAlchemy ORM
- **Cross-Platform:** Works on Windows, macOS, and Linux

## Quick Start

```bash
# Setup
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Database
alembic upgrade head

# Run tests
pytest

# Start API (Phase 8)
uvicorn src.api.main:app --reload
```

## Project Structure

- `src/api/` - FastAPI routes and endpoints
- `src/core/` - Database models and business logic
- `src/characters/` - Race-specific implementations
- `src/legacy/` - Legacy file format parsers
- `tests/` - Unit and integration tests
- `docs/` - Documentation

## Migration from Legacy Grapevine

1. Copy your .gv3 files to a working directory
2. Use the import API: `POST /api/v1/imports/legacy`
3. Verify data integrity
4. Export to new formats as needed

## License

MIT License - See LICENSE file
```

### Step 7.2: Create IMPLEMENTATION_PLAN.md

Create `IMPLEMENTATION_PLAN.md`:

```markdown
# Grapevine Migration - Implementation Plan

## Completed Phases

### Phase 1: Foundation ✓
- [x] Project directory structure
- [x] Python virtual environment
- [x] Dependencies installed
- [x] Configuration files (pyproject.toml, .gitignore, .env.example)

### Phase 2: Core Data Models ✓
- [x] Base SQLAlchemy model
- [x] Player model with PP tracking
- [x] Character base model
- [x] Trait model
- [x] APR models (Action, Plot, Rumor)
- [x] Item and Location models
- [x] Experience history tracking

### Phase 3: Race-Specific Characters ✓
- [x] Base RaceCharacter class
- [x] Vampire character implementation
- [x] Werewolf character implementation
- [x] Mage character implementation
- [x] Changeling character implementation
- [x] Wraith character implementation
- [x] Mummy character implementation
- [x] Kuei-Jin character implementation
- [x] Fera character implementation
- [x] Hunter character implementation
- [x] Demon character implementation
- [x] Mortal character implementation
- [x] Various character implementation
- [x] Character factory

### Phase 4: Legacy File Parsers ✓
- [x] GV3Parser (.gv3 game files)
- [x] GVMParser (.gvm menu files)
- [x] GEXParser (.gex exchange files)

### Phase 5: Database Migrations ✓
- [x] Alembic configuration
- [x] Initial migration
- [x] Database creation

### Phase 6: Testing Infrastructure ✓
- [x] pytest configuration
- [x] Test fixtures
- [x] Unit tests for models
- [x] Unit tests for characters
- [x] Integration test structure

### Phase 7: Documentation ✓
- [x] README.md
- [x] Implementation plan
- [x] AGENTS.md (this file)

## Next Phases (Future Work)

### Phase 8: API Development
- [ ] FastAPI application setup
- [ ] Character endpoints (CRUD)
- [ ] Player endpoints
- [ ] APR endpoints
- [ ] Query endpoints
- [ ] Import/Export endpoints

### Phase 9: Desktop UI
- [ ] PyQt6 application
- [ ] Character sheet forms
- [ ] Player management
- [ ] APR management
- [ ] Query builder
- [ ] Report output

### Phase 10: Web UI
- [ ] React frontend
- [ ] Dashboard
- [ ] Character management
- [ ] Responsive design

## Technical Debt & Known Issues

1. GV3 parser needs binary format analysis for complete implementation
2. Some race validation rules are simplified
3. Menu system (GVM) integration not yet complete
4. Report templates not yet migrated

## Success Metrics

- [x] 12 character types implemented
- [x] All core models created
- [x] Database migrations working
- [x] Tests passing
- [ ] API endpoints (Phase 8)
- [ ] UI implemented (Phase 9-10)
```

### Step 7.3: Final Commit

```bash
cd grapevine-modern
git add -A
git commit -m "Phase 7: Complete foundation - Ready for API development"
git log --oneline -10
```

---

## Build Commands Summary

### One-Time Setup
```bash
# Initialize project
mkdir -p grapevine-modern && cd grapevine-modern
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
```

### Development Commands
```bash
# Run tests
pytest -v

# Run with coverage
pytest --cov=src --cov-report=html

# Type checking
mypy src/

# Linting
ruff check src/
ruff format src/

# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

### Testing Legacy Parsers
```bash
# Place sample .gv3 files in tests/fixtures/
python -c "from src.legacy import GV3Parser; p = GV3Parser('tests/fixtures/sample.gv3'); print(p.parse())"
```

---

## Ralph Loop Completion Signal

When all phases are complete, output:

```
========================================
IMPLEMENTATION COMPLETE
========================================

Successfully implemented:
- Project structure and dependencies
- 12 race-specific character classes
- Core database models (SQLAlchemy)
- Legacy file parsers (GV3, GVM, GEX)
- Alembic migrations
- Testing infrastructure with pytest

Next Steps:
1. Run: pytest (verify all tests pass)
2. Check: grapevine-modern/ directory structure
3. Review: IMPLEMENTATION_PLAN.md for completion status
4. Proceed: Phase 8 (API Development)

Files created: ~50 source files
Database: SQLite schema initialized
Tests: Unit tests for models and characters
========================================
```

---

**End of AGENTS.md**
