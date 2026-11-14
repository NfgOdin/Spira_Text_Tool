"""
gui.dialogs.cheat_sheet - FFX & FFX-2 Control Tags Cheat Sheet Dialog.
"""

import tkinter as tk
from tkinter import ttk

def show_cheat_sheet_dialog(parent):
    root = parent.winfo_toplevel() if hasattr(parent, 'winfo_toplevel') else getattr(parent, 'root', parent)
    dialog = tk.Toplevel(root)
    dialog.title("FFX In-Game Control Tags Cheat Sheet")
    dialog.geometry("680x560")
    dialog.minsize(580, 420)
    
    bg_color = getattr(parent, 'bg_color', "#0e1117")
    accent_color = getattr(parent, 'accent_color', "#3b82f6")
    text_color = getattr(parent, 'text_color', "#f3f4f6")
    text_dim = getattr(parent, 'text_dim', "#9ca3af")
    border_color = getattr(parent, 'border_color', "#282d3d")
    card_color = getattr(parent, 'card_color', "#161922")
    
    dialog.configure(bg=bg_color)
    dialog.transient(root)

    # Center relative to parent
    dialog.update_idletasks()
    rx = root.winfo_x()
    ry = root.winfo_y()
    rw = root.winfo_width()
    rh = root.winfo_height()
    dx = rx + max(0, (rw - 680) // 2)
    dy = ry + max(0, (rh - 560) // 2)
    dialog.geometry(f"+{dx}+{dy}")

    header = ttk.Frame(dialog, padding=(18, 14, 18, 6))
    header.pack(fill="x")
    tk.Label(header, text="FFX In-Game Control Tags Cheat Sheet", font=("Segoe UI", 13, "bold"), fg=accent_color, bg=bg_color).pack(anchor="w")
    tk.Label(header, text="These tags represent special engine bytecodes (colors, pauses, speakers, variables, and line feeds).", font=("Segoe UI", 9), fg=text_dim, bg=bg_color).pack(anchor="w", pady=(3, 0))

    content_frame = ttk.Frame(dialog, padding=(18, 6, 18, 10))
    content_frame.pack(fill="both", expand=True)

    txt = tk.Text(content_frame, bg="#131418", fg="#e5e7eb", font=("Segoe UI", 9), wrap="word", relief="flat", highlightthickness=1, highlightbackground=border_color, padx=12, pady=12)
    scroll = ttk.Scrollbar(content_frame, orient="vertical", command=txt.yview)
    txt.configure(yscrollcommand=scroll.set)
    txt.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")

    txt.tag_config("sec_title", font=("Segoe UI", 10, "bold"), foreground=accent_color)
    txt.tag_config("tag_name", font=("Consolas", 10, "bold"), foreground="#6ee7b7")
    txt.tag_config("tag_sub", font=("Segoe UI", 9, "bold"), foreground="#f3f4f6")
    txt.tag_config("tag_desc", font=("Segoe UI", 9), foreground="#d1d5db")
    txt.tag_config("tag_ex", font=("Consolas", 9), foreground="#93c5fd")

    sections = [
        ("Formatting & Flow Control", [
            (r"\n or {\n}", "Line Break", "Advances text to the next row in the text box. In CSV files, line feeds are exported as {\\n} to prevent breaking spreadsheet rows.", r"Welcome!\nHow can I help you?"),
            ("{PAUSE}", "Player Input Pause", "Freezes text display until the player presses the confirm button or voiceover finishes.", r"Wait...{PAUSE}\nDid you hear that?"),
            ("{SPACE:XX}", "Horizontal Spacing (Pixels)", "Adds horizontal space in pixels (hex 00-FF). Useful for alignment, indenting, and tabulating.", r"{SPACE:0A}Option A"),
            ("{TIME:XX}", "Timed Delay (Frames)", "Waits XX frames before continuing text. Used in cutscenes to sync text with voice acting and gestures.", r"{TIME:1E}Now!")
        ]),
        ("Text Colors ({CLR:...})", [
            ("{CLR:WHITE}", "Default White", "Standard dialogue text color (byte 0x41).", "{CLR:WHITE}Standard message text"),
            ("{CLR:YELLOW}", "Highlight Yellow", "Used for key terms, location names, and items (byte 0x43).", "{CLR:YELLOW}Overdrive{CLR:WHITE}"),
            ("{CLR:GREY}", "Disabled / Subdued", "Used for inactive commands, footnotes, and disabled choices (byte 0x52).", "{CLR:GREY}(Inactive)"),
            ("{CLR:BLUE}", "Beneficial Blue", "Used for positive status effects, support magic, and helpful tips (byte 0x88).", "{CLR:BLUE}Haste{CLR:WHITE}"),
            ("{CLR:RED}", "Danger Red", "Used for debuffs, warnings, and boss attacks (byte 0x94).", "{CLR:RED}Doom{CLR:WHITE}"),
            ("{CLR:PINK}", "Pink / Special", "Used for special emphasis and rare prompts (byte 0x97).", "{CLR:PINK}Special Event{CLR:WHITE}"),
            ("{CLR:OL_PURPLE}", "Outlined Purple", "Outlined purple styling (byte 0xA1).", "{CLR:OL_PURPLE}Title"),
            ("{CLR:OL_CYAN}", "Outlined Cyan", "Outlined cyan styling (byte 0xB1).", "{CLR:OL_CYAN}Notice")
        ]),
        ("Speakers, Characters & Names", [
            ("{PC:XX}", "Playable Character", "00=Tidus, 01=Yuna, 02=Auron, 03=Kimahri, 04=Wakka, 05=Lulu, 06=Rikku, 07=Seymour. In cutscenes, placing this on line 1 sets the speaker nameplate.", "{PC:00}\nI am with you!"),
            ("{MCR:sXXlYY}", "Macro String Reference", "Fetches dynamic character, NPC, or location names from engine text bank XX, line YY. E.g. {MCR:s06l63}=Seymour, {MCR:s06l40}=Tromell, {MCR:s0Dl33}=Spira.", "{MCR:s06l63}\nThat is enough, {MCR:s06l40}."),
            ("{VAR:XX}", "Numeric Game Variable", "Live in-game numeric values (Gil, sphere level, timer, score, countdown).", "Obtained: {VAR:01} Gil"),
            ("{KEY:XX}", "Key Item Name", "Dynamically displays the name of Key Item index XX from inventory tables.", "Received {KEY:04}!")
        ]),
        ("Interactive Choices & Menus", [
            ("{CHOICE:XX}", "Choice Option", "Defines selectable choices in dialogue prompts. XX is option index (00, 01, etc.).", "{CHOICE:00} Yes\n{CHOICE:01} No{CHOICE-END}"),
            ("{CHOICE-END}", "End Choice Box", "Terminates the list of selectable options in a choice prompt.", "{CHOICE:00} Fight\n{CHOICE:01} Flee{CHOICE-END}")
        ]),
        ("Presentation & Internal Packets", [
            ("{CTRL:XX}", "Screen Presentation", "UI control byte used in .sps2 tutorial and Monster Arena screens (e.g. {CTRL:F0}).", " {CTRL:F0}"),
            ("{CMD:XX:YY}", "Raw Engine Bytecode", "Preserves unmapped 2-byte bytecode commands without data corruption.", "{CMD:28:01}")
        ])
    ]

    for sec_title, items in sections:
        txt.insert("end", f"■ {sec_title}\n\n", "sec_title")
        for tag, name, desc, example in items:
            txt.insert("end", f"  • {tag}", "tag_name")
            txt.insert("end", f"  —  {name}\n", "tag_sub")
            txt.insert("end", f"     {desc}\n", "tag_desc")
            txt.insert("end", f"     Example: {example}\n\n", "tag_ex")

    txt.config(state="disabled")

    btn_close = tk.Button(dialog, text="Close", command=dialog.destroy, bg=card_color, fg=text_color, font=("Segoe UI", 9), relief="flat", padx=16, pady=4)
    btn_close.pack(anchor="e", padx=18, pady=(0, 14))
