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
