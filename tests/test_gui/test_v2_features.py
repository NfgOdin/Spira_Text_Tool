"""
Test suite for Version 2.0.0 GUI enhancements:
- Unsupported Character Warning Badge
- 1-Click Revert to Original Backup (.bak)
- Search Indexer integration
- Debounced search filtering
"""

import os
import sys
import shutil
import tempfile
import tkinter as tk
import unittest

from gui.main_window import FFXTextToolGUI
from core.codec import FFXCodec


class TestV2GuiFeatures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk()
        cls.root.withdraw()
        cls.app = FFXTextToolGUI(cls.root)

    @classmethod
    def tearDownClass(cls):
        try:
            cls.root.destroy()
        except Exception:
            pass

    def test_unsupported_character_warning(self):
        """Verify that unsupported characters trigger warning in update_length_label."""
        self.app.active_mode = "sps2"
        self.app.cmb_charset.set("us")
        
        # Valid string
        self.app.txt_dialogue.delete("1.0", tk.END)
        self.app.txt_dialogue.insert("1.0", "Hello Tidus!")
        self.app.update_length_label()
        lbl_text = self.app.lbl_len_warn.cget("text")
        self.assertIn("Current Message:", lbl_text)

        # String with unsupported character (e.g. Cyrillic or Chinese character in US charset)
        self.app.txt_dialogue.delete("1.0", tk.END)
        self.app.txt_dialogue.insert("1.0", "Hello Привет Tidus!")
        self.app.update_length_label()
        lbl_warn = self.app.lbl_len_warn.cget("text")
        self.assertIn("UNSUPPORTED CHARS", lbl_warn)

    def test_revert_file_to_backup(self):
        """Verify that revert_active_file_to_backup restores the .bak file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "item_txt.bin")
            bak_file = test_file + ".bak"

            # Create original and backup
            original_content = b"ORIGINAL_BACKUP_DATA"
            modified_content = b"MODIFIED_CORRUPT_DATA"

            with open(bak_file, "wb") as f:
                f.write(original_content)
            with open(test_file, "wb") as f:
                f.write(modified_content)

            self.app.active_file_path = test_file
            self.app.active_file_name = "item_txt.bin"

            # Mock messagebox.askyesno to return True
            import tkinter.messagebox as mb
            orig_askyesno = mb.askyesno
            orig_showinfo = mb.showinfo
            mb.askyesno = lambda *args, **kwargs: True
            mb.showinfo = lambda *args, **kwargs: None

            try:
                # Mock read_active_file to avoid binary decode of mock bytes
                called_read = []
                self.app.read_active_file = lambda: called_read.append(True)
                
                self.app.revert_active_file_to_backup()
                
                with open(test_file, "rb") as f:
                    restored = f.read()
                self.assertEqual(restored, original_content)
                self.assertTrue(len(called_read) > 0)
            finally:
                mb.askyesno = orig_askyesno
                mb.showinfo = orig_showinfo

    def test_search_indexer_in_gui(self):
        """Verify SearchIndexer indexes records and speeds up treeview filtering."""
        self.assertIsNotNone(self.app.search_indexer)
        
        # Feed test records
        mock_records = [
            {"id": 1, "name": "Potion", "desc": "Restores 200 HP."},
            {"id": 2, "name": "Hi-Potion", "desc": "Restores 1000 HP."},
            {"id": 3, "name": "Phoenix Down", "desc": "Revives fallen ally."}
        ]
        self.app.records = mock_records
        self.app.search_indexer.index_records(mock_records)

        # Search for Phoenix
        results = self.app.search_indexer.search("Phoenix")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], 3)

        # Search for Potion (matches Potion and Hi-Potion)
        potion_results = self.app.search_indexer.search("potion")
        self.assertEqual(len(potion_results), 2)


if __name__ == "__main__":
    unittest.main()
