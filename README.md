# Coterie (Grapevine Modern)

A modern Python implementation of the Grapevine LARP character management system.

**Merged from:** Coterie UI + Grapevine-Modern API  
**Date:** February 21, 2026

## Features

- **Desktop UI:** PyQt6-based character management interface
- **REST API:** FastAPI backend for integrations
- **12 Character Types:** Vampire, Werewolf, Mage, Changeling, Wraith, Mummy, Kuei-Jin, Fera, Hunter, Demon, Mortal, Various
- **LARP Traits:** Mind's Eye Theater adjective-based trait system
- **Legacy Support:** Import from .gv3, .gvm, .gex files
- **Cross-Platform:** Windows, macOS, Linux

## Quick Start

```bash
# Setup
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run Desktop UI
python run_ui.py

# Run API (in another terminal)
uvicorn src.api.main:app --reload
```

## Project Structure

```
Coterie/
├── src/
│   ├── api/              # FastAPI REST API
│   ├── core/
│   │   ├── models/       # SQLAlchemy database models
│   │   ├── config.py     # Configuration
│   │   └── engine.py     # Database engine (sync for UI)
│   ├── characters/       # Race-specific character classes
│   ├── legacy/           # Legacy file parsers (GV3, GVM, GEX)
│   ├── ui/               # PyQt6 desktop UI
│   │   ├── main_window.py
│   │   ├── sheets/       # Character sheets
│   │   ├── dialogs/      # Dialogs
│   │   └── widgets/      # UI widgets
│   └── utils/            # Utilities
├── tests/                # Test suite
├── migrations/           # Alembic migrations
├── archive/              # Legacy VB6 source & sample data
└── docs/                 # Documentation
```

## Entry Points

| Command | Description |
|---------|-------------|
| `python run_ui.py` | Launch desktop UI |
| `uvicorn src.api.main:app --reload` | Start REST API |
| `pytest` | Run tests |
| `alembic upgrade head` | Apply migrations |

## Current Status

| Component | Status | Notes |
|-----------|--------|-------|
| Desktop UI | ✅ Working | Vampire sheet, character creation, import dialog |
| REST API | ⚠️ Partial | Models need primary keys added |
| Database Models | ✅ Working | Coterie-style polymorphic models |
| Character Races | ✅ Complete | 12 race types implemented |
| Legacy Parsers | ⚠️ Framework | Structure in place, needs completion |
| LARP Traits | ✅ Working | Adjective-based trait system |

## API Endpoints (When Fixed)

- `GET /api/v1/characters` - List characters
- `POST /api/v1/characters` - Create character
- `GET /api/v1/players` - List players
- `POST /api/v1/imports/legacy` - Import legacy files

API docs available at http://localhost:8000/docs when running.

## Documentation

- `docs/Grapevine-Migration-PRD.md` - Full requirements document
- `docs/MIGRATION_PLAN.md` - This merge's plan
- `archive/` - VB6 source code and sample data files

## Legacy File Support

| Format | Description | Status |
|--------|-------------|--------|
| .gv3 | Game database files | Parser framework |
| .gvm | Menu files | Parser framework |
| .gex | Character export | Parser framework |

## Merged From

- **Coterie** (original) - PyQt6 UI, LARP traits, vampire sheet
- **Grapevine-Modern** - FastAPI backend, 12 race classes, tests

## License

MIT License
