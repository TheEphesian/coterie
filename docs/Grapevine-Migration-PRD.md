# Product Requirements Document (PRD)
## Grapevine LARP Character Sheet Manager Migration
### VB6 to Python Modernization Project

**Version:** 1.0  
**Date:** February 13, 2026  
**Status:** Draft for Review  

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Project Goals and Objectives](#2-project-goals-and-objectives)
3. [Technical Architecture](#3-technical-architecture)
4. [Data Models and Schema](#4-data-models-and-schema)
5. [API Specifications](#5-api-specifications)
6. [User Interface Requirements](#6-user-interface-requirements)
7. [Feature Requirements](#7-feature-requirements)
8. [Migration Strategy](#8-migration-strategy)
9. [Security and Data Protection](#9-security-and-data-protection)
10. [Testing and Quality Assurance](#10-testing-and-quality-assurance)
11. [Success Criteria](#11-success-criteria)
12. [Timeline and Milestones](#12-timeline-and-milestones)
13. [Appendices](#13-appendices)

---

## 1. Executive Summary

### 1.1 Overview
Grapevine is a comprehensive Live Action Role-Playing (LARP) administration utility originally developed in Visual Basic 6 (2001). This PRD outlines the complete migration of the application to a modern Python-based architecture with a web-enabled API and contemporary user interface.

### 1.2 Current State
- **Platform:** Visual Basic 6 (legacy, unsupported)
- **Architecture:** Desktop-only, single-user file-based system
- **Data Storage:** Proprietary binary formats (.gv3, .gvm, .gex)
- **Character Support:** 12 World of Darkness game lines
- **Limitations:** Windows-only, no modern integration capabilities, maintenance burden

### 1.3 Target State
- **Platform:** Python 3.12+ with modern web technologies
- **Architecture:** API-first with pluggable UI (Desktop/Web/Mobile)
- **Data Storage:** SQLite (local) / PostgreSQL (multi-user) with JSON support
- **Compatibility:** Full backward compatibility with legacy file formats
- **Extensibility:** Plugin system, RESTful API, third-party integrations

### 1.4 Key Stakeholders
- **Primary Users:** LARP storytellers, game administrators, players
- **Secondary Users:** Game developers, system integrators
- **Technical Stakeholders:** Future maintainers, API consumers

---

## 2. Project Goals and Objectives

### 2.1 Primary Goals

1. **Functional Parity**
   - Migrate all existing features from VB6 Grapevine v3.0.1
   - Support all 12 character types with complete rule implementations
   - Maintain backward compatibility with existing .gv3 files

2. **Modern Architecture**
   - API-first design enabling multiple frontends
   - Clean separation between business logic and presentation
   - Plugin architecture for extensibility

3. **Cross-Platform Support**
   - Windows, macOS, Linux compatibility
   - Web-based interface for accessibility
   - Mobile-responsive design for on-the-go access

4. **Data Integrity and Migration**
   - Seamless import of legacy data formats
   - Zero data loss during migration
   - Export capabilities for interoperability

### 2.2 Secondary Goals

1. **Performance Improvements**
   - Sub-second query response times
   - Efficient handling of 1000+ character chronicles
   - Optimized report generation

2. **Enhanced User Experience**
   - Modern, intuitive UI/UX
   - Keyboard shortcuts and accessibility support
   - Contextual help and documentation

3. **Collaboration Features**
   - Multi-user support (optional server mode)
   - Role-based access control
   - Change tracking and audit logs

### 2.3 Non-Goals (Out of Scope for Initial Release)

- Real-time multiplayer game integration
- 3D character visualization
- AI-powered character generation
- Blockchain-based asset tracking
- In-app purchases or monetization

---

## 3. Technical Architecture

### 3.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Presentation Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  Desktop UI  │  │   Web UI     │  │   Mobile/Tablet      │  │
│  │  (PyQt/Tauri)│  │  (React/Vue) │  │   (PWA/Responsive)   │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
└─────────┼─────────────────┼────────────────────┼──────────────┘
          │                 │                    │
          └─────────────────┼────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                         API Layer                                │
│                    (FastAPI / Flask REST)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  Characters  │  │    APR       │  │   Reports/Output     │  │
│  │    API       │  │   System     │  │       API            │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   Queries    │  │   Import/    │  │    Configuration     │  │
│  │     API      │  │   Export     │  │        API           │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                      Business Logic Layer                        │
│                  (Python Domain Models)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  Character   │  │   Action/    │  │   Template Engine    │  │
│  │   Classes    │  │ Plot/Rumor   │  │   (Jinja2)           │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │    Query     │  │   Legacy     │  │    Plugin System     │  │
│  │   Engine     │  │   Importers  │  │                      │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                       Data Access Layer                          │
│              (SQLAlchemy ORM + Repository Pattern)               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   SQLite     │  │  PostgreSQL  │  │   Legacy Binary      │  │
│  │   (Local)    │  │  (Server)    │  │   Parsers (.gv3)     │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              File System (Templates, Exports)             │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Technology Stack

#### Backend
- **Language:** Python 3.12+
- **Web Framework:** FastAPI (async, OpenAPI/Swagger built-in)
- **ORM:** SQLAlchemy 2.0 with type hints
- **Data Validation:** Pydantic v2
- **Task Queue:** Celery (for background report generation)
- **Caching:** Redis (optional, for server deployments)

#### Frontend (Desktop)
- **Primary:** PyQt6 or Tauri (Rust-based with Python backend)
- **Styling:** Modern dark/light themes with CSS
- **Components:** Custom widgets for character sheets

#### Frontend (Web)
- **Framework:** React 18+ or Vue 3
- **State Management:** Zustand / Pinia
- **UI Library:** Tailwind CSS + Headless UI
- **Data Fetching:** React Query / TanStack Query
- **Forms:** React Hook Form with Zod validation

#### Data Storage
- **Primary:** SQLite (embedded, zero-config)
- **Enterprise:** PostgreSQL (multi-user, concurrent)
- **Migration:** Custom parsers for legacy formats
- **Export:** JSON, XML, PDF, Excel

#### Development Tools
- **Testing:** pytest with coverage
- **Linting:** ruff, mypy for type checking
- **Documentation:** Sphinx with Markdown support
- **CI/CD:** GitHub Actions

### 3.3 Project Structure

```
grapevine-modern/
├── docs/                          # Documentation
├── migrations/                    # Database migrations
├── src/
│   ├── api/                       # FastAPI routes
│   │   ├── routes/
│   │   │   ├── characters.py
│   │   │   ├── players.py
│   │   │   ├── actions.py
│   │   │   ├── plots.py
│   │   │   ├── rumors.py
│   │   │   ├── queries.py
│   │   │   ├── reports.py
│   │   │   ├── imports.py
│   │   │   └── config.py
│   │   ├── dependencies.py
│   │   └── main.py
│   ├── core/                      # Domain logic
│   │   ├── models/               # SQLAlchemy models
│   │   │   ├── character.py
│   │   │   ├── player.py
│   │   │   ├── action.py
│   │   │   ├── rumor.py
│   │   │   └── ...
│   │   ├── schemas/              # Pydantic schemas
│   │   ├── services/             # Business logic
│   │   └── repositories/         # Data access
│   ├── characters/               # Character implementations
│   │   ├── base.py
│   │   ├── vampire.py
│   │   ├── werewolf.py
│   │   ├── mage.py
│   │   └── ...
│   ├── legacy/                   # Legacy file support
│   │   ├── gv3_parser.py
│   │   ├── gvm_parser.py
│   │   └── gex_parser.py
│   ├── templates/                # Report templates
│   │   ├── html/
│   │   ├── text/
│   │   └── rtf/
│   ├── plugins/                  # Plugin system
│   └── utils/                    # Utilities
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/                 # Test data (including .gv3 files)
├── ui-desktop/                   # Desktop UI (PyQt/Tauri)
├── ui-web/                       # Web UI (React/Vue)
├── scripts/                      # Build and deployment
└── docker-compose.yml            # For server deployments
```

---

## 4. Data Models and Schema

### 4.1 Entity Relationship Diagram

```
┌─────────────────┐       ┌──────────────────┐       ┌─────────────────┐
│     Game        │       │     Player       │       │   Character     │
├─────────────────┤       ├──────────────────┤       ├─────────────────┤
│ PK id           │       │ PK id            │       │ PK id           │
│    name         │       │    name          │       │ FK player_id    │
│    description  │       │    email         │       │    name         │
│    email        │       │    phone         │       │    race_type    │
│    website      │       │    status        │       │    is_npc       │
│    created_at   │       │    pp_unspent    │       │    xp_unspent   │
│    updated_at   │       │    pp_earned     │       │    xp_earned    │
└────────┬────────┘       └────────┬─────────┘       │    status       │
         │                         │                │    created_at   │
         │                         │                └────────┬────────┘
         │                         │                         │
         └─────────────┬───────────┴─────────────────────────┘
                       │ 1:N
                       │
         ┌─────────────▼─────────────┐
         │    Character Traits       │
         ├───────────────────────────┤
         │ PK id                     │
         │ FK character_id           │
         │    category               │
         │    name                   │
         │    value                  │
         │    note                   │
         │    display_type           │
         └───────────────────────────┘

┌─────────────────┐       ┌──────────────────┐       ┌─────────────────┐
│     Action      │       │      Plot        │       │     Rumor       │
├─────────────────┤       ├──────────────────┤       ├─────────────────┤
│ PK id           │       │ PK id            │       │ PK id           │
│ FK character_id │       │    title         │       │    title        │
│    date         │       │    description   │       │    content      │
│    type         │       │    status        │       │    level        │
│    level        │       │    created_at    │       │    category     │
│    action_text  │       │    updated_at    │       │    date         │
│    result_text  │       └──────────────────┘       └─────────────────┘
│    growth       │
└─────────────────┘
```

### 4.2 Core Data Models

#### Character Base Model
```python
class CharacterBase(BaseModel):
    """Base character model - all races inherit from this"""
    
    # Core Information
    id: UUID
    name: str
    player_id: Optional[UUID]
    race_type: RaceType
    
    # Status
    is_npc: bool = False
    status: CharacterStatus = CharacterStatus.ACTIVE
    
    # Experience Points
    xp_unspent: int = 0
    xp_earned: int = 0
    
    # Core Traits (trait lists)
    physical_traits: List[Trait]
    social_traits: List[Trait]
    mental_traits: List[Trait]
    physical_neg: List[Trait]
    social_neg: List[Trait]
    mental_neg: List[Trait]
    abilities: List[Trait]
    backgrounds: List[Trait]
    influences: List[Trait]
    merits: List[Trait]
    flaws: List[Trait]
    
    # Tempers (permanent/temporary pairs)
    willpower: TemperPair
    health_levels: List[str]
    
    # Equipment & Locations
    equipment: List[ItemReference]
    locations: List[LocationReference]
    
    # Experience History
    xp_history: List[ExperienceEntry]
    
    # Narrative
    biography: Optional[str]
    notes: Optional[str]
    
    # Metadata
    narrator: Optional[str]
    created_at: datetime
    updated_at: datetime
```

#### Race-Specific Models

**Vampire Character:**
```python
class VampireCharacter(CharacterBase):
    race_type: RaceType = RaceType.VAMPIRE
    
    # Vampire-specific fields
    clan: str
    sect: str
    generation: int
    
    # Blood pool
    blood: TemperPair
    
    # Morality
    path: str
    path_rating: int
    
    # Vampire traits
    disciplines: List[Trait]
    rituals: List[Trait]
```

**Werewolf Character:**
```python
class WerewolfCharacter(CharacterBase):
    race_type: RaceType = RaceType.WEREWOLF
    
    # Werewolf-specific fields
    tribe: str
    breed: str
    auspice: str
    rank: str
    pack: Optional[str]
    totem: Optional[str]
    
    # Rage and Gnosis
    rage: TemperPair
    gnosis: TemperPair
    
    # Renown
    honor: RenownPair
    glory: RenownPair
    wisdom: RenownPair
    
    # Werewolf traits
    gifts: List[Trait]
    rites: List[Trait]
```

**Mage Character:**
```python
class MageCharacter(CharacterBase):
    race_type: RaceType = RaceType.MAGE
    
    # Mage-specific fields
    tradition: str
    essence: str
    cabal: Optional[str]
    rank: Optional[str]
    
    # Mage tempers
    arete: TemperPair
    quintessence: TemperPair
    paradox: TemperPair
    
    # Spheres
    spheres: List[Trait]
    
    # Rotes
    rotes: List[Rote]
    
    # Focus
    foci: Optional[str]
    resonance: List[Trait]
    reputation: List[Trait]
```

### 4.3 Supporting Models

**Player Model:**
```python
class Player(BaseModel):
    id: UUID
    name: str
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    
    # Player Points (staff positions)
    pp_unspent: int = 0
    pp_earned: int = 0
    pp_history: List[ExperienceEntry]
    
    status: PlayerStatus = PlayerStatus.ACTIVE
    position: Optional[str]
    
    created_at: datetime
    updated_at: datetime
```

**APR Models:**
```python
class Action(BaseModel):
    id: UUID
    character_id: UUID
    date: date
    action_type: str
    level: int
    unused: int
    total: int
    growth: int
    action_text: str
    result_text: str

class Plot(BaseModel):
    id: UUID
    title: str
    description: str
    status: PlotStatus
    created_at: datetime
    updated_at: datetime

class Rumor(BaseModel):
    id: UUID
    title: str
    content: str
    level: int
    category: RumorCategory
    date: date
    target_character_id: Optional[UUID]
    target_race: Optional[RaceType]
    target_group: Optional[str]
    target_influence: Optional[str]
```

### 4.4 Database Schema (SQLite/PostgreSQL)

```sql
-- Core Tables
CREATE TABLE games (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    email VARCHAR(255),
    website VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE players (
    id UUID PRIMARY KEY,
    game_id UUID REFERENCES games(id),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    pp_unspent INTEGER DEFAULT 0,
    pp_earned INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'active',
    position VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE characters (
    id UUID PRIMARY KEY,
    game_id UUID REFERENCES games(id),
    player_id UUID REFERENCES players(id),
    name VARCHAR(255) NOT NULL,
    race_type VARCHAR(50) NOT NULL,
    is_npc BOOLEAN DEFAULT FALSE,
    status VARCHAR(50) DEFAULT 'active',
    xp_unspent INTEGER DEFAULT 0,
    xp_earned INTEGER DEFAULT 0,
    biography TEXT,
    notes TEXT,
    narrator VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- JSON columns for flexible trait storage
    data JSONB  -- Stores all race-specific fields
);

CREATE TABLE traits (
    id UUID PRIMARY KEY,
    character_id UUID REFERENCES characters(id) ON DELETE CASCADE,
    category VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    value VARCHAR(255),
    note TEXT,
    display_type VARCHAR(50) DEFAULT 'simple',
    sort_order INTEGER DEFAULT 0
);

CREATE TABLE experience_history (
    id UUID PRIMARY KEY,
    character_id UUID REFERENCES characters(id) ON DELETE CASCADE,
    entry_type VARCHAR(50) NOT NULL, -- 'earned' or 'spent'
    change_amount INTEGER NOT NULL,
    reason TEXT,
    date DATE NOT NULL,
    unspent_after INTEGER,
    earned_after INTEGER
);

CREATE TABLE actions (
    id UUID PRIMARY KEY,
    game_id UUID REFERENCES games(id),
    character_id UUID REFERENCES characters(id) ON DELETE CASCADE,
    action_date DATE NOT NULL,
    action_type VARCHAR(100) NOT NULL,
    level INTEGER DEFAULT 0,
    unused INTEGER DEFAULT 0,
    total INTEGER DEFAULT 0,
    growth INTEGER DEFAULT 0,
    action_text TEXT,
    result_text TEXT
);

CREATE TABLE plots (
    id UUID PRIMARY KEY,
    game_id UUID REFERENCES games(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE rumors (
    id UUID PRIMARY KEY,
    game_id UUID REFERENCES games(id),
    title VARCHAR(255) NOT NULL,
    content TEXT,
    level INTEGER DEFAULT 1,
    category VARCHAR(50),
    rumor_date DATE NOT NULL,
    target_character_id UUID REFERENCES characters(id),
    target_race VARCHAR(50),
    target_group VARCHAR(100),
    target_influence VARCHAR(100)
);

CREATE TABLE items (
    id UUID PRIMARY KEY,
    game_id UUID REFERENCES games(id),
    name VARCHAR(255) NOT NULL,
    item_type VARCHAR(100),
    subtype VARCHAR(100),
    level INTEGER DEFAULT 0,
    bonus INTEGER DEFAULT 0,
    damage_type VARCHAR(50),
    damage_amount INTEGER DEFAULT 0,
    concealability VARCHAR(50),
    appearance TEXT,
    powers TEXT,
    data JSONB
);

CREATE TABLE locations (
    id UUID PRIMARY KEY,
    game_id UUID REFERENCES games(id),
    name VARCHAR(255) NOT NULL,
    location_type VARCHAR(100),
    level INTEGER DEFAULT 0,
    owner_id UUID REFERENCES characters(id),
    access TEXT,
    affinity VARCHAR(100),
    totem VARCHAR(255),
    security_traits INTEGER DEFAULT 0,
    security_retests INTEGER DEFAULT 0,
    gauntlet_shroud VARCHAR(50),
    where_description TEXT,
    appearance TEXT,
    security_description TEXT,
    umbra_description TEXT,
    links TEXT[]
);

-- Indexes for performance
CREATE INDEX idx_characters_game ON characters(game_id);
CREATE INDEX idx_characters_player ON characters(player_id);
CREATE INDEX idx_characters_race ON characters(race_type);
CREATE INDEX idx_traits_character ON traits(character_id);
CREATE INDEX idx_traits_category ON traits(category);
CREATE INDEX idx_actions_character ON actions(character_id);
CREATE INDEX idx_actions_date ON actions(action_date);
```

---

## 5. API Specifications

### 5.1 API Overview

**Base URL:** `http://localhost:8000/api/v1`

**Authentication:** Bearer token (JWT) for server mode, local auth for desktop

**Content-Type:** `application/json`

### 5.2 Character Endpoints

#### List Characters
```http
GET /characters
```

**Query Parameters:**
- `race` (optional): Filter by race type
- `player_id` (optional): Filter by player
- `is_npc` (optional): Filter NPCs
- `status` (optional): Filter by status
- `search` (optional): Text search on name
- `sort_by` (optional): Sort field (name, player, race, created_at)
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 50)

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "Character Name",
      "race_type": "vampire",
      "player_name": "Player Name",
      "is_npc": false,
      "status": "active",
      "xp_unspent": 15,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "page_size": 50
}
```

#### Get Character
```http
GET /characters/{character_id}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "Draven Blackwood",
  "player_id": "uuid",
  "race_type": "vampire",
  "is_npc": false,
  "status": "active",
  "xp_unspent": 15,
  "xp_earned": 145,
  "data": {
    "clan": "Toreador",
    "sect": "Camarilla",
    "generation": 10,
    "blood": {"permanent": 13, "temporary": 13},
    "path": "Humanity",
    "path_rating": 7
  },
  "traits": {
    "physical": [{"name": "Strength", "value": "3", "note": ""}],
    "social": [{"name": "Charisma", "value": "3", "note": ""}],
    "mental": [{"name": "Perception", "value": "3", "note": ""}],
    "disciplines": [{"name": "Auspex", "value": "2", "note": ""}],
    "backgrounds": [{"name": "Resources", "value": "3", "note": ""}]
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-20T15:45:00Z"
}
```

#### Create Character
```http
POST /characters
```

**Request Body:**
```json
{
  "name": "New Character",
  "player_id": "uuid",
  "race_type": "vampire",
  "is_npc": false,
  "data": {
    "clan": "Ventrue",
    "sect": "Camarilla",
    "generation": 11
  }
}
```

#### Update Character
```http
PUT /characters/{character_id}
```

#### Delete Character
```http
DELETE /characters/{character_id}
```

#### Update Traits
```http
PUT /characters/{character_id}/traits
```

**Request Body:**
```json
{
  "category": "disciplines",
  "traits": [
    {"name": "Celerity", "value": "3", "note": ""},
    {"name": "Fortitude", "value": "2", "note": ""}
  ]
}
```

#### Award XP
```http
POST /characters/{character_id}/xp
```

**Request Body:**
```json
{
  "amount": 5,
  "reason": "Attended game session",
  "date": "2024-01-20"
}
```

#### Spend XP
```http
POST /characters/{character_id}/xp/spend
```

**Request Body:**
```json
{
  "amount": 10,
  "reason": "Purchased Presence 3",
  "date": "2024-01-20"
}
```

### 5.3 Player Endpoints

```http
GET    /players
GET    /players/{player_id}
POST   /players
PUT    /players/{player_id}
DELETE /players/{player_id}
GET    /players/{player_id}/characters
```

### 5.4 Action/Plot/Rumor (APR) Endpoints

#### Actions
```http
GET    /actions
POST   /actions
GET    /actions/{action_id}
PUT    /actions/{action_id}
DELETE /actions/{action_id}
GET    /actions/by-date/{date}
```

#### Plots
```http
GET    /plots
POST   /plots
GET    /plots/{plot_id}
PUT    /plots/{plot_id}
DELETE /plots/{plot_id}
```

#### Rumors
```http
GET    /rumors
POST   /rumors
GET    /rumors/{rumor_id}
PUT    /rumors/{rumor_id}
DELETE /rumors/{rumor_id}
GET    /rumors/for-character/{character_id}
```

### 5.5 Query Endpoints

#### Execute Query
```http
POST /queries/execute
```

**Request Body:**
```json
{
  "name": "Active Vampires",
  "clauses": [
    {
      "field": "race_type",
      "operator": "equals",
      "value": "vampire"
    },
    {
      "field": "status",
      "operator": "equals",
      "value": "active"
    }
  ]
}
```

**Response:**
```json
{
  "name": "Active Vampires",
  "results": [
    {
      "id": "uuid",
      "name": "Character Name",
      "race_type": "vampire",
      "player_name": "Player Name"
    }
  ],
  "count": 45
}
```

#### Save Query
```http
POST /queries
```

#### List Saved Queries
```http
GET /queries
```

### 5.6 Report/Output Endpoints

#### Generate Report
```http
POST /reports/generate
```

**Request Body:**
```json
{
  "template": "character_sheet",
  "format": "html",
  "character_ids": ["uuid1", "uuid2"],
  "options": {
    "include_actions": true,
    "include_rumors": true,
    "include_history": false
  }
}
```

**Response:**
```json
{
  "report_id": "uuid",
  "status": "completed",
  "download_url": "/reports/uuid/download",
  "format": "html",
  "file_size": 45230
}
```

#### Get Available Templates
```http
GET /reports/templates
```

#### Preview Report
```http
POST /reports/preview
```

### 5.7 Import/Export Endpoints

#### Import Legacy File
```http
POST /imports/legacy
Content-Type: multipart/form-data
```

**Form Data:**
- `file`: Binary .gv3 file
- `options`: JSON string with import options

#### Export to Legacy Format
```http
POST /exports/legacy
```

**Request Body:**
```json
{
  "format": "gv3",
  "character_ids": ["uuid1", "uuid2"],
  "include_items": true,
  "include_locations": true
}
```

#### Export to JSON
```http
POST /exports/json
```

#### Export to PDF
```http
POST /exports/pdf
```

### 5.8 Configuration Endpoints

```http
GET    /config
PUT    /config
GET    /config/races
GET    /config/races/{race_type}/fields
GET    /config/health-levels
PUT    /config/health-levels
```

### 5.9 Statistics Endpoints

```http
GET /statistics/overview
GET /statistics/races
GET /statistics/traits
GET /statistics/xp-awards
GET /statistics/influences
```

### 5.10 WebSocket Endpoints (Real-time)

```
ws://localhost:8000/ws/updates
```

**Events:**
- `character_updated`
- `xp_awarded`
- `new_action_added`
- `new_rumor_added`

---

## 6. User Interface Requirements

### 6.1 Desktop Application Requirements

#### Main Window
- **MDI Interface:** Multiple document interface for managing multiple characters/plots
- **Navigation Panel:** Tree view for quick access to:
  - Characters (grouped by race)
  - Players
  - Actions by Date
  - Plots
  - Rumors
  - Items
  - Locations
  - Queries
  - Reports

#### Character Sheet Forms

**Layout:**
- Tabbed interface for different sections:
  - **Overview:** Core info, tempers, essential traits
  - **Traits:** Physical, Social, Mental with dot tallies
  - **Abilities & Powers:** Race-specific abilities
  - **Backgrounds:** Equipment, locations, backgrounds
  - **History:** XP history with filtering
  - **Notes:** Free-form text areas

**Visual Requirements:**
- Dot tallies for traits (●●●○○)
- Color coding by race (Vampire=Red, Werewolf=Brown, etc.)
- Drag-and-drop trait reordering
- Inline trait editing
- Auto-save on change

**Race-Specific Sections:**

| Race | Special Section |
|------|----------------|
| Vampire | Disciplines, Rituals, Blood Pool, Generation |
| Werewolf | Gifts, Rites, Rage, Gnosis, Renown |
| Mage | Spheres, Rotes, Arete, Quintessence, Paradox |
| Changeling | Arts, Realms, Glamour, Banality |
| Wraith | Arcanoi, Passions, Fetters, Shadow |
| Demon | Lores, Faith, Torment, Apocalyptic Form |

#### Player Management Form
- Player list with filtering
- Character assignment
- PP (Player Point) tracking
- Contact information

#### APR (Action/Plot/Rumor) Forms

**Action Form:**
- Date picker
- Character selector
- Action type dropdown (influence types)
- Level/Unused/Total/Growth fields
- Action text area (rich text)
- Result text area (rich text)

**Plot Form:**
- Title and description
- Status tracking (Active, Resolved, etc.)
- Linked characters
- Timeline of developments

**Rumor Form:**
- Content editor
- Level and category
- Distribution targeting (character, race, group, influence)

#### Query Builder
- Visual query builder
- Drag-and-drop clause composition
- Field selector with operators
- Live preview of results
- Save/load queries

#### Report Output
- Template selector
- Format options (HTML, PDF, Text)
- Preview pane
- Print dialog
- Email composition

#### Menu Editor
- Visual menu tree editor
- Drag-and-drop reordering
- Add/edit/delete menu items
- Link traits to menus
- Import/export menu files

### 6.2 Web Application Requirements

#### Responsive Design
- Desktop: Full sidebar + content layout
- Tablet: Collapsible sidebar
- Mobile: Bottom navigation, card-based layouts

#### Dashboard
- Game overview statistics
- Recent activity feed
- Quick actions (new character, quick search)
- Upcoming game dates

#### Character List View
- Table view with sorting/filtering
- Card grid view option
- Quick search
- Bulk actions (export, print, delete)
- Pagination

#### Character Detail View
- Read-only summary mode
- Edit mode with form validation
- Tabbed sections matching desktop
- Mobile-optimized forms

#### Mobile-Specific Features
- Touch-friendly trait tallies
- Swipe navigation between characters
- Quick XP award interface
- Camera integration for character portraits

### 6.3 UI/UX Standards

#### Accessibility
- WCAG 2.1 AA compliance
- Keyboard navigation support
- Screen reader compatibility
- High contrast mode
- Font size scaling

#### Localization
- i18n support for future translations
- Date/time format localization
- Number format localization

#### Theming
- Dark mode (default)
- Light mode
- Custom accent colors per game

---

## 7. Feature Requirements

### 7.1 Character Management (Priority: P0 - Critical)

| ID | Feature | Description | Acceptance Criteria |
|----|---------|-------------|---------------------|
| CM-001 | Create Character | Create new character with race selection | All 12 races supported, validation works |
| CM-002 | Edit Character | Modify character traits and data | Auto-save, validation, undo/redo |
| CM-003 | Delete Character | Remove character with confirmation | Soft delete with restore option |
| CM-004 | Duplicate Character | Copy existing character as template | Deep copy with rename prompt |
| CM-005 | Trait Management | Add/remove/edit traits | Dot tallies, categories, sorting |
| CM-006 | XP Tracking | Award and spend experience points | History maintained, calculations correct |
| CM-007 | Equipment Assignment | Assign items to characters | Equipment cards display correctly |
| CM-008 | Location Assignment | Assign locations (havens, etc.) | Location cards display correctly |

### 7.2 Player Management (Priority: P0)

| ID | Feature | Description | Acceptance Criteria |
|----|---------|-------------|---------------------|
| PM-001 | Player CRUD | Create, read, update, delete players | All CRUD operations functional |
| PM-002 | Character Linking | Associate characters with players | One-to-many relationship works |
| PM-003 | PP Tracking | Track Player Points for staff | History and current balance accurate |
| PM-004 | Contact Management | Store email, phone, address | Privacy controls implemented |

### 7.3 APR System (Priority: P0)

| ID | Feature | Description | Acceptance Criteria |
|----|---------|-------------|---------------------|
| APR-001 | Action Management | Create/edit actions per date | All action types supported |
| APR-002 | Plot Management | Track long-term storylines | Timeline view works |
| APR-003 | Rumor Management | Create and distribute rumors | All rumor categories functional |
| APR-004 | Calendar View | View actions/plots by date | Month/week views, filtering |
| APR-005 | Bulk Rumor Distribution | Send rumors to multiple targets | Filter by race, group, influence |

### 7.4 Query System (Priority: P1 - High)

| ID | Feature | Description | Acceptance Criteria |
|----|---------|-------------|---------------------|
| QY-001 | Query Builder | Visual query construction | All field types supported |
| QY-002 | Saved Queries | Save and load queries | Named queries persist |
| QY-003 | Default Queries | Pre-built common queries | All races have default queries |
| QY-004 | Complex Queries | Multi-clause queries with AND/OR | Boolean logic works correctly |
| QY-005 | Query Results | Display and export results | Sorting, filtering, export |

### 7.5 Report Generation (Priority: P1)

| ID | Feature | Description | Acceptance Criteria |
|----|---------|-------------|---------------------|
| RP-001 | Character Sheets | Generate formatted character sheets | All races have templates |
| RP-002 | Rosters | Player and character rosters | Grouping, sorting options |
| RP-003 | Action Reports | Action summaries by date/date range | Master action report works |
| RP-004 | Rumor Reports | Rumor distribution reports | Master rumor report works |
| RP-005 | Equipment Reports | Item and location cards | Formatted correctly for printing |
| RP-006 | Custom Reports | User-defined report templates | Template syntax documented |
| RP-007 | Export Formats | PDF, HTML, Text, RTF exports | All formats render correctly |
| RP-008 | Email Reports | Send reports via email | SMTP configuration works |

### 7.6 Import/Export (Priority: P0)

| ID | Feature | Description | Acceptance Criteria |
|----|---------|-------------|---------------------|
| IE-001 | Import GV3 | Import legacy .gv3 files | All data imports correctly |
| IE-002 | Import GVM | Import menu files | Menu structure preserved |
| IE-003 | Import GEX | Import exchange files | Partial imports work |
| IE-004 | Export GV3 | Export to legacy format | Files open in original Grapevine |
| IE-005 | Export JSON | Modern JSON export | Schema documented |
| IE-006 | Export XML | XML export for interoperability | Valid XML output |
| IE-007 | Merge Games | Combine two game files | Conflict resolution UI works |
| IE-008 | Duplicate Detection | Find potential duplicates | Fuzzy matching works |

### 7.7 Menu System (Priority: P1)

| ID | Feature | Description | Acceptance Criteria |
|----|---------|-------------|---------------------|
| MS-001 | Menu Editor | Visual menu configuration | Add, edit, delete, reorder items |
| MS-002 | Trait Linking | Link menu items to traits | Selections populate correctly |
| MS-003 | Import Menus | Load .gvm files | Menu files import correctly |
| MS-004 | Multiple Menus | Support for alternate menu sets | Dark Ages, custom menus work |
| MS-005 | Menu Export | Save menus to .gvm | Files compatible with legacy app |

### 7.8 Statistics (Priority: P2 - Medium)

| ID | Feature | Description | Acceptance Criteria |
|----|---------|-------------|---------------------|
| ST-001 | Overview Stats | Game-wide statistics dashboard | Numbers accurate |
| ST-002 | Race Distribution | Character counts by race | Charts display correctly |
| ST-003 | Trait Statistics | Most common traits, averages | Sums, maxima, distributions |
| ST-004 | XP Statistics | XP awards and spending trends | Charts over time |
| ST-005 | Influence Analysis | Influence distribution report | All influence types covered |

### 7.9 Configuration (Priority: P1)

| ID | Feature | Description | Acceptance Criteria |
|----|---------|-------------|---------------------|
| CF-001 | Game Settings | Game name, email, website | Settings persist |
| CF-002 | Health Levels | Customizable health levels | Default and custom configs |
| CF-003 | XP Awards | Standard XP award definitions | Template awards work |
| CF-004 | Template Management | Add/edit output templates | Template syntax validation |
| CF-005 | Backup/Restore | Automatic and manual backups | Scheduled backups work |

### 7.10 Collaboration (Priority: P3 - Low, Future)

| ID | Feature | Description | Acceptance Criteria |
|----|---------|-------------|---------------------|
| CL-001 | Multi-User Mode | Server mode for multiple users | Concurrent access works |
| CL-002 | Role-Based Access | Admin, storyteller, player roles | Permissions enforced |
| CL-003 | Audit Log | Track all changes | Immutable log |
| CL-004 | Change Notifications | Real-time updates | WebSocket updates work |
| CL-005 | Conflict Resolution | Handle concurrent edits | Last-write-wins with notification |

---

## 8. Migration Strategy

### 8.1 Data Migration Approach

#### Phase 1: File Format Analysis (Week 1)
1. **Binary Format Analysis**
   - Document .gv3 file structure
   - Identify all data blocks and headers
   - Map legacy data types to Python types
   - Create test corpus of sample files

2. **XML Format Support**
   - Review existing XML export format
   - Enhance schema if needed
   - Implement bidirectional XML conversion

#### Phase 2: Legacy Parsers (Weeks 2-3)
1. **Implement GV3 Parser**
   ```python
   class GV3Parser:
       def parse(self, file_path: Path) -> Game
       def export(self, game: Game, file_path: Path)
   ```

2. **Implement GVM Parser**
   ```python
   class GVMParser:
       def parse(self, file_path: Path) -> MenuSet
       def export(self, menu_set: MenuSet, file_path: Path)
   ```

3. **Implement GEX Parser**
   ```python
   class GEXParser:
       def parse(self, file_path: Path) -> ExchangeData
       def export(self, data: ExchangeData, file_path: Path)
   ```

#### Phase 3: Data Validation (Week 4)
1. Create migration test suite
2. Compare parsed data with original application
3. Validate all character types
4. Test round-trip conversion (import → export → compare)

### 8.2 Application Migration Phases

#### Phase 1: Backend Foundation (Weeks 1-6)
1. **Project Setup**
   - Repository structure
   - CI/CD pipeline
   - Testing framework
   - Documentation skeleton

2. **Core Models**
   - Base character model
   - All 12 race-specific models
   - Player, Game, APR models
   - SQLAlchemy mappings

3. **Data Layer**
   - SQLite implementation
   - Repository pattern
   - Migration system (Alembic)

4. **Legacy Support**
   - File parsers
   - Import/export service
   - Conversion utilities

#### Phase 2: API Development (Weeks 7-10)
1. **API Foundation**
   - FastAPI application setup
   - Authentication/authorization
   - Error handling
   - API documentation (OpenAPI)

2. **Endpoint Implementation**
   - Character endpoints (CRUD)
   - Player endpoints
   - APR endpoints
   - Query endpoints
   - Report endpoints
   - Import/export endpoints

3. **Business Logic**
   - Character service
   - XP calculation service
   - Query engine
   - Template engine

#### Phase 3: Desktop UI (Weeks 11-18)
1. **UI Framework**
   - PyQt6 application shell
   - Theming system
   - Navigation framework

2. **Character Forms**
   - Base character sheet
   - All 12 race-specific sheets
   - Trait editing widgets
   - Dot tally controls

3. **Management Forms**
   - Player management
   - APR management
   - Query builder
   - Report output
   - Menu editor

#### Phase 4: Web UI (Weeks 15-22)
1. **Frontend Setup**
   - React/Vue application
   - API client generation
   - Component library

2. **Core Views**
   - Dashboard
   - Character list/detail
   - Player management
   - APR views
   - Query interface

3. **Responsive Design**
   - Mobile optimization
   - Touch controls
   - Offline support (PWA)

#### Phase 5: Testing & Polish (Weeks 23-26)
1. **Testing**
   - Unit tests (90%+ coverage)
   - Integration tests
   - End-to-end tests
   - User acceptance testing

2. **Documentation**
   - User manual
   - API documentation
   - Migration guide
   - Developer docs

3. **Performance Optimization**
   - Query optimization
   - Caching implementation
   - Lazy loading

### 8.3 Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Legacy format incompatibility | Extensive testing with diverse .gv3 files |
| Data loss during migration | Backup warnings, dry-run mode, validation |
| Performance issues with large games | Pagination, database indexing, caching |
| UI complexity for 12 races | Component reuse, template-driven forms |
| API breaking changes | Versioning strategy from day one |

### 8.4 Rollback Plan

1. **Maintain Legacy Compatibility**
   - Always export to .gv3 format
   - Keep original files untouched
   - Parallel testing during development

2. **Phased Rollout**
   - Beta testing with select games
   - Import-only mode initially
   - Export verification before full cutover

---

## 9. Security and Data Protection

### 9.1 Authentication & Authorization

**Desktop Mode:**
- Local file-based authentication (optional)
- File encryption at rest (optional password)

**Server Mode:**
- JWT-based authentication
- Role-based access control (RBAC):
  - **Admin:** Full access, user management
  - **Storyteller:** Character edit, APR management
  - **Player:** Own character view/edit (if enabled)
  - **Read-Only:** View only access

### 9.2 Data Protection

- **Encryption at Rest:** AES-256 for database files
- **Encryption in Transit:** TLS 1.3 for API
- **Sensitive Data:** Email/phone encryption
- **Backups:** Encrypted backup files

### 9.3 Input Validation

- SQL injection prevention (parameterized queries)
- XSS prevention (output encoding)
- File upload validation (type, size, content)
- Rate limiting on API endpoints

### 9.4 Audit Logging

- All data modifications logged
- User actions tracked
- Failed authentication attempts
- Export/download tracking

---

## 10. Testing and Quality Assurance

### 10.1 Testing Strategy

#### Unit Tests
- **Target:** 90%+ code coverage
- **Tools:** pytest, pytest-cov
- **Scope:** Models, services, utilities
- **Mocking:** Database, file system, external APIs

#### Integration Tests
- **API Tests:** FastAPI test client
- **Database Tests:** SQLite in-memory, PostgreSQL test container
- **File I/O Tests:** Temp files, round-trip validation
- **Tools:** pytest-asyncio, httpx

#### End-to-End Tests
- **Desktop:** pytest-qt for PyQt
- **Web:** Playwright or Cypress
- **Critical Paths:** Character CRUD, import/export, reports

#### Compatibility Tests
- **Operating Systems:** Windows 10/11, macOS 12+, Ubuntu 22.04
- **Browsers:** Chrome, Firefox, Safari, Edge (latest 2 versions)
- **File Formats:** Legacy .gv3 files from various sources

### 10.2 Test Data

- **Sample Games:** Create test corpus from original VB6
- **Edge Cases:** Empty games, 1000+ characters, all races
- **Legacy Files:** Real-world .gv3 files (anonymized)

### 10.3 Quality Metrics

- **Code Coverage:** ≥90%
- **Type Coverage:** 100% (strict mypy)
- **Documentation:** All public APIs documented
- **Performance:** <500ms for character load, <2s for reports

### 10.4 User Acceptance Testing

- **Beta Program:** 5-10 existing Grapevine users
- **Test Scenarios:**
  1. Import existing .gv3 game
  2. Create new characters for all races
  3. Manage actions/plots/rumors
  4. Generate and print reports
  5. Export and share data
- **Feedback Collection:** Structured surveys, issue tracking

---

## 11. Success Criteria

### 11.1 Functional Success

1. **Feature Completeness:** 100% of VB6 Grapevine v3.0.1 features implemented
2. **Data Integrity:** 100% of legacy data imports correctly
3. **Race Support:** All 12 character types fully functional
4. **Export Compatibility:** Files open in original Grapevine

### 11.2 Technical Success

1. **Performance:** 10x faster than VB6 version
2. **Reliability:** <0.1% crash rate
3. **Compatibility:** Runs on Windows, macOS, Linux
4. **Maintainability:** Clean architecture, documented code

### 11.3 User Success

1. **Usability:** Users can complete core tasks without documentation
2. **Satisfaction:** NPS score >50
3. **Adoption:** 80% of beta users switch to new version
4. **Productivity:** 20% faster character management

### 11.4 Business Success

1. **Timeline:** Delivered within 6 months
2. **Budget:** Within allocated resources
3. **Technical Debt:** Zero critical issues at launch
4. **Future-Proof:** Plugin system enables extensibility

---

## 12. Timeline and Milestones

### 12.1 Project Timeline (26 Weeks)

```
Week  1-3:  Phase 1 - Foundation & Analysis
Week  4-6:  Phase 2 - Backend Core
Week  7-10: Phase 3 - API Development
Week 11-18: Phase 4 - Desktop UI
Week 15-22: Phase 5 - Web UI (parallel with Desktop)
Week 23-24: Phase 6 - Integration & Testing
Week 25-26: Phase 7 - Documentation & Launch
```

### 12.2 Milestones

| Milestone | Date | Deliverables | Success Criteria |
|-----------|------|--------------|------------------|
| **M1: Foundation** | Week 3 | Project setup, data models, parsers | All models defined, can parse .gv3 |
| **M2: Backend Core** | Week 6 | Database layer, business logic | All CRUD operations working |
| **M3: API Complete** | Week 10 | REST API, all endpoints | API documentation complete, tests pass |
| **M4: Desktop Alpha** | Week 14 | Character forms, basic UI | Can create/edit all races |
| **M5: Desktop Beta** | Week 18 | Full feature parity | All VB6 features implemented |
| **M6: Web Alpha** | Week 18 | Web UI core features | Character management works in browser |
| **M7: Web Beta** | Week 22 | Full web feature set | Desktop parity achieved |
| **M8: Integration** | Week 24 | All components integrated | End-to-end tests pass |
| **M9: Release Ready** | Week 26 | Documentation, installers | Ready for public release |

### 12.3 Resource Allocation

| Role | Effort | Responsibilities |
|------|--------|------------------|
| Project Lead | 100% | Architecture, coordination, review |
| Backend Engineer | 100% | API, database, business logic |
| Desktop UI Developer | 100% | PyQt6 application |
| Web UI Developer | 100% | React/Vue frontend |
| QA Engineer | 75% | Testing, automation, validation |
| Technical Writer | 50% | Documentation, user guides |

---

## 13. Appendices

### Appendix A: Glossary

- **APR:** Actions, Plots, Rumors system
- **Grapevine:** Original VB6 LARP management application
- **GV3:** Legacy game file format (Grapevine 3.x)
- **GVM:** Menu configuration file format
- **GEX:** Data exchange file format
- **LARP:** Live Action Role-Play
- **PP:** Player Points (staff experience system)
- **XP:** Experience Points (character advancement)

### Appendix B: Race-Specific Fields Reference

| Race | Unique Fields |
|------|--------------|
| Vampire | Clan, Sect, Generation, Blood, Path, Disciplines, Rituals |
| Werewolf | Tribe, Breed, Auspice, Rank, Pack, Rage, Gnosis, Gifts, Rites, Renown |
| Mage | Tradition, Essence, Arete, Quintessence, Paradox, Spheres, Rotes, Foci |
| Changeling | Kith, Seeming, Court, Glamour, Banality, Arts, Realms, Legacies |
| Wraith | Guild, Legion, Pathos, Corpus, Arcanoi, Passions, Fetters, Shadow |
| Mummy | Amenti, Sekhem, Balance, Ba, Ka, Hekau |
| Kuei-Jin | Dharma, Direction, Hun, Po, Yin Chi, Yang Chi, Demon Chi |
| Fera | Fera Type, Breed, Auspice, Rank, Gifts, Rites |
| Hunter | Creed, Camp, Conviction, Mercy, Vision, Zeal, Edges |
| Demon | House, Faction, Faith, Torment, Lores, Apocalyptic Form |
| Various | Class, Subclass, Affinity, Plane, Brood |
| Mortal | Motivation, Association, Humanity, Numina |

### Appendix C: Legacy File Format Specifications

#### GV3 File Structure
```
Header (16 bytes):
  - Magic: "GVBG" (4 bytes)
  - Version: Float (4 bytes)
  - Reserved: 8 bytes

Data Sections (sequential):
  - Game Info Section
  - Player List Section
  - Character List Section
  - Item List Section
  - Rote List Section
  - Location List Section
  - Menu Set Section
  - Query Engine Section
  - APR Engine Section
  - Calendar Section
  - Template List Section
```

### Appendix D: API Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| 1001 | Invalid character ID | 404 |
| 1002 | Invalid race type | 400 |
| 1003 | Character name required | 400 |
| 2001 | Invalid player ID | 404 |
| 3001 | Invalid action ID | 404 |
| 4001 | Import format error | 400 |
| 4002 | Legacy file corrupted | 422 |
| 5001 | Template not found | 404 |
| 5002 | Report generation failed | 500 |
| 9001 | Unauthorized | 401 |
| 9002 | Forbidden | 403 |

### Appendix E: Template Syntax Reference

#### Field Tags
```
[fieldname]           - Insert field value
[#fieldname]          - Insert count of items
[+fieldname]          - Advance trait list cursor
[Tally X Y]           - Generate dot tally for tempers
```

#### Conditionals
```
[?field value]...[/?] - Include if field equals value
[!field value]...[/!] - Exclude if field equals value
[option type]...[/option] - Include section if condition met
```

#### Loops
```
[repeat]...[repeat]   - Iterate through trait list
[report type]...[/report] - Sub-report for related data
```

#### Formatting
```
[divider X]           - Insert separator X between items
[dateformat format]   - Set date format
[pagebreak]           - Page break for printing
```

### Appendix F: Dependencies

#### Backend
```
fastapi>=0.104.0
sqlalchemy>=2.0.0
pydantic>=2.5.0
alembic>=1.12.0
uvicorn>=0.24.0
python-multipart>=0.0.6
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
jinja2>=3.1.0
reportlab>=4.0.0
openpyxl>=3.1.0
structlog>=23.0.0
```

#### Desktop
```
PyQt6>=6.6.0
qt-material>=2.14.0
requests>=2.31.0
```

#### Web Frontend
```
react>=18.2.0
@tanstack/react-query>=5.0.0
axios>=1.6.0
react-hook-form>=7.48.0
zod>=3.22.0
tailwindcss>=3.3.0
```

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-13 | AI Assistant | Initial PRD creation |

---

**End of Document**
