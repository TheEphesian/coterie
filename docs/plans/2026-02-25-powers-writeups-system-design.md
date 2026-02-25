# Powers & Writeups System - Design Document

## Goal

Create a data system for storing game powers (disciplines, rituals, merits, flaws, backgrounds, abilities) with full writeups from source books. Support multiple source books per power with selectable writeups per chronicle.

## Architecture

A **Power** is an abstract game element (e.g., "Feral Whispers" — Animalism Basic). A **PowerWriteup** is a specific source book's description of that power. Each power can have multiple writeups from different books. Chronicles can override which writeup is active for any given power.

Data flows: PDF/Markdown source → JSON extraction file → DB import → UI display.

## Tech Stack

- SQLAlchemy ORM models (consistent with existing Coterie models)
- JSON data files for extracted content (intermediate format, importable)
- Python PDF extraction via pymupdf for initial LotN extraction
- PyQt6 UI integration (future — not in this phase)

## Data Model

### PowerCategory

Classifies powers into types.

| Column | Type | Notes |
|--------|------|-------|
| id | int PK | |
| name | str(50) | "Discipline", "Merit", "Flaw", "Ritual", "Background", "Ability", "Thaumaturgy Path", "Necromancy Path" |

### Power

A single game power/trait.

| Column | Type | Notes |
|--------|------|-------|
| id | int PK | |
| name | str(200) | e.g., "Feral Whispers", "Eat Food", "Allies" |
| category_id | FK(PowerCategory) | |
| power_type | str(100) | Grouping within category: "Animalism", "Physical", "Supernatural", etc. |
| level_tier | str(50), nullable | "Basic", "Intermediate", "Advanced", null for merits/flaws |
| level_order | int, default 1 | Sort order within tier (1st Basic, 2nd Basic, etc.) |
| trait_cost | int, nullable | For Merits/Flaws: 1-7 Traits |
| prerequisites | str, nullable | Free text: "Intermediate Animalism" |
| retest_ability | str(50), nullable | "Animal Ken", "Occult", etc. |
| clans | str(500), nullable | Comma-separated: "Gangrel,Nosferatu,Ravnos,Tzimisce" |

### PowerWriteup

A source book's description of a power.

| Column | Type | Notes |
|--------|------|-------|
| id | int PK | |
| power_id | FK(Power) | |
| source_book | str(200) | "Laws of the Night Revised" |
| page_number | int | |
| description | text | Full rules text |
| system_text | text, nullable | Mechanical rules (if separable from flavor) |
| is_default | bool, default False | True = default writeup when no chronicle preference set |

### ChronicleWriteupPreference

Per-chronicle override for which writeup to use.

| Column | Type | Notes |
|--------|------|-------|
| chronicle_id | FK(Chronicle) | Composite PK |
| power_id | FK(Power) | Composite PK |
| writeup_id | FK(PowerWriteup) | Selected writeup |

## JSON Data File Structure

Extracted data lives in `src/data/powers/` as JSON files, one per source book:

```
src/data/powers/
├── laws_of_the_night_revised.json
├── sabbat_guide.json  (future)
└── ...
```

### Format: `laws_of_the_night_revised.json`

```json
{
  "source_book": "Laws of the Night Revised",
  "disciplines": {
    "Animalism": {
      "clans": ["Gangrel", "Nosferatu", "Ravnos", "Tzimisce"],
      "retest_ability": "Animal Ken",
      "powers": [
        {
          "name": "Feral Whispers",
          "tier": "Basic",
          "order": 1,
          "page": 122,
          "description": "Full flavor + rules text here...",
          "system": "Mechanical rules portion if separable..."
        },
        {
          "name": "Beckoning",
          "tier": "Basic",
          "order": 2,
          "page": 122,
          "description": "...",
          "system": "..."
        }
      ]
    }
  },
  "thaumaturgy_paths": {
    "Path of Blood": {
      "retest_ability": "Occult",
      "powers": [
        {
          "name": "A Taste for Blood",
          "tier": "Basic",
          "order": 1,
          "page": 161,
          "description": "...",
          "system": "..."
        }
      ]
    }
  },
  "necromancy_paths": {
    "Sepulchre Path": {
      "retest_ability": "Occult",
      "powers": [...]
    }
  },
  "rituals": {
    "Thaumaturgy": [
      {
        "name": "Ritual Name",
        "tier": "Basic",
        "page": 170,
        "description": "...",
        "system": "..."
      }
    ],
    "Necromancy": [...]
  },
  "merits": {
    "Physical": [
      {
        "name": "Eat Food",
        "trait_cost": 1,
        "page": 103,
        "description": "Perhaps you developed this capacity..."
      }
    ],
    "Mental": [...],
    "Social": [...],
    "Supernatural": [...]
  },
  "flaws": {
    "Physical": [...],
    "Mental": [...],
    "Social": [...],
    "Supernatural": [...]
  },
  "backgrounds": [
    {
      "name": "Allies",
      "page": 67,
      "description": "Mortal confederates and aides..."
    }
  ],
  "abilities": [
    {
      "name": "Academics",
      "page": 80,
      "description": "...",
      "focusing_required": false
    }
  ]
}
```

## Import Flow

1. JSON file is read by a data loader utility
2. For each entry, find-or-create `Power` + `PowerWriteup`
3. First import sets `is_default=True` on all writeups
4. Subsequent imports from other books create additional `PowerWriteup` rows with `is_default=False`

## Future Features (Not This Phase)

- **XP Cost Calculator**: Powers will gain `xp_cost_creation` and `xp_cost_upgrade` columns. Character creation vs. XP purchase costs differ (e.g., disciplines are free at creation, 3/5/7/10 XP to buy later). A radio toggle on the sheet will mark traits as "bought at creation" vs "bought with XP".
- **XP Granting System**: Automated monthly XP grants with graduated levels (0-100 earned = 10/grant, 101-200 = 8/grant). Manual override capability.
- **UI Integration**: Power browser dialog, writeup viewer with source book selector dropdown, character sheet integration with power descriptions on hover/click.
- **Ritual Support**: Rituals extracted alongside disciplines, stored as separate PowerCategory.

## Implementation Scope (This Phase)

1. Create SQLAlchemy models: `PowerCategory`, `Power`, `PowerWriteup`, `ChronicleWriteupPreference`
2. Create JSON data directory structure
3. Extract ALL disciplines from LotN PDF → JSON (including Thaumaturgy paths, rituals)
4. Extract ALL merits & flaws from LotN PDF → JSON
5. Extract backgrounds and abilities from LotN PDF → JSON
6. Create import utility to load JSON → DB
7. Update CLAUDE.md / project documentation
