# Coterie - MET LARP Character Manager

## Project Overview
Coterie is a desktop application for managing Mind's Eye Theater (MET) LARP characters, chronicles, and game data. Built with PyQt6 for the UI and SQLAlchemy for data persistence.

## Tech Stack
- Python 3.14
- PyQt6 (desktop UI)
- SQLAlchemy ORM (database)
- SQLite (storage)
- FastAPI (optional REST API)

## Project Structure
```
src/
├── api/           # FastAPI routes (characters, players, boons, APR, imports)
├── characters/    # WoD character type definitions
├── core/
│   ├── engine.py  # DB engine, get_session(), init_db()
│   └── models/    # SQLAlchemy ORM models
│       ├── character.py   # Base Character (polymorphic)
│       ├── vampire.py     # Vampire subclass
│       ├── chronicle.py   # Chronicle + GameSession
│       ├── player.py      # Player
│       ├── staff.py       # Staff
│       ├── larp_trait.py  # LarpTrait + TraitCategory (MET adjective system)
│       ├── power.py       # Power + PowerWriteup + PowerCategory + ChronicleWriteupPreference
│       └── ...
├── ui/
│   ├── main_window.py            # Main application window
│   ├── dialogs/                  # Character creation, chronicle creation, staff manager
│   ├── sheets/vampire_sheet.py   # Vampire character sheet
│   └── widgets/                  # Reusable widgets (LarpTraitWidget, etc.)
├── utils/
│   ├── data_loader.py        # Grapevine import, character loading
│   ├── trait_converter.py    # MET trait adjective conversion
│   ├── power_extractor.py    # PDF → JSON extraction for game data
│   └── power_importer.py     # JSON → DB import for game data
├── data/
│   ├── trait_adjectives.json              # Canonical MET trait lists
│   └── powers/
│       └── laws_of_the_night_revised.json # All LotN disciplines, merits, flaws, etc.
└── legacy/        # Grapevine file parsers (.gex, .gv3, .gvm)
```

## Key Architecture Decisions

### MET Trait System
Characters use adjective-based traits (e.g., "Brawny", "Quick") rather than numeric values. Each trait level is a separate LarpTrait record. Abilities are a flat list (not split into Talents/Skills/Knowledges -- that's tabletop VtM, not MET).

### Powers & Writeups System
Game powers (disciplines, merits, flaws, rituals, etc.) are stored in the `Power` table. Each power can have multiple `PowerWriteup` records from different source books. Chronicles can set per-power writeup preferences via `ChronicleWriteupPreference`.

Data flow: PDF/Markdown source -> `power_extractor.py` -> JSON file -> `power_importer.py` -> Database

### Adding a New Source Book
1. Create JSON file in `src/data/powers/<book_name>.json` following the existing format
2. Run: `from src.utils.power_importer import import_powers_from_json; import_powers_from_json('path/to/file.json', set_as_default=False)`
3. Existing powers get additional writeups; new powers are created automatically

### Chronicle -> Player FK
Chronicles link to an HST via `storyteller_id` FK to `Player`. The `narrator` text field provides quick display access. Creating a chronicle auto-creates a Player record if one doesn't exist for the HST name.

## Database
- SQLite file at `~/.coterie/coterie.db` (Linux) or `%APPDATA%/Coterie/coterie.db` (Windows)
- `init_db()` in `engine.py` drops and recreates all tables (development mode)
- Sync SQLAlchemy (not async) for UI; async sessions available for API

## Running
```bash
python run_ui.py          # Launch desktop UI
python -m uvicorn src.api.main:app  # Launch API server
```

## Future Features Roadmap
- **XP Cost Calculator**: Powers will gain xp_cost_creation and xp_cost_upgrade columns. Character creation vs XP purchase costs differ. A toggle on the sheet marks traits as "bought at creation" vs "bought with XP".
- **Automated XP Granting**: Monthly XP grants with graduated levels (0-100 earned = 10/grant, 101-200 = 8/grant). Manual override. Configurable schedule per chronicle.
- **UI Power Browser**: Dialog for browsing/selecting powers with writeup viewer and source book selector dropdown.
- **Additional Source Books**: Import data from Sabbat Guide, Camarilla Guide, etc. via Markdown extraction.
- **Non-Vampire Sheets**: Character sheets for Werewolf, Mage, etc. (currently shows "Not Implemented").

## Reference Materials
- `docs/LawsOfTheNightRevised.pdf` -- Primary rules reference (252 pages)
- `docs/plans/` -- Design documents and implementation plans
