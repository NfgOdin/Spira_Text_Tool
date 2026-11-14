"""
gui.components.debounced_search - 200ms Debounced Search Bar with Match Badge & Clear Button.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

class DebouncedSearchFrame(ttk.Frame):
    def __init__(self, parent, on_search: Callable[[str], None], delay_ms: int = 200, **kwargs):
        super().__init__(parent, **kwargs)
        self.on_search = on_search
        self.delay_ms = delay_ms
        self._after_id = None
        
        self.columnconfigure(0, weight=1)
        
        # Search entry
        self.ent_search = ttk.Entry(self)
        self.ent_search.grid(row=0, column=0, sticky="ew")
        self.ent_search.bind("<KeyRelease>", self._on_key_release)
        self.ent_search.bind("<Escape>", lambda e: self.clear())
        
        # Match counter badge
        self.lbl_count = ttk.Label(self, text="0 entries", font=("Segoe UI", 8), foreground="#9ca3af")
        self.lbl_count.grid(row=0, column=1, padx=(6, 4))
        
        # Clear button
        self.btn_clear = tk.Button(self, text="✕", command=self.clear,
                                   bg="#161922", fg="#9ca3af", font=("Segoe UI", 8),
                                   relief="flat", bd=0, padx=4, pady=0)
        self.btn_clear.grid(row=0, column=2, padx=(0, 2))

    def _on_key_release(self, event=None):
        if event and event.keysym in ("Up", "Down", "Left", "Right", "Return", "Escape", "Control_L", "Control_R"):
            return
        if self._after_id is not None:
            self.after_cancel(self._after_id)
        self._after_id = self.after(self.delay_ms, self._trigger_search)

    def _trigger_search(self):
        self._after_id = None
        query = self.get()
        self.on_search(query)

    def get(self) -> str:
        return self.ent_search.get().strip()

    def set_count(self, count_text: str):
        self.lbl_count.config(text=count_text)

    def clear(self):
        if self._after_id is not None:
            self.after_cancel(self._after_id)
            self._after_id = None
        self.ent_search.delete(0, tk.END)
        self.on_search("")
        self.ent_search.focus_set()

    def focus_set(self):
        self.ent_search.focus_set()

    def select_range(self, start, end):
        self.ent_search.select_range(start, end)

DebouncedSearch = DebouncedSearchFrame
