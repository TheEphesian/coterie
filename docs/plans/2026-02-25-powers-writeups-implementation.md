# Powers & Writeups System Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create DB models for game powers with multi-source writeups, extract all disciplines/merits/flaws/rituals from Laws of the Night Revised PDF into JSON, and build an import utility.

**Architecture:** SQLAlchemy models define the Power/PowerWriteup/ChronicleWriteupPreference schema. A Python extraction script reads the LotN PDF (via pymupdf) and writes structured JSON. An import utility loads JSON into the DB. The JSON files serve as the canonical data source and can be version-controlled.

**Tech Stack:** Python 3.14, SQLAlchemy ORM, pymupdf (fitz), PyQt6 (future UI), SQLite

**Reference:** `docs/LawsOfTheNightRevised.pdf`, `docs/plans/2026-02-25-powers-writeups-system-design.md`

---

### Task 1: Create Power System SQLAlchemy Models

**Files:**
- Create: `src/core/models/power.py`
- Modify: `src/core/models/__init__.py`

**Step 1: Create the models file**

```python
"""Power and writeup models for game rules data."""

from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, Boolean, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.models.base import Base

if TYPE_CHECKING:
    from .chronicle import Chronicle


class PowerCategory(Base):
    """Category of power (Discipline, Merit, Flaw, Ritual, etc.)."""
    __tablename__ = "power_categories"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

    powers: Mapped[List["Power"]] = relationship("Power", back_populates="category")

    def __repr__(self) -> str:
        return f"<PowerCategory {self.name}>"


class Power(Base):
    """A game power, trait, merit, flaw, or ability."""
    __tablename__ = "powers"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    category_id: Mapped[int] = mapped_column(ForeignKey("power_categories.id"))
    power_type: Mapped[str] = mapped_column(String(100))
    level_tier: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    level_order: Mapped[int] = mapped_column(Integer, default=1)
    trait_cost: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    prerequisites: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retest_ability: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    clans: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    category: Mapped["PowerCategory"] = relationship("PowerCategory", back_populates="powers")
    writeups: Mapped[List["PowerWriteup"]] = relationship("PowerWriteup", back_populates="power")

    def __repr__(self) -> str:
        return f"<Power {self.name} ({self.power_type})>"


class PowerWriteup(Base):
    """A source book's description of a power."""
    __tablename__ = "power_writeups"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    power_id: Mapped[int] = mapped_column(ForeignKey("powers.id"))
    source_book: Mapped[str] = mapped_column(String(200))
    page_number: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(Text)
    system_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    power: Mapped["Power"] = relationship("Power", back_populates="writeups")

    def __repr__(self) -> str:
        return f"<PowerWriteup {self.power.name} from {self.source_book} p.{self.page_number}>"


class ChronicleWriteupPreference(Base):
    """Per-chronicle override for which writeup to use for a power."""
    __tablename__ = "chronicle_writeup_preferences"
    __table_args__ = {'extend_existing': True}

    chronicle_id: Mapped[int] = mapped_column(ForeignKey("chronicles.id"), primary_key=True)
    power_id: Mapped[int] = mapped_column(ForeignKey("powers.id"), primary_key=True)
    writeup_id: Mapped[int] = mapped_column(ForeignKey("power_writeups.id"))

    writeup: Mapped["PowerWriteup"] = relationship("PowerWriteup")
```

**Step 2: Register models in `__init__.py`**

Add to `src/core/models/__init__.py`:

```python
from .power import PowerCategory, Power, PowerWriteup, ChronicleWriteupPreference
```

And add to `__all__`.

**Step 3: Verify**

Run: `python -c "from src.core.models.power import Power, PowerWriteup, PowerCategory; print('OK')"`

**Step 4: Commit**

```bash
git add -A
git commit -m "feat: add Power, PowerWriteup, PowerCategory models for rules data system"
```

---

### Task 2: Create JSON Data Directory and Extraction Script

**Files:**
- Create: `src/data/powers/` directory
- Create: `src/utils/power_extractor.py`

**Step 1: Create directory**

```bash
mkdir -p src/data/powers
```

**Step 2: Create the extraction script**

Create `src/utils/power_extractor.py` — a utility that reads the LotN PDF and outputs structured JSON. This script uses pymupdf to extract text page by page, then parses discipline/merit/flaw/ability/background entries.

The script should:
1. Open the PDF with `fitz.open()`
2. Extract text from the discipline pages (122-175)
3. Parse each discipline's powers (name, tier, description, page number)
4. Extract merits (pages 103-109) with trait costs
5. Extract flaws (pages 103-109) with trait costs
6. Extract backgrounds (pages 86-96)
7. Extract abilities (pages 80-85)
8. Write everything to `src/data/powers/laws_of_the_night_revised.json`

The extraction should be conservative — better to include too much text than too little. Full writeup text including system/mechanics. Page numbers from the PDF page index.

Key parsing approach for disciplines:
- Each discipline section starts with the discipline name as a header
- Powers within are prefixed by their tier: "Basic [Discipline]", "Intermediate [Discipline]", "Advanced [Discipline]"
- Individual power names appear as bold/distinct lines followed by description paragraphs
- The description continues until the next power name or discipline section

Key parsing approach for merits/flaws:
- Format: "Name (N Trait Merit/Flaw)" followed by description text
- Category headers: "Physical Merits and Flaws", "Mental Merits and Flaws", etc.

**Step 3: Commit**

```bash
git add -A
git commit -m "feat: add power extraction script for LotN PDF"
```

---

### Task 3: Extract Disciplines from LotN PDF

**Files:**
- Create: `src/data/powers/laws_of_the_night_revised.json`

**Page Map for Disciplines:**
- Animalism: 122-124 (Basic: Feral Whispers, Beckoning; Intermediate: Quell the Beast, Subsume the Spirit; Advanced: Drawing Out the Beast)
- Auspex: 125-127 (Basic: Heightened Senses, Aura Perception; Intermediate: Spirit's Touch, Telepathy; Advanced: Psychic Projection)
- Celerity: 128-129 (Basic: Alacrity, Swiftness; Intermediate: Legerity; Advanced: Fleetness)
- Chimerstry: 129-131 (Basic: Ignis Fatuus, Fata Morgana; Intermediate: Apparition; Advanced: Permanency)
- Dementation: 131-133 (Basic: Passion, The Haunting; Intermediate: Eyes of Chaos; Advanced: Total Insanity)
- Dominate: 133-135 (Basic: Command, Mesmerize; Intermediate: Forgetful Mind; Advanced: Possession)
- Fortitude: 135-136 (Basic: Endurance, Mettle; Intermediate: Resilience; Advanced: Resistance)
- Melpominee: 137-138 (Basic: The Missing Voice, Phantom Speaker; Intermediate: Madrigal; Advanced: Siren's Beckoning)
- Necromancy Paths: 139-145 (Sepulchre Path, Bone Path, Ash Path — each with Basic/Intermediate/Advanced)
- Obeah: 145-146 (Basic: Panacea, Anesthetic Touch; Intermediate: Neutral Guard; Advanced: Renewed Vigor)
- Obfuscate: 146-149 (Basic: Cloak of Shadows, Unseen Presence; Intermediate: Mask of a Thousand Faces; Advanced: Vanish)
- Obtenebration: 149-151 (Basic: Shadow Play, Shroud of Night; Intermediate: Arms of the Abyss; Advanced: Black Metamorphosis)
- Potence: 152-153 (Basic: Prowess, Might; Intermediate: Vigor; Advanced: Puissance)
- Presence: 153-155 (Basic: Awe, Dread Gaze; Intermediate: Entrancement; Advanced: Summon)
- Protean: 155-157 (Basic: Gleam of Red Eyes, Earth Meld; Intermediate: Shape of the Beast; Advanced: Mist Form)
- Quietus: 157-158 (Basic: Silence of Death, Weakness; Intermediate: Disease; Advanced: Baal's Caress)
- Serpentis: 158-160 (Basic: Eyes of the Serpent, Tongue of the Asp; Intermediate: Mummify/Skin of the Adder; Advanced: Form of the Cobra)
- Thanatosis: 160-161 (Basic: Hag's Wrinkles, Putrefaction; Intermediate: Ashes to Ashes; Advanced: Withering)
- Thaumaturgy Paths: 161-170 (Path of Blood, Lure of Flames, Movement of the Mind, Hands of Destruction, Weather Control — each with Basic/Intermediate/Advanced)
- Vicissitude: 172-175 (Basic: Changeling, Fleshcraft; Intermediate: Bonecraft; Advanced: Horrid Form)

**Also extract Thaumaturgy Rituals** (pages ~170-172, plus any listed elsewhere)

**Step 1: Run the extraction script against the PDF**

The script should output `src/data/powers/laws_of_the_night_revised.json` with all disciplines, their powers, full writeup text, and page numbers.

**Step 2: Manually verify a few entries**

Spot-check that Animalism/Feral Whispers has correct text from page 122, and that trait costs for merits/flaws are correct.

**Step 3: Commit**

```bash
git add -A
git commit -m "feat: extract all LotN disciplines, merits, flaws to JSON"
```

---

### Task 4: Extract Merits, Flaws, Backgrounds, and Abilities

**Files:**
- Modify: `src/data/powers/laws_of_the_night_revised.json` (add to existing)

**Merits & Flaws Pages:** 103-109
- Physical: Eat Food (1), Blush of Health (2), Enchanting Voice (2), Daredevil (3), Efficient Digestion (3), Huge Size (4)
- Physical Flaws: Hard of Hearing (1), Short (1), etc.
- Mental: Common Sense (1), Concentration (1), Time Sense (1), Code of Honor (2), Iron Will (3)
- Mental Flaws: Deep Sleeper (1), Nightmares (1), Prey Exclusion (1), etc.
- Social: Natural Leader (1), Prestigious Sire (1), Debt of Gratitude (1-3)
- Social Flaws: Enemy (1-5), Hunted (4), etc.
- Supernatural: Magic Resistance (2), Medium (2), Lucky (3), Oracular Ability (3), True Faith (7)
- Supernatural Flaws: Cursed (1-5), Cast No Reflection (1), Repulsed by Garlic (1), etc.

**Backgrounds Pages:** 67, 86-96
- Allies, Contacts, Fame, Generation, Herd, Influence, Mentor, Resources, Retainers, Status

**Abilities Pages:** 80-85
- Full list: Academics, Alertness, Animal Ken, Athletics, Brawl, Computer, Crafts, Dodge, Drive, Empathy, Etiquette, Expression, Finance, Firearms, Hobby/Expert, Intimidation, Investigation, Law, Leadership, Linguistics, Medicine, Melee, Occult, Performance, Politics, Repair, Science, Security, Stealth, Streetwise, Subterfuge, Survival

**Step 1: Run extraction for these sections**

**Step 2: Verify JSON structure**

**Step 3: Commit**

```bash
git add -A
git commit -m "feat: extract merits, flaws, backgrounds, abilities from LotN"
```

---

### Task 5: Create Power Import Utility

**Files:**
- Create: `src/utils/power_importer.py`

**Step 1: Create the importer**

```python
"""Import powers from JSON data files into the database."""

import json
import logging
from pathlib import Path
from typing import Dict, Any

from src.core.engine import get_session
from src.core.models.power import Power, PowerCategory, PowerWriteup

logger = logging.getLogger(__name__)


def import_powers_from_json(json_path: str, set_as_default: bool = True) -> Dict[str, int]:
    """Import powers from a JSON file into the database.

    Args:
        json_path: Path to the JSON data file
        set_as_default: Whether to mark these writeups as default

    Returns:
        Dict with counts: {"powers": N, "writeups": N, "categories": N}
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    source_book = data["source_book"]
    counts = {"powers": 0, "writeups": 0, "categories": 0}

    session = get_session()
    try:
        # Import disciplines
        if "disciplines" in data:
            cat = _get_or_create_category(session, "Discipline")
            counts["categories"] += 1
            for disc_name, disc_data in data["disciplines"].items():
                for power_data in disc_data.get("powers", []):
                    _import_power(session, cat, disc_name, power_data, source_book,
                                 disc_data.get("retest_ability"),
                                 disc_data.get("clans"),
                                 set_as_default)
                    counts["powers"] += 1
                    counts["writeups"] += 1

        # Import thaumaturgy paths
        if "thaumaturgy_paths" in data:
            cat = _get_or_create_category(session, "Thaumaturgy Path")
            counts["categories"] += 1
            for path_name, path_data in data["thaumaturgy_paths"].items():
                for power_data in path_data.get("powers", []):
                    _import_power(session, cat, path_name, power_data, source_book,
                                 path_data.get("retest_ability"), None, set_as_default)
                    counts["powers"] += 1
                    counts["writeups"] += 1

        # Import necromancy paths
        if "necromancy_paths" in data:
            cat = _get_or_create_category(session, "Necromancy Path")
            counts["categories"] += 1
            for path_name, path_data in data["necromancy_paths"].items():
                for power_data in path_data.get("powers", []):
                    _import_power(session, cat, path_name, power_data, source_book,
                                 path_data.get("retest_ability"), None, set_as_default)
                    counts["powers"] += 1
                    counts["writeups"] += 1

        # Import rituals
        if "rituals" in data:
            cat = _get_or_create_category(session, "Ritual")
            counts["categories"] += 1
            for ritual_type, rituals in data["rituals"].items():
                for ritual_data in rituals:
                    _import_power(session, cat, ritual_type, ritual_data, source_book,
                                 "Occult", None, set_as_default)
                    counts["powers"] += 1
                    counts["writeups"] += 1

        # Import merits
        if "merits" in data:
            cat = _get_or_create_category(session, "Merit")
            counts["categories"] += 1
            for merit_type, merits in data["merits"].items():
                for merit_data in merits:
                    _import_merit_flaw(session, cat, merit_type, merit_data, source_book, set_as_default)
                    counts["powers"] += 1
                    counts["writeups"] += 1

        # Import flaws
        if "flaws" in data:
            cat = _get_or_create_category(session, "Flaw")
            counts["categories"] += 1
            for flaw_type, flaws in data["flaws"].items():
                for flaw_data in flaws:
                    _import_merit_flaw(session, cat, flaw_type, flaw_data, source_book, set_as_default)
                    counts["powers"] += 1
                    counts["writeups"] += 1

        # Import backgrounds
        if "backgrounds" in data:
            cat = _get_or_create_category(session, "Background")
            counts["categories"] += 1
            for bg_data in data["backgrounds"]:
                _import_simple_power(session, cat, "Background", bg_data, source_book, set_as_default)
                counts["powers"] += 1
                counts["writeups"] += 1

        # Import abilities
        if "abilities" in data:
            cat = _get_or_create_category(session, "Ability")
            counts["categories"] += 1
            for ability_data in data["abilities"]:
                _import_simple_power(session, cat, "Ability", ability_data, source_book, set_as_default)
                counts["powers"] += 1
                counts["writeups"] += 1

        session.commit()
        logger.info(f"Imported from {source_book}: {counts}")
        return counts

    except Exception as e:
        session.rollback()
        logger.error(f"Import failed: {e}")
        raise
    finally:
        session.close()


def _get_or_create_category(session, name: str) -> PowerCategory:
    cat = session.query(PowerCategory).filter(PowerCategory.name == name).first()
    if not cat:
        cat = PowerCategory(name=name)
        session.add(cat)
        session.flush()
    return cat


def _import_power(session, category, power_type, power_data, source_book,
                   retest_ability, clans, set_as_default):
    clans_str = ",".join(clans) if clans else None

    power = session.query(Power).filter(
        Power.name == power_data["name"],
        Power.power_type == power_type
    ).first()

    if not power:
        power = Power(
            name=power_data["name"],
            category_id=category.id,
            power_type=power_type,
            level_tier=power_data.get("tier"),
            level_order=power_data.get("order", 1),
            retest_ability=retest_ability,
            clans=clans_str,
            prerequisites=power_data.get("prerequisites")
        )
        session.add(power)
        session.flush()

    writeup = PowerWriteup(
        power_id=power.id,
        source_book=source_book,
        page_number=power_data["page"],
        description=power_data.get("description", ""),
        system_text=power_data.get("system"),
        is_default=set_as_default
    )
    session.add(writeup)


def _import_merit_flaw(session, category, sub_type, data, source_book, set_as_default):
    power = session.query(Power).filter(
        Power.name == data["name"],
        Power.category_id == category.id
    ).first()

    if not power:
        power = Power(
            name=data["name"],
            category_id=category.id,
            power_type=sub_type,
            trait_cost=data.get("trait_cost"),
        )
        session.add(power)
        session.flush()

    writeup = PowerWriteup(
        power_id=power.id,
        source_book=source_book,
        page_number=data["page"],
        description=data.get("description", ""),
        is_default=set_as_default
    )
    session.add(writeup)


def _import_simple_power(session, category, power_type, data, source_book, set_as_default):
    power = session.query(Power).filter(
        Power.name == data["name"],
        Power.category_id == category.id
    ).first()

    if not power:
        power = Power(
            name=data["name"],
            category_id=category.id,
            power_type=power_type,
        )
        session.add(power)
        session.flush()

    writeup = PowerWriteup(
        power_id=power.id,
        source_book=source_book,
        page_number=data["page"],
        description=data.get("description", ""),
        is_default=set_as_default
    )
    session.add(writeup)
```

**Step 2: Verify import works**

Run: `python -c "from src.utils.power_importer import import_powers_from_json; print('OK')"`

**Step 3: Commit**

```bash
git add -A
git commit -m "feat: add power import utility for loading JSON into DB"
```

---

### Task 6: Run Full Extraction and Import

**Step 1: Run extraction script**

```bash
python src/utils/power_extractor.py
```

**Step 2: Verify JSON output**

```bash
python -c "
import json
with open('src/data/powers/laws_of_the_night_revised.json') as f:
    data = json.load(f)
print(f'Disciplines: {len(data.get(\"disciplines\", {}))}')
print(f'Thaum Paths: {len(data.get(\"thaumaturgy_paths\", {}))}')
print(f'Necro Paths: {len(data.get(\"necromancy_paths\", {}))}')
print(f'Merit categories: {len(data.get(\"merits\", {}))}')
print(f'Flaw categories: {len(data.get(\"flaws\", {}))}')
print(f'Backgrounds: {len(data.get(\"backgrounds\", []))}')
print(f'Abilities: {len(data.get(\"abilities\", []))}')
"
```

**Step 3: Test import**

```bash
python -c "
from src.utils.power_importer import import_powers_from_json
counts = import_powers_from_json('src/data/powers/laws_of_the_night_revised.json')
print(counts)
"
```

**Step 4: Commit**

```bash
git add -A
git commit -m "feat: complete LotN data extraction - all disciplines, merits, flaws, abilities"
```

---

### Task 7: Update Project Documentation

**Files:**
- Create or update: `CLAUDE.md` (if it doesn't exist)
- Update: `docs/plans/2026-02-25-powers-writeups-system-design.md` (mark as implemented)

**Step 1: Create/update CLAUDE.md with project context**

Include:
- Project overview (Coterie = MET LARP character manager)
- Key directories and their purposes
- Power system architecture (Power → PowerWriteup, JSON → DB flow)
- How to add a new source book (create JSON file, run importer)
- Key models and their relationships
- Future features roadmap (XP calculator, automated XP granting, UI power browser)

**Step 2: Commit**

```bash
git add -A
git commit -m "docs: update project documentation for powers system and future LLM iterations"
```
