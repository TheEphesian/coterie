When adding traits, should be a menu of available options or the ability to add custom traits. Traits are found in laws of the night. 
When adding multiple levels, levels currently show separately. If i add two levels of the melee ability, it should show as Melee x2. 
Abilities should be in some sort of menu i can add from a list of pre-populated items or the ability to add custom. 
no space for negative traits (reference Laws of the night text for negative traits) 
Merits should not say "enter trait name" when entering. This should have a "Merit" and "Point cost" - these point costs are single cost when purchased at character creation and double cost when purchased afterwards. Allow the user to manually adjust the point cost. There is a document of all powers / abilities / merits / etc in json format that have been pulled from Laws of the night. This should be incorporated. 

going through new character, when you are done and press next you get this error: Error loading character: Parent instance <Vampire at 0x76f5ba8696d0> is not bound to a Session; lazy load operation of attribute 'chronicle' cannot proceed (Background on this error at: https://sqlalche.me/e/20/bhk3)

This brings you to the main ui in that character sheet's tab. Clicking save from here exits the program. ╰─❯ python3 run_ui.py
Traceback (most recent call last):
  File "/mnt/d/TheEdge/KingmakerTM/Coterie/src/ui/main_window.py", line 533, in _open_character
    if character.id in self.open_character_sheets:
       ^^^^^^^^^^^^
AttributeError: 'int' object has no attribute 'id'
Aborted (core dumped)


Chronicles on first page should have be in card format. List chronicle name and HST. Use a bigger font and make them easier to see. Characters should also be bound to chronicles. When double clicking on a chronicle, bring up the character listing for that chronicle. 
