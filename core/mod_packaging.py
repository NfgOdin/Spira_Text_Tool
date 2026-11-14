"""
core.mod_packaging - Mod Packaging Engine for Spira Mod Manager & Nexus Mods.
Builds release-ready ZIP packages with modinfo.spiramod, modinfo.json,
and standard ffx_ps2/ffx/master/ or ffx_ps2/ffx2/master/ path trees.
"""

import os
import json
import base64
import zipfile
from typing import List, Tuple, Dict, Any, Optional

SPIRAMOD_KEY = b"AuronTidusYunaRikkuLuluWakkaKimahri"

def encode_spiramod_meta(meta_dict: Dict[str, Any]) -> str:
    """XOR-obfuscates and base64 encodes mod metadata for Spira Mod Manager format."""
    try:
        json_str = json.dumps(meta_dict, indent=2)
        data_bytes = json_str.encode('utf-8')
        obfuscated = bytes([b ^ SPIRAMOD_KEY[i % len(SPIRAMOD_KEY)] for i, b in enumerate(data_bytes)])
        return base64.b64encode(obfuscated).decode('utf-8')
    except Exception:
        return ""

def decode_spiramod_meta(encoded_str: str) -> Optional[Dict[str, Any]]:
    """Decodes Spira Mod Manager .spiramod metadata payload."""
    try:
        data_bytes = base64.b64decode(encoded_str.strip())
        deobfuscated = bytes([b ^ SPIRAMOD_KEY[i % len(SPIRAMOD_KEY)] for i, b in enumerate(data_bytes)])
        return json.loads(deobfuscated.decode('utf-8'))
    except Exception:
        return None

def create_mod_archive(
    out_path: str,
    files_to_pack: List[Tuple[str, str]],
    name: str = "FFX Mod",
    author: str = "Modder",
    version: str = "1.0.0",
    category: str = "Translations & Text",
    description: str = "",
    nexus_id: str = "",
    is_ffx2: bool = False,
    generator_version: str = "2.0.0"
) -> Tuple[bool, int, float, str]:
    """
    Creates a Spira Mod Manager & Nexus Mods compatible .zip package.
    Returns: (success, file_count, size_kb, message_or_error)
    """
    if not files_to_pack:
        return False, 0, 0.0, "No files provided to package."

    game_meta = "FFX-2" if is_ffx2 else "FFX"
    nexus_game = "finalfantasyx2" if is_ffx2 else "finalfantasyx"
    nexus_link = f"https://www.nexusmods.com/{nexus_game}/mods/{nexus_id}" if nexus_id else ""

    rel_manifest_files = [rel for (_, rel) in files_to_pack]
    export_meta = {
        "name": name,
        "game": game_meta,
        "author": author,
        "creator": author,
        "version": version,
        "category": category,
        "description": description,
        "nexus_id": nexus_id,
        "link": nexus_link,
        "files": rel_manifest_files,
        "generator": f"Spira Text Tool v{generator_version} (Spira Mod Manager Ready)"
    }

    try:
        spiramod_data = encode_spiramod_meta(export_meta)
        json_data = json.dumps(export_meta, indent=2)

        os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
        with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("modinfo.spiramod", spiramod_data)
            z.writestr("modinfo.json", json_data)
            for abs_p, rel_p in files_to_pack:
                z.write(abs_p, rel_p)

        pkg_size_kb = os.path.getsize(out_path) / 1024.0
        return True, len(files_to_pack), pkg_size_kb, "Successfully created package."
    except Exception as e:
        return False, 0, 0.0, str(e)
