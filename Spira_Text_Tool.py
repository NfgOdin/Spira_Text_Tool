"""
Spira Text Tool
The Ultimate Final Fantasy X & X-2 HD Remaster Text & Localization Studio.
Primary application entrypoint.
"""

import sys
import os

# Ensure project root is in sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from gui.main_window import (
    FFXTextToolGUI,
    SpiraTextToolGUI,
    APP_VERSION,
    AUTHOR,
    WEBSITE_URL,
    DAMAGE_FORMULAS,
    CONFIG_FILE,
    get_resource_path,
)
from gui.app import main

if __name__ == "__main__":
    main()
