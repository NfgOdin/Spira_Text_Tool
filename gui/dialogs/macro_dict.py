"""
gui.dialogs.macro_dict - In-Game Macro Dictionary ({MCR:...}) Browser & Editor Dialog.
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

def show_macro_dictionary_dialog(parent):
    root = parent.winfo_toplevel() if hasattr(parent, 'winfo_toplevel') else getattr(parent, 'root', parent)
    
    if not hasattr(parent, 'macro_db') or not parent.macro_db:
        if hasattr(parent, 'load_macro_dictionary'):
            parent.load_macro_dictionary()

    macro_db = getattr(parent, 'macro_db', {})
    dialog = tk.Toplevel(root)
    dialog.title(f"🔍 FFX Macro Dictionary Browser ({len(macro_db)} Terms)")
    dialog.geometry("780x540")
    dialog.minsize(640, 420)
    
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
    dx = rx + max(0, (rw - 780) // 2)
    dy = ry + max(0, (rh - 540) // 2)
    dialog.geometry(f"+{dx}+{dy}")

    # Header Frame
    header = ttk.Frame(dialog, padding=(18, 14, 18, 6))
    header.pack(fill="x")

    tk.Label(
        header,
        text="FFX In-Game Macro Dictionary ({MCR:...})",
        font=("Segoe UI", 13, "bold"),
        fg=accent_color,
        bg=bg_color
    ).pack(anchor="w")

    tk.Label(
        header,
        text="Search characters, blitzball players/techs, and locations. Double-click or click 'Insert into Text' to place tag into active editor.",
        font=("Segoe UI", 9),
        fg=text_dim,
        bg=bg_color
    ).pack(anchor="w", pady=(2, 0))

    # Filter bar
    filter_frame = tk.Frame(dialog, bg=card_color, padx=12, pady=8, highlightbackground=border_color, highlightthickness=1)
    filter_frame.pack(fill="x", padx=18, pady=(4, 10))

    tk.Label(filter_frame, text="Search:", font=("Segoe UI", 9, "bold"), fg=text_color, bg=card_color).pack(side="left", padx=(0, 6))
    
    ent_search = ttk.Entry(filter_frame, width=26, font=("Segoe UI", 9))
    ent_search.pack(side="left", padx=(0, 14))
    ent_search.focus_set()

    tk.Label(filter_frame, text="Category:", font=("Segoe UI", 9, "bold"), fg=text_color, bg=card_color).pack(side="left", padx=(0, 6))

    categories = ["All Categories", "Characters & NPCs", "Blitzball Players", "Blitzball Techniques", "Field & Map Locations", "World Regions & Places"]
    cmb_cat = ttk.Combobox(filter_frame, values=categories, state="readonly", width=22, font=("Segoe UI", 9))
    cmb_cat.set("All Categories")
    cmb_cat.pack(side="left", padx=(0, 10))

    btn_clear = tk.Button(
        filter_frame, text="Clear", command=lambda: (ent_search.delete(0, tk.END), cmb_cat.set("All Categories"), refresh_list()),
        bg=bg_color, fg=text_dim, font=("Segoe UI", 8), relief="flat", padx=8, pady=2
    )
    btn_clear.pack(side="left")

    # Table container
    table_frame = tk.Frame(dialog, bg=bg_color, padx=18)
    table_frame.pack(fill="both", expand=True)

    cols = ("tag", "category", "text")
    tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")
    tree.heading("tag", text="Macro Tag", anchor="w")
    tree.heading("category", text="Category", anchor="w")
    tree.heading("text", text="In-Game Name / Text", anchor="w")

    tree.column("tag", width=120, minwidth=100, stretch=False)
    tree.column("category", width=190, minwidth=140, stretch=False)
    tree.column("text", width=420, minwidth=250, stretch=True)

    tree_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=tree_scroll.set)
    tree.pack(side="left", fill="both", expand=True)
    tree_scroll.pack(side="right", fill="y")

    # Edit Strip
    edit_strip = tk.Frame(dialog, bg=card_color, padx=12, pady=6, highlightbackground=border_color, highlightthickness=1)
    edit_strip.pack(fill="x", padx=18, pady=(6, 4))
    
    tk.Label(edit_strip, text="Selected Macro Text:", font=("Segoe UI", 9, "bold"), fg=text_color, bg=card_color).pack(side="left", padx=(0, 6))
    ent_macro_text = ttk.Entry(edit_strip, font=("Segoe UI", 9))
    ent_macro_text.pack(side="left", fill="x", expand=True, padx=(0, 8))

    def apply_macro_edit():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Select a macro entry in the table first.")
            return
        new_text = ent_macro_text.get()
        vals = tree.item(sel[0], "values")
        tag = vals[0]
        cat = vals[1]
        tag_clean = tag.replace("{MCR:", "").replace("}", "").strip().lower()
        if tag_clean in parent.macro_db:
            parent.macro_db[tag_clean]['text'] = new_text
        tree.item(sel[0], values=(tag, cat, new_text))
        lbl_count.config(text=f"Updated '{tag}' to '{new_text}' (In-memory).")
        if hasattr(parent, 'update_live_preview'):
            parent.update_live_preview()

    btn_apply_macro = tk.Button(edit_strip, text="✏️ Apply Edit", command=apply_macro_edit,
                                bg=accent_color, fg="white", font=("Segoe UI", 8, "bold"), relief="flat", padx=10, pady=2)
    btn_apply_macro.pack(side="left")

    def save_macrodic_to_disk():
        loc = parent.cmb_local.get() if hasattr(parent, 'cmb_local') else ""
        charset = parent.cmb_charset.get() if hasattr(parent, 'cmb_charset') else "us"
        master_path = getattr(parent.codec, 'ffx_master_path', None) if hasattr(parent, 'codec') else None
        default_path = os.path.join(master_path, loc, "menu", "macrodic.dcp") if master_path and loc else "macrodic.dcp"
        save_path = filedialog.asksaveasfilename(
            title="Save macrodic.dcp",
            initialfile="macrodic.dcp",
            initialdir=os.path.dirname(default_path) if os.path.exists(os.path.dirname(default_path)) else None,
            defaultextension=".dcp",
            filetypes=[("FFX Macro Dictionary", "*.dcp"), ("All Files", "*.*")]
        )
        if not save_path:
            return
        bak = save_path + ".bak"
        if os.path.exists(save_path) and not os.path.exists(bak):
            import shutil
            shutil.copy2(save_path, bak)
        res = parent.codec.write_macrodic_dcp(save_path, parent.macro_db, charset)
        if res > 0:
            if hasattr(parent, 'log'):
                parent.log(f"Successfully saved {res} bytes to macrodic.dcp: {save_path}", "success")
            messagebox.showinfo("Success", f"Successfully saved macrodic.dcp ({res} bytes)!\n\nPath:\n{save_path}")
        else:
            messagebox.showerror("Error", "Failed to write macrodic.dcp file.")

    # Bottom Action Bar
    bottom = tk.Frame(dialog, bg=bg_color, padx=18, pady=12)
    bottom.pack(fill="x")

    lbl_count = tk.Label(bottom, text="", font=("Segoe UI", 9, "italic"), fg=text_dim, bg=bg_color)
    lbl_count.pack(side="left")

    btn_close = tk.Button(
        bottom, text="Close", command=dialog.destroy,
        bg=card_color, fg=text_color, font=("Segoe UI", 9),
        relief="flat", padx=14, pady=4
    )
    btn_close.pack(side="right", padx=(8, 0))

    btn_save = tk.Button(
        bottom, text="💾 Save macrodic.dcp...", command=save_macrodic_to_disk,
        bg=card_color, fg=text_color, font=("Segoe UI", 9),
        relief="flat", padx=12, pady=4
    )
    btn_save.pack(side="right", padx=(8, 0))

    def on_macro_tree_select(event=None):
        sel = tree.selection()
        if not sel:
            return
        vals = tree.item(sel[0], "values")
        ent_macro_text.delete(0, tk.END)
        ent_macro_text.insert(0, vals[2])

    tree.bind("<<TreeviewSelect>>", on_macro_tree_select)

    def refresh_list(event=None):
        query = ent_search.get().strip().lower()
        cat_filter = cmb_cat.get()
        
        for r in tree.get_children():
            tree.delete(r)

        matched_count = 0
        for tag_key, data in sorted(parent.macro_db.items()):
            tag_display = f"{{MCR:{tag_key}}}"
            if isinstance(data, dict):
                cat = data.get('category', 'General')
                text_val = data.get('text', '')
            else:
                cat = 'General'
                text_val = str(data)

            if cat_filter != "All Categories" and cat != cat_filter:
                continue

            if query:
                if (query not in tag_display.lower() and 
                    query not in cat.lower() and 
                    query not in text_val.lower()):
                    continue

            tree.insert("", "end", values=(tag_display, cat, text_val))
            matched_count += 1

        lbl_count.config(text=f"Showing {matched_count} of {len(parent.macro_db)} macros")

    def insert_selected_macro():
        sel = tree.selection()
        if not sel:
            return
        vals = tree.item(sel[0], "values")
        tag = vals[0]
        
        inserted = False
        if hasattr(parent, 'active_mode') and parent.active_mode in ('sps2', 'msg', 'macro') and hasattr(parent, 'txt_dialogue'):
            parent.txt_dialogue.insert("insert", tag)
            if hasattr(parent, 'on_dialogue_key_release'):
                parent.on_dialogue_key_release(None)
            inserted = True
        elif hasattr(parent, 'ent_name'):
            parent.ent_name.insert(tk.INSERT, tag)
            if hasattr(parent, 'update_length_label'):
                parent.update_length_label()
            if hasattr(parent, 'update_live_preview'):
                parent.update_live_preview()
            inserted = True

        if inserted:
            lbl_count.config(text=f"Inserted '{tag}' into editor at cursor.")
        else:
            root.clipboard_clear()
            root.clipboard_append(tag)
            lbl_count.config(text=f"Copied '{tag}' to clipboard.")

    btn_insert = tk.Button(
        bottom, text="⚡ Insert into Text", command=insert_selected_macro,
        bg=accent_color, fg="white", font=("Segoe UI", 9, "bold"),
        relief="flat", padx=14, pady=4
    )
    btn_insert.pack(side="right")

    tree.bind("<Double-1>", lambda e: insert_selected_macro())
    ent_search.bind("<KeyRelease>", refresh_list)
    cmb_cat.bind("<<ComboboxSelected>>", refresh_list)

    refresh_list()
