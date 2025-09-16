import argparse


# External library imports

# Local library imports
from pysxpg.core import utils


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="pysxpg",
        description="Interactive console application to simplify the SXPG_CALL_SYSTEM usage on a targeted SAP system."
        add_help=True,
    )

    parser.add_argument(
        "target",
        type=str,
        help="Target SAP system (as defined in your saplogon.ini or SAP GUI)",
    )


def main() -> int:
    """Run the interactive console application."""
    if not utils.check_nwrfc_sdk():
        return 1
    
    print(utils.banner())
    
    args = parse_args()
    print(f"[i] Connecting to SAP system: {args.target}")
    print(f"|-> Username: {args.username}")


    return 0