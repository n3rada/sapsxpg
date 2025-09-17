## File: sapsxpg/cli.py

"""Command Line Interface for SAP SXPG Command Execution.

This module provides the command-line interface for executing SAP system commands
through the SXPG_CALL_SYSTEM function module. It handles argument parsing,
initializes the SAP connection, and manages the interactive terminal session.

The CLI supports various connection parameters and operating system filtering
options for command execution.
"""

import argparse
from pathlib import Path

# External library imports

# Local library imports
from sapsxpg.core import terminal
from sapsxpg.core import sap
from sapsxpg.utils import methods


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="sapsxpg",
        description="Interactive console application to simplify the SXPG_CALL_SYSTEM usage on a targeted SAP system.",
        add_help=True,
    )

    parser.add_argument(
        "target",
        type=str,
        help="Target SAP system (as defined in your saplogon.ini or SAP GUI)",
    )

    parser.add_argument(
        "username",
        type=str,
        help="SAP username",
    )

    parser.add_argument(
        "password",
        type=str,
        help="SAP password",
    )

    parser.add_argument(
        "-c", "--client", default="500", help="SAP client number (default: 500)"
    )

    parser.add_argument(
        "-s",
        "--sysnr",
        default="00",
        help="SAP system number (default: 00)",
    )

    parser.add_argument(
        "-g", "--group", default="SPACE", help="SAP logon group (default: SPACE)"
    )

    parser.add_argument(
        "--os",
        default=None,
        choices=["linux", "windows", "unix", "all", "anyos"],
        help="Command filter type (default: auto-detect current OS)",
    )

    parser.add_argument(
        "--rce-poc",
        default="ZSH",
        type=str,
        help="Produce a workable Remote Command Execution (RCE) proof-of-concept Python3 code with the given SAP command.",
    )

    return parser.parse_args()


def main() -> int:
    """Run the interactive console application."""
    if not methods.check_nwrfc_sdk():
        return 1

    print(methods.banner())

    args = parse_args()

    if args.rce_poc is not None:
        poc_code = Path(__file__).parent / "utils" / "template.py"
        if not poc_code.exists():
            print(f"[x] PoC template file not found: {poc_code}")
            return 1

        print(f"[i] Producing PoC code for command: {args.rce_poc}")
        command = args.rce_poc
        with open(poc_code, "r", encoding="utf-8") as file:
            poc_template = file.read()
            poc_template = poc_template.replace("<USERNAME>", args.username)
            poc_template = poc_template.replace("<PASSWORD>", args.password)
            poc_template = poc_template.replace("<HOST>", args.target)
            poc_template = poc_template.replace("<GROUP>", args.group)
            poc_template = poc_template.replace("<SYSNR>", args.sysnr)
            poc_template = poc_template.replace("<CLIENT>", args.client)
            poc_template = poc_template.replace("<SAP_COMMAND>", command)

            poc_file = Path.cwd() / f"poc_{args.target}_{command}.py"
            poc_file.unlink(missing_ok=True)
            poc_file.write_text(poc_template, encoding="utf-8")

            print(f"[i] PoC code written to: {poc_file}")

        return 0

    print(f"[i] Connecting to SAP system: {args.target}")
    print(f"|-> Username: {args.username}")
    print(f"|-> Client: {args.client}")
    print(f"|-> Group: {args.group}")

    try:
        # Create SAP system instance
        with sap.SAPSystem(
            host=args.target,
            user=args.username,
            passwd=args.password,
            client=args.client,
            sysnr=args.sysnr,
            group=args.group,
        ) as sap_system:

            # Set OS filter
            if args.os is not None:
                sap_system.os = args.os
            else:
                sap_system.detect_current_os()

            terminal.run(sap_system)
    except Exception as exc:
        print(f"[x] An error occurred: {exc}")
    finally:
        # Delete all .trc SAP log files
        for trc_file in Path.cwd().glob("*.trc"):
            trc_file.unlink(missing_ok=True)

    return 0
