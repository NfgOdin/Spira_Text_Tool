"""
gui.dialogs.about - About Studio Dialog.
"""

import tkinter as tk
from tkinter import ttk
import webbrowser

APP_VERSION = "2.0.0"

def show_about_dialog(parent):
    root = parent.winfo_toplevel() if hasattr(parent, 'winfo_toplevel') else getattr(parent, 'root', parent)
    dialog = tk.Toplevel(root)
    dialog.title("About Spira Text Tool")
    dialog.geometry("460x320")
    dialog.resizable(False, False)
    
    bg_color = getattr(parent, 'bg_color', "#0e1117")
    accent_color = getattr(parent, 'accent_color', "#3b82f6")
    text_color = getattr(parent, 'text_color', "#f3f4f6")
    text_dim = getattr(parent, 'text_dim', "#9ca3af")
    card_color = getattr(parent, 'card_color', "#161922")
    
    dialog.configure(bg=bg_color)
    dialog.transient(root)
    dialog.grab_set()

    # Center relative to parent
    dialog.update_idletasks()
    rx = root.winfo_x()
    ry = root.winfo_y()
    rw = root.winfo_width()
    rh = root.winfo_height()
    dx = rx + max(0, (rw - 460) // 2)
    dy = ry + max(0, (rh - 320) // 2)
    dialog.geometry(f"+{dx}+{dy}")

    card = ttk.Frame(dialog, padding=20)
    card.pack(fill="both", expand=True, padx=15, pady=15)

    lbl_title = tk.Label(
        card,
        text="Spira Text Tool\nFFX & FFX-2 Text & Localization Studio",
        font=("Segoe UI", 13, "bold"),
        fg=accent_color,
        bg=bg_color,
        justify="center"
    )
    lbl_title.pack(pady=(0, 6))

    lbl_ver = tk.Label(
        card,
        text=f"Version {APP_VERSION} (The Studio Edition)",
        font=("Segoe UI", 10, "bold"),
        fg=text_color,
        bg=bg_color
    )
    lbl_ver.pack(pady=(0, 4))

    lbl_auth = tk.Label(
        card,
        text="Author: NfgOdin",
        font=("Segoe UI", 9),
        fg=text_dim,
        bg=bg_color
    )
    lbl_auth.pack(pady=(0, 10))

    lbl_repo = tk.Label(
        card,
        text="GitHub Repository",
        font=("Segoe UI", 9, "underline"),
        fg=accent_color,
        bg=bg_color,
        cursor="hand2"
    )
    lbl_repo.pack(pady=(0, 14))
    lbl_repo.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/NfgOdin/FFX_Text_Tool"))

    btn_close = tk.Button(
        card,
        text="Close",
        command=dialog.destroy,
        bg=card_color,
        fg=text_color,
        font=("Segoe UI", 9),
        relief="flat",
        padx=18,
        pady=3
    )
    btn_close.pack()
