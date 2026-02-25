When making a new chronicle. Populated Name / HST / Description. Pressed "Create Chronicle" Got Error: Failed to Create chronicle: 'narrator' is an invalid keyword argument for Chronicle
When making character, Abilities should not be split into Talents Skills and Knowledges. Adding multiple of the same ability results in error - should be able to add multiple levels of abilities. 
Adding common Talents - the talents added are actually traits (they're from all three categories and in the wrong place)
Adding Common Skills - Crafty isn't a thing. "Stealthy" should be "Stealth" and "Technical" isn't a thing. Where are these adjectives pulled from? 
Knowledges (adding common) - Academics should be Academics. Where are these being pulled from? 
In all of these, you can't add multiple levels of the same discipline / background etc. 
The advantages tab should just be disciplines. We should then split out other tabs - Backgrounds / Merits / Flaws / Status / Virtues. Vampire sheet is missing blood / willpower and should also have Sire. Check the grapevine sheets for what fields are missing in which character types - this test is only vampire. 

When pressing OK on character creation "Viewing Character Characters is not yet implemented"

in top menu, selecting STAFF MANAGER exits the program. 
Failed to create chronicle: 'narrator' is an invalid keyword argument for Chronicle
Error preparing character for UI: Object '<Character at 0x749c7825b0e0>' is already attached to session '4' (this is '5')
Traceback (most recent call last):
  File /mnt/d/TheEdge/KingmakerTM/Coterie/src/ui/main_window.py, line 900, in _show_staff_manager
    from src.ui.dialogs.staff_manager import StaffManagerDialog
  File /mnt/d/TheEdge/KingmakerTM/Coterie/src/ui/dialogs/staff_manager.py, line 11, in <module>
    from ...models.chronicle import Chronicle
ModuleNotFoundError: No module named 'src.models'
Aborted (core dumped)
