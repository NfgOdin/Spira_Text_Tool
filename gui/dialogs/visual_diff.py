"""
Visual Side-by-Side Diff Dialog
Compares active entry against vanilla baseline (new_uspc) with byte deltas.
"""

import tkinter as tk
from tkinter import ttk, messagebox


def open_visual_diff_dialog(parent):
    """
    Visual Side-by-Side Diff Viewer (Pillar 4).
    Compares active entry against vanilla baseline (new_uspc) with byte deltas.
    Includes interactive previous/next entry navigation and Alt+Left / Alt+Right hotkeys.
    """
    if not parent.records:
        messagebox.showwarning("Warning", "No active records loaded.")
        return

    sel = parent.tree.selection()
    start_idx = 0
    if sel:
        try:
            target_id = int(sel[0])
            for i, r in enumerate(parent.records):
                if r['id'] == target_id:
                    start_idx = i
                    break
        except ValueError:
            for i, r in enumerate(parent.records):
                if str(r['id']) == sel[0]:
                    start_idx = i
                    break

    current_diff_idx = start_idx
    ref_recs = parent.get_reference_records_for_file(parent.active_file_path, "new_uspc") if parent.active_file_path else []
    ref_map = {r['id']: r for r in ref_recs}
    charset = parent.cmb_charset.get() if hasattr(parent, 'cmb_charset') else 'us'

    dialog = tk.Toplevel(parent.root)
    dialog.title(f"🔍 Visual String Diff — ({parent.active_file_name or 'Entry'})")
    dialog.geometry("780x500")
    dialog.minsize(660, 380)
    dialog.configure(bg=parent.bg_color)
    dialog.transient(parent.root)
    dialog.grab_set()

    dialog.update_idletasks()
    rx = parent.root.winfo_x()
    ry = parent.root.winfo_y()
    rw = parent.root.winfo_width()
    rh = parent.root.winfo_height()
    dx = rx + max(0, (rw - 780) // 2)
    dy = ry + max(0, (rh - 500) // 2)
    dialog.geometry(f"+{dx}+{dy}")

    header = ttk.Frame(dialog, padding=(18, 14, 18, 6))
    header.pack(fill="x")
    lbl_diff_title = tk.Label(header, text="🔍 Visual Side-by-Side Diff", font=("Segoe UI", 12, "bold"), fg=parent.accent_color, bg=parent.bg_color)
    lbl_diff_title.pack(anchor="w")

    lbl_diff_sub = tk.Label(header, text="", font=("Segoe UI", 9), fg=parent.text_dim, bg=parent.bg_color)
    lbl_diff_sub.pack(anchor="w", pady=(2, 0))

    panes = ttk.PanedWindow(dialog, orient="horizontal")
    panes.pack(fill="both", expand=True, padx=18, pady=8)

    # Left: Reference
    f_left = ttk.LabelFrame(panes, text=" Vanilla Reference (new_uspc) ", padding=8)
    panes.add(f_left, weight=1)
    t_ref = tk.Text(f_left, bg="#1a1113", fg="#fca5a5", font=("Consolas", 10), wrap="word", relief="flat")
    t_ref.pack(fill="both", expand=True)

    # Right: Active
    f_right = ttk.LabelFrame(panes, text=" Active / Translated ", padding=8)
    panes.add(f_right, weight=1)
    t_act = tk.Text(f_right, bg="#0d1f14", fg="#86efac", font=("Consolas", 10), wrap="word", relief="flat")
    t_act.pack(fill="both", expand=True)

    bottom = tk.Frame(dialog, bg=parent.bg_color, padx=18, pady=10)
    bottom.pack(fill="x")

    def load_entry(idx):
        nonlocal current_diff_idx
        if not parent.records or idx < 0 or idx >= len(parent.records):
            return
        current_diff_idx = idx
        rec = parent.records[idx]
        eid = rec['id']
        ref_rec = ref_map.get(eid)

        active_text = rec.get('name', '')
        if rec.get('desc') and rec.get('desc') != '-':
            active_text += "\n" + rec.get('desc')

        ref_text = ""
        if ref_rec:
            ref_text = ref_rec.get('name', '')
            if ref_rec.get('desc') and ref_rec.get('desc') != '-':
                ref_text += "\n" + ref_rec.get('desc')

        ref_b = len(parent.codec.encode_ffx_string(ref_text, charset)) if ref_text else 0
        act_b = len(parent.codec.encode_ffx_string(active_text, charset)) if active_text else 0
        diff_b = act_b - ref_b
        delta_str = f"+{diff_b}B" if diff_b > 0 else f"{diff_b}B"

        dialog.title(f"🔍 Visual String Diff — ID #{eid} ({idx + 1} of {len(parent.records)})")
        lbl_diff_title.config(text=f"🔍 Visual Side-by-Side Diff: Entry #{eid}")
        lbl_diff_sub.config(text=f"Entry {idx + 1} of {len(parent.records)} in {parent.active_file_name or 'file'}  |  Byte Delta: {delta_str}")

        f_left.config(text=f" Vanilla Reference (new_uspc) — {ref_b} Bytes ")
        t_ref.config(state="normal")
        t_ref.delete("1.0", tk.END)
        t_ref.insert("1.0", ref_text if ref_text else "(No reference string found in vanilla new_uspc)")
        t_ref.config(state="disabled")

        f_right.config(text=f" Active / Translated — {act_b} Bytes (Delta: {delta_str}) ")
        t_act.config(state="normal")
        t_act.delete("1.0", tk.END)
        t_act.insert("1.0", active_text)
        t_act.config(state="disabled")

        # Sync main window selection
        if str(eid) in parent.tree.get_children():
            parent.tree.selection_set(str(eid))
            parent.tree.see(str(eid))

        btn_prev.config(state="normal" if idx > 0 else "disabled")
        btn_next.config(state="normal" if idx < len(parent.records) - 1 else "disabled")

    btn_prev = tk.Button(bottom, text="⬅️ Previous Entry (Alt+Left)", command=lambda: load_entry(current_diff_idx - 1),
                         bg=parent.card_color, fg=parent.text_color, font=("Segoe UI", 9), relief="flat", padx=10, pady=3)
    btn_prev.pack(side="left", padx=(0, 8))
    parent.bind_hover(btn_prev)

    btn_next = tk.Button(bottom, text="Next Entry ➡️ (Alt+Right)", command=lambda: load_entry(current_diff_idx + 1),
                         bg=parent.card_color, fg=parent.text_color, font=("Segoe UI", 9), relief="flat", padx=10, pady=3)
    btn_next.pack(side="left")
    parent.bind_hover(btn_next)

    btn_close = tk.Button(bottom, text="Close", command=dialog.destroy, bg=parent.card_color, fg=parent.text_color, font=("Segoe UI", 9), relief="flat", padx=14, pady=3)
    btn_close.pack(side="right")
    parent.bind_hover(btn_close)

    dialog.bind("<Alt-Left>", lambda e: load_entry(current_diff_idx - 1))
    dialog.bind("<Alt-Right>", lambda e: load_entry(current_diff_idx + 1))

    load_entry(current_diff_idx)
