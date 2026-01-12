# sapsxpg/core/sap.py

import json
import os
import getpass
from pathlib import Path
import tempfile

try:
    from pyrfc import Connection
except ImportError:
    Connection = None  # Handle missing pyrfc gracefully


def get_os_variants(os_name):
    """Get OS variants for command filtering"""
    os_lower = os_name.lower()

    # Handle special filter types
    if os_lower == "all":
        # Return all possible OS types - will match everything
        return [
            "anyos",
            "linux",
            "unix",
            "windows",
            "windows nt",
            "sunos",
            "aix",
            "os/400",
            "as/400",
        ]

    if os_lower == "anyos":
        return ["anyos"]

    # Standard OS mapping
    variants = ["anyos"]  # ANYOS works for all systems

    if os_lower in ["linux"]:
        variants.extend(["linux", "unix"])
    elif os_lower in ["windows", "windows nt"]:
        variants.extend(["windows nt", "windows"])
    elif os_lower in ["unix"]:
        variants.extend(["unix", "linux", "sunos", "aix"])
    elif os_lower in ["sunos"]:
        variants.extend(["sunos", "unix"])
    elif os_lower in ["aix"]:
        variants.extend(["aix", "unix"])
    else:
        # For any other OS, try exact matches
        variants.extend([os_lower])

    return variants


class SAPSystem:
    """Main SAP system class that handles configuration, connection, and command execution"""

    def __init__(
        self,
        host,
        user,
        passwd,
        client="500",
        sysnr="00",
        group=None,
        mshost=None,
        r3name=None,
        timeout=30,
        trace=True,
    ):
        self.__host = host
        self.__user = user
        self.__passwd = passwd
        self.__client = client
        self.__sysnr = sysnr
        self.__group = group
        self.__mshost = mshost
        self.__r3name = r3name
        self.__timeout = timeout
        self.__trace = trace
        self.__os = "all"  # Default OS filter

        self.__conn = None  # Persistent SAP connection

        # Determine connection mode
        self.__use_load_balancing = mshost is not None and r3name is not None

        # Get the current user's username
        username = getpass.getuser()

        # Use tempfile and pathlib for user-specific temporary directory
        host_identifier = mshost if self.__use_load_balancing else host
        self.__temp_dir = Path(tempfile.gettempdir()) / username / host_identifier
        self.__temp_dir.mkdir(parents=True, exist_ok=True)

        self.__log_file = f"SAP-{host_identifier}.log"
        self.__histfile = f"{self.__temp_dir}/.sapsxpg_history"

    def __connect(self):
        """Establish a persistent SAP connection"""
        if self.__conn is None:
            try:
                # Build connection parameters based on connection mode
                if self.__use_load_balancing:
                    # Load-balanced connection via Message Server
                    conn_params = {
                        "user": self.__user,
                        "passwd": self.__passwd,
                        "mshost": self.__mshost,
                        "r3name": self.__r3name,
                        "group": self.__group,
                        "client": self.__client,
                        "lang": "EN",
                        "config": {"timeout": self.__timeout},
                    }
                else:
                    # Direct connection to Application Server
                    conn_params = {
                        "user": self.__user,
                        "passwd": self.__passwd,
                        "ashost": self.__host,
                        "client": self.__client,
                        "sysnr": self.__sysnr,
                        "lang": "EN",
                        "config": {"timeout": self.__timeout},
                    }

                    # Only include group if it's not None (for direct connection)
                    if self.__group is not None:
                        conn_params["group"] = self.__group

                # Add trace parameter if enabled
                if self.__trace:
                    conn_params["trace"] = "3"

                self.__conn = Connection(**conn_params)

                mode = "load-balanced" if self.__use_load_balancing else "direct"
                print(f"[i] SAP connection established ({mode})")
            except KeyboardInterrupt:
                print("\n[!] Connection interrupted by user")
                raise  # Re-raise to let CLI handle it
            except Exception as e:
                print(f"[!] Failed to establish SAP connection: {e}")
                raise  # Re-raise to let CLI handle it
                raise  # Re-raise to let CLI handle it

    def __disconnect(self):
        """Close the persistent SAP connection"""
        if self.__conn:

            self.__conn.close()
            print("[i] SAP connection closed")

    def detect_current_os(self):
        """Auto-detect the remote SAP system's operating system"""
        os_cache_file = f"{self.__temp_dir}/os"

        # Check if cached OS detection exists
        if os.path.exists(os_cache_file):
            try:
                with open(os_cache_file, "r") as f:
                    cached_os = f.read().strip()
                print(f"[i] Using cached OS detection: {cached_os}")
                self.__os = cached_os
                return cached_os
            except Exception as e:
                print(f"[w] Could not read OS cache file: {e}")

        try:
            # Connect to SAP and run ENV command to detect OS
            print("[i] Detecting remote OS via SAP ENV command...")

            # XPG_CALL_SYSTEM has a 128-char limit for the argument string
            response = self.__connection.call(
                "SXPG_CALL_SYSTEM", COMMANDNAME="ENV", ADDITIONAL_PARAMETERS=""
            )

            # Parse environment variables to detect OS
            env_output = ""
            for result in response["EXEC_PROTOCOL"]:
                env_output += result["MESSAGE"] + "\n"

            env_lower = env_output.lower()

            # Detect OS based on environment variables
            detected_os = None
            if any(
                x in env_lower
                for x in ["windir=", "windows", "comspec=", "programfiles="]
            ):
                detected_os = "Windows"
            elif any(
                x in env_lower for x in ["shell=/bin/bash", "shell=/usr/bin/bash"]
            ):
                detected_os = "Linux"
            elif any(
                x in env_lower for x in ["shell=/bin/ksh", "shell=/usr/bin/ksh", "aix"]
            ):
                detected_os = "Unix"  # Likely AIX
            elif any(x in env_lower for x in ["sunos", "solaris"]):
                detected_os = "Unix"  # SunOS/Solaris
            elif "shell=" in env_lower and "/" in env_lower:
                # Generic Unix-like system
                detected_os = "Linux"  # Most common case
            elif "path=" in env_lower and "/" in env_lower:
                # Unix-like system with PATH variable
                detected_os = "Linux"
            else:
                detected_os = "Linux"  # Final fallback

            # Cache the detected OS
            if detected_os:
                try:
                    with open(os_cache_file, "w") as f:
                        f.write(detected_os)
                    print(f"[i] Cached OS detection to: {os_cache_file}")
                except Exception as e:
                    print(f"[w] Could not cache OS detection: {e}")

            self.__os = detected_os
            return detected_os

        except Exception as e:
            print(f"[w] Could not auto-detect remote OS: {e}")
            print("[i] Falling back to Linux filter")
            detected_os = "Linux"  # Safe fallback

            # Still try to cache the fallback
            try:
                with open(os_cache_file, "w") as f:
                    f.write(detected_os)
            except:
                pass

            self.__os = detected_os
            return detected_os

    def get_commands_for_os(self, target_os: str | None = None) -> str:
        """Read commands from JSON file and filter by OS"""
        if target_os is None:
            target_os = self.__os

        filename = f"{self.__temp_dir}/commands.json"

        try:
            # Check if file exists
            if not os.path.exists(filename):
                return f"[!] Commands file not found: {filename}\n[i] Run 'h' or 'help' first to generate the commands list."

            # Read JSON file
            with open(filename, "r") as f:
                data = json.load(f)

            result = f"Available Commands for {target_os}\n"
            result += "=" * 40 + "\n\n"

            # Look for commands matching the target OS with comprehensive mapping
            matching_commands = []

            # Create OS mapping for better compatibility
            os_variants = get_os_variants(target_os)

            for os_name, commands in data.get("commands_by_os", {}).items():
                if os_name in os_variants:
                    matching_commands.extend(commands)

            if not matching_commands:
                result += f"[!] No commands found for OS: {target_os}\n"
                result += f"Available OS types: {', '.join(data.get('commands_by_os', {}).keys())}"
                return result

            # Remove duplicates based on command NAME
            unique_commands = {}
            for cmd in matching_commands:
                name = cmd.get("NAME", "")
                if name not in unique_commands:
                    unique_commands[name] = cmd

            # Format commands nicely
            result += f"Found {len(unique_commands)} unique commands:\n\n"

            for cmd in sorted(
                unique_commands.values(), key=lambda x: x.get("NAME", "")
            ):
                name = cmd.get("NAME", "")
                opcommand = cmd.get("OPCOMMAND", "")
                parameters = cmd.get("PARAMETERS", "")
                addpar = cmd.get("ADDPAR") == "X"

                result += f"• {name}\n"
                result += f"  Underlying command: {opcommand}\n"
                if parameters:
                    result += f"  Default params: {parameters}\n"
                if addpar:
                    result += "  Additional parameters: Yes\n"
                result += "-" * 30 + "\n"

            return result

        except Exception as e:
            return f"[!] Error reading commands file: {e}"

    def is_command_available(self, command_name: str) -> dict | None:
        """Check if a command is available in the SAP system and return its details"""
        filename = f"{self.__temp_dir}/commands.json"

        if not os.path.exists(filename):
            return None

        try:
            with open(filename, "r") as f:
                data = json.load(f)

            # Get OS variants for current system
            os_variants = get_os_variants(self.__os)

            # Search for command in compatible OS categories (return first match to avoid duplicates)
            for os_name, commands in data.get("commands_by_os", {}).items():
                if os_name in os_variants:
                    for cmd in commands:
                        if cmd.get("NAME", "").upper() == command_name.upper():
                            return cmd

            return None

        except Exception:
            return None

    def execute_command(self, command: str, parameters: str = "") -> str | None:
        """Execute a command on the SAP system"""

        if command in ["h", "help", "?"]:
            return self.__handle_help_command()

        function_name = "SXPG_CALL_SYSTEM"
        function_to_execute = None

        if command == "ls":
            function_to_execute = {
                "COMMANDNAME": "LIST_DB2DUMP",
                "ADDITIONAL_PARAMETERS": parameters,
            }
        elif command == "cat":
            function_to_execute = {
                "COMMANDNAME": "CAT",
                "ADDITIONAL_PARAMETERS": parameters,
            }
        elif command == "ps":
            function_to_execute = {
                "COMMANDNAME": "PS",
                "ADDITIONAL_PARAMETERS": parameters,
            }
        elif command == "env":
            function_to_execute = {
                "COMMANDNAME": "ENV",
            }
        else:
            # Check if the command is available in SAP system
            cmd_info = self.is_command_available(command)
            if cmd_info:
                # Command found, execute it directly
                command_name = cmd_info.get("NAME", "")

                # Build function parameters
                function_to_execute = {
                    "COMMANDNAME": command_name,
                }

                # Add parameters if the command accepts them and parameters were provided
                if cmd_info.get("ADDPAR") == "X" and parameters:
                    function_to_execute["ADDITIONAL_PARAMETERS"] = parameters
                elif parameters and not cmd_info.get("ADDPAR") == "X":
                    print(
                        f"[w] Command {command_name} does not accept additional parameters, ignoring: {parameters}"
                    )
            else:
                print(f"[x] Command not found: {command}")
                print("[i] Use 'h' or 'help' to see available commands")
                return None

        command_name = function_to_execute.get("COMMANDNAME", command)
        parameters = function_to_execute.get("ADDITIONAL_PARAMETERS", "")

        # Guard: DEFINED_PARAMETERS + ADDITIONAL_PARAMETERS must be <= 128 chars
        defined_parameters = command_name if command_name else ""
        additional_parameters = parameters if parameters else ""
        total_length = len(defined_parameters) + len(additional_parameters)
        if total_length >= 128:
            print(
                f"[x] SAP SXPG argument limit exceeded: {total_length} chars (max 128). Aborting call."
            )
            print(
                f"[i] COMMANDNAME: '{defined_parameters}' ({len(defined_parameters)} chars)"
            )
            print(
                f"[i] ADDITIONAL_PARAMETERS: '{additional_parameters}' ({len(additional_parameters)} chars)"
            )
            return None

        print(f"[i] Executing SAP command: {command_name} {parameters}")

        with open(self.__log_file, mode="a", encoding="utf-8") as log_file:
            log_file.write(f"> {command_name} {parameters}\n")

        try:
            # Execute the remote function call
            response = self.__connection.call(function_name, **function_to_execute)
        except Exception as e:
            print(f"[-] Error: {e}")
            return None

        # Handle SXPG_CALL_SYSTEM response
        results = response["EXEC_PROTOCOL"]
        result_txt = ""
        for result in results:
            result_txt = f"{result_txt}{result['MESSAGE']}\n"

        with open(self.__log_file, mode="a", encoding="utf-8") as log_file:
            log_file.write(f"{result_txt}\n")

        return result_txt

    def __handle_help_command(self) -> str:
        """Handle help command - fetch and cache command list"""
        # First check if we have a cached commands file
        filename = f"{self.__temp_dir}/commands.json"
        if os.path.exists(filename):
            # Read the cached file and show summary + filtered commands
            try:
                with open(filename, "r") as f:
                    data = json.load(f)

                # Display summary from cached data
                summary = (
                    "SAP External Commands (SM69) Summary\n"
                    + "=" * 40
                    + "\n"
                    + f"Total Commands: {data['meta']['total_commands']}\n"
                    + f"Operating Systems: {len(data['commands_by_os'])}\n\n"
                )

                # Show command count per OS
                for os_name, commands in data["commands_by_os"].items():
                    summary += f"  {os_name}: {len(commands)} commands\n"
                summary += "\n"
                # Also show filtered commands for current OS
                summary += self.get_commands_for_os()

                return summary
            except Exception as e:
                print(f"[!] Error reading cached file: {e}")
                # Fall back to fetching fresh data

        try:
            response = self.__connection.call("SXPG_COMMAND_LIST_GET")
        except Exception as e:
            return f"[!] Error fetching command list: {e}"

        # Handle command list response
        if "COMMAND_LIST" in response:
            command_list = response["COMMAND_LIST"]

            # Create organized JSON structure
            organized_commands = {
                "meta": {
                    "host": self.__host,
                    "total_commands": len(command_list),
                },
                "commands_by_os": {},
                "all_commands": command_list,
            }

            # Group commands by operating system
            for cmd in command_list:
                os_name = cmd.get(
                    "OPSYSTEM", "UNKNOWN"
                ).lower()  # Normalize to lowercase
                if os_name not in organized_commands["commands_by_os"]:
                    organized_commands["commands_by_os"][os_name] = []
                organized_commands["commands_by_os"][os_name].append(cmd)

            try:
                with open(filename, "w") as cmd_file:
                    json.dump(
                        organized_commands, cmd_file, indent=2, ensure_ascii=False
                    )
                print(f"[+] Command list saved as JSON to: {filename}")
            except Exception as e:
                print(f"[-] Failed to save command list: {e}")

            summary = (
                "SAP External Commands (SM69) Summary\n"
                + "=" * 40
                + "\n"
                + f"Total Commands: {len(command_list)}\n"
                + f"Operating Systems: {len(organized_commands['commands_by_os'])}\n\n"
            )

            # Show command count per OS
            for os_name, commands in organized_commands["commands_by_os"].items():
                summary += f"  {os_name}: {len(commands)} commands\n"

            # Also show filtered commands for current OS
            summary += self.get_commands_for_os()

            return summary
        else:
            return "[!] No command list found in SAP response"

    def get_available_commands(self) -> list:
        """Get list of available command names for current OS"""
        filename = f"{self.__temp_dir}/commands.json"

        if not os.path.exists(filename):
            return []

        try:
            with open(filename, "r") as f:
                data = json.load(f)

            # Get OS variants for current system
            os_variants = get_os_variants(self.__os)

            # Collect unique commands for current OS
            unique_commands = set()
            for os_name, commands in data.get("commands_by_os", {}).items():
                if os_name in os_variants:
                    for cmd in commands:
                        name = cmd.get("NAME", "").lower()
                        if name:
                            unique_commands.add(name)

            return sorted(list(unique_commands))

        except Exception:
            return []

    # Properties
    @property
    def host(self):
        """Get the display host (mshost if load-balanced, else ashost)"""
        return self.__mshost if self.__use_load_balancing else self.__host

    @property
    def connection_mode(self):
        """Get the connection mode description"""
        return "load-balanced" if self.__use_load_balancing else "direct"

    @property
    def os(self):
        return self.__os

    @os.setter
    def os(self, value):
        self.__os = value

    @property
    def user(self):
        return self.__user

    @property
    def histfile(self):
        return self.__histfile

    @property
    def __connection(self):
        """Get the current SAP connection (establish if not connected)"""
        if self.__conn is None:
            self.__connect()
        return self.__conn

    def __enter__(self):
        """Enter the runtime context related to this object."""
        self.__connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the runtime context and clean up the connection."""
        self.__disconnect()
