# sapsxpg/cli.py

import argparse
from pathlib import Path

# External library imports

# Local library imports
from sapsxpg.core import terminal
from sapsxpg.core import sap
from sapsxpg.utils import methods


def build_parser() -> argparse.ArgumentParser:
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

    parser.add_argument("-g", "--group", default=None, help="SAP logon group")

    parser.add_argument(
        "-t",
        "--timeout",
        type=int,
        default=30,
        help="Connection timeout in seconds (default: 30)",
    )

    parser.add_argument(
        "--no-trace",
        action="store_true",
        help="Disable SAP RFC trace logging",
    )

    parser.add_argument(
        "--os",
        default=None,
        choices=["linux", "windows", "unix", "all", "anyos"],
        help="Command filter type (default: auto-detect current OS)",
    )

    parser.add_argument(
        "--rce-poc",
        default=None,
        type=str,
        help="Produce a workable Remote Command Execution (RCE) proof-of-concept Python3 code with the given SAP command (if no value is provided, 'ZSH' will be used).",
        nargs="?",
        const="ZSH",
    )

    return parser


def main() -> int:
    """Run the interactive console application."""
    print(methods.banner())

    parser = build_parser()
    args = parser.parse_args()

    # Show help if no cli args provided
    if len(sys.argv) <= 1:
        parser.print_help()
        return 1

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
            poc_template = poc_template.replace("<SYSNR>", args.sysnr)
            poc_template = poc_template.replace("<CLIENT>", args.client)
            poc_template = poc_template.replace("<SAP_COMMAND>", command)
            poc_template = poc_template.replace("<TIMEOUT>", str(args.timeout))

            # Conditionally add group parameter
            if args.group is not None:
                group_param = f'conn_params["group"] = "{args.group}"'
            else:
                group_param = "# No group specified"
            poc_template = poc_template.replace("<GROUP_PARAM>", group_param)

            # Conditionally add trace parameter
            if not args.no_trace:
                trace_param = 'conn_params["trace"] = "3"'
            else:
                trace_param = "# Trace disabled"

            poc_template = poc_template.replace("<TRACE_PARAM>", trace_param)

            poc_file = Path.cwd() / f"poc_{args.target}_{command}.py"
            poc_file.unlink(missing_ok=True)
            poc_file.write_text(poc_template, encoding="utf-8")

            print(f"[i] PoC code written to: {poc_file}")

        return 0

    if not methods.check_nwrfc_sdk():
        print(methods.nwrfc_sdk_tips())
        return 1

    print(f"[i] Connecting to SAP system: {args.target}")
    print(f"|-> Timeout: {args.timeout}s")
    print(f"|-> SysNr: {args.sysnr}")
    print(f"|-> Username: {args.username}")
    print(f"|-> Client: {args.client}")
    print(f"|-> Group: {args.group}")
    print(f"|-> Trace: {'disabled' if args.no_trace else 'enabled'}")

    try:
        # Create SAP system instance
        with sap.SAPSystem(
            host=args.target,
            user=args.username,
            passwd=args.password,
            client=args.client,
            sysnr=args.sysnr,
            group=args.group,
            timeout=args.timeout,
            trace=not args.no_trace,
        ) as sap_system:

            # Set OS filter
            if args.os is not None:
                sap_system.os = args.os
            else:
                sap_system.detect_current_os()

            terminal.run(sap_system)
    except Exception as exc:
        print(f"[!] An error occurred: \n\n{exc}")
        return 1
    except KeyboardInterrupt:
        return 1

    return 0
