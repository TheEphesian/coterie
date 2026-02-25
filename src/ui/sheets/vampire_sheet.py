"""Vampire character sheet display for Coterie.

This module implements the character sheet interface for Vampire: The Masquerade
characters, displaying all relevant attributes, abilities, and other traits using
the Mind's Eye Theater LARP adjective-based trait system.
"""

from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QSpinBox, QGroupBox,
    QScrollArea, QPushButton, QTabWidget, QFrame, QGridLayout,
    QComboBox, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from src.core.models.vampire import Vampire
from src.core.models.larp_trait import LarpTrait, TraitCategory
from src.utils.data_loader import load_character, prepare_character_for_ui
from src.ui.widgets.larp_trait_widget import LarpTraitWidget, LarpTraitCategoryWidget

class VampireSheet(QWidget):
    """Character sheet display for Vampire: The Masquerade LARP characters."""

    modified = pyqtSignal()
    character_changed = pyqtSignal()

    def __init__(self, parent=None):
        """Initialize the vampire character sheet.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Store character reference
        self.character = None
        self.character_id = None

        # Set up main layout
        self.main_layout = QVBoxLayout(self)

        # Create character info header
        self._create_character_info_section()

        # Create the main content area with scrolling
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.main_layout.addWidget(self.scroll_area)

        # Create content widget for scroll area
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.scroll_area.setWidget(self.content_widget)

        # Create tabs
        self.tabs = QTabWidget()
        self.content_layout.addWidget(self.tabs)

        # === Traits Tab (Attributes + Abilities) ===
        self.traits_tab = QWidget()
        self.traits_layout = QVBoxLayout(self.traits_tab)
        self.tabs.addTab(self.traits_tab, "Traits")

        # Attributes (adjective-based, split Physical/Social/Mental)
        self.attributes = LarpTraitCategoryWidget(
            category_name="Attributes",
            trait_categories={"Physical": [], "Social": [], "Mental": []}
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

        # === Disciplines Tab ===
        self.disciplines_tab = QWidget()
        self.disciplines_layout = QVBoxLayout(self.disciplines_tab)
        self.tabs.addTab(self.disciplines_tab, "Disciplines")

        self.disciplines = LarpTraitWidget("Disciplines")
        self.disciplines.traitChanged.connect(lambda n, t: self.modified.emit())
        self.disciplines_layout.addWidget(self.disciplines)

        # === Backgrounds Tab ===
        self.backgrounds_tab = QWidget()
        self.backgrounds_layout = QVBoxLayout(self.backgrounds_tab)
        self.tabs.addTab(self.backgrounds_tab, "Backgrounds")

        self.backgrounds = LarpTraitWidget("Backgrounds")
        self.backgrounds.traitChanged.connect(lambda n, t: self.modified.emit())
        self.backgrounds_layout.addWidget(self.backgrounds)

        # === Virtues & Morality Tab ===
        self.virtues_tab = QWidget()
        self.virtues_layout = QVBoxLayout(self.virtues_tab)
        self.tabs.addTab(self.virtues_tab, "Virtues & Morality")

        self.virtues = LarpTraitCategoryWidget(
            category_name="Virtues",
            trait_categories={"Conscience": [], "Self-Control": [], "Courage": []}
        )
        self.virtues.categoryChanged.connect(lambda c, t: self.modified.emit())
        self.virtues_layout.addWidget(self.virtues)

        path_group = QGroupBox("Path / Morality")
        path_group_layout = QVBoxLayout(path_group)
        self.path_traits = LarpTraitWidget("Path")
        self.path_traits.traitChanged.connect(lambda n, t: self.modified.emit())
        path_group_layout.addWidget(self.path_traits)
        self.virtues_layout.addWidget(path_group)

        # === Status Tab (Willpower, Blood) ===
        self.status_tab = QWidget()
        self.status_layout = QVBoxLayout(self.status_tab)
        self.tabs.addTab(self.status_tab, "Status")

        wp_group = QGroupBox("Willpower")
        wp_group_layout = QVBoxLayout(wp_group)
        self.willpower_widget = LarpTraitWidget("Willpower")
        self.willpower_widget.traitChanged.connect(lambda n, t: self.modified.emit())
        wp_group_layout.addWidget(self.willpower_widget)
        self.status_layout.addWidget(wp_group)

        blood_group = QGroupBox("Blood Pool")
        blood_group_layout = QVBoxLayout(blood_group)
        self.blood_widget = LarpTraitWidget("Blood")
        self.blood_widget.traitChanged.connect(lambda n, t: self.modified.emit())
        blood_group_layout.addWidget(self.blood_widget)
        self.status_layout.addWidget(blood_group)

        # === Merits & Flaws Tab ===
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

        # === Notes Tab ===
        self.notes_tab = QWidget()
        self.notes_layout = QVBoxLayout(self.notes_tab)
        self.tabs.addTab(self.notes_tab, "Notes")

        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Enter character notes here...")
        self.notes_layout.addWidget(self.notes_edit)

        # Add save button
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_character)
        self.main_layout.addWidget(self.save_button)

    def _create_character_info_section(self) -> None:
        """Create the character information section."""
        # Character info group
        info_group = QGroupBox("Character Information")
        info_layout = QFormLayout(info_group)
        self.main_layout.addWidget(info_group)

        # Character name
        self.name = QLineEdit()
        self.name.textChanged.connect(lambda: self.modified.emit())
        info_layout.addRow("Name:", self.name)

        # Player name
        self.player_name = QLineEdit()
        self.player_name.textChanged.connect(lambda: self.modified.emit())
        info_layout.addRow("Player:", self.player_name)

        # Chronicle section
        chronicle_layout = QHBoxLayout()
        self.chronicle_name = QLineEdit()
        self.chronicle_name.setReadOnly(True)  # Chronicle name is read-only
        chronicle_layout.addWidget(self.chronicle_name)

        # Add button to assign a chronicle
        self.assign_chronicle_button = QPushButton("Assign")
        self.assign_chronicle_button.clicked.connect(self._on_assign_chronicle)
        chronicle_layout.addWidget(self.assign_chronicle_button)

        info_layout.addRow("Chronicle:", chronicle_layout)

        # Nature and Demeanor
        self.nature = QLineEdit()
        self.nature.textChanged.connect(lambda: self.modified.emit())
        info_layout.addRow("Nature:", self.nature)

        self.demeanor = QLineEdit()
        self.demeanor.textChanged.connect(lambda: self.modified.emit())
        info_layout.addRow("Demeanor:", self.demeanor)

        # Clan
        self.clan = QLineEdit()
        self.clan.textChanged.connect(lambda: self.modified.emit())
        info_layout.addRow("Clan:", self.clan)

        # Generation
        self.generation = QSpinBox()
        self.generation.setRange(3, 15)
        self.generation.setValue(13)
        self.generation.valueChanged.connect(lambda: self.modified.emit())
        info_layout.addRow("Generation:", self.generation)

        # Sect
        self.sect = QLineEdit()
        self.sect.textChanged.connect(lambda: self.modified.emit())
        info_layout.addRow("Sect:", self.sect)

        # HST (formerly Storyteller)
        self.storyteller = QLineEdit()
        self.storyteller.textChanged.connect(lambda: self.modified.emit())
        info_layout.addRow("HST:", self.storyteller)

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

    def _on_assign_chronicle(self) -> None:
        """Show dialog to assign the character to a chronicle."""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QDialogButtonBox, QLabel, QListWidgetItem
        from PyQt6.QtCore import Qt
        from src.core.engine import get_session
        from src.core.models.chronicle import Chronicle

        # Create a dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Assign Chronicle")
        dialog.setMinimumWidth(400)

        # Create layout
        layout = QVBoxLayout(dialog)

        # Add label
        layout.addWidget(QLabel("Select a chronicle to assign this character to:"))

        # Add list widget
        chronicle_list = QListWidget()
        layout.addWidget(chronicle_list)

        # Add buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        # Get chronicles from database
        session = get_session()
        try:
            chronicles = session.query(Chronicle).all()

            # Add chronicles to list
            for chronicle in chronicles:
                narrator_display = chronicle.narrator or "No HST"
                item = QListWidgetItem(f"{chronicle.name} (HST: {narrator_display})")
                item.setData(Qt.ItemDataRole.UserRole, chronicle.id)
                chronicle_list.addItem(item)

                # Pre-select the current chronicle if set
                if self.character and self.character.chronicle_id == chronicle.id:
                    chronicle_list.setCurrentItem(item)

        finally:
            session.close()

        # Show dialog
        if dialog.exec() == QDialog.DialogCode.Accepted and chronicle_list.currentItem():
            chronicle_id = chronicle_list.currentItem().data(Qt.ItemDataRole.UserRole)

            # Update the character's chronicle
            if self.character:
                session = get_session()
                try:
                    # Store current traits before assignment
                    current_traits = self.character.larp_traits if hasattr(self.character, 'larp_traits') else []

                    # Update chronicle
                    self.character.chronicle_id = chronicle_id

                    # Ensure traits are preserved
                    if hasattr(self.character, 'larp_traits'):
                        self.character.larp_traits = current_traits

                    session.add(self.character)
                    session.commit()

                    # Update the displayed chronicle name
                    chronicle = session.query(Chronicle).filter_by(id=chronicle_id).first()
                    if chronicle:
                        self.chronicle_name.setText(chronicle.name)

                    self.modified.emit()
                finally:
                    session.close()

    def load_character(self, character) -> None:
        """Load a character into the sheet.

        Args:
            character: Character object or character ID (int)
        """
        try:
            # Handle both object and ID
            if isinstance(character, int):
                character = load_character(character)

            if not character:
                QMessageBox.critical(self, "Load Error", "Failed to load character")
                return

            self.character = character
            self.character_id = character.id

            # Update character info section
            self.name.setText(character.name or "")
            self.player_name.setText(character.player_name or "")
            self.clan.setText(character.clan if hasattr(character, 'clan') else "")
            self.generation.setValue(character.generation if hasattr(character, 'generation') else 13)
            self.nature.setText(character.nature or "")
            self.demeanor.setText(character.demeanor or "")
            self.sect.setText(character.sect if hasattr(character, 'sect') else "")
            self.storyteller.setText(character.narrator or "")
            self.sire.setText(character.sire if hasattr(character, 'sire') else "")
            self.title.setText(character.title if hasattr(character, 'title') else "")
            self.concept.setText("")  # No concept field on model yet

            # Chronicle name
            if hasattr(character, 'chronicle') and character.chronicle:
                self.chronicle_name.setText(character.chronicle.name)
            else:
                self.chronicle_name.setText("")

            # Notes
            if hasattr(character, 'notes') and character.notes:
                self.notes_edit.setText(character.notes)

            # Load LARP traits
            self._load_larp_traits(character)

        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"Error loading character: {str(e)}")

    def _load_larp_traits(self, character: Vampire) -> None:
        """Load LARP traits into appropriate widgets by category.

        Args:
            character: Vampire character to load traits from
        """
        # Initialize trait category dictionaries
        attribute_traits = {
            "Physical": [],
            "Social": [],
            "Mental": []
        }

        ability_traits = []

        virtue_traits = {
            "Conscience": [],
            "Self-Control": [],
            "Courage": []
        }

        discipline_traits = []
        background_traits = []
        path_traits = []
        willpower_traits = []
        blood_traits = []
        merit_traits = []
        flaw_traits = []

        # Process all LARP traits if available
        if hasattr(character, 'larp_traits') and character.larp_traits:
            for trait in character.larp_traits:
                # Safety check for categories attribute
                if not hasattr(trait, 'categories'):
                    continue

                # Check each trait's categories
                for category in trait.categories:
                    category_name = category.name.lower()

                    # Handle attributes
                    if category_name == "physical":
                        attribute_traits["Physical"].append(trait.display_name)
                    elif category_name == "social":
                        attribute_traits["Social"].append(trait.display_name)
                    elif category_name == "mental":
                        attribute_traits["Mental"].append(trait.display_name)

                    # Handle abilities (unified flat list)
                    elif category_name in ("abilities", "talents", "skills", "knowledges"):
                        ability_traits.append(trait.display_name)

                    # Handle virtues
                    elif category_name == "conscience":
                        virtue_traits["Conscience"].append(trait.display_name)
                    elif category_name == "self-control":
                        virtue_traits["Self-Control"].append(trait.display_name)
                    elif category_name == "courage":
                        virtue_traits["Courage"].append(trait.display_name)

                    # Handle other types
                    elif category_name == "disciplines":
                        discipline_traits.append(trait.display_name)
                    elif category_name == "backgrounds":
                        background_traits.append(trait.display_name)
                    elif category_name == "path":
                        path_traits.append(trait.display_name)
                    elif category_name == "willpower":
                        willpower_traits.append(trait.display_name)
                    elif category_name == "blood":
                        blood_traits.append(trait.display_name)
                    elif category_name == "merits":
                        merit_traits.append(trait.display_name)
                    elif category_name == "flaws":
                        flaw_traits.append(trait.display_name)

        # Update widgets with collected traits
        self.attributes.set_category_traits(attribute_traits)
        self.abilities.set_traits(ability_traits)
        self.virtues.set_category_traits(virtue_traits)
        self.disciplines.set_traits(discipline_traits)
        self.backgrounds.set_traits(background_traits)
        self.path_traits.set_traits(path_traits)
        self.willpower_widget.set_traits(willpower_traits)
        self.blood_widget.set_traits(blood_traits)
        self.merits.set_traits(merit_traits)
        self.flaws.set_traits(flaw_traits)

    def save_character(self) -> None:
        """Save the current character."""
        if not self.character_id:
            return

        from src.core.engine import get_session
        from src.core.models import Vampire

        session = None
        try:
            session = get_session()
            character = session.query(Vampire).filter(Vampire.id == self.character_id).first()

            if not character:
                QMessageBox.critical(self, "Save Error", f"Failed to load character {self.character_id}")
                return

            # Update basic info
            character.name = self.name.text()
            character.player_name = self.player_name.text()
            character.clan = self.clan.text()
            character.generation = self.generation.value()
            character.nature = self.nature.text()
            character.demeanor = self.demeanor.text()
            character.sect = self.sect.text()
            character.narrator = self.storyteller.text()
            character.sire = self.sire.text()
            character.title = self.title.text()

            # Update notes
            character.notes = self.notes_edit.toPlainText()

            character.last_modified = datetime.now()

            session.commit()
            self.character_changed.emit()

            QMessageBox.information(self, "Save Success", "Character saved successfully.")

        except Exception as e:
            if session:
                session.rollback()
            QMessageBox.critical(self, "Save Error", f"Error saving character: {str(e)}")
        finally:
            if session:
                session.close()

    def get_character_data(self) -> Dict:
        """Get the character data from the sheet.

        Returns:
            Dictionary of character data
        """
        data = {
            "name": self.name.text(),
            "player_name": self.player_name.text(),
            "narrator": self.storyteller.text(),
            "nature": self.nature.text(),
            "demeanor": self.demeanor.text(),
            "clan": self.clan.text(),
            "generation": self.generation.value(),
            "sect": self.sect.text(),
            "sire": self.sire.text(),
            "title": self.title.text(),
            "chronicle_id": self.character.chronicle_id if self.character and hasattr(self.character, 'chronicle_id') else None,
            "larp_traits": self._collect_all_larp_traits()
        }
        return data

    def _collect_all_larp_traits(self) -> Dict:
        """Collect all LARP traits from the sheet.

        Returns:
            Dictionary of trait lists by category
        """
        larp_traits = {}

        # Get attributes
        attribute_traits = self.attributes.get_category_traits()
        for subcategory, traits in attribute_traits.items():
            larp_traits[subcategory.lower()] = traits

        # Get abilities (flat list)
        larp_traits["abilities"] = self.abilities.get_traits()

        # Get virtues
        virtue_traits = self.virtues.get_category_traits()
        for subcategory, traits in virtue_traits.items():
            larp_traits[subcategory.lower()] = traits

        # Get other trait types
        larp_traits["disciplines"] = self.disciplines.get_traits()
        larp_traits["backgrounds"] = self.backgrounds.get_traits()
        larp_traits["path"] = self.path_traits.get_traits()
        larp_traits["willpower"] = self.willpower_widget.get_traits()
        larp_traits["blood"] = self.blood_widget.get_traits()
        larp_traits["merits"] = self.merits.get_traits()
        larp_traits["flaws"] = self.flaws.get_traits()

        return larp_traits
