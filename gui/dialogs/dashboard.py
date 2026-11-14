"""
Translation Memory & Progress Dashboard Dialog
Calculates string counts and completion rates across all categories against baseline.
"""

import os
import struct
import tkinter as tk
from tkinter import ttk


def open_project_dashboard_dialog(parent):
    """
    Translation Memory & Progress Dashboard (Pillar 3).
    Calculates string counts and completion rates across all categories
    by comparing against the vanilla baseline (new_uspc).
    """
    dialog = tk.Toplevel(parent.root)
    dialog.title("📊 Translation Memory & Progress Dashboard")
    dialog.geometry("760x560")
    dialog.minsize(640, 440)
    dialog.configure(bg=parent.bg_color)
    dialog.transient(parent.root)
    dialog.grab_set()

    dialog.update_idletasks()
    rx = parent.root.winfo_x()
    ry = parent.root.winfo_y()
    rw = parent.root.winfo_width()
    rh = parent.root.winfo_height()
    dx = rx + max(0, (rw - 760) // 2)
    dy = ry + max(0, (rh - 560) // 2)
    dialog.geometry(f"+{dx}+{dy}")

    header = ttk.Frame(dialog, padding=(18, 14, 18, 6))
    header.pack(fill="x")
    tk.Label(header, text="📊 Translation Memory & Progress Dashboard", font=("Segoe UI", 13, "bold"), fg=parent.accent_color, bg=parent.bg_color).pack(anchor="w")
    loc = parent.cmb_local.get() if hasattr(parent, 'cmb_local') else "new_uspc"
    tk.Label(header, text=f"Tracks localized completion against vanilla reference (new_uspc) for active localization: {loc}",
             font=("Segoe UI", 9), fg=parent.text_dim, bg=parent.bg_color).pack(anchor="w", pady=(2, 0))

    # Overall Progress Card
    card_overall = tk.Frame(dialog, bg=parent.card_color, padx=16, pady=12, highlightbackground=parent.border_color, highlightthickness=1)
    card_overall.pack(fill="x", padx=18, pady=(6, 12))

    lbl_tot_rate = tk.Label(card_overall, text="Project Overall Progress: Calculating...", font=("Segoe UI", 11, "bold"), fg=parent.text_color, bg=parent.card_color)
    lbl_tot_rate.pack(anchor="w", pady=(0, 6))

    pbar_overall = ttk.Progressbar(card_overall, orient="horizontal", mode="determinate")
    pbar_overall.pack(fill="x", pady=(0, 6))

    lbl_tot_counts = tk.Label(card_overall, text="", font=("Segoe UI", 9), fg=parent.text_dim, bg=parent.card_color)
    lbl_tot_counts.pack(anchor="w")

    # Active File Card
    card_file = tk.Frame(dialog, bg=parent.card_color, padx=16, pady=10, highlightbackground=parent.border_color, highlightthickness=1)
    card_file.pack(fill="x", padx=18, pady=(0, 12))

    lbl_file_title = tk.Label(card_file, text=f"Active File Progress ({parent.active_file_name or 'No file loaded'}):", font=("Segoe UI", 10, "bold"), fg=parent.text_color, bg=parent.card_color)
    lbl_file_title.pack(anchor="w", pady=(0, 4))

    pbar_file = ttk.Progressbar(card_file, orient="horizontal", mode="determinate")
    pbar_file.pack(fill="x", pady=(0, 4))

    lbl_file_stat = tk.Label(card_file, text="", font=("Segoe UI", 9), fg=parent.text_dim, bg=parent.card_color)
    lbl_file_stat.pack(anchor="w")

    # Category Breakdown Table
    lbl_cat_head = tk.Label(dialog, text="Category Breakdown:", font=("Segoe UI", 10, "bold"), fg=parent.text_color, bg=parent.bg_color)
    lbl_cat_head.pack(anchor="w", padx=18, pady=(0, 4))

    tree_cat = ttk.Treeview(dialog, columns=("cat", "files", "total", "trans", "pct"), show="headings", height=6)
    tree_cat.heading("cat", text="Category", anchor="w")
    tree_cat.heading("files", text="Files", anchor="center")
    tree_cat.heading("total", text="Total Strings", anchor="center")
    tree_cat.heading("trans", text="Modified / Translated", anchor="center")
    tree_cat.heading("pct", text="Completion %", anchor="center")

    tree_cat.column("cat", width=220, minwidth=160, stretch=True)
    tree_cat.column("files", width=70, minwidth=60, stretch=False, anchor="center")
    tree_cat.column("total", width=110, minwidth=90, stretch=False, anchor="center")
    tree_cat.column("trans", width=140, minwidth=110, stretch=False, anchor="center")
    tree_cat.column("pct", width=120, minwidth=90, stretch=False, anchor="center")
    tree_cat.pack(fill="both", expand=True, padx=18, pady=(0, 10))

    # Bottom Bar
    bottom = tk.Frame(dialog, bg=parent.bg_color, padx=18, pady=8)
    bottom.pack(fill="x")

    def get_file_string_count(filepath):
        try:
            ext = os.path.splitext(filepath)[1].lower()
            with open(filepath, "rb") as f:
                header = f.read(32)
            if len(header) < 16:
                return 0
            if ext == ".sps2":
                if len(header) >= 20:
                    hdr = struct.unpack("<5I", header[:20])
                    ptr_table_off = hdr[4]
                    fsize = os.path.getsize(filepath)
                    if 0 <= ptr_table_off < fsize:
                        with open(filepath, "rb") as f2:
                            f2.seek(ptr_table_off)
                            p_bytes = f2.read(4)
                            if len(p_bytes) == 4:
                                first_ptr = struct.unpack("<I", p_bytes)[0]
                                if first_ptr > ptr_table_off and first_ptr <= fsize:
                                    return (first_ptr - ptr_table_off) // 4
            elif ext == ".bin":
                min_idx, max_idx, rec_len, tot_len = struct.unpack("<HHHH", header[8:16])
                if 0 < rec_len <= 128 and 0 <= min_idx <= max_idx < 10000:
                    return max_idx - min_idx + 1
                raw_first_ptr = struct.unpack("<I", header[:4])[0]
                fsize = os.path.getsize(filepath)
                if 0 < raw_first_ptr <= fsize and raw_first_ptr % 4 == 0:
                    count = raw_first_ptr // 4
                    if 0 < count < 5000:
                        return count
        except Exception:
            pass
        return 12

    def compute_metrics():
        if parent.records and parent.active_file_path:
            ref_recs = parent.get_reference_records_for_file(parent.active_file_path, "new_uspc")
            ref_map = {r['id']: r for r in ref_recs}
            f_tot = len(parent.records)
            f_mod = 0
            for r in parent.records:
                orig = ref_map.get(r['id'])
                if not orig or r.get('name') != orig.get('name') or r.get('desc') != orig.get('desc'):
                    f_mod += 1
            f_pct = (f_mod / max(1, f_tot)) * 100.0
            pbar_file['value'] = f_pct
            lbl_file_stat.config(text=f"{f_mod} of {f_tot} strings differing from vanilla reference ({f_pct:.1f}% customized)")
        else:
            pbar_file['value'] = 0
            lbl_file_stat.config(text="No file records loaded.")

        for r in tree_cat.get_children():
            tree_cat.delete(r)

        categories = [
            ("⚔️ Battle Kernel Tables", "battle/kernel"),
            ("🏟️ Monster Arena & Help", "help"),
            ("📜 Story & Cutscene Dialogue", "event"),
            ("🎙️ Battle Quotes & Voice", "battle/btl"),
            ("⚙️ Menu & System Text", "menu")
        ]

        grand_total = 0
        grand_trans = 0
        loc_name = parent.cmb_local.get() if hasattr(parent, 'cmb_local') else "new_uspc"
        master_p = parent.codec.ffx_master_path

        for c_name, sub in categories:
            c_dir = os.path.join(master_p, loc_name, sub) if master_p else ""
            c_files = 0
            c_total = 0
            c_trans = 0
            if c_dir and os.path.exists(c_dir):
                for root, dirs, files in os.walk(c_dir):
                    for f in files:
                        if f.endswith(".bin") or f.endswith(".sps2") or f.endswith(".dcp"):
                            if f.endswith(".bak") or f.startswith("ffxsjis"):
                                continue
                            fp = os.path.join(root, f)
                            str_cnt = get_file_string_count(fp)
                            c_files += 1
                            c_total += str_cnt
                            if os.path.exists(fp + ".bak"):
                                c_trans += str_cnt
            pct = (c_trans / max(1, c_total)) * 100.0 if c_total else 0.0
            tree_cat.insert("", "end", values=(c_name, c_files, c_total, c_trans, f"{pct:.1f}%"))
            grand_total += c_total
            grand_trans += c_trans

        tot_pct = (grand_trans / max(1, grand_total)) * 100.0 if grand_total else 0.0
        pbar_overall['value'] = tot_pct
        lbl_tot_rate.config(text=f"Project Overall Progress: {tot_pct:.1f}%")
        lbl_tot_counts.config(text=f"{grand_trans} translated strings out of ~{grand_total} total localization strings across Spira")

    btn_refresh = tk.Button(bottom, text="🔄 Recalculate Metrics", command=compute_metrics, bg=parent.accent_color, fg="white", font=("Segoe UI", 9, "bold"), relief="flat", padx=12, pady=3)
    btn_refresh.pack(side="left")
    parent.bind_hover(btn_refresh, is_primary=True)

    btn_close = tk.Button(bottom, text="Close", command=dialog.destroy, bg=parent.card_color, fg=parent.text_color, font=("Segoe UI", 9), relief="flat", padx=14, pady=3)
    btn_close.pack(side="right")
    parent.bind_hover(btn_close)

    dialog.after(100, compute_metrics)
