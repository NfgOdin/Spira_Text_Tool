"""
gui.components.tooltip - Floating Modern Tooltip for in-game control tags and UI elements.
"""

import tkinter as tk

class ToolTip:
    """Floating modern tooltip for in-game control tags and UI elements."""
    def __init__(self, root):
        self.root = root
        self.tip_window = None
        self.current_text = ""

    def show(self, text: str, x: int, y: int):
        if self.tip_window and self.current_text == text:
            return
        self.hide()
        self.current_text = text
        self.tip_window = tk.Toplevel(self.root)
        self.tip_window.wm_overrideredirect(True)
        self.tip_window.wm_geometry(f"+{x+14}+{y+16}")
        self.tip_window.attributes("-topmost", True)
        
        container = tk.Frame(self.tip_window, bg="#1a1e2b", highlightbackground="#3b82f6", highlightthickness=1, padx=9, pady=5)
        container.pack()
        
        lbl = tk.Label(
            container,
            text=text,
            bg="#1a1e2b",
            fg="#f3f4f6",
            font=("Segoe UI", 9),
            justify="left"
        )
        lbl.pack()

    def show_tip(self, text: str, x: int = 100, y: int = 100):
        self.show(text, x, y)

    def hide(self):
        if self.tip_window:
            try:
                self.tip_window.destroy()
            except Exception:
                pass
            self.tip_window = None
            self.current_text = ""
