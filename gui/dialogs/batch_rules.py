"""
Batch Ruleset Manager Dialog
Allows creating, saving, loading, and batch executing replacement rulesets.
"""

import os
import json
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from core.rules_engine import apply_rules_to_string
from core.codec import FILE_RECORD_SIZES
from core.task_worker import TaskWorker
from gui.components.progress_dialog import TaskProgressDialog


def open_batch_ruleset_dialog(parent):
    """
    Reusable Batch Replacement Ruleset Manager (Pillar 4).
    Enables localization teams to create, save, load, and execute JSON rulesets
    across single files or the entire localization tree.
    """
    if not hasattr(parent, 'batch_rules') or parent.batch_rules is None:
        parent.batch_rules = []

    dialog = tk.Toplevel(parent.root)
    dialog.title("⚡ Reusable Batch Replacement Ruleset Manager")
    dialog.geometry("780x560")
    dialog.minsize(660, 440)
    dialog.configure(bg=parent.bg_color)
    dialog.transient(parent.root)
    dialog.grab_set()

    dialog.update_idletasks()
    rx = parent.root.winfo_x()
    ry = parent.root.winfo_y()
    rw = parent.root.winfo_width()
    rh = parent.root.winfo_height()
    dx = rx + max(0, (rw - 780) // 2)
    dy = ry + max(0, (rh - 560) // 2)
    dialog.geometry(f"+{dx}+{dy}")

    header = ttk.Frame(dialog, padding=(18, 14, 18, 6))
    header.pack(fill="x")
    tk.Label(header, text="⚡ Reusable Batch Replacement Ruleset Manager", font=("Segoe UI", 13, "bold"), fg=parent.accent_color, bg=parent.bg_color).pack(anchor="w")
    tk.Label(header, text="Define sequential nomenclature rulesets (e.g., standardizing ability or item names) and batch apply them with automatic backups.",
             font=("Segoe UI", 9), fg=parent.text_dim, bg=parent.bg_color).pack(anchor="w", pady=(2, 0))

    # Rule Editor Strip
    ed_strip = tk.Frame(dialog, bg=parent.card_color, padx=14, pady=10, highlightbackground=parent.border_color, highlightthickness=1)
    ed_strip.pack(fill="x", padx=18, pady=(4, 10))

    tk.Label(ed_strip, text="Find Pattern:", font=("Segoe UI", 9, "bold"), fg=parent.text_color, bg=parent.card_color).grid(row=0, column=0, sticky="w", padx=(0, 6))
    ent_find = ttk.Entry(ed_strip, width=22)
    ent_find.grid(row=0, column=1, sticky="ew", padx=(0, 12))

    tk.Label(ed_strip, text="Replace With:", font=("Segoe UI", 9, "bold"), fg=parent.text_color, bg=parent.card_color).grid(row=0, column=2, sticky="w", padx=(0, 6))
    ent_repl = ttk.Entry(ed_strip, width=22)
    ent_repl.grid(row=0, column=3, sticky="ew", padx=(0, 12))

    var_mc = tk.BooleanVar(value=True)
    chk_mc = ttk.Checkbutton(ed_strip, text="Match Case", variable=var_mc)
    chk_mc.grid(row=0, column=4, padx=(0, 8))

    var_rgx = tk.BooleanVar(value=False)
    chk_rgx = ttk.Checkbutton(ed_strip, text="Regex", variable=var_rgx)
    chk_rgx.grid(row=0, column=5, padx=(0, 12))

    tree_rules = ttk.Treeview(dialog, columns=("num", "find", "repl", "mc", "regex"), show="headings", height=8)
    tree_rules.heading("num", text="#", anchor="center")
    tree_rules.heading("find", text="Find Pattern", anchor="w")
    tree_rules.heading("repl", text="Replace With", anchor="w")
    tree_rules.heading("mc", text="Match Case", anchor="center")
    tree_rules.heading("regex", text="Regex", anchor="center")

    tree_rules.column("num", width=45, minwidth=35, stretch=False, anchor="center")
    tree_rules.column("find", width=250, minwidth=140, stretch=True)
    tree_rules.column("repl", width=250, minwidth=140, stretch=True)
    tree_rules.column("mc", width=90, minwidth=70, stretch=False, anchor="center")
    tree_rules.column("regex", width=80, minwidth=60, stretch=False, anchor="center")
    tree_rules.pack(fill="both", expand=True, padx=18, pady=(0, 10))

    def refresh_rules_table():
        for r in tree_rules.get_children():
            tree_rules.delete(r)
        for i, rule in enumerate(parent.batch_rules, 1):
            tree_rules.insert("", "end", values=(i, rule.get('find', ''), rule.get('replace', ''), "Yes" if rule.get('match_case') else "No", "Yes" if rule.get('regex') else "No"))

    def add_rule():
        f = ent_find.get().strip()
        r = ent_repl.get()
        if not f:
            messagebox.showwarning("Warning", "Find pattern cannot be empty.")
            return
        parent.batch_rules.append({"find": f, "replace": r, "match_case": var_mc.get(), "regex": var_rgx.get()})
        refresh_rules_table()
        ent_find.delete(0, tk.END)
        ent_repl.delete(0, tk.END)

    def delete_rule():
        sel = tree_rules.selection()
        if not sel:
            return
        idx = tree_rules.index(sel[0])
        if 0 <= idx < len(parent.batch_rules):
            parent.batch_rules.pop(idx)
            refresh_rules_table()

    def clear_rules():
        parent.batch_rules.clear()
        refresh_rules_table()

    def load_ruleset():
        p = filedialog.askopenfilename(title="Load Ruleset JSON", filetypes=[("JSON Ruleset", "*.json"), ("All Files", "*.*")])
        if p:
            try:
                with open(p, "r", encoding="utf-8") as f:
                    rules = json.load(f)
                    if isinstance(rules, list):
                        parent.batch_rules = rules
                        refresh_rules_table()
                        messagebox.showinfo("Success", f"Loaded {len(rules)} rules from {os.path.basename(p)}.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load ruleset: {e}")

    def save_ruleset():
        if not parent.batch_rules:
            messagebox.showwarning("Warning", "No rules to save.")
            return
        p = filedialog.asksaveasfilename(title="Save Ruleset JSON", defaultextension=".json", filetypes=[("JSON Ruleset", "*.json")])
        if p:
            try:
                with open(p, "w", encoding="utf-8") as f:
                    json.dump(parent.batch_rules, f, indent=2)
                    messagebox.showinfo("Success", f"Ruleset saved successfully to {os.path.basename(p)}.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save ruleset: {e}")

    btn_add = tk.Button(ed_strip, text="➕ Add Rule", command=add_rule, bg=parent.accent_color, fg="white", font=("Segoe UI", 9, "bold"), relief="flat", padx=10, pady=2)
    btn_add.grid(row=0, column=6)
    parent.bind_hover(btn_add, is_primary=True)

    act_strip = tk.Frame(dialog, bg=parent.bg_color, padx=18, pady=4)
    act_strip.pack(fill="x")

    btn_del = tk.Button(act_strip, text="🗑️ Delete Selected", command=delete_rule, bg=parent.card_color, fg=parent.text_color, font=("Segoe UI", 8), relief="flat", padx=8, pady=2)
    btn_del.pack(side="left", padx=(0, 6))
    parent.bind_hover(btn_del)

    btn_clr = tk.Button(act_strip, text="🧹 Clear All", command=clear_rules, bg=parent.card_color, fg=parent.text_color, font=("Segoe UI", 8), relief="flat", padx=8, pady=2)
    btn_clr.pack(side="left", padx=(0, 14))
    parent.bind_hover(btn_clr)

    btn_load = tk.Button(act_strip, text="📁 Load Ruleset (.json)", command=load_ruleset, bg=parent.card_color, fg=parent.text_color, font=("Segoe UI", 8, "bold"), relief="flat", padx=8, pady=2)
    btn_load.pack(side="left", padx=(0, 6))
    parent.bind_hover(btn_load)

    btn_save = tk.Button(act_strip, text="💾 Save Ruleset (.json)", command=save_ruleset, bg=parent.card_color, fg=parent.text_color, font=("Segoe UI", 8, "bold"), relief="flat", padx=8, pady=2)
    btn_save.pack(side="left")
    parent.bind_hover(btn_save)

    bottom = tk.Frame(dialog, bg=parent.card_color, padx=18, pady=10, highlightbackground=parent.border_color, highlightthickness=1)
    bottom.pack(fill="x", side="bottom")

    def execute_on_file():
        if not parent.records:
            messagebox.showwarning("Warning", "No active file records loaded.")
            return
        if not parent.batch_rules:
            messagebox.showwarning("Warning", "Ruleset is empty.")
            return
        tot = 0
        for r in parent.records:
            for fld in ('name', 'sname', 'desc', 'sdesc', 'w_wakka', 'w_lulu', 'w_rikku'):
                if fld in r and isinstance(r[fld], str):
                    new_s, n = apply_rules_to_string(r[fld], parent.batch_rules)
                    if n > 0:
                        r[fld] = new_s
                        tot += n
        parent.filter_treeview()
        sel = parent.tree.selection()
        if sel:
            parent.on_tree_row_selected(None)
        parent.update_live_preview()
        parent.log(f"Batch rules executed: Replaced {tot} occurrences in active file.", "success")
        messagebox.showinfo("Success", f"Replaced {tot} occurrences in active file!\n\nRemember to save changes (Ctrl+S).")

    btn_run_file = tk.Button(bottom, text="▶️ Execute on Current File", command=execute_on_file, bg=parent.accent_color, fg="white", font=("Segoe UI", 9, "bold"), relief="flat", padx=12, pady=4)
    btn_run_file.pack(side="left", padx=(0, 10))
    parent.bind_hover(btn_run_file, is_primary=True)

    def execute_on_entire_loc():
        if not parent.batch_rules:
            messagebox.showwarning("Warning", "Ruleset is empty. Add at least one rule first.")
            return
        loc_name = parent.cmb_local.get() if hasattr(parent, 'cmb_local') else "new_uspc"
        master_p = parent.codec.ffx_master_path
        loc_dir = os.path.join(master_p, loc_name) if master_p else ""
        if not loc_dir or not os.path.exists(loc_dir):
            messagebox.showerror("Error", f"Localization directory '{loc_name}' not found under Master folder.")
            return
            
        if not messagebox.askyesno("Confirm Batch Localization Run",
            f"Apply all {len(parent.batch_rules)} rule(s) across all .bin and .sps2 files in '{loc_name}'?\n\n"
            f"• An automatic .bak backup will be generated for every modified file before writing.\n"
            f"• This operation directly modifies localization files on disk.\n\n"
            f"Proceed with batch localization execution?"):
            return
            
        charset = parent.cmb_charset.get() if hasattr(parent, 'cmb_charset') else 'us'

        # Gather target files
        candidate_files = []
        for root, dirs, files in os.walk(loc_dir):
            for f in files:
                if f.endswith(".bak") or f.startswith("ffxsjis"):
                    continue
                if not (f.endswith(".bin") or f.endswith(".sps2") or f.endswith(".dcp")):
                    continue
                candidate_files.append((f, os.path.join(root, f)))

        total_files = len(candidate_files)
        if total_files == 0:
            messagebox.showinfo("Batch Execution", "No target files found in localization folder.")
            return

        def worker_fn(worker: TaskWorker):
            mod_files = 0
            total_reps = 0
            for i, (f, fpath) in enumerate(candidate_files):
                if worker.is_cancelled():
                    break
                worker.report_progress(i, total_files, f"Processing {f}...")
                try:
                    record_len = FILE_RECORD_SIZES.get(f, 16)
                    recs, min_id, max_id, magic_part, m = parent.codec.load_any_ffx_file(fpath, record_len, charset)
                    file_reps = 0
                    for r in recs:
                        for fld in ('name', 'sname', 'desc', 'sdesc', 'w_wakka', 'w_lulu', 'w_rikku'):
                            if fld in r and isinstance(r[fld], str):
                                new_s, n = apply_rules_to_string(r[fld], parent.batch_rules)
                                if n > 0:
                                    r[fld] = new_s
                                    file_reps += n
                    if file_reps > 0:
                        bak_p = fpath + ".bak"
                        if not os.path.exists(bak_p):
                            shutil.copy2(fpath, bak_p)
                        parent.codec.save_any_ffx_file(fpath, recs, min_id, max_id, magic_part, charset)
                        mod_files += 1
                        total_reps += file_reps
                        
                        if fpath == parent.active_file_path:
                            parent.records = recs
                            parent.root.after(0, parent.filter_treeview)
                            parent.root.after(0, parent.update_live_preview)
                except Exception as err:
                    parent.log(f"Error executing rules on {f}: {err}", "error")

            return (total_files, mod_files, total_reps)

        def on_complete(result):
            if result:
                tot_f, mod_f, tot_r = result
                parent.log(f"Batch Localization Complete: Processed {tot_f} files, modified {mod_f} files, {tot_r} replacements made.", "success")
                messagebox.showinfo("Batch Execution Complete",
                    f"Batch localization execution complete!\n\n"
                    f"• Scanned files: {tot_f}\n"
                    f"• Modified files: {mod_f}\n"
                    f"• Total replacements: {tot_r}\n\n"
                    f"Automatic .bak backup files were created for all modified files.")

        prog_dlg = TaskProgressDialog(dialog, "Batch Localization Execution", "Applying batch rulesets across files...")
        prog_dlg.run_worker(worker_fn, on_complete)

    btn_run_loc = tk.Button(bottom, text="🚀 Execute on Entire Localization (All Files)", command=execute_on_entire_loc, bg=parent.card_color, fg="#38bdf8", font=("Segoe UI", 9, "bold"), relief="flat", padx=12, pady=4)
    btn_run_loc.pack(side="left")
    parent.bind_hover(btn_run_loc)

    btn_close = tk.Button(bottom, text="Close", command=dialog.destroy, bg=parent.bg_color, fg=parent.text_color, font=("Segoe UI", 9), relief="flat", padx=14, pady=4)
    btn_close.pack(side="right")
    parent.bind_hover(btn_close)

    refresh_rules_table()
