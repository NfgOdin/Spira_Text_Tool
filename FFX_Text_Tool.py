"""
FFX Text Tool (Legacy Wrapper)
Delegates directly to Spira_Text_Tool for 100% backwards compatibility.
"""

import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from Spira_Text_Tool import (
    FFXTextToolGUI,
    SpiraTextToolGUI,
    APP_VERSION,
    AUTHOR,
    WEBSITE_URL,
    DAMAGE_FORMULAS,
    CONFIG_FILE,
    get_resource_path,
    main,
)

if __name__ == "__main__":
    main()
