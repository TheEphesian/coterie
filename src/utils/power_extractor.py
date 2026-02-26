#!/usr/bin/env python3
"""
Extract game data from Laws of the Night Revised PDF into structured JSON.

Uses pymupdf (fitz) to read text from specific page ranges, then parses
disciplines, thaumaturgy/necromancy paths, rituals, merits, flaws,
backgrounds, and abilities into a single JSON file.
"""

import json
import os
import re
import sys

import fitz  # pymupdf


PDF_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'docs', 'LawsOfTheNightRevised.pdf')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'powers', 'laws_of_the_night_revised.json')


def get_pages_text(doc, start_page, end_page):
    """Extract text from pages (1-indexed, inclusive)."""
    text = ""
    for i in range(start_page - 1, end_page):
        text += doc[i].get_text()
    return text


def clean_text(text):
    """Clean up extracted text: normalize whitespace, fix common OCR issues."""
    # Collapse multiple spaces but keep paragraph breaks
    text = re.sub(r'[ \t]+', ' ', text)
    # Normalize line breaks: single newlines become spaces, double become paragraph breaks
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def find_page_for_text(doc, search_text, start_page, end_page):
    """Find which page (1-indexed) contains a given text string."""
    for i in range(start_page - 1, end_page):
        if search_text.lower() in doc[i].get_text().lower():
            return i + 1
    return start_page


# ---------------------------------------------------------------------------
# Discipline definitions
# ---------------------------------------------------------------------------

DISCIPLINE_DEFS = [
    {
        "name": "Animalism",
        "pages": (122, 124),
        "clans": ["Gangrel", "Nosferatu", "Ravnos", "Tzimisce"],
        "retest_ability": "Animal Ken",
        "powers": [
            ("Feral Whispers", "Basic", 1),
            ("Beckoning", "Basic", 2),
            ("Quell the Beast", "Intermediate", 3),
            ("Subsume the Spirit", "Intermediate", 4),
            ("Drawing Out the Beast", "Advanced", 5),
        ]
    },
    {
        "name": "Auspex",
        "pages": (125, 127),
        "clans": ["Malkavian", "Toreador", "Tremere", "Tzimisce"],
        "retest_ability": "Investigation",
        "powers": [
            ("Heightened Senses", "Basic", 1),
            ("Aura Perception", "Basic", 2),
            ("Spirit's Touch", "Intermediate", 3),
            ("Telepathy", "Intermediate", 4),
            ("Psychic Projection", "Advanced", 5),
        ]
    },
    {
        "name": "Celerity",
        "pages": (128, 130),
        "clans": ["Assamite", "Brujah", "Toreador"],
        "retest_ability": None,
        "powers": [
            ("Alacrity", "Basic", 1),
            ("Swiftness", "Basic", 2),
            ("Rapidity", "Intermediate", 3),
            ("Legerity", "Intermediate", 4),
            ("Fleetness", "Advanced", 5),
        ]
    },
    {
        "name": "Chimerstry",
        "pages": (129, 132),
        "clans": ["Ravnos"],
        "retest_ability": "Subterfuge",
        "powers": [
            ("Ignis Fatuus", "Basic", 1),
            ("Fata Morgana", "Basic", 2),
            ("Apparition", "Intermediate", 3),
            ("Permanency", "Intermediate", 4),
            ("Horrid Reality", "Advanced", 5),
        ]
    },
    {
        "name": "Dementation",
        "pages": (131, 134),
        "clans": ["Malkavian"],
        "retest_ability": "Empathy",
        "powers": [
            ("Passion", "Basic", 1),
            ("The Haunting", "Basic", 2),
            ("Eyes of Chaos", "Intermediate", 3),
            ("Voice of Madness", "Intermediate", 4),
            ("Total Insanity", "Advanced", 5),
        ]
    },
    {
        "name": "Dominate",
        "pages": (133, 136),
        "clans": ["Giovanni", "Lasombra", "Tremere", "Ventrue"],
        "retest_ability": "Intimidation",
        "powers": [
            ("Command", "Basic", 1),
            ("Mesmerism", "Basic", 2),
            ("Forgetful Mind", "Intermediate", 3),
            ("Conditioning", "Intermediate", 4),
            ("Possession", "Advanced", 5),
        ]
    },
    {
        "name": "Fortitude",
        "pages": (135, 137),
        "clans": ["Gangrel", "Ravnos", "Ventrue"],
        "retest_ability": "Survival",
        "powers": [
            ("Endurance", "Basic", 1),
            ("Mettle", "Basic", 2),
            ("Resilience", "Intermediate", 3),
            ("Resistance", "Intermediate", 4),
            ("Aegis", "Advanced", 5),
        ]
    },
    {
        "name": "Melpominee",
        "pages": (137, 139),
        "clans": ["Daughters of Cacophony"],
        "retest_ability": "Performance",
        "powers": [
            ("The Missing Voice", "Basic", 1),
            ("Phantom Speaker", "Basic", 2),
            ("Madrigal", "Intermediate", 3),
            ("Siren's Beckoning", "Intermediate", 4),
            ("Virtuosa", "Advanced", 5),
        ]
    },
    {
        "name": "Obeah",
        "pages": (144, 146),
        "clans": ["Salubri"],
        "retest_ability": "Medicine",
        "powers": [
            ("Sense Vitality", "Basic", 1),
            ("Anesthetic Touch", "Basic", 2),
            ("Corpore Sano", "Intermediate", 3),
            ("Mens Sana", "Intermediate", 4),
            ("Unburdening the Bestial Soul", "Advanced", 5),
        ]
    },
    {
        "name": "Obfuscate",
        "pages": (146, 149),
        "clans": ["Assamite", "Followers of Set", "Malkavian", "Nosferatu"],
        "retest_ability": "Stealth",
        "powers": [
            ("Cloak of Shadows", "Basic", 1),
            ("Unseen Presence", "Basic", 2),
            ("Mask of a Thousand Faces", "Intermediate", 3),
            ("Vanish from the Mind's Eye", "Intermediate", 4),
            ("Cloak the Gathering", "Advanced", 5),
        ]
    },
    {
        "name": "Obtenebration",
        "pages": (149, 152),
        "clans": ["Lasombra"],
        "retest_ability": "Occult",
        "powers": [
            ("Shadow Play", "Basic", 1),
            ("Shroud of Night", "Basic", 2),
            ("Arms of the Abyss", "Intermediate", 3),
            ("Black Metamorphosis", "Intermediate", 4),
            ("Tenebrous Form", "Advanced", 5),
        ]
    },
    {
        "name": "Potence",
        "pages": (151, 153),
        "clans": ["Brujah", "Giovanni", "Lasombra", "Nosferatu"],
        "retest_ability": None,
        "powers": [
            ("Prowess", "Basic", 1),
            ("Might", "Basic", 2),
            ("Vigor", "Intermediate", 3),
            ("Intensity", "Intermediate", 4),
            ("Puissance", "Advanced", 5),
        ]
    },
    {
        "name": "Presence",
        "pages": (153, 155),
        "clans": ["Brujah", "Followers of Set", "Toreador", "Ventrue"],
        "retest_ability": "Leadership",
        "powers": [
            ("Awe", "Basic", 1),
            ("Dread Gaze", "Basic", 2),
            ("Entrancement", "Intermediate", 3),
            ("Summon", "Intermediate", 4),
            ("Majesty", "Advanced", 5),
        ]
    },
    {
        "name": "Protean",
        "pages": (154, 157),
        "clans": ["Gangrel"],
        "retest_ability": "Survival",
        "powers": [
            ("Eyes of the Beast", "Basic", 1),
            ("Feral Claws", "Basic", 2),
            ("Earth Meld", "Intermediate", 3),
            ("Shape of the Beast", "Intermediate", 4),
            ("Mist Form", "Advanced", 5),
        ]
    },
    {
        "name": "Quietus",
        "pages": (156, 158),
        "clans": ["Assamite"],
        "retest_ability": "Athletics",
        "powers": [
            ("Silence of Death", "Basic", 1),
            ("Scorpion's Touch", "Basic", 2),
            ("Dagon's Call", "Intermediate", 3),
            ("Baal's Caress", "Intermediate", 4),
            ("Taste of Death", "Advanced", 5),
        ]
    },
    {
        "name": "Serpentis",
        "pages": (158, 160),
        "clans": ["Followers of Set"],
        "retest_ability": "Dodge",
        "powers": [
            ("The Eyes of the Serpent", "Basic", 1),
            ("The Tongue of the Asp", "Basic", 2),
            ("The Skin of the Adder", "Intermediate", 3),
            ("The Form of the Cobra", "Intermediate", 4),
            ("The Heart of Darkness", "Advanced", 5),
        ]
    },
    {
        "name": "Thanatosis",
        "pages": (159, 161),
        "clans": ["Samedi"],
        "retest_ability": "Occult",
        "powers": [
            ("Hags' Wrinkles", "Basic", 1),
            ("Putrefaction", "Basic", 2),
            ("Ashes to Ashes", "Intermediate", 3),
            ("Withering", "Intermediate", 4),
            ("Necrosis", "Advanced", 5),
        ]
    },
    {
        "name": "Vicissitude",
        "pages": (171, 173),
        "clans": ["Tzimisce"],
        "retest_ability": "Medicine",
        "powers": [
            ("Malleable Visage", "Basic", 1),
            ("Fleshcraft", "Basic", 2),
            ("Bonecraft", "Intermediate", 3),
            ("Horrid Form", "Intermediate", 4),
            ("Bloodform", "Advanced", 5),
        ]
    },
]


# ---------------------------------------------------------------------------
# Thaumaturgy / Necromancy path definitions
# ---------------------------------------------------------------------------

THAUMATURGY_PATHS = [
    {
        "name": "Path of Blood",
        "alt_name": "Rego Vitae",
        "pages": (161, 163),
        "retest_ability": "Occult",
        "powers": [
            ("A Taste for Blood", "Basic", 1),
            ("Blood Rage", "Basic", 2),
            ("Blood of Potency", "Intermediate", 3),
            ("Theft of Vitae", "Intermediate", 4),
            ("Cauldron of Blood", "Advanced", 5),
        ]
    },
    {
        "name": "Lure of Flames",
        "alt_name": "Creo Ignem",
        "pages": (162, 164),
        "retest_ability": "Occult",
        "powers": [
            ("Hand of Flame", "Basic", 1),
            ("Flame Bolt", "Basic", 2),
            ("Wall of Fire", "Intermediate", 3),
            ("Engulf", "Intermediate", 4),
            ("Firestorm", "Advanced", 5),
        ]
    },
    {
        "name": "Movement of the Mind",
        "alt_name": "Rego Motus",
        "pages": (164, 166),
        "retest_ability": "Occult",
        "powers": [
            ("Force Bolt", "Basic", 1),
            ("Manipulate", "Basic", 2),
            ("Flight", "Intermediate", 3),
            ("Repulse", "Intermediate", 4),
            ("Control", "Advanced", 5),
        ]
    },
    {
        "name": "Conjuring",
        "alt_name": None,
        "pages": (166, 168),
        "retest_ability": "Occult",
        "powers": [
            ("Summon the Simple Form", "Basic", 1),
            ("Permanency", "Basic", 2),
            ("Magic of the Smith", "Intermediate", 3),
            ("Reverse Conjuration", "Intermediate", 4),
            ("Power Over Life", "Advanced", 5),
        ]
    },
    {
        "name": "Hands of Destruction",
        "alt_name": None,
        "pages": (167, 169),
        "retest_ability": "Occult",
        "powers": [
            ("Decay", "Basic", 1),
            ("Gnarl Wood", "Basic", 2),
            ("Acidic Touch", "Intermediate", 3),
            ("Turn to Dust", "Advanced", 4),
        ]
    },
]

NECROMANCY_PATHS = [
    {
        "name": "Sepulchre Path",
        "pages": (139, 141),
        "retest_ability": "Occult",
        "powers": [
            ("Insight", "Basic", 1),
            ("Summon Soul", "Basic", 2),
            ("Compel Soul", "Intermediate", 3),
            ("Haunting", "Intermediate", 4),
            ("Torment", "Advanced", 5),
        ]
    },
    {
        "name": "Ash Path",
        "pages": (140, 142),
        "retest_ability": "Occult",
        "powers": [
            ("Shroudsight", "Basic", 1),
            ("Lifeless Tongues", "Basic", 2),
            ("Dead Hand", "Intermediate", 3),
            ("Ex Nihilo", "Intermediate", 4),
            ("Shroud Mastery", "Advanced", 5),
        ]
    },
    {
        "name": "Bone Path",
        "pages": (141, 143),
        "retest_ability": "Occult",
        "powers": [
            ("Tremens", "Basic", 1),
            ("Apprentice's Brooms", "Basic", 2),
            ("Shambling Hordes", "Intermediate", 3),
            ("Soul Stealing", "Intermediate", 4),
            ("Daemonic Possession", "Advanced", 5),
        ]
    },
]


# ---------------------------------------------------------------------------
# Merits and Flaws definitions
# ---------------------------------------------------------------------------

MERITS_DEFS = {
    "Physical": [
        ("Eat Food", 1),
        ("Blush of Health", 2),
        ("Enchanting Voice", 2),
        ("Daredevil", 3),
        ("Efficient Digestion", 3),
        ("Huge Size", 4),
    ],
    "Mental": [
        ("Common Sense", 1),
        ("Concentration", 1),
        ("Time Sense", 1),
        ("Code of Honor", 2),
        ("Eidetic Memory", 2),
        ("Light Sleeper", 2),
        ("Natural Linguist", 2),
        ("Calm Heart", 3),
        ("Iron Will", 3),
    ],
    "Social": [
        ("Natural Leader", 1),
        ("Prestigious Sire", 1),
        ("Debt of Gratitude", 1),  # 1-3 variable
    ],
    "Supernatural": [
        ("Magic Resistance", 2),
        ("Medium", 2),
        ("Lucky", 3),
        ("Oracular Ability", 3),
        ("Spirit Mentor", 3),
        ("Unbondable", 3),
        ("True Love", 4),
        ("Nine Lives", 6),
        ("True Faith", 7),
    ],
}

FLAWS_DEFS = {
    "Physical": [
        ("Hard of Hearing", 1),
        ("Short", 1),
        ("Smell Of The Grave", 1),
        ("Bad Sight", 1),  # 1-3 variable
        ("Fourteenth Generation", 2),
        ("Disfigured", 2),
        ("One Eye", 2),
        ("Addiction", 3),
        ("Child", 3),
        ("Deformity", 3),
        ("Infections Bite", 3),
        ("Lame", 3),
        ("Monstrous", 3),
        ("Permanent Wound", 3),
        ("Slow Healing", 3),
        ("Deaf", 4),
        ("Disease Carrier", 4),
        ("Mute", 4),
        ("Thin Blood", 4),
        ("Flesh of The Corpse", 5),
        ("Blind", 6),
    ],
    "Mental": [
        ("Deep Sleeper", 1),
        ("Nightmares", 1),
        ("Prey Exclusion", 1),
        ("Shy", 1),
        ("Soft-Hearted", 1),
        ("Speech Impediment", 1),
        ("Amnesia", 2),
        ("Lunacy", 2),
        ("Phobia", 2),
        ("Shortfuse", 2),
        ("Territorial", 2),
        ("Vengeful", 2),
        ("Weak Willed", 3),
        ("Conspicuous Consumption", 4),
    ],
    "Social": [
        ("Dark Secret", 1),
        ("Enemy", 1),  # 1-5 variable
        ("Infamous Sire", 1),
        ("Mistaken Identity", 1),
        ("Sire's Resentment", 1),
        ("Hunted", 4),
        ("Probationary Sect Member", 4),
    ],
    "Supernatural": [
        ("Cast No Reflection", 1),
        ("Cursed", 1),  # 1-5 variable
        ("Repulsed by Garlic", 1),
        ("Touch of Frost", 1),
        ("Eerie Presence", 2),
        ("Can't Cross Running Water", 3),
        ("Haunted", 3),
        ("Repelled by Crosses", 3),
        ("Grip of the Damned", 4),
        ("Dark Fate", 5),
        ("Light-Sensitive", 5),
    ],
}


BACKGROUNDS_LIST = [
    "Allies", "Contacts", "Fame", "Generation", "Herd",
    "Influence", "Mentor", "Resources", "Retainers", "Status",
]

ABILITIES_LIST = [
    "Academics", "Animal Ken", "Athletics", "Awareness", "Brawl",
    "Computer", "Crafts", "Dodge", "Drive", "Empathy",
    "Etiquette", "Expression", "Finance", "Firearms",
    "Intimidation", "Investigation",
    "Law", "Leadership", "Linguistics", "Medicine", "Melee",
    "Occult", "Performance", "Politics", "Repair", "Science",
    "Scrounge", "Security", "Stealth", "Streetwise", "Subterfuge", "Survival",
]


# ---------------------------------------------------------------------------
# Thaumaturgy / Necromancy ritual definitions
# ---------------------------------------------------------------------------

THAUM_RITUALS = {
    "Basic": [
        "Communicate with Kindred Sire",
        "Defense of the Sacred Haven",
        "Deflection of Wooden Doom",
        "Devil's Touch",
        "The Open Passage",
        "Principal Focus of Vitae Infusion",
        "Scent of the Lupine's Passing",
        "Wake with Evening's Freshness",
        "Ward versus Ghouls",
    ],
    "Intermediate": [
        "Bone of Lies",
        "Incorporeal Passage",
        "Pavis of Foul Presence",
        "Rutor's Hands",
        "Soul of the Homunculi",
    ],
    "Advanced": [
        "Blood Contract",
        "Nectar of the Bitter Rose",
        "Umbra Walk",
    ],
}

NECRO_RITUALS = {
    "Basic": [
        "Call of the Hungry Dead",
        "Eyes of the Grave",
        "Spirit Beacon",
    ],
    "Intermediate": [
        "Cadaver's Touch",
        "Call On the Shadow's Grace",
        "Ritual of the Unearthed Fetter",
    ],
    "Advanced": [
        "Grasp the Ghostly",
    ],
}


# ---------------------------------------------------------------------------
# Extraction functions
# ---------------------------------------------------------------------------

def extract_power_text(doc, full_text, power_name, next_power_name, start_page, end_page):
    """Extract description text for a single power from the section text."""
    # Try to find the power name as a heading (standalone line or after a newline)
    # Prefer the version that appears after a tier marker or on its own line
    search_variants = [
        power_name,
        power_name.replace("'", "\u2019"),
        power_name.replace("'", "\u2018"),
    ]

    idx = -1
    for variant in search_variants:
        # Look for it as a standalone heading: "\nPowerName\n"
        heading_pattern = '\n' + variant + '\n'
        idx = full_text.find(heading_pattern)
        if idx != -1:
            idx += 1  # skip the leading newline
            break
        # Also try "\nPowerName." or "\nPowerName "
        for suffix in ['.', ' ']:
            heading_pattern2 = '\n' + variant + suffix
            idx = full_text.find(heading_pattern2)
            if idx != -1:
                idx += 1
                break
        if idx != -1:
            break

    if idx == -1:
        # Fallback: find last occurrence (often the heading is after intro text)
        for variant in search_variants:
            # Find all occurrences and pick the one that looks most like a heading
            pos = 0
            best_idx = -1
            while True:
                found = full_text.find(variant, pos)
                if found == -1:
                    break
                # Check if it's at start of a line
                if found == 0 or full_text[found - 1] == '\n':
                    best_idx = found
                    break
                pos = found + 1
                best_idx = found  # keep last found as fallback
            if best_idx != -1:
                idx = best_idx
                break

    if idx == -1:
        # Case-insensitive fallback
        lower = full_text.lower()
        idx = lower.find(power_name.lower())

    if idx == -1:
        return f"[Text for {power_name} not found in pages {start_page}-{end_page}]"

    # Start from just after the power name heading
    text_start = idx + len(power_name)

    # Find end: next power name or end of section
    if next_power_name:
        # Search for next power as a heading too
        next_variants = [
            next_power_name,
            next_power_name.replace("'", "\u2019"),
            next_power_name.replace("'", "\u2018"),
        ]
        end_idx = -1
        for nv in next_variants:
            # Try as heading first
            for prefix in ['\n']:
                ni = full_text.find(prefix + nv, text_start)
                if ni != -1:
                    end_idx = ni + len(prefix)
                    break
            if end_idx != -1:
                break
            # Plain search fallback
            ni = full_text.find(nv, text_start)
            if ni != -1:
                end_idx = ni
                break
        if end_idx == -1:
            # Also check for tier headers before next power
            end_idx = len(full_text)
    else:
        end_idx = len(full_text)

    description = full_text[text_start:end_idx].strip()
    # Remove tier headers that may appear at start (e.g. "Basic Animalism")
    description = re.sub(r'^(Basic|Intermediate|Advanced)\s+[\w\s]+?\n', '', description, count=1).strip()
    return clean_text(description)


def extract_discipline(doc, disc_def):
    """Extract a single discipline with all its powers."""
    start_page, end_page = disc_def["pages"]
    full_text = get_pages_text(doc, start_page, end_page)

    powers = []
    power_list = disc_def["powers"]
    for i, (name, tier, order) in enumerate(power_list):
        next_name = power_list[i + 1][0] if i + 1 < len(power_list) else None

        # For the next power, we also need to search for tier headers
        # that may precede it
        description = extract_power_text(doc, full_text, name, next_name, start_page, end_page)
        page = find_page_for_text(doc, name, start_page, end_page)

        powers.append({
            "name": name,
            "tier": tier,
            "order": order,
            "page": page,
            "description": description,
        })

    result = {
        "clans": disc_def["clans"],
        "retest_ability": disc_def["retest_ability"],
        "powers": powers,
    }
    return result


def extract_path(doc, path_def):
    """Extract a thaumaturgy or necromancy path."""
    start_page, end_page = path_def["pages"]
    full_text = get_pages_text(doc, start_page, end_page)

    powers = []
    power_list = path_def["powers"]
    for i, (name, tier, order) in enumerate(power_list):
        next_name = power_list[i + 1][0] if i + 1 < len(power_list) else None
        description = extract_power_text(doc, full_text, name, next_name, start_page, end_page)
        page = find_page_for_text(doc, name, start_page, end_page)

        powers.append({
            "name": name,
            "tier": tier,
            "order": order,
            "page": page,
            "description": description,
        })

    result = {
        "alt_name": path_def.get("alt_name"),
        "retest_ability": path_def["retest_ability"],
        "powers": powers,
    }
    return result


def extract_merit_or_flaw(doc, name, trait_cost, pages_start, pages_end):
    """Extract a single merit or flaw description."""
    full_text = get_pages_text(doc, pages_start, pages_end)

    # Search for the merit/flaw name followed by trait info
    # Common patterns: "Name (X Trait Merit)" or "Name(X Trait Flaw)"
    patterns = [
        name,
        name.replace("'", "\u2019"),
        name.replace("'", "\u2018"),
    ]

    idx = -1
    for pat in patterns:
        idx = full_text.find(pat)
        if idx != -1:
            break
    if idx == -1:
        idx = full_text.lower().find(name.lower())

    if idx == -1:
        return {
            "name": name,
            "trait_cost": trait_cost,
            "description": f"[Text for {name} not found]",
            "page": pages_start,
        }

    # Find the description after the name and cost indicator
    text_after = full_text[idx:]
    # Skip past the name and trait cost line
    # Look for pattern like "Name (X Trait Merit/Flaw)" then grab text after
    match = re.search(r'(?:Trait\s+(?:Merit|Flaw)\s*\)?)\s*', text_after, re.IGNORECASE)
    if match:
        desc_start = match.end()
    else:
        desc_start = len(name)

    # Find end: next merit/flaw entry (pattern: "Word (N Trait")
    remaining = text_after[desc_start:]
    # Look for next entry pattern
    next_entry = re.search(r'\n\s*[A-Z][A-Za-z\s\'\u2019-]+\s*\(\s*\d+\s*(?:to\s+\d+\s+)?Trait', remaining)
    if next_entry:
        description = remaining[:next_entry.start()]
    else:
        # Also look for section headers like "Mental Merits and Flaws" etc.
        next_section = re.search(r'\n\s*(?:Mental|Social|Supernatural|Physical)\s+(?:Merits|Flaws)', remaining)
        if next_section:
            description = remaining[:next_section.start()]
        else:
            description = remaining[:500]  # fallback: take reasonable chunk

    page = find_page_for_text(doc, name, pages_start, pages_end)
    return {
        "name": name,
        "trait_cost": trait_cost,
        "description": clean_text(description),
        "page": page,
    }


def extract_background(doc, name, pages_start=86, pages_end=96):
    """Extract a single background description."""
    # Generation is on page 88, Allies on 86-87
    # Use broader range to find all backgrounds
    full_text = get_pages_text(doc, 86, 96)

    idx = full_text.find(name + '\n')
    if idx == -1:
        idx = full_text.find(name)
    if idx == -1:
        idx = full_text.lower().find(name.lower())

    if idx == -1:
        # Try even broader range
        full_text = get_pages_text(doc, 67, 96)
        idx = full_text.find(name + '\n')
        if idx == -1:
            idx = full_text.find(name)
        if idx == -1:
            return {"name": name, "description": f"[Text for {name} not found]", "page": pages_start}

    text_after = full_text[idx + len(name):]

    # Find next background entry or section break
    bg_names = ["Allies", "Contacts", "Fame", "Generation", "Herd",
                "Influence", "Mentor", "Resources", "Retainers", "Status"]
    other_bgs = [b for b in bg_names if b != name]
    bg_pattern = '|'.join(re.escape(b) for b in other_bgs)
    next_bg = re.search(rf'\n(?:{bg_pattern})\b', text_after)
    if next_bg:
        description = text_after[:next_bg.start()]
    else:
        # Also check for section breaks
        next_section = re.search(r'\n(?:Disciplines|Chapter|Abilities)\b', text_after)
        if next_section:
            description = text_after[:next_section.start()]
        else:
            description = text_after[:1500]

    page = find_page_for_text(doc, name, 86, 96)
    if page == 86 and name in ["Allies", "Generation"]:
        page = find_page_for_text(doc, name, 67, 96)

    return {
        "name": name,
        "description": clean_text(description),
        "page": page,
    }


def extract_ability(doc, name, pages_start=80, pages_end=86):
    """Extract a single ability description."""
    full_text = get_pages_text(doc, pages_start, pages_end)

    idx = full_text.find(name)
    if idx == -1:
        idx = full_text.lower().find(name.lower())
    if idx == -1:
        return {"name": name, "description": f"[Text for {name} not found]", "page": pages_start}

    text_after = full_text[idx + len(name):]

    # Find next ability entry: a line starting with a capitalized word that matches known abilities
    ability_pattern = '|'.join(re.escape(a) for a in ABILITIES_LIST if a != name)
    next_ability = re.search(rf'\n(?:{ability_pattern})\b', text_after)
    if next_ability:
        description = text_after[:next_ability.start()]
    else:
        description = text_after[:600]

    page = find_page_for_text(doc, name, pages_start, pages_end)
    return {
        "name": name,
        "description": clean_text(description),
        "page": page,
    }


def extract_rituals(doc, ritual_defs, ritual_type, pages_start, pages_end):
    """Extract rituals for Thaumaturgy or Necromancy."""
    full_text = get_pages_text(doc, pages_start, pages_end)

    # Build a flat list of all ritual names for boundary detection
    all_names = []
    for tier_rituals in ritual_defs.values():
        all_names.extend(tier_rituals)

    rituals = []
    for tier, ritual_names in ritual_defs.items():
        for rname in ritual_names:
            idx = full_text.find(rname)
            if idx == -1:
                for variant in [rname.replace("'", "\u2019"), rname.replace("'", "\u2018")]:
                    idx = full_text.find(variant)
                    if idx != -1:
                        break
            if idx == -1:
                idx = full_text.lower().find(rname.lower())

            if idx == -1:
                rituals.append({
                    "name": rname,
                    "tier": tier,
                    "type": ritual_type,
                    "description": f"[Text for {rname} not found]",
                    "page": pages_start,
                })
                continue

            text_after = full_text[idx + len(rname):]

            # Find next ritual or section boundary
            other_names = [n for n in all_names if n != rname]
            best_end = len(text_after)
            for other in other_names:
                oidx = text_after.find(other)
                if oidx == -1:
                    oidx = text_after.lower().find(other.lower())
                if oidx != -1 and oidx < best_end:
                    best_end = oidx

            # Also check for section boundaries
            section_break = re.search(r'\n(?:Vicissitude|Obeah|The\s+\w+\s+Path|Advanced\s+Rituals|Intermediate\s+Rituals|Basic\s+Rituals)', text_after)
            if section_break and section_break.start() < best_end:
                best_end = section_break.start()

            description = text_after[:best_end].strip()
            page = find_page_for_text(doc, rname, pages_start, pages_end)

            rituals.append({
                "name": rname,
                "tier": tier,
                "type": ritual_type,
                "description": clean_text(description),
                "page": page,
            })

    return rituals


def main():
    print(f"Opening PDF: {os.path.abspath(PDF_PATH)}")
    doc = fitz.open(PDF_PATH)
    print(f"Total pages: {len(doc)}")

    data = {
        "source_book": "Laws of the Night Revised",
        "disciplines": {},
        "thaumaturgy_paths": {},
        "necromancy_paths": {},
        "rituals": {
            "Thaumaturgy": [],
            "Necromancy": [],
        },
        "merits": {},
        "flaws": {},
        "backgrounds": [],
        "abilities": [],
    }

    # --- Disciplines ---
    print("\nExtracting disciplines...")
    for disc_def in DISCIPLINE_DEFS:
        name = disc_def["name"]
        print(f"  {name} (pages {disc_def['pages'][0]}-{disc_def['pages'][1]})")
        data["disciplines"][name] = extract_discipline(doc, disc_def)

    # --- Thaumaturgy Paths ---
    print("\nExtracting Thaumaturgy paths...")
    for path_def in THAUMATURGY_PATHS:
        name = path_def["name"]
        print(f"  {name} (pages {path_def['pages'][0]}-{path_def['pages'][1]})")
        data["thaumaturgy_paths"][name] = extract_path(doc, path_def)

    # --- Necromancy Paths ---
    print("\nExtracting Necromancy paths...")
    for path_def in NECROMANCY_PATHS:
        name = path_def["name"]
        print(f"  {name} (pages {path_def['pages'][0]}-{path_def['pages'][1]})")
        data["necromancy_paths"][name] = extract_path(doc, path_def)

    # --- Rituals ---
    print("\nExtracting Thaumaturgy rituals...")
    data["rituals"]["Thaumaturgy"] = extract_rituals(doc, THAUM_RITUALS, "Thaumaturgy", 168, 171)

    print("Extracting Necromancy rituals...")
    data["rituals"]["Necromancy"] = extract_rituals(doc, NECRO_RITUALS, "Necromancy", 143, 145)

    # --- Merits ---
    print("\nExtracting merits...")
    for category, merit_list in MERITS_DEFS.items():
        data["merits"][category] = []
        for mname, cost in merit_list:
            entry = extract_merit_or_flaw(doc, mname, cost, 103, 111)
            data["merits"][category].append(entry)
            print(f"  [{category}] {mname}: {len(entry['description'])} chars")

    # --- Flaws ---
    print("\nExtracting flaws...")
    for category, flaw_list in FLAWS_DEFS.items():
        data["flaws"][category] = []
        for fname, cost in flaw_list:
            entry = extract_merit_or_flaw(doc, fname, cost, 103, 111)
            data["flaws"][category].append(entry)
            print(f"  [{category}] {fname}: {len(entry['description'])} chars")

    # --- Backgrounds ---
    print("\nExtracting backgrounds...")
    for bg_name in BACKGROUNDS_LIST:
        entry = extract_background(doc, bg_name)
        data["backgrounds"].append(entry)
        print(f"  {bg_name}: {len(entry['description'])} chars")

    # --- Abilities ---
    print("\nExtracting abilities...")
    for ab_name in ABILITIES_LIST:
        entry = extract_ability(doc, ab_name)
        data["abilities"].append(entry)
        print(f"  {ab_name}: {len(entry['description'])} chars")

    # --- Write JSON ---
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nJSON written to: {os.path.abspath(OUTPUT_PATH)}")

    # --- Verification ---
    print("\n=== VERIFICATION ===")
    disc_count = sum(len(d['powers']) for d in data.get('disciplines', {}).values())
    print(f"Disciplines: {len(data.get('disciplines', {}))} types, {disc_count} powers")
    print(f"Thaum Paths: {len(data.get('thaumaturgy_paths', {}))}")
    print(f"Necro Paths: {len(data.get('necromancy_paths', {}))}")
    thaum_power_count = sum(len(p['powers']) for p in data.get('thaumaturgy_paths', {}).values())
    necro_power_count = sum(len(p['powers']) for p in data.get('necromancy_paths', {}).values())
    print(f"Thaum Path Powers: {thaum_power_count}")
    print(f"Necro Path Powers: {necro_power_count}")
    thaum_ritual_count = len(data.get('rituals', {}).get('Thaumaturgy', []))
    necro_ritual_count = len(data.get('rituals', {}).get('Necromancy', []))
    print(f"Thaum Rituals: {thaum_ritual_count}")
    print(f"Necro Rituals: {necro_ritual_count}")
    merit_count = sum(len(m) for m in data.get('merits', {}).values())
    flaw_count = sum(len(f) for f in data.get('flaws', {}).values())
    print(f"Merits: {merit_count}, Flaws: {flaw_count}")
    print(f"Backgrounds: {len(data.get('backgrounds', []))}")
    print(f"Abilities: {len(data.get('abilities', []))}")

    # Check for empty/missing descriptions
    missing = []
    for dname, ddata in data['disciplines'].items():
        for p in ddata['powers']:
            if '[Text for' in p['description'] or len(p['description']) < 20:
                missing.append(f"Discipline {dname}: {p['name']}")
    for pname, pdata in data['thaumaturgy_paths'].items():
        for p in pdata['powers']:
            if '[Text for' in p['description'] or len(p['description']) < 20:
                missing.append(f"Thaum Path {pname}: {p['name']}")
    for pname, pdata in data['necromancy_paths'].items():
        for p in pdata['powers']:
            if '[Text for' in p['description'] or len(p['description']) < 20:
                missing.append(f"Necro Path {pname}: {p['name']}")
    for rtype, rituals in data['rituals'].items():
        for r in rituals:
            if '[Text for' in r['description'] or len(r['description']) < 20:
                missing.append(f"Ritual {rtype}: {r['name']}")

    if missing:
        print(f"\nWARNING: {len(missing)} entries with missing/short descriptions:")
        for m in missing:
            print(f"  - {m}")
    else:
        print("\nAll entries have descriptions!")

    doc.close()


if __name__ == '__main__':
    main()
