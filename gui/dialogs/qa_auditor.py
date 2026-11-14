"""
Automated QA & Syntax Crash Auditor Dialog
Deep-scans text records for syntax corruption, unclosed tags, ruler overflow,
byte overflow, and 16-bit offset pool limits.
"""

import os
import csv
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from core.qa_engine import QAEngine, auto_fix_string
from core.codec import FILE_RECORD_SIZES
from core.task_worker import TaskWorker
from gui.components.progress_dialog import TaskProgressDialog


def open_qa_auditor_dialog(parent):
    """
    Automated QA & Crash Prevention Engine (Pillar 2).
    Deep-scans for:
    - Bracket balance ({ vs })
    - Unknown/malformed engine tags
    - Unclosed color tags ({CLR:...} without terminating {CLR:WHITE})
    - Dialogue line width overflow (>43 chars)
    - Dialogue line height overflow (>4 lines)
    - Entry byte overflow (>500B warning, >800B critical)
    - 16-bit offset pool overflow (>60,000B warning, >65,535B FATAL)
    Provides double-click jump to file/entry, 1-click Auto-Fix, and CSV export.
    """
    dialog = tk.Toplevel(parent.root)
    dialog.title("🛡️ Automated QA & Syntax Crash Auditor")
    dialog.geometry("860x600")
    dialog.minsize(720, 480)
    dialog.configure(bg=parent.bg_color)
    dialog.transient(parent.root)
    dialog.grab_set()

    dialog.update_idletasks()
    rx = parent.root.winfo_x()
    ry = parent.root.winfo_y()
    rw = parent.root.winfo_width()
    rh = parent.root.winfo_height()
    dx = rx + max(0, (rw - 860) // 2)
    dy = ry + max(0, (rh - 600) // 2)
    dialog.geometry(f"+{dx}+{dy}")

    header = ttk.Frame(dialog, padding=(18, 14, 18, 6))
    header.pack(fill="x")
    tk.Label(header, text="🛡️ Automated QA & Syntax Crash Auditor", font=("Segoe UI", 13, "bold"), fg=parent.accent_color, bg=parent.bg_color).pack(anchor="w")
    tk.Label(header, text="Deep-scans text records for syntax corruption, unclosed tags, ruler overflow, byte overflow, and fatal 16-bit offset pool limits.",
             font=("Segoe UI", 9), fg=parent.text_dim, bg=parent.bg_color).pack(anchor="w", pady=(2, 0))

    # Controls Strip
    ctrl_frame = tk.Frame(dialog, bg=parent.card_color, padx=12, pady=8, highlightbackground=parent.border_color, highlightthickness=1)
    ctrl_frame.pack(fill="x", padx=18, pady=(4, 8))

    tk.Label(ctrl_frame, text="Audit Scope:", font=("Segoe UI", 9, "bold"), fg=parent.text_color, bg=parent.card_color).pack(side="left", padx=(0, 6))
    cmb_scope = ttk.Combobox(ctrl_frame, values=["Current File", "Current Category", "Entire Localization"], state="readonly", width=18, font=("Segoe UI", 9))
    cmb_scope.set("Current File")
    cmb_scope.pack(side="left", padx=(0, 14))

    tk.Label(ctrl_frame, text="Severity Filter:", font=("Segoe UI", 9, "bold"), fg=parent.text_color, bg=parent.card_color).pack(side="left", padx=(0, 6))
    cmb_sev = ttk.Combobox(ctrl_frame, values=["All Issues", "🔴 Critical Only", "🟡 Warnings Only"], state="readonly", width=16, font=("Segoe UI", 9))
    cmb_sev.set("All Issues")
    cmb_sev.pack(side="left", padx=(0, 14))

    # Results treeview
    tree_frame = tk.Frame(dialog, bg=parent.bg_color, padx=18)
    tree_frame.pack(fill="both", expand=True)

    cols = ("sev", "file", "id", "field", "issue", "snip")
    tree_audit = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="browse")
    tree_audit.heading("sev", text="Severity", anchor="center")
    tree_audit.heading("file", text="File", anchor="w")
    tree_audit.heading("id", text="ID", anchor="center")
    tree_audit.heading("field", text="Field", anchor="w")
    tree_audit.heading("issue", text="Detected Issue", anchor="w")
    tree_audit.heading("snip", text="Snippet / Preview", anchor="w")

    tree_audit.column("sev", width=85, minwidth=70, stretch=False, anchor="center")
    tree_audit.column("file", width=130, minwidth=100, stretch=False)
    tree_audit.column("id", width=55, minwidth=45, stretch=False, anchor="center")
    tree_audit.column("field", width=80, minwidth=70, stretch=False)
    tree_audit.column("issue", width=300, minwidth=180, stretch=True)
    tree_audit.column("snip", width=190, minwidth=120, stretch=True)

    tree_audit.tag_configure("critical", foreground="#f87171", background="#2a1215")
    tree_audit.tag_configure("warning", foreground="#fbbf24", background="#261e12")
    tree_audit.tag_configure("info", foreground="#38bdf8", background="#111c2e")

    scr = ttk.Scrollbar(tree_frame, orient="vertical", command=tree_audit.yview)
    tree_audit.configure(yscrollcommand=scr.set)
    tree_audit.pack(side="left", fill="both", expand=True)
    scr.pack(side="right", fill="y")

    # Bottom Bar
    bottom = tk.Frame(dialog, bg=parent.bg_color, padx=18, pady=10)
    bottom.pack(fill="x")

    lbl_summary = tk.Label(bottom, text="Ready to audit.", font=("Segoe UI", 9, "bold"), fg=parent.text_dim, bg=parent.bg_color)
    lbl_summary.pack(side="left")

    all_detected_issues = []  # list of tuples: (sev, file, id, field, issue, snip, is_safe, fix_type, fpath)

    qa_engine = QAEngine(codec=parent.codec)

    def run_scanner():
        nonlocal all_detected_issues
        for r in tree_audit.get_children():
            tree_audit.delete(r)
        all_detected_issues.clear()

        scope = cmb_scope.get()
        charset = parent.cmb_charset.get() if hasattr(parent, 'cmb_charset') else 'us'

        files_to_scan = []  # list of (file_label, full_path, records_or_none)
        if scope == "Current File":
            if parent.active_file_path and os.path.exists(parent.active_file_path):
                files_to_scan.append((parent.active_file_name, parent.active_file_path, parent.records))
        elif scope == "Current Category":
            for rel, fpath in getattr(parent, 'file_map', {}).items():
                if os.path.exists(fpath):
                    recs = parent.records if (fpath == parent.active_file_path) else None
                    files_to_scan.append((rel, fpath, recs))
        else:  # Entire Localization
            loc = parent.cmb_local.get() if hasattr(parent, 'cmb_local') else "new_uspc"
            loc_dir = os.path.join(parent.codec.ffx_master_path, loc) if parent.codec.ffx_master_path else ""
            if loc_dir and os.path.exists(loc_dir):
                for root, dirs, files in os.walk(loc_dir):
                    for f in files:
                        if f.endswith(".bin") or f.endswith(".sps2") or f.endswith(".dcp"):
                            if f.endswith(".bak") or f.startswith("ffxsjis") or f.endswith("_page.sps2"):
                                continue
                            fp = os.path.join(root, f)
                            rel = os.path.relpath(fp, loc_dir).replace("\\", "/")
                            recs = parent.records if (fp == parent.active_file_path) else None
                            files_to_scan.append((rel, fp, recs))

        if not files_to_scan:
            messagebox.showwarning("Warning", "No files found to audit.")
            return

        def do_scan(worker: TaskWorker = None):
            crit_count = 0
            warn_count = 0
            detected = []

            for i, (fname, fpath, loaded_recs) in enumerate(files_to_scan):
                if worker and worker.is_cancelled():
                    break
                if worker:
                    worker.report_progress(i, len(files_to_scan), f"Scanning {fname}...")

                recs = loaded_recs
                if recs is None:
                    try:
                        record_len = FILE_RECORD_SIZES.get(os.path.basename(fname), 16)
                        recs, _, _, _, _ = parent.codec.load_any_ffx_file(fpath, record_len, charset)
                    except Exception:
                        recs = []

                if not recs:
                    continue

                errors = qa_engine.audit_file(fname, fpath, recs, charset)
                for err in errors:
                    iss = (
                        f"🔴 {err.severity}" if err.severity == "CRITICAL" else f"🟡 {err.severity}",
                        err.file_name,
                        err.entry_id,
                        err.field,
                        err.message,
                        err.snippet,
                        err.is_auto_fixable,
                        err.fix_type,
                        err.file_path or fpath
                    )
                    detected.append(iss)
                    if err.severity == "CRITICAL":
                        crit_count += 1
                    else:
                        warn_count += 1

            return (detected, crit_count, warn_count)

        if len(files_to_scan) > 5:
            def on_complete(result):
                nonlocal all_detected_issues
                if result:
                    detected, crit_count, warn_count = result
                    all_detected_issues = detected
                    parent.current_audit_issues = list(all_detected_issues)
                    populate_audit_tree()
                    lbl_summary.config(text=f"Scan complete across {len(files_to_scan)} file(s):  🔴 {crit_count} Critical  |  🟡 {warn_count} Warnings")

            prog = TaskProgressDialog(dialog, "QA Localization Scanner", "Deep scanning localization files...")
            prog.run_worker(do_scan, on_complete)
        else:
            detected, crit_count, warn_count = do_scan(None)
            all_detected_issues = detected
            parent.current_audit_issues = list(all_detected_issues)
            populate_audit_tree()
            lbl_summary.config(text=f"Scan complete across {len(files_to_scan)} file(s):  🔴 {crit_count} Critical  |  🟡 {warn_count} Warnings")

    def populate_audit_tree():
        for r in tree_audit.get_children():
            tree_audit.delete(r)
        sev_filter = cmb_sev.get()

        for iss in all_detected_issues:
            sev = iss[0]
            if "Critical" in sev_filter and "CRITICAL" not in sev:
                continue
            if "Warnings" in sev_filter and "WARNING" not in sev:
                continue
            tag = "critical" if "CRITICAL" in sev else ("warning" if "WARNING" in sev else "info")
            tree_audit.insert("", "end", values=(iss[0], iss[1], iss[2], iss[3], iss[4], iss[5]), tags=(tag,))

    cmb_sev.bind("<<ComboboxSelected>>", lambda e: populate_audit_tree())

    def on_audit_double_click(event):
        sel = tree_audit.selection()
        if not sel:
            return
        vals = tree_audit.item(sel[0], "values")
        fname = vals[1]
        try:
            target_id = int(vals[2])
        except ValueError:
            target_id = vals[2]
        target_fld = vals[3]

        matching_iss = next((i for i in all_detected_issues if i[1] == fname and str(i[2]) == str(target_id) and i[3] == target_fld), None)
        if not matching_iss:
            return
        target_fpath = matching_iss[8]

        if target_fpath != parent.active_file_path:
            switched = False
            for k, p in getattr(parent, 'file_map', {}).items():
                if p == target_fpath or os.path.basename(p) == fname or k == fname:
                    parent.cmb_bin_file.set(k)
                    parent.on_bin_file_selected()
                    switched = True
                    break
            if not switched and os.path.exists(target_fpath):
                parent.load_from_absolute_path(target_fpath)

        if str(target_id) in parent.tree.get_children():
            parent.tree.selection_set(str(target_id))
            parent.tree.see(str(target_id))
            parent.on_tree_row_selected(None)

            if target_fld == 'name' and hasattr(parent, 'ent_name'):
                parent.ent_name.focus_set()
            elif target_fld == 'desc' and hasattr(parent, 'ent_desc'):
                parent.ent_desc.focus_set()
            elif hasattr(parent, 'txt_dialogue'):
                parent.txt_dialogue.focus_set()

    tree_audit.bind("<Double-1>", on_audit_double_click)

    def auto_fix_safe_issues():
        safe_issues = [i for i in all_detected_issues if i[6]]
        if not safe_issues:
            messagebox.showinfo("Auto-Fix", "No safe issues (e.g. unclosed color tags, tag whitespace, trailing whitespace) detected to auto-fix.")
            return

        if not messagebox.askyesno("Confirm Auto-Fix",
            f"Found {len(safe_issues)} safe issues across audited files:\n\n"
            f"• Close unclosed color tags with {{CLR:WHITE}}\n"
            f"• Normalize whitespace inside engine tags\n"
            f"• Trim trailing whitespace on dialogue lines\n\n"
            f"Auto-fix these safe issues (automatic .bak backups will be created)?"):
            return

        issues_by_file = {}
        for iss in safe_issues:
            issues_by_file.setdefault(iss[8], []).append(iss)

        charset = parent.cmb_charset.get() if hasattr(parent, 'cmb_charset') else 'us'
        fixed_count = 0
        fixed_files = 0

        for fpath, f_issues in issues_by_file.items():
            if fpath == parent.active_file_path:
                file_modified = False
                for iss in f_issues:
                    eid, fld, fix_kind = iss[2], iss[3], iss[7]
                    rec = next((r for r in parent.records if str(r.get('id')) == str(eid)), None)
                    if rec and fld in rec and isinstance(rec[fld], str):
                        s = rec[fld]
                        new_s = auto_fix_string(s, fix_kind)
                        if new_s != s:
                            rec[fld] = new_s
                            fixed_count += 1
                            file_modified = True
                if file_modified:
                    fixed_files += 1
                    parent.filter_treeview()
                    sel = parent.tree.selection()
                    if sel:
                        parent.on_tree_row_selected(None)
                    parent.update_live_preview()
            elif os.path.exists(fpath):
                try:
                    record_len = FILE_RECORD_SIZES.get(os.path.basename(fpath), 16)
                    recs, min_id, max_id, magic_part, m = parent.codec.load_any_ffx_file(fpath, record_len, charset)
                    file_modified = False
                    for iss in f_issues:
                        eid, fld, fix_kind = iss[2], iss[3], iss[7]
                        rec = next((r for r in recs if str(r.get('id')) == str(eid)), None)
                        if rec and fld in rec and isinstance(rec[fld], str):
                            s = rec[fld]
                            new_s = auto_fix_string(s, fix_kind)
                            if new_s != s:
                                rec[fld] = new_s
                                fixed_count += 1
                                file_modified = True
                    if file_modified:
                        bak_p = fpath + ".bak"
                        if not os.path.exists(bak_p):
                            shutil.copy2(fpath, bak_p)
                        parent.codec.save_any_ffx_file(fpath, recs, min_id, max_id, magic_part, charset)
                        fixed_files += 1
                except Exception as err:
                    parent.log(f"Error auto-fixing file {fpath}: {err}", "error")

        if fixed_count > 0:
            parent.log(f"Auto-fixed {fixed_count} safe issues across {fixed_files} file(s).", "success")

        run_scanner()
        messagebox.showinfo("Auto-Fix Completed", f"Successfully auto-fixed {fixed_count} safe issues across {fixed_files} file(s)!\n\nRemember to save active file changes (Ctrl+S).")

    def export_audit_csv():
        if not all_detected_issues:
            messagebox.showwarning("Warning", "No audit issues to export. Run the scanner first!")
            return
        p = filedialog.asksaveasfilename(
            title="Export QA Audit Report CSV",
            defaultextension=".csv",
            filetypes=[("CSV Spreadsheet", "*.csv"), ("All Files", "*.*")]
        )
        if not p:
            return
        try:
            with open(p, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["Severity", "File", "Entry ID", "Field", "Issue Detected", "Snippet / Details", "File Path"])
                for iss in all_detected_issues:
                    writer.writerow([iss[0], iss[1], iss[2], iss[3], iss[4], iss[5], iss[8]])
            messagebox.showinfo("Export Successful", f"Successfully exported {len(all_detected_issues)} audit issues to:\n{os.path.basename(p)}")
            parent.log(f"Exported QA audit report ({len(all_detected_issues)} rows) to {p}", "success")
        except Exception as err:
            messagebox.showerror("Export Failed", f"Failed to export CSV report:\n{err}")

    btn_run = tk.Button(ctrl_frame, text="🔍 Run Audit Scanner", command=run_scanner, bg=parent.accent_color, fg="white", font=("Segoe UI", 9, "bold"), relief="flat", padx=10, pady=2)
    btn_run.pack(side="left", padx=(10, 6))
    parent.bind_hover(btn_run, is_primary=True)

    btn_fix = tk.Button(ctrl_frame, text="⚡ 1-Click Auto-Fix Safe Issues", command=auto_fix_safe_issues, bg=parent.card_color, fg="#4ade80", font=("Segoe UI", 9, "bold"), relief="flat", padx=10, pady=2)
    btn_fix.pack(side="left", padx=(0, 6))
    parent.bind_hover(btn_fix)

    btn_export = tk.Button(ctrl_frame, text="📄 Export Audit Report (CSV)", command=export_audit_csv, bg=parent.card_color, fg=parent.text_color, font=("Segoe UI", 9, "bold"), relief="flat", padx=10, pady=2)
    btn_export.pack(side="left")
    parent.bind_hover(btn_export)

    btn_close = tk.Button(bottom, text="Close", command=dialog.destroy, bg=parent.card_color, fg=parent.text_color, font=("Segoe UI", 9), relief="flat", padx=14, pady=3)
    btn_close.pack(side="right")
    parent.bind_hover(btn_close)

    dialog.after(100, run_scanner)
