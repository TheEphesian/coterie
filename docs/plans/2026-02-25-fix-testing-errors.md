# Fix Testing Errors Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix all 11 bugs found in testing (crashes, wrong ability names, missing UI fields, broken imports) and complete the VampireSheet.

**Architecture:** Fix model columns first (foundation), then crash-causing bugs, then UI restructuring. The Chronicle model gains `narrator` (text), `last_modified`, `is_active` columns AND wires HST through Player FK. The character creation dialog and VampireSheet get restructured to match Laws of the Night MET rules.

**Tech Stack:** Python 3.14, SQLAlchemy ORM, PyQt6, SQLite

**Key Reference:** `docs/LawsOfTheNightRevised.pdf` pages 60-80 (character creation rules)

---

### Task 1: Fix LarpTrait Model — Add Missing Columns

**Files:**
- Modify: `src/core/models/larp_trait.py:49-86`

**Step 1: Add missing Boolean columns to LarpTrait**

In `src/core/models/larp_trait.py`, add these mapped columns after `description` (line 57):

```python
from sqlalchemy import String, Integer, Boolean, ForeignKey, Table, Column
```

And in the class body after `description`:

```python
    # Trait state flags
    is_negative: Mapped[bool] = mapped_column(Boolean, default=False)
    is_spent: Mapped[bool] = mapped_column(Boolean, default=False)
    is_temporary: Mapped[bool] = mapped_column(Boolean, default=False)
    is_custom: Mapped[bool] = mapped_column(Boolean, default=False)
```

**Step 2: Verify the app launches**

Run: `cd /mnt/d/TheEdge/KingmakerTM/Coterie && python -c "from src.core.models.larp_trait import LarpTrait; print('OK')"`
Expected: `OK`

**Step 3: Commit**

```bash
git add src/core/models/larp_trait.py
git commit -m "fix: add missing Boolean columns to LarpTrait model"
```

---

### Task 2: Fix TraitConverter — Add Missing `dot_rating_to_adjectives()`

**Files:**
- Modify: `src/utils/trait_converter.py`

**Step 1: Add the missing method**

Add this classmethod to `TraitConverter` after `get_random_trait_adjectives`:

```python
    @classmethod
    def dot_rating_to_adjectives(cls, trait_name: str, rating: int, category: str) -> List[str]:
        """Convert a dot rating to a list of adjective traits.

        Used for Grapevine import: converts numeric ratings (e.g., Athletics 3)
        to MET adjective traits (e.g., ["Athletic", "Agile", "Nimble"]).

        Args:
            trait_name: The trait name (e.g., "athletics", "brawl")
            rating: The numeric rating (1-5)
            category: The trait category (physical, social, mental, talents, skills, knowledges)

        Returns:
            List of adjective traits matching the rating count
        """
        # For attribute categories, pull directly from the category pool
        if category in ("physical", "social", "mental"):
            adjectives = cls.get_trait_adjectives(category)
            if adjectives:
                return adjectives[:min(rating, len(adjectives))]
            return [f"{trait_name.title()} x{i+1}" for i in range(rating)]

        # For ability categories, try to find ability-specific adjectives
        adjectives = cls.get_ability_trait_adjectives(category, trait_name)
        if adjectives:
            return adjectives[:min(rating, len(adjectives))]

        # Fallback: generate numbered traits
        display_name = trait_name.replace("_", " ").title()
        return [f"{display_name} x{i+1}" for i in range(rating)]
```

**Step 2: Verify import works**

Run: `python -c "from src.utils.trait_converter import TraitConverter; print(TraitConverter.dot_rating_to_adjectives('athletics', 3, 'talents'))"`
Expected: `['Athletic', 'Agile', 'Nimble']`

**Step 3: Commit**

```bash
git add src/utils/trait_converter.py
git commit -m "fix: add missing dot_rating_to_adjectives to TraitConverter"
```

---

### Task 3: Fix Staff Manager — Broken Imports

**Files:**
- Modify: `src/ui/dialogs/staff_manager.py:11-12`

**Step 1: Fix imports**

Replace lines 11-12:

```python
# OLD:
from ...models.chronicle import Chronicle
from ...models.staff import Staff

# NEW:
from src.core.models.chronicle import Chronicle
from src.core.models.staff import Staff
```

**Step 2: Verify import**

Run: `python -c "from src.ui.dialogs.staff_manager import StaffManagerDialog; print('OK')"`
Expected: `OK`

**Step 3: Commit**

```bash
git add src/ui/dialogs/staff_manager.py
git commit -m "fix: correct imports in staff_manager.py"
```

---

### Task 4: Fix Session Conflict in `prepare_character_for_ui`

**Files:**
- Modify: `src/utils/data_loader.py:1029-1086`

**Step 1: Fix prepare_character_for_ui to use merge instead of add**

Replace the function body to handle already-attached objects:

```python
def prepare_character_for_ui(character: Any) -> Any:
    """Prepare a character for use in the UI by ensuring all required data is loaded."""
    if not character:
        return None

    session = get_session()
    try:
        # Use merge() instead of add() to handle objects already attached to other sessions
        character = session.merge(character)

        # Force access to key attributes to ensure they're loaded
        _ = character.id
        _ = character.name
        _ = character.player_name
        _ = character.nature
        _ = character.demeanor
        _ = character.type

        # Access type-specific attributes
        from src.core.models import Vampire
        if isinstance(character, Vampire):
            _ = character.clan
            _ = character.generation
            _ = character.sect
            _ = character.sire
            _ = character.conscience
            _ = character.self_control
            _ = character.courage
            _ = character.path
            _ = character.willpower
            _ = character.blood

        # Force load all collection attributes
        if hasattr(character, 'traits'):
            _ = list(character.traits)

        if hasattr(character, 'larp_traits'):
            larp_traits = list(character.larp_traits)
            for trait in larp_traits:
                if hasattr(trait, 'categories'):
                    _ = list(trait.categories)

        # Expunge so it can be used outside this session
        session.expunge(character)
        return character

    except Exception as e:
        logger.error(f"Error preparing character for UI: {e}")
        return character
    finally:
        session.close()
```

**Step 2: Commit**

```bash
git add src/utils/data_loader.py
git commit -m "fix: use session.merge() in prepare_character_for_ui to prevent session conflicts"
```

---

### Task 5: Fix Chronicle Model — Add Missing Columns

**Files:**
- Modify: `src/core/models/chronicle.py:24-47`

**Step 1: Add narrator, last_modified, is_active columns**

Add imports and columns to the Chronicle model:

```python
from sqlalchemy import String, Boolean, ForeignKey, Table, Column, DateTime
```

Add these columns after `end_date` (line 33), before `storyteller_id`:

```python
    # HST/Narrator name (text field for quick access; storyteller FK is the formal link)
    narrator: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_modified: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
```

Make `storyteller_id` nullable (so chronicles can exist without a linked Player):

```python
    storyteller_id: Mapped[Optional[int]] = mapped_column(ForeignKey("players.id"), nullable=True)
    storyteller: Mapped[Optional["Player"]] = relationship("Player", back_populates="chronicles_run")
```

Also update the Player model relationship in `src/core/models/player.py` to match:

```python
    chronicles_run: Mapped[List["Chronicle"]] = relationship(
        "Chronicle",
        back_populates="storyteller",
        foreign_keys="Chronicle.storyteller_id"
    )
```

**Step 2: Verify model loads**

Run: `python -c "from src.core.models.chronicle import Chronicle; print('OK')"`
Expected: `OK`

**Step 3: Commit**

```bash
git add src/core/models/chronicle.py src/core/models/player.py
git commit -m "fix: add narrator, last_modified, is_active columns to Chronicle model"
```

---

### Task 6: Fix Chronicle Creation — Wire HST Through Player FK

**Files:**
- Modify: `src/ui/main_window.py:331-371` (`_create_chronicle` method)
- Modify: `src/ui/main_window.py:285-323` (`_refresh_chronicles` method)

**Step 1: Fix `_create_chronicle` to find-or-create Player**

```python
def _create_chronicle(self, data: Dict[str, Any]) -> None:
    """Create a new chronicle in the database."""
    try:
        session = get_session()

        from src.core.models.player import Player

        # Find or create a Player record for the HST
        hst_name = data.get("narrator", "").strip()
        storyteller = None
        if hst_name:
            storyteller = session.query(Player).filter(Player.name == hst_name).first()
            if not storyteller:
                storyteller = Player(name=hst_name, status="Active")
                session.add(storyteller)
                session.flush()

        chronicle = Chronicle(
            name=data["name"],
            narrator=hst_name,
            description=data.get("description", ""),
            start_date=data["start_date"],
            last_modified=data.get("last_modified"),
            is_active=data.get("is_active", True),
            storyteller_id=storyteller.id if storyteller else None
        )

        session.add(chronicle)
        session.commit()

        self.active_chronicle = chronicle
        self._refresh_chronicles()

        self.status_bar.showMessage(f"Created new chronicle: {data['name']}")
        logger.info(f"Created new chronicle: {data['name']}")

    except Exception as e:
        error_msg = f"Failed to create chronicle: {str(e)}"
        logger.error(error_msg)
        QMessageBox.critical(self, "Error", error_msg)
        if session:
            session.rollback()
    finally:
        session.close()
```

**Step 2: Fix `_refresh_chronicles` to use narrator field**

In the `_refresh_chronicles` method, line 298, change:

```python
# OLD:
item = QListWidgetItem(f"{chronicle.name} (Narrator: {chronicle.narrator})")

# NEW (narrator field now exists):
narrator_display = chronicle.narrator or "No HST"
item = QListWidgetItem(f"{chronicle.name} (HST: {narrator_display})")
```

**Step 3: Also fix `vampire_sheet.py:264` which reads `chronicle.narrator`**

In `_on_assign_chronicle`, line 264:

```python
# OLD:
item = QListWidgetItem(f"{chronicle.name} (HST: {chronicle.narrator})")

# NEW:
narrator_display = chronicle.narrator or "No HST"
item = QListWidgetItem(f"{chronicle.name} (HST: {narrator_display})")
```

**Step 4: Commit**

```bash
git add src/ui/main_window.py src/ui/sheets/vampire_sheet.py
git commit -m "fix: wire chronicle HST through Player FK, fix chronicle creation"
```

---

### Task 7: Fix Character Creation — Unify Abilities & Fix Names

**Files:**
- Modify: `src/ui/dialogs/character_creation.py`

**Step 1: Update `_create_trait_sections` — unify Abilities**

Replace the Abilities section (lines 203-238) with a unified flat list:

```python
        # Abilities section
        abilities_group = QGroupBox("Abilities")
        abilities_layout = QVBoxLayout(abilities_group)
        parent_layout.addWidget(abilities_group)

        abilities_instr = QLabel(
            "Select your character's abilities. Each ability can be taken multiple times "
            "to represent higher levels of expertise."
        )
        abilities_instr.setWordWrap(True)
        abilities_layout.addWidget(abilities_instr)

        # Single flat list for all abilities (MET doesn't split into Talents/Skills/Knowledges)
        self.abilities = LarpTraitWidget("Abilities")
        abilities_layout.addWidget(self.abilities)

        # Single button for common abilities
        abilities_button = QPushButton("Add Common Abilities")
        abilities_button.clicked.connect(self._add_common_abilities_flat)
        abilities_layout.addWidget(abilities_button)
```

**Step 2: Replace `_add_common_abilities` with `_add_common_abilities_flat`**

Delete the old `_add_common_abilities` method (lines 300-333) and replace with:

```python
    def _add_common_abilities_flat(self) -> None:
        """Add common MET abilities from the Laws of the Night rulebook."""
        common_abilities = [
            "Academics", "Alertness", "Animal Ken", "Athletics", "Brawl",
            "Computer", "Crafts", "Dodge", "Drive", "Empathy",
            "Etiquette", "Expression", "Finance", "Firearms",
            "Intimidation", "Investigation", "Law", "Leadership",
            "Linguistics", "Medicine", "Melee", "Occult",
            "Performance", "Politics", "Science", "Security",
            "Stealth", "Streetwise", "Subterfuge", "Survival"
        ]
        self.abilities.set_traits(common_abilities)
```

**Step 3: Update `get_character_data` to emit flat abilities**

In `get_character_data` (line 423-426), replace the ability trait gathering:

```python
        # Add abilities (flat list in MET)
        larp_traits["abilities"] = self.abilities.get_traits()
```

Remove the old loop over `self.abilities.get_category_traits()`.

**Step 4: Commit**

```bash
git add src/ui/dialogs/character_creation.py
git commit -m "fix: unify abilities into flat list, use correct MET ability names"
```

---

### Task 8: Allow Duplicate Traits in LarpTraitWidget

**Files:**
- Modify: `src/ui/widgets/larp_trait_widget.py:74-97`

**Step 1: Remove duplicate check from `_add_trait`**

In `LarpTraitWidget._add_trait()`, remove the duplicate check block (lines 83-89):

```python
    def _add_trait(self):
        """Add a new trait through user input."""
        trait, ok = QInputDialog.getText(
            self,
            f"Add {self.trait_name} Trait",
            "Enter new trait adjective:"
        )

        if ok and trait:
            # Add to internal list and UI (duplicates allowed for multiple levels)
            self.traits.append(trait)
            self.trait_list_widget.addItem(QListWidgetItem(trait))
            self.traitChanged.emit(self.trait_name, self.traits)
```

**Step 2: Commit**

```bash
git add src/ui/widgets/larp_trait_widget.py
git commit -m "fix: allow duplicate traits in LarpTraitWidget for multi-level abilities"
```

---

### Task 9: Restructure Character Creation Tabs

**Files:**
- Modify: `src/ui/dialogs/character_creation.py`

**Step 1: Update `__init__` to add new tabs**

After the existing Advantages tab setup, add new tabs:

```python
        # Backgrounds tab
        backgrounds_tab = QWidget()
        self.tabs.addTab(backgrounds_tab, "Backgrounds")
        backgrounds_scroll = QScrollArea()
        backgrounds_scroll.setWidgetResizable(True)
        backgrounds_layout = QVBoxLayout(backgrounds_tab)
        backgrounds_layout.addWidget(backgrounds_scroll)
        backgrounds_content = QWidget()
        backgrounds_scroll_layout = QVBoxLayout(backgrounds_content)
        backgrounds_scroll.setWidget(backgrounds_content)
        self._create_backgrounds_section(backgrounds_scroll_layout)

        # Merits & Flaws tab
        merits_flaws_tab = QWidget()
        self.tabs.addTab(merits_flaws_tab, "Merits & Flaws")
        merits_flaws_scroll = QScrollArea()
        merits_flaws_scroll.setWidgetResizable(True)
        merits_flaws_layout = QVBoxLayout(merits_flaws_tab)
        merits_flaws_layout.addWidget(merits_flaws_scroll)
        merits_flaws_content = QWidget()
        merits_flaws_scroll_layout = QVBoxLayout(merits_flaws_content)
        merits_flaws_scroll.setWidget(merits_flaws_content)
        self._create_merits_flaws_section(merits_flaws_scroll_layout)
```

**Step 2: Update `_create_advantage_sections` — Disciplines only**

Remove the Backgrounds group from this method. Keep only Disciplines.

**Step 3: Add new section methods**

```python
    def _create_backgrounds_section(self, parent_layout: QVBoxLayout) -> None:
        """Create the backgrounds section."""
        backgrounds_group = QGroupBox("Backgrounds")
        backgrounds_layout = QVBoxLayout(backgrounds_group)
        parent_layout.addWidget(backgrounds_group)

        backgrounds_instr = QLabel(
            "Backgrounds represent social connections and resources. "
            "You may take five Background Traits."
        )
        backgrounds_instr.setWordWrap(True)
        backgrounds_layout.addWidget(backgrounds_instr)

        self.backgrounds = LarpTraitWidget("Backgrounds")
        backgrounds_layout.addWidget(self.backgrounds)

        suggest_bg_button = QPushButton("Add Common Backgrounds")
        suggest_bg_button.clicked.connect(self._add_common_backgrounds)
        backgrounds_layout.addWidget(suggest_bg_button)

    def _create_merits_flaws_section(self, parent_layout: QVBoxLayout) -> None:
        """Create the merits and flaws section."""
        # Merits
        merits_group = QGroupBox("Merits")
        merits_layout = QVBoxLayout(merits_group)
        parent_layout.addWidget(merits_group)

        merits_instr = QLabel("Merits are special advantages purchased with Free Traits.")
        merits_instr.setWordWrap(True)
        merits_layout.addWidget(merits_instr)

        self.merits = LarpTraitWidget("Merits")
        merits_layout.addWidget(self.merits)

        # Flaws
        flaws_group = QGroupBox("Flaws")
        flaws_layout = QVBoxLayout(flaws_group)
        parent_layout.addWidget(flaws_group)

        flaws_instr = QLabel(
            "Flaws represent specific deficiencies. Each Flaw grants additional Free Traits. "
            "A character may total up to seven Traits of Flaws."
        )
        flaws_instr.setWordWrap(True)
        flaws_layout.addWidget(flaws_instr)

        self.flaws = LarpTraitWidget("Flaws")
        flaws_layout.addWidget(self.flaws)
```

**Step 4: Update `get_character_data` to include new trait types**

```python
        larp_traits["merits"] = self.merits.get_traits()
        larp_traits["flaws"] = self.flaws.get_traits()
```

**Step 5: Commit**

```bash
git add src/ui/dialogs/character_creation.py
git commit -m "feat: restructure character creation tabs (Backgrounds, Merits & Flaws)"
```

---

### Task 10: Complete VampireSheet — Add Missing Fields & Widgets

This is the largest task. The VampireSheet currently references widgets (`self.attributes`, `self.abilities`, `self.virtues`, `self.path_traits`, `self.willpower`, `self.blood`, `self.sire`, `self.concept`, `self.title`) that don't exist in `__init__`.

**Files:**
- Modify: `src/ui/sheets/vampire_sheet.py`

**Step 1: Add missing fields to `_create_character_info_section`**

After the HST field (line 227), add:

```python
        # Sire
        self.sire = QLineEdit()
        self.sire.textChanged.connect(lambda: self.modified.emit())
        info_layout.addRow("Sire:", self.sire)

        # Title
        self.title = QLineEdit()
        self.title.textChanged.connect(lambda: self.modified.emit())
        info_layout.addRow("Title:", self.title)

        # Concept
        self.concept = QLineEdit()
        self.concept.textChanged.connect(lambda: self.modified.emit())
        info_layout.addRow("Concept:", self.concept)
```

**Step 2: Replace the traits tab with proper Attributes + Abilities widgets**

Replace the traits tab creation (lines 103-116) with:

```python
        # Create traits tab with Attributes and Abilities
        self.traits_tab = QWidget()
        self.traits_layout = QVBoxLayout(self.traits_tab)
        self.tabs.addTab(self.traits_tab, "Traits")

        # Attributes (adjective-based, split by Physical/Social/Mental)
        self.attributes = LarpTraitCategoryWidget(
            category_name="Attributes",
            trait_categories={
                "Physical": [],
                "Social": [],
                "Mental": []
            }
        )
        self.attributes.categoryChanged.connect(lambda c, t: self.modified.emit())
        self.traits_layout.addWidget(self.attributes)

        # Abilities (flat list, MET style)
        abilities_group = QGroupBox("Abilities")
        abilities_group_layout = QVBoxLayout(abilities_group)
        self.abilities = LarpTraitWidget("Abilities")
        self.abilities.traitChanged.connect(lambda n, t: self.modified.emit())
        abilities_group_layout.addWidget(self.abilities)
        self.traits_layout.addWidget(abilities_group)
```

**Step 3: Replace the disciplines tab**

Replace the disciplines tab (lines 119-132) with:

```python
        # Disciplines tab
        self.disciplines_tab = QWidget()
        self.disciplines_layout = QVBoxLayout(self.disciplines_tab)
        self.tabs.addTab(self.disciplines_tab, "Disciplines")

        self.disciplines = LarpTraitWidget("Disciplines")
        self.disciplines.traitChanged.connect(lambda n, t: self.modified.emit())
        self.disciplines_layout.addWidget(self.disciplines)
```

**Step 4: Replace the backgrounds tab**

Replace the backgrounds tab (lines 134-148) with:

```python
        # Backgrounds tab
        self.backgrounds_tab = QWidget()
        self.backgrounds_layout = QVBoxLayout(self.backgrounds_tab)
        self.tabs.addTab(self.backgrounds_tab, "Backgrounds")

        self.backgrounds = LarpTraitWidget("Backgrounds")
        self.backgrounds.traitChanged.connect(lambda n, t: self.modified.emit())
        self.backgrounds_layout.addWidget(self.backgrounds)
```

**Step 5: Add Virtues, Path, Willpower, Blood tabs/widgets**

After the backgrounds tab, add:

```python
        # Virtues & Morality tab
        self.virtues_tab = QWidget()
        self.virtues_layout = QVBoxLayout(self.virtues_tab)
        self.tabs.addTab(self.virtues_tab, "Virtues & Morality")

        # Virtues (Conscience/Self-Control/Courage as category widget)
        self.virtues = LarpTraitCategoryWidget(
            category_name="Virtues",
            trait_categories={
                "Conscience": [],
                "Self-Control": [],
                "Courage": []
            }
        )
        self.virtues.categoryChanged.connect(lambda c, t: self.modified.emit())
        self.virtues_layout.addWidget(self.virtues)

        # Path/Morality traits
        path_group = QGroupBox("Path / Morality")
        path_group_layout = QVBoxLayout(path_group)
        self.path_traits = LarpTraitWidget("Path")
        self.path_traits.traitChanged.connect(lambda n, t: self.modified.emit())
        path_group_layout.addWidget(self.path_traits)
        self.virtues_layout.addWidget(path_group)

        # Status tab (Willpower, Blood)
        self.status_tab = QWidget()
        self.status_layout = QVBoxLayout(self.status_tab)
        self.tabs.addTab(self.status_tab, "Status")

        # Willpower traits
        wp_group = QGroupBox("Willpower")
        wp_group_layout = QVBoxLayout(wp_group)
        self.willpower = LarpTraitWidget("Willpower")
        self.willpower.traitChanged.connect(lambda n, t: self.modified.emit())
        wp_group_layout.addWidget(self.willpower)
        self.status_layout.addWidget(wp_group)

        # Blood traits
        blood_group = QGroupBox("Blood Pool")
        blood_group_layout = QVBoxLayout(blood_group)
        self.blood = LarpTraitWidget("Blood")
        self.blood.traitChanged.connect(lambda n, t: self.modified.emit())
        blood_group_layout.addWidget(self.blood)
        self.status_layout.addWidget(blood_group)

        # Merits & Flaws tab
        self.merits_flaws_tab = QWidget()
        self.merits_flaws_layout = QVBoxLayout(self.merits_flaws_tab)
        self.tabs.addTab(self.merits_flaws_tab, "Merits & Flaws")

        merits_group = QGroupBox("Merits")
        merits_group_layout = QVBoxLayout(merits_group)
        self.merits = LarpTraitWidget("Merits")
        self.merits.traitChanged.connect(lambda n, t: self.modified.emit())
        merits_group_layout.addWidget(self.merits)
        self.merits_flaws_layout.addWidget(merits_group)

        flaws_group = QGroupBox("Flaws")
        flaws_group_layout = QVBoxLayout(flaws_group)
        self.flaws = LarpTraitWidget("Flaws")
        self.flaws.traitChanged.connect(lambda n, t: self.modified.emit())
        flaws_group_layout.addWidget(self.flaws)
        self.merits_flaws_layout.addWidget(flaws_group)
```

**Step 6: Update `_load_larp_traits` to handle unified abilities**

The existing method already handles most categories. Add handling for the unified abilities category and merits/flaws:

```python
                    # Handle abilities (unified flat list)
                    elif category_name == "abilities":
                        ability_traits.append(trait.display_name)
                    # Also keep backwards compat with split categories
                    elif category_name in ("talents", "skills", "knowledges"):
                        ability_traits.append(trait.display_name)

                    # Handle merits and flaws
                    elif category_name == "merits":
                        merit_traits.append(trait.display_name)
                    elif category_name == "flaws":
                        flaw_traits.append(trait.display_name)
```

And update the widget assignments:

```python
        # Update widgets
        self.attributes.set_category_traits(attribute_traits)
        self.abilities.set_traits(ability_traits)
        self.virtues.set_category_traits(virtue_traits)
        self.disciplines.set_traits(discipline_traits)
        self.backgrounds.set_traits(background_traits)
        self.path_traits.set_traits(path_traits)
        self.willpower.set_traits(willpower_traits)
        self.blood.set_traits(blood_traits)
        self.merits.set_traits(merit_traits)
        self.flaws.set_traits(flaw_traits)
```

**Step 7: Update `_collect_all_larp_traits` to include merits/flaws**

Add to the method:

```python
        larp_traits["merits"] = self.merits.get_traits()
        larp_traits["flaws"] = self.flaws.get_traits()
```

**Step 8: Update `load_character` to populate new fields**

In the `load_character` method, after setting existing fields, add:

```python
            if hasattr(character, "sire"):
                self.sire.setText(character.sire or "")
            if hasattr(character, "title"):
                self.title.setText(character.title or "")
```

**Step 9: Store character reference for later use**

Add `self.character = None` in `__init__` and set it in `load_character`:

```python
self.character = character
```

**Step 10: Commit**

```bash
git add src/ui/sheets/vampire_sheet.py
git commit -m "feat: complete VampireSheet with all MET fields (virtues, blood, willpower, merits, flaws)"
```

---

### Task 11: Update Attribute Trait Lists to Match Laws of the Night

**Files:**
- Modify: `src/data/trait_adjectives.json`

**Step 1: Update the physical/social/mental lists to match the canonical LotN lists**

Update `trait_adjectives.json` with the official trait lists from Laws of the Night Revised (pages 65, 75-79):

Physical: `["Agile", "Brawny", "Brutal", "Dexterous", "Enduring", "Energetic", "Ferocious", "Graceful", "Lithe", "Nimble", "Quick", "Resilient", "Robust", "Rugged", "Stalwart", "Steady", "Tenacious", "Tireless", "Tough", "Vigorous", "Wiry"]`

Social: `["Alluring", "Beguiling", "Charismatic", "Charming", "Commanding", "Dignified", "Diplomatic", "Elegant", "Eloquent", "Empathetic", "Expressive", "Friendly", "Genial", "Gorgeous", "Ingratiating", "Intimidating", "Magnetic", "Persuasive", "Seductive", "Witty"]`

Mental: `["Astute", "Attentive", "Clever", "Creative", "Cunning", "Dedicated", "Determined", "Discerning", "Disciplined", "Insightful", "Intuitive", "Knowledgeable", "Observant", "Patient", "Rational", "Reflective", "Shrewd", "Vigilant", "Wily", "Wise"]`

Also update the negative trait lists to match LotN (pages 76-79):

Negative Physical: `["Clumsy", "Cowardly", "Decrepit", "Delicate", "Docile", "Flabby", "Lame", "Lethargic", "Puny", "Sickly"]`

Negative Social: `["Bestial", "Callous", "Condescending", "Dull", "Feral", "Naive", "Obnoxious", "Repugnant", "Shy", "Tactless", "Untrustworthy"]`

Negative Mental: `["Forgetful", "Gullible", "Ignorant", "Impatient", "Oblivious", "Predictable", "Shortsighted", "Submissive", "Violent", "Witless"]`

**Step 2: Commit**

```bash
git add src/data/trait_adjectives.json
git commit -m "fix: update trait adjectives to match Laws of the Night Revised canonical lists"
```

---

### Task 12: Fix `create_vampire_from_dict` — Wrong Field Name

**Files:**
- Modify: `src/utils/data_loader.py:906`

**Step 1: Fix `player` → `player_name`**

Line 908:
```python
# OLD:
player=character_data.get('player', ''),

# NEW:
player_name=character_data.get('player', ''),
```

**Step 2: Commit**

```bash
git add src/utils/data_loader.py
git commit -m "fix: correct player field name in create_vampire_from_dict"
```

---

### Task 13: Update `_create_character` in main_window to Handle Unified Abilities

**Files:**
- Modify: `src/ui/main_window.py:460-502`

**Step 1: Update character type detection**

The `_create_character` method checks `data["type"].lower() == "vampire"` but the dialog sends full names like "Vampire: The Masquerade". Fix:

```python
        if "vampire" in data["type"].lower():
            character = Vampire(
                clan=data.get("clan", ""),
                generation=data.get("generation", 13),
                sect=data.get("sect", ""),
                sire="",
                path="Humanity",
                path_traits=0,
                temp_path_traits=0,
                conscience=0,
                temp_conscience=0,
                self_control=0,
                temp_self_control=0,
                courage=0,
                temp_courage=0,
                blood=0,
                temp_blood=0,
            )
        else:
            character = Character()
            character.type = data["type"].split(":")[0].lower().strip()
```

**Step 2: Commit**

```bash
git add src/ui/main_window.py
git commit -m "fix: handle full character type names in character creation"
```

---

### Task 14: Final Verification

**Step 1: Run existing tests**

```bash
cd /mnt/d/TheEdge/KingmakerTM/Coterie
python -m pytest tests/ -v --tb=short 2>&1 | head -50
```

**Step 2: Verify all imports work**

```bash
python -c "
from src.core.models import *
from src.core.models.larp_trait import LarpTrait
from src.ui.dialogs.staff_manager import StaffManagerDialog
from src.ui.dialogs.character_creation import CharacterCreationDialog
from src.ui.dialogs.chronicle_creation import ChronicleCreationDialog
from src.utils.trait_converter import TraitConverter
from src.utils.data_loader import prepare_character_for_ui
print('All imports OK')
"
```

**Step 3: Final commit if any remaining fixes**

```bash
git add -A
git commit -m "fix: final verification and cleanup"
```
