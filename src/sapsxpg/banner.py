# sapsxpg/banner.py

# Local library imports
from . import __version__ as version

def display_banner() -> str:
    return rf"""
        _____  ___    ____
        /  ___|/ _ \  |  _ \
        \ `--./ /_\ \ | |_) |
         `--. \  _  | |  __/
        /\__/ / | | | | |   SXPG_CALL_SYSTEM
        \____/\_| |_/ |_|             v{version}
        """
