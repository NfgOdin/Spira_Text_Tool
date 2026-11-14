"""
Application entry point and Tkinter bootstrap for FFX & FFX-2 Text & Localization Studio.
"""

import sys
import tkinter as tk
from gui.main_window import FFXTextToolGUI, APP_VERSION


def main():
    root = tk.Tk()
    # Apply dark mode window border coloring on modern Windows if possible
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    app = FFXTextToolGUI(root, is_embedded=False)
    root.mainloop()


if __name__ == "__main__":
    main()
