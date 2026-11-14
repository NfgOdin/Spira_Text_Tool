"""
1-Click Mod Packager Dialog
Generates Nexus and Spira Mod Manager compatible mod release archives.
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from core.mod_packaging import create_mod_archive


def open_mod_packager_dialog(parent):
    """
    1-Click Mod Packaging Engine for Spira Mod Manager & Nexus Mods.
    Packages modified/active localization files into a release-ready .zip
    with modinfo.spiramod, modinfo.json, and the standard ffx_ps2/ffx/master/<loc>/... tree.
    """
    dialog = tk.Toplevel(parent.root)
    dialog.title("📦 Package Mod for Spira Mod Manager & Nexus Mods")
    dialog.geometry("560x580")
    dialog.minsize(500, 480)
    dialog.configure(bg=parent.bg_color)
    dialog.transient(parent.root)
    dialog.grab_set()

    # Center relative to main window
    dialog.update_idletasks()
    rx = parent.root.winfo_x()
    ry = parent.root.winfo_y()
    rw = parent.root.winfo_width()
    rh = parent.root.winfo_height()
    dx = rx + max(0, (rw - 560) // 2)
    dy = ry + max(0, (rh - 580) // 2)
    dialog.geometry(f"+{dx}+{dy}")

    header = ttk.Frame(dialog, padding=(18, 14, 18, 6))
    header.pack(fill="x")
    tk.Label(header, text="📦 1-Click Mod Packaging Engine", font=("Segoe UI", 13, "bold"), fg=parent.accent_color, bg=parent.bg_color).pack(anchor="w")
    tk.Label(header, text="Generates a 100% Spira Mod Manager & Nexus Mods compatible release archive (.zip) with modinfo metadata and correct relative paths.",
             font=("Segoe UI", 9), fg=parent.text_dim, bg=parent.bg_color, wraplength=520, justify="left").pack(anchor="w", pady=(3, 0))

    content = ttk.Frame(dialog, padding=(18, 6, 18, 10))
    content.pack(fill="both", expand=True)

    # Mod Metadata Group
    grp_meta = ttk.LabelFrame(content, text=" Mod Information ", padding=12)
    grp_meta.pack(fill="x", pady=(0, 10))
    grp_meta.columnconfigure(1, weight=1)

    ttk.Label(grp_meta, text="Mod Name:").grid(row=0, column=0, sticky="w", pady=4)
    ent_mod_name = ttk.Entry(grp_meta)
    loc = parent.cmb_local.get() if hasattr(parent, 'cmb_local') else "new_uspc"
    is_ffx2 = ("X-2" in getattr(parent, "active_game", "Final Fantasy X"))
    game_tag = "FFX-2" if is_ffx2 else "FFX"
    ent_mod_name.insert(0, f"{game_tag} {loc.upper()} Text Translation Patch")
    ent_mod_name.grid(row=0, column=1, sticky="ew", pady=4, padx=(8, 0))

    ttk.Label(grp_meta, text="Author / Creator:").grid(row=1, column=0, sticky="w", pady=4)
    ent_author = ttk.Entry(grp_meta)
    ent_author.insert(0, "NfgOdin / Translator")
    ent_author.grid(row=1, column=1, sticky="ew", pady=4, padx=(8, 0))

    ttk.Label(grp_meta, text="Version:").grid(row=2, column=0, sticky="w", pady=4)
    ent_ver = ttk.Entry(grp_meta)
    ent_ver.insert(0, "1.0.0")
    ent_ver.grid(row=2, column=1, sticky="ew", pady=4, padx=(8, 0))

    ttk.Label(grp_meta, text="Category:").grid(row=3, column=0, sticky="w", pady=4)
    cmb_cat = ttk.Combobox(grp_meta, state="readonly", values=[
        "Miscellaneous",
        "User Interface",
        "Gameplay and Balancing",
        "Armour and Clothing",
        "Audio",
        "Models and Textures",
        "Saved Games",
        "Utilities",
        "Visuals and Graphics",
        "General"
    ])
    cmb_cat.set("Miscellaneous")
    cmb_cat.grid(row=3, column=1, sticky="ew", pady=4, padx=(8, 0))

    ttk.Label(grp_meta, text="Nexus Mod ID (Optional):").grid(row=4, column=0, sticky="w", pady=4)
    ent_nexus = ttk.Entry(grp_meta)
    ent_nexus.grid(row=4, column=1, sticky="ew", pady=4, padx=(8, 0))

    ttk.Label(grp_meta, text="Description:").grid(row=5, column=0, sticky="nw", pady=4)
    txt_desc = tk.Text(grp_meta, height=3, bg=parent.card_color, fg=parent.text_color, font=("Segoe UI", 9), relief="flat", highlightbackground=parent.border_color, highlightthickness=1)
    txt_desc.insert("1.0", f"Localization and dialogue text modifications for {'Final Fantasy X-2' if is_ffx2 else 'Final Fantasy X'} ({loc}). Compatible with Spira Mod Manager and manual install.")
    txt_desc.grid(row=5, column=1, sticky="ew", pady=4, padx=(8, 0))

    # File Selection Scope Group
    grp_scope = ttk.LabelFrame(content, text=" Packaging Scope ", padding=12)
    grp_scope.pack(fill="x", pady=(0, 10))

    var_scope = tk.StringVar(value="modified")
    ttk.Radiobutton(grp_scope, text="Modified files only (files with .bak backups or active session changes)", variable=var_scope, value="modified").pack(anchor="w", pady=3)
    ttk.Radiobutton(grp_scope, text=f"All files in the currently active category ({parent.cmb_category.get() if hasattr(parent, 'cmb_category') else 'Category'})", variable=var_scope, value="category").pack(anchor="w", pady=3)
    ttk.Radiobutton(grp_scope, text=f"All supported files in active localization folder ({loc})", variable=var_scope, value="loc").pack(anchor="w", pady=3)

    # Output Zip Path Group
    grp_out = ttk.LabelFrame(content, text=" Output Release Archive (.zip) ", padding=12)
    grp_out.pack(fill="x", pady=(0, 10))
    grp_out.columnconfigure(0, weight=1)

    ent_out_zip = ttk.Entry(grp_out)
    default_zip_name = f"{ent_mod_name.get().replace(' ', '_')}_v{ent_ver.get()}.zip"
    ent_out_zip.insert(0, os.path.abspath(default_zip_name))
    ent_out_zip.grid(row=0, column=0, sticky="ew", padx=(0, 8))

    def browse_zip_out():
        p = filedialog.asksaveasfilename(
            title="Select Output Release Zip",
            initialfile=os.path.basename(ent_out_zip.get()),
            defaultextension=".zip",
            filetypes=[("Zip Archive", "*.zip")]
        )
        if p:
            ent_out_zip.delete(0, tk.END)
            ent_out_zip.insert(0, os.path.abspath(p))

    btn_browse_zip = tk.Button(grp_out, text="Browse...", command=browse_zip_out, bg=parent.card_color, fg=parent.text_color, font=("Segoe UI", 9), relief="flat")
    btn_browse_zip.grid(row=0, column=1, sticky="e")
    parent.bind_hover(btn_browse_zip)

    def build_package():
        name = ent_mod_name.get().strip() or "FFX Mod"
        author = ent_author.get().strip() or "Modder"
        version = ent_ver.get().strip() or "1.0.0"
        category = cmb_cat.get()
        nexus_id = ent_nexus.get().strip()
        desc = txt_desc.get("1.0", "end").strip()
        out_path = ent_out_zip.get().strip()
        scope = var_scope.get()

        if not out_path:
            messagebox.showwarning("Warning", "Please specify an output zip filename.")
            return

        # Gather target files to package
        files_to_pack = []  # list of (abs_path, rel_path_in_zip)
        master_p = parent.codec.ffx_master_path
        loc_name = parent.cmb_local.get() if hasattr(parent, 'cmb_local') else "new_uspc"
        loc_dir = os.path.join(master_p, loc_name) if master_p else ""
        is_ffx2 = ("X-2" in getattr(parent, "active_game", "Final Fantasy X"))
        game_dir = "ffx2" if is_ffx2 else "ffx"
        game_meta = "FFX-2" if is_ffx2 else "FFX"

        if scope == "modified":
            if loc_dir and os.path.exists(loc_dir):
                for root, dirs, files in os.walk(loc_dir):
                    for f in files:
                        if f.endswith(".bak"):
                            orig_f = f[:-4]
                            orig_abs = os.path.join(root, orig_f)
                            if os.path.exists(orig_abs):
                                rel_from_loc = os.path.relpath(orig_abs, loc_dir).replace("\\", "/")
                                rel_in_zip = f"ffx_ps2/{game_dir}/master/{loc_name}/{rel_from_loc}"
                                files_to_pack.append((orig_abs, rel_in_zip))
            if parent.active_file_path and os.path.exists(parent.active_file_path):
                if not any(f[0] == parent.active_file_path for f in files_to_pack):
                    rel_from_loc = os.path.relpath(parent.active_file_path, loc_dir).replace("\\", "/") if loc_dir else parent.active_file_name
                    rel_in_zip = f"ffx_ps2/{game_dir}/master/{loc_name}/{rel_from_loc}"
                    files_to_pack.append((parent.active_file_path, rel_in_zip))
        elif scope == "category":
            for rel_key, fpath in getattr(parent, 'file_map', {}).items():
                if os.path.exists(fpath):
                    rel_from_loc = os.path.relpath(fpath, loc_dir).replace("\\", "/") if loc_dir else rel_key
                    rel_in_zip = f"ffx_ps2/{game_dir}/master/{loc_name}/{rel_from_loc}"
                    files_to_pack.append((fpath, rel_in_zip))
        else:  # full loc
            if loc_dir and os.path.exists(loc_dir):
                for root, dirs, files in os.walk(loc_dir):
                    for f in files:
                        if f.endswith(".bak") or f.endswith(".tmp"):
                            continue
                        abs_p = os.path.join(root, f)
                        rel_from_loc = os.path.relpath(abs_p, loc_dir).replace("\\", "/")
                        rel_in_zip = f"ffx_ps2/{game_dir}/master/{loc_name}/{rel_from_loc}"
                        files_to_pack.append((abs_p, rel_in_zip))

        if not files_to_pack:
            messagebox.showwarning("No Files Found", 
                "No matching modified or localization files were found to package.\n\n"
                "Make sure you have saved edits (which generates .bak backups), or select 'All files in category'.")
            return

        try:
            rel_manifest_files = [rel for (_, rel) in files_to_pack]
            app_ver = getattr(parent, 'app_version', "2.0.0")
            export_meta = {
                "name": name,
                "game": game_meta,
                "author": author,
                "creator": author,
                "version": version,
                "category": category,
                "description": desc,
                "nexus_id": nexus_id,
                "link": f"https://www.nexusmods.com/{'finalfantasyx2' if is_ffx2 else 'finalfantasyx'}/mods/{nexus_id}" if nexus_id else "",
                "files": rel_manifest_files,
                "generator": f"Spira Text Tool {app_ver} (Spira Mod Manager Ready)"
            }

            create_mod_archive(out_path, files_to_pack, export_meta)
            pkg_size = os.path.getsize(out_path) / 1024.0
            parent.log(f"Mod Packager: Created release archive '{os.path.basename(out_path)}' ({len(files_to_pack)} files, {pkg_size:.1f} KB).", "success")
            dialog.destroy()
            messagebox.showinfo("Packaging Complete!",
                f"🎉 Successfully packaged mod release archive!\n\n"
                f"• Archive: {os.path.basename(out_path)}\n"
                f"• Packaged Files: {len(files_to_pack)}\n"
                f"• Size: {pkg_size:.1f} KB\n"
                f"• Location: {out_path}\n\n"
                "100% Compatible with:\n"
                "✓ Spira Mod Manager (Install via 'Install Mod Archive' or Drag & Drop)\n"
                "✓ Nexus Mods / Vortex / Manual extract")
        except Exception as e:
            parent.log(f"Mod packaging failed: {e}", "error")
            messagebox.showerror("Packaging Error", f"Failed to build mod archive:\n{e}")

    # Bottom Button Bar
    btn_bar = ttk.Frame(dialog, padding=(18, 10))
    btn_bar.pack(fill="x")

    btn_build = tk.Button(btn_bar, text="📦 Build Release Archive (.zip)", command=build_package,
                          bg=parent.accent_color, fg="white", font=("Segoe UI", 10, "bold"), relief="flat", activebackground=parent.accent_hover, activeforeground="white", padx=18, pady=6)
    btn_build.pack(side="right")
    parent.bind_hover(btn_build, is_primary=True)

    btn_cancel = tk.Button(btn_bar, text="Cancel", command=dialog.destroy,
                           bg=parent.card_color, fg=parent.text_color, font=("Segoe UI", 9), relief="flat", padx=12, pady=4)
    btn_cancel.pack(side="right", padx=(0, 10))
    parent.bind_hover(btn_cancel)
