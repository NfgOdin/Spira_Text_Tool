"""
GUI Dialogs package for FFX & FFX-2 Text & Localization Studio.
"""

from gui.dialogs.about import show_about_dialog
from gui.dialogs.cheat_sheet import show_cheat_sheet_dialog
from gui.dialogs.lore_glossary import show_canonical_lore_dialog
from gui.dialogs.macro_dict import show_macro_dictionary_dialog
from gui.dialogs.batch_rules import open_batch_ruleset_dialog
from gui.dialogs.mod_packager import open_mod_packager_dialog
from gui.dialogs.visual_diff import open_visual_diff_dialog
from gui.dialogs.dashboard import open_project_dashboard_dialog
from gui.dialogs.qa_auditor import open_qa_auditor_dialog
from gui.dialogs.search_replace import open_search_replace_dialog

__all__ = [
    "show_about_dialog",
    "show_cheat_sheet_dialog",
    "show_canonical_lore_dialog",
    "show_macro_dictionary_dialog",
    "open_batch_ruleset_dialog",
    "open_mod_packager_dialog",
    "open_visual_diff_dialog",
    "open_project_dashboard_dialog",
    "open_qa_auditor_dialog",
    "open_search_replace_dialog",
]
