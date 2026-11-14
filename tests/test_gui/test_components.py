import os
import sys
import tkinter as tk
from tkinter import ttk
import unittest
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from gui.components import ToolTip, DebouncedSearchFrame, TaskProgressDialog
from core.task_worker import TaskWorker

class TestGuiComponents(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk()
        cls.root.withdraw()

    @classmethod
    def tearDownClass(cls):
        try:
            cls.root.destroy()
        except Exception:
            pass

    def test_01_tooltip(self):
        tooltip = ToolTip(self.root)
        tooltip.show("Test tooltip content", 100, 100)
        self.assertIsNotNone(tooltip.tip_window)
        self.assertEqual(tooltip.current_text, "Test tooltip content")
        tooltip.hide()
        self.assertIsNone(tooltip.tip_window)

    def test_02_debounced_search(self):
        searched_queries = []
        def on_search(q):
            searched_queries.append(q)

        frame = DebouncedSearchFrame(self.root, on_search=on_search, delay_ms=50)
        frame.pack()

        # Insert query
        frame.ent_search.insert(0, "Blitzball")
        frame._on_key_release()

        # Before delay_ms, callback shouldn't have fired yet
        self.assertEqual(len(searched_queries), 0)

        # Wait for delay_ms
        self.root.update()
        time.sleep(0.08)
        self.root.update()

        self.assertIn("Blitzball", searched_queries)
        frame.set_count("5 of 20")
        self.assertEqual(frame.lbl_count.cget("text"), "5 of 20")

        # Clear
        frame.clear()
        self.assertEqual(frame.get(), "")
        self.assertEqual(searched_queries[-1], "")

    def test_03_progress_dialog(self):
        def worker_task(w: TaskWorker):
            w.post_progress(50, 100, "Halfway done")
            time.sleep(0.02)
            w.post_progress(100, 100, "Complete")
            return "SUCCESS_RESULT"

        worker = TaskWorker(worker_task, "TestWorkerTask")
        completed_results = []
        def on_done(prog):
            completed_results.append(prog)

        dlg = TaskProgressDialog(self.root, "Processing...", worker, on_complete=on_done)
        
        # Poll dialog loop
        start_t = time.time()
        while time.time() - start_t < 1.0 and not completed_results:
            self.root.update()
            time.sleep(0.03)

        self.assertEqual(len(completed_results), 1)
        self.assertEqual(completed_results[0].stage, "complete")
        self.assertEqual(completed_results[0].result, "SUCCESS_RESULT")

if __name__ == "__main__":
    unittest.main()
