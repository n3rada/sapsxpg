# sapspxpg/cli.py

# Built-in imports
import sys
import argparse
from pathlib import Path

# External library imports

# Local library imports
from sapsxpg import __version__
from sapsxpg.core import terminal
from sapsxpg.core import sap
from sapsxpg.utils import methods, banner


def build_parser() -> argparse.ArgumentParser:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="sapsxpg",
        description="Interactive console application to simplify the SXPG_CALL_SYSTEM usage on a targeted SAP system.",
        add_help=True,
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show version and exit.",
    )

    parser.add_argument(
        "target",
        type=str,
        help="Target SAP system hostname or IP address",
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

    # Connection mode - mutually exclusive
    conn_mode = parser.add_argument_group(
        "Connection Mode",
        "Choose between direct application server or load-balanced connection",
    )

    mode_group = conn_mode.add_mutually_exclusive_group()

    # Option 1: Direct connection (specify system number)
    mode_group.add_argument(
        "-s",
        "--sysnr",
        default=None,
        metavar="NN",
        help="System number for direct connection to application server (default: 00 if neither -s nor -m specified)",
    )

    # Option 2: Load-balanced connection (specify message server)
    mode_group.add_argument(
        "-m",
        "--mshost",
        metavar="HOST",
        help="Message server hostname for load-balanced connection (requires -r and -g)",
    )

    # Additional parameters for load-balanced mode
    conn_mode.add_argument(
        "-r",
        "--r3name",
        metavar="SID",
        help="SAP system ID (R/3 name) - required when using -m/--mshost",
    )

    conn_mode.add_argument(
        "-g",
        "--group",
        metavar="GROUP",
        help="SAP logon group (required for -m/--mshost, optional for -s/--sysnr)",
    )

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
    print(banner.display_banner())

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

        # Determine connection mode
        use_load_balancing = args.mshost is not None and args.r3name is not None

        with open(poc_code, "r", encoding="utf-8") as file:
            poc_template = file.read()
            poc_template = poc_template.replace("<USERNAME>", args.username)
            poc_template = poc_template.replace("<PASSWORD>", args.password)
            poc_template = poc_template.replace("<CLIENT>", args.client)
            poc_template = poc_template.replace("<SAP_COMMAND>", command)
            poc_template = poc_template.replace("<TIMEOUT>", str(args.timeout))

            # Connection mode specific replacements
            if use_load_balancing:
                conn_mode_params = f'''conn_params["mshost"] = "{args.mshost}"
    conn_params["r3name"] = "{args.r3name}"
    conn_params["group"] = "{args.group}"'''
            else:
                conn_mode_params = f'''conn_params["ashost"] = "{args.target}"
    conn_params["sysnr"] = "{args.sysnr}"'''

                # Add group for direct connection if specified
                if args.group is not None:
                    conn_mode_params += f'\n    conn_params["group"] = "{args.group}"'

            poc_template = poc_template.replace("<CONNECTION_PARAMS>", conn_mode_params)

            # Conditionally add trace parameter
            if not args.no_trace:
                trace_param = 'conn_params["trace"] = "3"'
            else:
                trace_param = "# Trace disabled"

            poc_template = poc_template.replace("<TRACE_PARAM>", trace_param)

            identifier = args.mshost if use_load_balancing else args.target
            poc_file = Path.cwd() / f"poc_{identifier}_{command}.py"
            poc_file.unlink(missing_ok=True)
            poc_file.write_text(poc_template, encoding="utf-8")

            print(f"[i] PoC code written to: {poc_file}")

        return 0

    if not methods.check_nwrfc_sdk():
        print(methods.nwrfc_sdk_tips())
        return 1

    # Determine connection mode
    use_load_balancing = args.mshost is not None

    # Validate connection parameters
    if use_load_balancing:
        # Load-balanced mode requires mshost, r3name, and group
        if not args.r3name:
            print("[x] Error: --mshost requires --r3name (SAP system ID)")
            return 1
        if not args.group:
            print("[x] Error: --mshost requires --group (logon group)")
            return 1
    else:
        # Direct mode - set default sysnr if not specified
        if args.sysnr is None:
            args.sysnr = "00"

        # Warn if load-balancing parameters specified without mshost
        if args.r3name:
            print("[w] Warning: --r3name ignored without --mshost")

    # Display connection info
    if use_load_balancing:
        print(f"[i] Connection mode: Load-balanced via Message Server")
        print(f"|-> Message Server: {args.mshost}")
        print(f"|-> System ID (R3NAME): {args.r3name}")
        print(f"|-> Logon Group: {args.group}")
        print(f"|-> Username: {args.username}")
        print(f"|-> Client: {args.client}")
        print(f"|-> Timeout: {args.timeout}s")
        print(f"|-> Trace: {'disabled' if args.no_trace else 'enabled'}")
    else:
        print(f"[i] Connection mode: Direct to Application Server")
        print(f"|-> Target: {args.target}")
        print(f"|-> System Number: {args.sysnr}")
        print(f"|-> Username: {args.username}")
        print(f"|-> Client: {args.client}")
        if args.group:
            print(f"|-> Logon Group: {args.group}")
        print(f"|-> Timeout: {args.timeout}s")
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
            mshost=args.mshost,
            r3name=args.r3name,
            timeout=args.timeout,
            trace=not args.no_trace,
        ) as sap_system:

            # Set OS filter
            if args.os is not None:
                sap_system.os = args.os
            else:
                sap_system.detect_current_os()

            return terminal.run(sap_system)
    except KeyboardInterrupt:
        print("\n[!] Operation interrupted by user")
        return 130
    except Exception as exc:
        print(f"[!] An error occurred: \n\n{exc}")
        return 1

    return 0
