# Spira Text Tool (v2.0.0)
### Final Fantasy X & X-2 HD Remaster — Text & Localization Studio

A comprehensive professional localization and text modding suite designed to view, decode, edit, audit, translate, and repack all text and dialogue binary tables from both **Final Fantasy X** and **Final Fantasy X-2 HD Remaster**.

[![Repository](https://img.shields.io/badge/GitHub-Spira__Text__Tool-blue?logo=github)](https://github.com/NfgOdin/Spira_Text_Tool)
[![Version](https://img.shields.io/badge/Version-2.0.0-emerald)](#release-changelog)

---

## Key Pillars & Features

- **Dual-Engine Game Support (FFX & FFX-2)**:
  - Seamlessly toggle between **Final Fantasy X** and **Final Fantasy X-2 HD Remaster** with 1 click.
  - Dynamic game-aware UI theme switching: **Sin Blue** (`#3b82f6`) for FFX vs **Celsius Purple** (`#a855f7`) for FFX-2.
  - Dedicated support for FFX-2 extended kernel tables (`acc.bin`, `accessory.bin`, `dress.bin`, `monmagic.bin`, etc.) and dressphere party equipment slots (Yuna Gunner, Rikku Thief, Paine Warrior, plus creature slots).
- **Interactive Choice Simulator & Live Preview**:
  - Real-time in-game dialogue simulator rendering line-by-line formatting, custom colors, and speaker nameplates.
  - **Interactive Choice Navigation**: Navigate multi-option dialogue prompts (`{CHOICE:XX}`) with keyboard $\uparrow/\downarrow$ arrow keys, simulated auto-indentation, and an animated blinking cursor.
- **Dynamic Translation Memory & Multilingual Canonical Lore Glossary**:
  - Over 137 verified canonical glossary terms indexed across 6 languages (English, Japanese, German, French, Italian, Spanish).
  - Proactive translation suggestion banner above the editor with `Ctrl+T` / 1-click auto-insertion.
  - Searchable Lore Glossary browser and Translation Dashboard.
- **QA Syntax & Crash Prevention Auditor**:
  - Deep-scanning syntax validator detecting unclosed brackets, invalid color codes, missing resets, line overflows ($>43$ chars per line), and 16-bit offset pool overflow risks.
  - **1-Click Safe Auto-Fix**: Automatically repair formatting errors across the current file, category, or entire localization with `.bak` safety backups.
  - **Cutscene VO Timing Estimator**: Calculates display duration, Characters Per Second (CPS), and Words Per Minute (WPM) based on `{TIME:XX}` engine delays to assist cutscene voice dubbing.
- **Reusable Batch Replacement Ruleset Manager**:
  - Create, save, load, and execute JSON regex/text replacement pipelines across single files, categories, or the entire localization tree.
- **1-Click Mod Packager (Spira Mod Manager & Nexus Mods)**:
  - Generate release-ready mod archives (`.zip`) with automatically structured `manifest.json` metadata compatible with Spira Mod Manager and Nexus Mods.
  - Dynamic game path routing (`ffx_ps2/ffx/master` vs `ffx_ps2/ffx2/master`).
- **Visual Side-by-Side Diff Viewer**:
  - Compare edited files directly against original or reference localizations with color-coded additions, deletions, and modifications.
- **Data Safety, Recent Files & Editing Polish**:
  - **Unsupported Character Pre-Warning**: Real-time warning badge alerting translators immediately if a character is not supported in the active charset.
  - **1-Click Revert to Backup**: Instant `File -> Revert File to Original Backup (.bak)` safety restore.
  - **Exit & Navigation Protection**: Prompts with `Yes / No / Cancel` on unsaved changes before switching rows, loading files, or exiting (`WM_DELETE_WINDOW`).
  - **Recent Files Menu**: Native `File -> Recent Files` dynamic cascade with universal category path resolution.
  - **Rich Context Menu**: Right-click editing menu (Cut, Copy, Paste, Delete, Select All, Lore TM, and control tag wrapping).
  - **Standalone Bundled Encodings**: Packaged with all official character encoding tables (`us`, `jp`, `ch`, `cn`, `kr`) for zero external dependencies.

---

## Release Changelog

### v2.0.0 (The Studio Edition — Rebranded to Spira Text Tool)
- **Official Rebranding to Spira Text Tool**:
  - Integrated into the Spira modding ecosystem (alongside Spira Mod Manager).
  - Primary launcher is now `Spira_Text_Tool.py` (`FFX_Text_Tool.py` retained as 100% backwards-compatible wrapper).
- **Decoupled Layered Architecture**:
  - Modularized into `core/` (headless business engines) and `gui/` (components, dialogs, main window).
- **Asynchronous Task Workers & Progress Modals**:
  - Thread-safe background execution for heavy batch QA scans and localization-wide rules with cancellation.
- **In-Memory Normalized Search & 200ms Debouncing**:
  - Sub-millisecond record querying powered by `core.search_indexer.SearchIndexer`.
- **Full Dual-Engine Support (FFX & FFX-2)**:
  - Complete support for Final Fantasy X and Final Fantasy X-2 HD Remaster text assets.
  - Adaptive visual themes: *Sin Blue* for FFX and *Celsius Purple* for FFX-2.
  - Added FFX-2 tables (`acc.bin`, `accessory.bin`, `dress.bin`, `monmagic.bin`, etc.) and party equipment mappings.
- **Interactive Choice Simulator**:
  - Live interactive choice box simulator with animated blinking cursor, keyboard navigation ($\uparrow/\downarrow$), and accurate in-game line indentation.
- **Translation Memory & Canonical Lore Glossary**:
  - Proactive Lore TM suggestion engine with `Ctrl+T` insertion.
  - 137 verified canonical terms across English, Japanese, German, French, Italian, and Spanish.
- **QA Syntax & Crash Prevention Auditor**:
  - Complete error detection for unclosed control tags, invalid color codes, and line overflows ($>43$ chars).
  - 1-click batch safe auto-fix for active memory and disk files with automatic `.bak` backups.
  - Cutscene Voice-Over (VO) timing and speech-rate estimator (CPS / WPM).
- **Reusable Batch Replacement Ruleset Manager**:
  - Save, load, and run persistent JSON replacement pipelines across files and localizations.
- **1-Click Mod Packager**:
  - Export structured `.zip` mod packages with Spira Mod Manager `manifest.json` and Nexus Mods compatibility.
- **Visual Side-by-Side Diff Dialog**:
  - Interactive comparison tool with color-coded diffs, filter by changes, and `Alt+Left` / `Alt+Right` entry navigation.

### v1.2.0 (The Ultimate Text & Dialogue Update)
- Modernized UI palette and zebra-striped table view.
- Multi-line dialogue editor with syntax highlighting and quick-insert tag toolbar.
- Interactive syntax tag hover tooltips for all in-game codes.
- Live in-game dialogue box preview with speaker nameplate parsing.
- Support for Monster Arena `.sps2` files, cutscenes (`event/obj_ps3`), battle quotes (`battle/btl`), and menus.

### v1.1.0
- Added monster sensor and scan table support (`monster1.bin`, `monster2.bin`, `monster3.bin`).

### v1.0.0
- Initial public release supporting kernel tables, FFX character encoding, and CSV batch tools.

---

## In-Game Control Tags Cheat Sheet

FFX text files use special inline control codes enclosed in curly brackets `{...}` to represent formatting, speaker nameplates, variables, pauses, and colors. These tags can be edited freely or preserved in dialogue:

### 1. Formatting & Flow Control
| Tag | Name | Description | Example |
| :--- | :--- | :--- | :--- |
| `\n` or `{\n}` | **Line Break** | Advances dialogue to the next line in the text box. In CSV exports, formatted as `{\n}` to maintain single-row integrity. | `Welcome!\nHow can I help you?` |
| `{PAUSE}` | **Player Input Pause** | Halts text display until the player presses confirm or voice acting finishes. | `Wait...{PAUSE}\nDid you hear that?` |
| `{SPACE:XX}` | **Pixel Spacing** | Adds horizontal spacing in pixels (`XX` = hex 00–FF). Used for indenting or table columns. | `{SPACE:0A}Option A` |
| `{TIME:XX}` | **Timed Delay** | Delays subsequent text by `XX` frames to sync lines with gestures and animations. | `{TIME:1E}Now!` |

### 2. Text Colors (`{CLR:...}`)
| Tag | Hex Code | Purpose & Appearance | Example |
| :--- | :--- | :--- | :--- |
| `{CLR:WHITE}` | `0x41` | Default standard text color. | `{CLR:WHITE}Normal text` |
| `{CLR:YELLOW}` | `0x43` | Highlighted keywords, locations, item names, and battle terms. | `{CLR:YELLOW}Overdrive{CLR:WHITE}` |
| `{CLR:GREY}` | `0x52` | Subdued, inactive, or disabled text/choices. | `{CLR:GREY}(Unavailable)` |
| `{CLR:BLUE}` | `0x88` | Beneficial status effects, positive buffs, and defensive stats. | `{CLR:BLUE}Haste{CLR:WHITE}` |
| `{CLR:RED}` | `0x94` | Debuffs, warnings, boss attacks, and danger status. | `{CLR:RED}Doom{CLR:WHITE}` |
| `{CLR:PINK}` | `0x97` | Special emphasis or unique cues. | `{CLR:PINK}Special{CLR:WHITE}` |
| `{CLR:OL_PURPLE}` | `0xA1` | Outlined purple title text. | `{CLR:OL_PURPLE}Notice` |
| `{CLR:OL_CYAN}` | `0xB1` | Outlined cyan header text. | `{CLR:OL_CYAN}Info` |

### 3. Speakers, Characters & Variables
| Tag | Description | Notes / Values | Example |
| :--- | :--- | :--- | :--- |
| `{PC:XX}` | **Playable Character Name** | `00`=Tidus, `01`=Yuna, `02`=Auron, `03`=Kimahri, `04`=Wakka, `05`=Lulu, `06`=Rikku, `07`=Seymour. Placing this on line 1 of a cutscene dialogue box sets the speaker nameplate. | `{PC:00}\nI am with you!` |
| `{MCR:sXXlYY}` | **Macro String Lookup** | Fetches dynamic strings from engine Section `XX`, Line `YY`. Used for NPC speaker nameplates and consistent location/character names across localizations. | `{MCR:s06l63}\nThat is enough, {MCR:s06l40}.` |
| `{VAR:XX}` | **Dynamic Number** | Live in-game numbers (Gil balance, timer, countdown seconds, score). | `Obtained: {VAR:01} Gil` |
| `{KEY:XX}` | **Key Item Name** | Dynamically looks up and displays the Key Item name for inventory index `XX`. | `Received {KEY:04}!` |

### 4. Interactive Choices & Menus
| Tag | Name | Description | Example |
| :--- | :--- | :--- | :--- |
| `{CHOICE:XX}` | **Choice Option** | Marks a selectable dialogue choice (`00`=First, `01`=Second, etc.). | `{CHOICE:00} Yes\n{CHOICE:01} No{CHOICE-END}` |
| `{CHOICE-END}` | **End Choice Box** | Closes the selectable choice prompt. | `{CHOICE:00} Fight\n{CHOICE:01} Flee{CHOICE-END}` |

---

## Getting Started

### Prerequisites

- **Python 3.8 or higher**
- **Tkinter** (usually included with standard Python installations)

### Running the Application

Execute the primary script:

```bash
python Spira_Text_Tool.py
```

*(Note: `python FFX_Text_Tool.py` also works as a backwards-compatible launcher.)*

### Packaging into an Executable

Run the automated build script:

```bash
python build_exe.py
```

The script runs all 20 automated verification test suites, cleans artifacts, invokes PyInstaller with `Spira_Text_Tool.spec`, and validates the output executable: `dist/Spira_Text_Tool.exe`.

---

## Contributing & Repository

For updates, issues, and contributions, visit the repository:
[https://github.com/NfgOdin/Spira_Text_Tool](https://github.com/NfgOdin/Spira_Text_Tool)

Developed by **NfgOdin** (Copyright © 2026).
All rights reserved.
