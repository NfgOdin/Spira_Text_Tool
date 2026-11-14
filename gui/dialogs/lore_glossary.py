"""
gui.dialogs.lore_glossary - Canonical Lore & Multi-Language Terminology Glossary Dialog.
"""

import tkinter as tk
from tkinter import ttk
from core.lore_db import CANONICAL_LORE_GLOSSARY

def show_canonical_lore_dialog(parent):
    root = parent.winfo_toplevel() if hasattr(parent, 'winfo_toplevel') else getattr(parent, 'root', parent)
    dialog = tk.Toplevel(root)
    dialog.title(f"📚 Canonical Lore Glossary ({len(CANONICAL_LORE_GLOSSARY)} Terms)")
    dialog.geometry("860x560")
    dialog.minsize(700, 420)
    
    bg_color = getattr(parent, 'bg_color', "#0e1117")
    accent_color = getattr(parent, 'accent_color', "#3b82f6")
    text_color = getattr(parent, 'text_color', "#f3f4f6")
    text_dim = getattr(parent, 'text_dim', "#9ca3af")
    border_color = getattr(parent, 'border_color', "#282d3d")
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
    dx = rx + max(0, (rw - 860) // 2)
    dy = ry + max(0, (rh - 560) // 2)
    dialog.geometry(f"+{dx}+{dy}")

    header = ttk.Frame(dialog, padding=(18, 14, 18, 6))
    header.pack(fill="x")
    tk.Label(header, text="📚 Canonical Multi-Language Lore Glossary", font=("Segoe UI", 13, "bold"), fg=accent_color, bg=bg_color).pack(anchor="w")
    tk.Label(header, text="Official Square Enix terminology across 6 languages (EN, IT, DE, FR, ES, JP). Search any term and double-click to copy.",
             font=("Segoe UI", 9), fg=text_dim, bg=bg_color).pack(anchor="w", pady=(2, 0))

    # Filter Strip
    f_strip = tk.Frame(dialog, bg=card_color, padx=12, pady=8, highlightbackground=border_color, highlightthickness=1)
    f_strip.pack(fill="x", padx=18, pady=(4, 10))

    tk.Label(f_strip, text="Search Term:", font=("Segoe UI", 9, "bold"), fg=text_color, bg=card_color).pack(side="left", padx=(0, 6))
    ent_q = ttk.Entry(f_strip, width=22)
    ent_q.pack(side="left", padx=(0, 14))
    ent_q.focus_set()

    tk.Label(f_strip, text="Category:", font=("Segoe UI", 9, "bold"), fg=text_color, bg=card_color).pack(side="left", padx=(0, 6))
    cats = ["All Categories", "Characters (FFX)", "Characters (FFX-2)", "Supporting Cast", "Aeons", "Lore & Concepts", "Systems & Mechanics", "Spells & Skills", "Locations"]
    cmb_c = ttk.Combobox(f_strip, values=cats, state="readonly", width=18)
    cmb_c.set("All Categories")
    cmb_c.pack(side="left", padx=(0, 10))

    tree_frame = tk.Frame(dialog, bg=bg_color, padx=18)
    tree_frame.pack(fill="both", expand=True)

    cols = ("cat", "en", "it", "de", "fr", "es", "jp")
    tree_lore = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="browse")
    tree_lore.heading("cat", text="Category", anchor="w")
    tree_lore.heading("en", text="English", anchor="w")
    tree_lore.heading("it", text="Italian", anchor="w")
    tree_lore.heading("de", text="German", anchor="w")
    tree_lore.heading("fr", text="French", anchor="w")
    tree_lore.heading("es", text="Spanish", anchor="w")
    tree_lore.heading("jp", text="Japanese", anchor="w")

    tree_lore.column("cat", width=130, minwidth=100, stretch=False)
    tree_lore.column("en", width=120, minwidth=80, stretch=True)
    tree_lore.column("it", width=120, minwidth=80, stretch=True)
    tree_lore.column("de", width=120, minwidth=80, stretch=True)
    tree_lore.column("fr", width=120, minwidth=80, stretch=True)
    tree_lore.column("es", width=120, minwidth=80, stretch=True)
    tree_lore.column("jp", width=120, minwidth=80, stretch=True)

    scr_l = ttk.Scrollbar(tree_frame, orient="vertical", command=tree_lore.yview)
    tree_lore.configure(yscrollcommand=scr_l.set)
    tree_lore.pack(side="left", fill="both", expand=True)
    scr_l.pack(side="right", fill="y")

    bottom = tk.Frame(dialog, bg=bg_color, padx=18, pady=10)
    bottom.pack(fill="x")
    lbl_info = tk.Label(bottom, text="", font=("Segoe UI", 9, "italic"), fg=text_dim, bg=bg_color)
    lbl_info.pack(side="left")

    def copy_selected(col_idx=1):
        sel = tree_lore.selection()
        if not sel:
            return
        vals = tree_lore.item(sel[0], "values")
        txt = vals[col_idx]
        root.clipboard_clear()
        root.clipboard_append(txt)
        lbl_info.config(text=f"Copied '{txt}' to clipboard!")

    def refresh_lore(event=None):
        q = ent_q.get().strip().lower()
        cat_f = cmb_c.get()
        for r in tree_lore.get_children():
            tree_lore.delete(r)
        cnt = 0
        for item in CANONICAL_LORE_GLOSSARY:
            if cat_f != "All Categories" and item.get('category') != cat_f:
                continue
            if q:
                matched = False
                for k in ('en', 'it', 'de', 'fr', 'es', 'jp', 'category'):
                    if q in item.get(k, '').lower():
                        matched = True
                        break
                if not matched:
                    continue
            tree_lore.insert("", "end", values=(
                item.get('category', ''),
                item.get('en', ''),
                item.get('it', ''),
                item.get('de', ''),
                item.get('fr', ''),
                item.get('es', ''),
                item.get('jp', '')
            ))
            cnt += 1
        lbl_info.config(text=f"Showing {cnt} of {len(CANONICAL_LORE_GLOSSARY)} terms. Double-click row to copy English term.")

    ent_q.bind("<KeyRelease>", refresh_lore)
    cmb_c.bind("<<ComboboxSelected>>", refresh_lore)
    tree_lore.bind("<Double-1>", lambda e: copy_selected(1))

    btn_close = tk.Button(bottom, text="Close", command=dialog.destroy, bg=card_color, fg=text_color, font=("Segoe UI", 9), relief="flat", padx=14, pady=3)
    btn_close.pack(side="right")

    refresh_lore()
