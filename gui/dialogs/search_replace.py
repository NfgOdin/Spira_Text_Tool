"""
Global Search and Replace Dialog
Supports Regex, case-sensitive matching, dry-run match previews, and automatic backups.
"""

import os
import re
import shutil
import tkinter as tk
from tkinter import ttk, messagebox
from core.codec import FILE_RECORD_SIZES


def open_search_replace_dialog(parent):
    """
    Global Search & Replace dialog with scope filtering, preview window,
    regex support, and automatic backups.
    """
    if not getattr(parent, 'records', None):
        messagebox.showwarning("Warning", "Load the target table file in the editor first.")
        return

    dialog = tk.Toplevel(parent.root)
    dialog.title("Global Search & Replace")
    dialog.geometry("480x280")
    dialog.resizable(False, False)
    dialog.configure(bg=parent.bg_color)
    dialog.transient(parent.root)
    dialog.grab_set()

    dialog.columnconfigure(1, weight=1)

    ttk.Label(dialog, text="Find Text:").grid(row=0, column=0, sticky="w", padx=15, pady=(15, 5))
    ent_find = ttk.Entry(dialog, width=40)
    ent_find.grid(row=0, column=1, sticky="ew", padx=15, pady=(15, 5))

    ttk.Label(dialog, text="Replace With:").grid(row=1, column=0, sticky="w", padx=15, pady=5)
    ent_replace = ttk.Entry(dialog, width=40)
    ent_replace.grid(row=1, column=1, sticky="ew", padx=15, pady=5)

    ttk.Label(dialog, text="Scope:").grid(row=2, column=0, sticky="w", padx=15, pady=5)
    cmb_scope = ttk.Combobox(dialog, state="readonly", values=["Current File only", "Current Category files", "All Files in Localization"])
    cmb_scope.grid(row=2, column=1, sticky="w", padx=15, pady=5)
    cmb_scope.set("Current File only")

    opts_frame = ttk.Frame(dialog)
    opts_frame.grid(row=3, column=1, sticky="w", padx=15, pady=5)

    var_case = tk.BooleanVar(value=False)
    chk_case = ttk.Checkbutton(opts_frame, text="Case Sensitive", variable=var_case)
    chk_case.pack(side="left", padx=(0, 15))

    var_regex = tk.BooleanVar(value=False)
    chk_regex = ttk.Checkbutton(opts_frame, text="Regular Expressions (Regex)", variable=var_regex)
    chk_regex.pack(side="left")

    btn_frame = ttk.Frame(dialog)
    btn_frame.grid(row=4, column=0, columnspan=2, sticky="ew", padx=15, pady=15)

    def compile_pattern(find_txt, case_sens, is_regex):
        flags = 0 if case_sens else re.IGNORECASE
        if is_regex:
            return re.compile(find_txt, flags)
        else:
            return re.compile(re.escape(find_txt), flags)

    def collect_matches(find_txt, replace_txt, scope, case_sens, is_regex):
        try:
            pattern = compile_pattern(find_txt, case_sens, is_regex)
        except Exception as e:
            messagebox.showerror("Regex Error", f"Invalid Regular Expression pattern:\n{e}")
            return None

        matches = []  # list of dicts: {disp_name, fpath, id, field, old, new, is_mem, rec}
        if scope == "Current File only":
            fields = ['name', 'sname', 'desc', 'sdesc'] if parent.active_mode == 'kernel' else ['name']
            if parent.active_file_name == "w_name.bin":
                fields.extend(['w_wakka', 'w_lulu', 'w_rikku'])

            for r in parent.records:
                for fld in fields:
                    orig = r.get(fld, "")
                    if not orig:
                        continue
                    try:
                        new_val, sub_cnt = pattern.subn(replace_txt, orig)
                        if sub_cnt > 0:
                            matches.append({
                                'file': parent.active_file_name,
                                'fpath': parent.active_file_path,
                                'id': r['id'],
                                'field': fld,
                                'old': orig,
                                'new': new_val,
                                'is_mem': True,
                                'rec': r
                            })
                    except Exception:
                        pass
        elif scope == "Current Category files":
            charset = parent.cmb_charset.get() if hasattr(parent, 'cmb_charset') else 'us'
            for fname, fpath in parent.file_map.items():
                try:
                    recs, min_id, max_id, magic, mode = parent.codec.load_any_ffx_file(fpath, 16, charset)
                    fields = ['name', 'sname', 'desc', 'sdesc'] if mode == 'kernel' else ['name']
                    if fname == "w_name.bin":
                        fields.extend(['w_wakka', 'w_lulu', 'w_rikku'])
                    for r in recs:
                        for fld in fields:
                            orig = r.get(fld, "")
                            if not orig:
                                continue
                            new_val, sub_cnt = pattern.subn(replace_txt, orig)
                            if sub_cnt > 0:
                                matches.append({
                                    'file': fname,
                                    'fpath': fpath,
                                    'id': r['id'],
                                    'field': fld,
                                    'old': orig,
                                    'new': new_val,
                                    'is_mem': False,
                                    'rec': r
                                })
                except Exception:
                    pass
        else:
            loc = parent.cmb_local.get() if hasattr(parent, 'cmb_local') else 'new_uspc'
            loc_dir = os.path.join(parent.codec.ffx_master_path, loc) if parent.codec.ffx_master_path else ""
            all_files = []
            if loc_dir and os.path.exists(loc_dir):
                kernel_dir = os.path.join(loc_dir, "battle", "kernel")
                if os.path.exists(kernel_dir):
                    for f in os.listdir(kernel_dir):
                        if f.endswith(".bin") and f in FILE_RECORD_SIZES:
                            all_files.append((f"kernel/{f}", os.path.join(kernel_dir, f)))
                help_dir = os.path.join(loc_dir, "help")
                if os.path.exists(help_dir):
                    for root, dirs, files in os.walk(help_dir):
                        for f in files:
                            if f.endswith(".sps2"):
                                rel = os.path.relpath(os.path.join(root, f), help_dir).replace("\\", "/")
                                if not rel.endswith("_page.sps2") and not any(sub in rel.lower() for sub in ["/gcm/", "/gnm/", "/gxm/", "gcm/", "gnm/", "gxm/"]):
                                    all_files.append((f"help/{rel}", os.path.join(root, f)))
                evt_dir = os.path.join(loc_dir, "event", "obj_ps3")
                if not os.path.exists(evt_dir):
                    evt_dir = os.path.join(loc_dir, "event", "obj_psv")
                if not os.path.exists(evt_dir):
                    evt_dir = os.path.join(loc_dir, "event")
                if os.path.exists(evt_dir):
                    for root, dirs, files in os.walk(evt_dir):
                        for f in files:
                            if f.endswith(".bin"):
                                all_files.append((f"event/{f}", os.path.join(root, f)))
                btl_dir = os.path.join(loc_dir, "battle", "btl")
                if os.path.exists(btl_dir):
                    for root, dirs, files in os.walk(btl_dir):
                        for f in files:
                            if f.endswith(".bin"):
                                all_files.append((f"btl/{f}", os.path.join(root, f)))
                menu_dir = os.path.join(loc_dir, "menu")
                if os.path.exists(menu_dir):
                    for f in os.listdir(menu_dir):
                        if (f.endswith(".bin") or f == "macrodic.dcp") and not f.startswith("ffxsjis"):
                            all_files.append((f"menu/{f}", os.path.join(menu_dir, f)))

            charset = parent.cmb_charset.get() if hasattr(parent, 'cmb_charset') else 'us'
            for disp_name, fpath in all_files:
                try:
                    recs, min_id, max_id, magic, mode = parent.codec.load_any_ffx_file(fpath, 16, charset)
                    fields = ['name', 'sname', 'desc', 'sdesc'] if mode == 'kernel' else ['name']
                    if "w_name.bin" in fpath.lower():
                        fields.extend(['w_wakka', 'w_lulu', 'w_rikku'])
                    for r in recs:
                        for fld in fields:
                            orig = r.get(fld, "")
                            if not orig:
                                continue
                            new_val, sub_cnt = pattern.subn(replace_txt, orig)
                            if sub_cnt > 0:
                                matches.append({
                                    'file': disp_name,
                                    'fpath': fpath,
                                    'id': r['id'],
                                    'field': fld,
                                    'old': orig,
                                    'new': new_val,
                                    'is_mem': False,
                                    'rec': r
                                })
                except Exception:
                    pass
        return matches

    def run_preview():
        find_txt = ent_find.get()
        replace_txt = ent_replace.get()
        scope = cmb_scope.get()
        case_sens = var_case.get()
        is_regex = var_regex.get()

        if not find_txt:
            messagebox.showwarning("Warning", "Please enter text to find.")
            return

        matches = collect_matches(find_txt, replace_txt, scope, case_sens, is_regex)
        if matches is None:
            return
        if not matches:
            messagebox.showinfo("Preview Matches", f"No occurrences found for '{find_txt}'.")
            return

        prev_win = tk.Toplevel(dialog)
        prev_win.title(f"🔍 Search & Replace Preview - {len(matches)} Matches")
        prev_win.geometry("860x520")
        prev_win.configure(bg=parent.bg_color)
        prev_win.transient(dialog)
        prev_win.grab_set()

        p_hdr = ttk.Frame(prev_win, padding=(15, 10))
        p_hdr.pack(fill="x")
        tk.Label(p_hdr, text=f"Found {len(matches)} match(es) across {len(set(m['file'] for m in matches))} file(s)", font=("Segoe UI", 11, "bold"), fg=parent.accent_color, bg=parent.bg_color).pack(anchor="w")
        tk.Label(p_hdr, text=f"Find: '{find_txt}'  ➔  Replace: '{replace_txt}' (Regex: {is_regex}, Case Sensitive: {case_sens})", font=("Segoe UI", 9), fg=parent.text_dim, bg=parent.bg_color).pack(anchor="w")

        tbl_frame = ttk.Frame(prev_win, padding=10)
        tbl_frame.pack(fill="both", expand=True)

        p_tree = ttk.Treeview(tbl_frame, columns=("file", "id", "field", "old", "new"), show="headings")
        p_tree.heading("file", text="File")
        p_tree.heading("id", text="ID")
        p_tree.heading("field", text="Field")
        p_tree.heading("old", text="Before")
        p_tree.heading("new", text="After")

        p_tree.column("file", width=140, anchor="w")
        p_tree.column("id", width=55, anchor="center")
        p_tree.column("field", width=75, anchor="w")
        p_tree.column("old", width=280, anchor="w")
        p_tree.column("new", width=280, anchor="w")

        p_scroll = ttk.Scrollbar(tbl_frame, orient="vertical", command=p_tree.yview)
        p_tree.configure(yscrollcommand=p_scroll.set)
        p_tree.pack(side="left", fill="both", expand=True)
        p_scroll.pack(side="right", fill="y")

        for m in matches:
            p_tree.insert("", tk.END, values=(m['file'], m['id'], m['field'], m['old'].replace("\n", "{\\n}"), m['new'].replace("\n", "{\\n}")))

        b_bar = ttk.Frame(prev_win, padding=(15, 10))
        b_bar.pack(fill="x")

        def execute_from_preview():
            prev_win.destroy()
            run_replace()

        btn_apply_prev = tk.Button(b_bar, text=f"✅ Apply All {len(matches)} Replacements", command=execute_from_preview,
                                   bg=parent.accent_color, fg="white", font=("Segoe UI", 9, "bold"), relief="flat", padx=15, pady=4)
        btn_apply_prev.pack(side="right", padx=(8, 0))
        parent.bind_hover(btn_apply_prev, is_primary=True)

        btn_cancel_prev = tk.Button(b_bar, text="Cancel", command=prev_win.destroy,
                                    bg=parent.card_color, fg=parent.text_color, font=("Segoe UI", 9), relief="flat", padx=12, pady=4)
        btn_cancel_prev.pack(side="right")
        parent.bind_hover(btn_cancel_prev)

    def run_replace():
        find_txt = ent_find.get()
        replace_txt = ent_replace.get()
        scope = cmb_scope.get()
        case_sens = var_case.get()
        is_regex = var_regex.get()

        if not find_txt:
            messagebox.showwarning("Warning", "Please enter text to find.")
            return

        try:
            pattern = compile_pattern(find_txt, case_sens, is_regex)
        except Exception as e:
            messagebox.showerror("Regex Error", f"Invalid Regular Expression:\n{e}")
            return

        if scope == "Current File only":
            count = 0
            fields = ['name', 'sname', 'desc', 'sdesc'] if parent.active_mode == 'kernel' else ['name']
            if parent.active_file_name == "w_name.bin":
                fields.extend(['w_wakka', 'w_lulu', 'w_rikku'])

            for r in parent.records:
                for field in fields:
                    orig = r.get(field, "")
                    if not orig:
                        continue
                    new_val, sub_count = pattern.subn(replace_txt, orig)
                    if sub_count > 0:
                        r[field] = new_val
                        count += sub_count
            if count > 0:
                parent.log(f"Search & Replace: Replaced {count} occurrences in current file memory.", "success")
                parent.filter_treeview()
                parent.clear_editor_fields()
                messagebox.showinfo("Success", f"Replaced {count} occurrences in the current file.\n\nNote: Changes are in-memory. Click 'Repack & Save' to write them to disk.")
                dialog.destroy()
            else:
                messagebox.showinfo("Search & Replace", "No occurrences found.")
        elif scope == "Current Category files":
            cat_name = parent.cmb_category.get() if hasattr(parent, 'cmb_category') else "Category"
            ans = messagebox.askyesno("Confirm Category Action",
                f"This will read, modify, and save all {len(parent.file_map)} files in the active category: '{cat_name}'.\n"
                "Automatic backup files (.bak) will be created for any modified files.\n\n"
                "Are you sure you want to perform this category-wide replacement?")
            if not ans:
                return

            charset = parent.cmb_charset.get() if hasattr(parent, 'cmb_charset') else 'us'
            modified_files = []
            total_replaced = 0

            for fname, fpath in parent.file_map.items():
                try:
                    recs, min_id, max_id, magic, mode = parent.codec.load_any_ffx_file(fpath, 16, charset)
                    file_mod = False
                    file_replaced = 0
                    fields = ['name', 'sname', 'desc', 'sdesc'] if mode == 'kernel' else ['name']
                    if fname == "w_name.bin":
                        fields.extend(['w_wakka', 'w_lulu', 'w_rikku'])

                    for r in recs:
                        for field in fields:
                            orig = r.get(field, "")
                            if not orig:
                                continue
                            new_val, sub_count = pattern.subn(replace_txt, orig)
                            if sub_count > 0:
                                r[field] = new_val
                                file_replaced += sub_count
                                file_mod = True
                    if file_mod:
                        bak_path = fpath + ".bak"
                        if not os.path.exists(bak_path):
                            shutil.copy2(fpath, bak_path)
                        parent.codec.save_any_ffx_file(fpath, recs, min_id, max_id, magic, charset)
                        modified_files.append(fname)
                        total_replaced += file_replaced
                except Exception as e:
                    parent.log(f"Failed to process '{fname}' for replacement: {e}", "error")

            if total_replaced > 0:
                parent.log(f"Category Search & Replace: Replaced {total_replaced} occurrences across files: {', '.join(modified_files)}", "success")
                parent.on_bin_file_selected()
                messagebox.showinfo("Success", f"Replaced {total_replaced} occurrences across {len(modified_files)} files in category '{cat_name}':\n\n" + "\n".join(modified_files[:15]) + ("\n..." if len(modified_files) > 15 else ""))
                dialog.destroy()
            else:
                messagebox.showinfo("Search & Replace", f"No occurrences found in category '{cat_name}'.")
        else:
            loc = parent.cmb_local.get() if hasattr(parent, 'cmb_local') else 'new_uspc'
            loc_dir = os.path.join(parent.codec.ffx_master_path, loc) if parent.codec.ffx_master_path else ""
            all_files = []

            if loc_dir and os.path.exists(loc_dir):
                kernel_dir = os.path.join(loc_dir, "battle", "kernel")
                if os.path.exists(kernel_dir):
                    for f in os.listdir(kernel_dir):
                        if f.endswith(".bin") and f in FILE_RECORD_SIZES:
                            all_files.append((f"kernel/{f}", os.path.join(kernel_dir, f)))
                help_dir = os.path.join(loc_dir, "help")
                if os.path.exists(help_dir):
                    for root, dirs, files in os.walk(help_dir):
                        for f in files:
                            if f.endswith(".sps2"):
                                rel = os.path.relpath(os.path.join(root, f), help_dir).replace("\\", "/")
                                if not rel.endswith("_page.sps2") and not any(sub in rel.lower() for sub in ["/gcm/", "/gnm/", "/gxm/", "gcm/", "gnm/", "gxm/"]):
                                    all_files.append((f"help/{rel}", os.path.join(root, f)))
                evt_dir = os.path.join(loc_dir, "event", "obj_ps3")
                if not os.path.exists(evt_dir):
                    evt_dir = os.path.join(loc_dir, "event", "obj_psv")
                if not os.path.exists(evt_dir):
                    evt_dir = os.path.join(loc_dir, "event")
                if os.path.exists(evt_dir):
                    for root, dirs, files in os.walk(evt_dir):
                        for f in files:
                            if f.endswith(".bin"):
                                all_files.append((f"event/{f}", os.path.join(root, f)))
                btl_dir = os.path.join(loc_dir, "battle", "btl")
                if os.path.exists(btl_dir):
                    for root, dirs, files in os.walk(btl_dir):
                        for f in files:
                            if f.endswith(".bin"):
                                all_files.append((f"btl/{f}", os.path.join(root, f)))
                menu_dir = os.path.join(loc_dir, "menu")
                if os.path.exists(menu_dir):
                    for f in os.listdir(menu_dir):
                        if (f.endswith(".bin") or f == "macrodic.dcp") and not f.startswith("ffxsjis"):
                            all_files.append((f"menu/{f}", os.path.join(menu_dir, f)))

            ans = messagebox.askyesno("Confirm Global Action",
                f"This will scan, modify, and save across all {len(all_files)} supported files in '{loc}'.\n"
                "Automatic backup files (.bak) will be created for any modified files.\n\n"
                "Are you sure you want to perform this global replacement?")
            if not ans:
                return

            charset = parent.cmb_charset.get() if hasattr(parent, 'cmb_charset') else 'us'
            modified_files = []
            total_replaced = 0

            for disp_name, fpath in all_files:
                try:
                    recs, min_id, max_id, magic, mode = parent.codec.load_any_ffx_file(fpath, 16, charset)
                    file_mod = False
                    file_replaced = 0
                    fields = ['name', 'sname', 'desc', 'sdesc'] if mode == 'kernel' else ['name']
                    if "w_name.bin" in fpath.lower():
                        fields.extend(['w_wakka', 'w_lulu', 'w_rikku'])

                    for r in recs:
                        for field in fields:
                            orig = r.get(field, "")
                            if not orig:
                                continue
                            new_val, sub_count = pattern.subn(replace_txt, orig)
                            if sub_count > 0:
                                r[field] = new_val
                                file_replaced += sub_count
                                file_mod = True
                    if file_mod:
                        bak_path = fpath + ".bak"
                        if not os.path.exists(bak_path):
                            shutil.copy2(fpath, bak_path)
                        parent.codec.save_any_ffx_file(fpath, recs, min_id, max_id, magic, charset)
                        modified_files.append(disp_name)
                        total_replaced += file_replaced
                except Exception as e:
                    parent.log(f"Failed to process '{disp_name}' for replacement: {e}", "error")

            if total_replaced > 0:
                parent.log(f"Global Search & Replace: Replaced {total_replaced} occurrences across files: {', '.join(modified_files)}", "success")
                parent.on_bin_file_selected()
                messagebox.showinfo("Success", f"Replaced {total_replaced} occurrences across {len(modified_files)} files:\n\n" + "\n".join(modified_files[:20]) + ("\n..." if len(modified_files) > 20 else ""))
                dialog.destroy()
            else:
                messagebox.showinfo("Search & Replace", "No occurrences found in any files.")

    btn_run = tk.Button(btn_frame, text="Replace All", command=run_replace, bg=parent.accent_color, fg="white",
                         font=("Segoe UI", 9, "bold"), relief="flat", activebackground=parent.accent_hover, activeforeground="white", padx=15, pady=4)
    btn_run.pack(side="right")
    parent.bind_hover(btn_run, is_primary=True)

    btn_prev = tk.Button(btn_frame, text="🔍 Preview Matches (Dry Run)", command=run_preview, bg=parent.card_color, fg=parent.text_color,
                         font=("Segoe UI", 9, "bold"), relief="flat", activebackground=parent.border_color, activeforeground=parent.text_color, padx=12, pady=4)
    btn_prev.pack(side="right", padx=(0, 8))
    parent.bind_hover(btn_prev)

    btn_cancel = tk.Button(btn_frame, text="Cancel", command=dialog.destroy, bg=parent.card_color, fg=parent.text_color,
                           font=("Segoe UI", 9, "bold"), relief="flat", activebackground=parent.border_color, activeforeground=parent.text_color, padx=15, pady=4)
    btn_cancel.pack(side="left")
    parent.bind_hover(btn_cancel)
