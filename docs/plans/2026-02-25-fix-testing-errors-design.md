# Fix Testing Errors - Design Document

## Context
Errors found during testing documented in `errorsfoundintesting.md`, plus additional bugs found during code review.

## Fixes

### Group A: Crash Fixes

**A1. Chronicle Creation — Wire HST through Player FK**
- Add `last_modified` (DateTime, nullable) and `is_active` (Boolean, default True) columns to Chronicle model
- Keep existing `storyteller_id` FK; make it nullable for chronicles without an HST yet
- `_create_chronicle()`: find-or-create Player by name, set `storyteller_id`
- `_refresh_chronicles()`: display `chronicle.storyteller.name` instead of `chronicle.narrator`
- Files: `chronicle.py`, `main_window.py`, `chronicle_creation.py`, `vampire_sheet.py`

**A2. Staff Manager — Fix imports**
- `staff_manager.py:11-12`: change relative imports to absolute `src.core.models.*`
- Files: `staff_manager.py`

**A3. Session Conflict — Fix prepare_character_for_ui**
- Use `session.merge()` instead of `session.add()` to handle already-attached objects
- Files: `data_loader.py`

### Group B: Ability/Trait Fixes

**B1. Fix "Add Common" ability names**
- Read ability names from `trait_adjectives.json` keys (proper-cased) instead of hardcoded wrong adjectives
- Files: `character_creation.py`

**B2. Allow multiple levels of same ability**
- Remove duplicate check in `LarpTraitWidget._add_trait()`
- Files: `larp_trait_widget.py`

**B3. Unify Abilities list**
- Replace `LarpTraitCategoryWidget` (Talents/Skills/Knowledges) with single `LarpTraitWidget`
- Single "Add Common Abilities" button
- Files: `character_creation.py`

### Group C: Tab Restructuring

**C1. Restructure character creation Advantages**
- Advantages tab: Disciplines only
- New tabs: Backgrounds, Merits & Flaws
- Files: `character_creation.py`

**C2. Complete VampireSheet**
- Add missing fields: Sire, Title, Concept to character info section
- Add LARP trait widgets: Abilities, Virtues (as LarpTraitCategoryWidget), Path/Willpower/Blood (as LarpTraitWidget)
- Wire `_load_larp_traits` and `_collect_all_larp_traits` to actual widgets
- Files: `vampire_sheet.py`

### Group D: Hidden Bug Fixes

**D1. LarpTrait model — add missing columns**
- Add `is_negative`, `is_spent`, `is_temporary`, `is_custom` as Boolean mapped columns with defaults
- Files: `larp_trait.py`

**D2. TraitConverter — add dot_rating_to_adjectives()**
- Implement missing method for Grapevine import compatibility
- Files: `trait_converter.py`

## Implementation Order
1. D1 (LarpTrait columns) - foundation fix
2. D2 (TraitConverter method) - foundation fix
3. A2 (Staff Manager imports) - one-line fix
4. A3 (Session conflict) - small fix
5. A1 (Chronicle creation) - model + UI change
6. B1-B3 (Ability fixes) - character creation UI
7. C1 (Character creation tabs) - UI restructure
8. C2 (VampireSheet completion) - largest piece
