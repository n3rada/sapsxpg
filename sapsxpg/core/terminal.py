## File: sapsxpg/core/terminal.py

"""Interactive Terminal Interface Module.

This module provides an interactive command-line interface for executing
SAP system commands. It handles command input, autocompletion, history
management, and result display in a terminal-like environment.

The terminal supports command history, tab completion, and displays command
output in a user-friendly format.
"""

# External library imports
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import ThreadedAutoSuggest, AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import ThreadedHistory, FileHistory
from prompt_toolkit.cursor_shapes import CursorShape


class SAPCommandCompleter(Completer):
    """Custom completer for SAP commands"""

    def __init__(self, sap_system):
        self.__sap_system = sap_system
        self.__built_in_commands = ["ls", "cat", "ps", "env", "h", "help", "?", "exit"]
        self.__sap_commands = []
        self.refresh_commands()

    def get_completions(self, document, complete_event):
        """Generate completions for the current input"""
        word = document.get_word_before_cursor()

        # Combine built-in and SAP commands
        all_commands = self.__built_in_commands + self.__sap_commands

        # Filter commands that start with the current word
        for command in all_commands:
            if command.lower().startswith(word.lower()):
                yield Completion(command, start_position=-len(word), display=command)

    def refresh_commands(self):
        """Refresh the SAP commands list"""
        self.__sap_commands = self.__sap_system.get_available_commands()


def run(sap_system) -> None:
    """Run the interactive SAP command shell"""

    # Create command completer
    command_completer = SAPCommandCompleter(sap_system)

    prompt_session = PromptSession(
        cursor=CursorShape.BLINKING_BLOCK,
        multiline=False,
        enable_history_search=True,
        wrap_lines=True,
        auto_suggest=ThreadedAutoSuggest(auto_suggest=AutoSuggestFromHistory()),
        history=ThreadedHistory(history=FileHistory(f"{sap_system.histfile}")),
        completer=command_completer,
        complete_while_typing=True,
    )

    try:
        while True:
            try:
                prompt = f"{sap_system.host} ({sap_system.os})$ "
                command_line = prompt_session.prompt(message=prompt).strip()

                if not command_line:
                    continue

                # Parse command and parameters
                parts = command_line.split(" ", 1)
                command = parts[0]
                parameters = parts[1] if len(parts) > 1 else ""

                # Handle exit commands
                if command.lower() in ["exit", "quit", "q"]:
                    print("👋 Goodbye!")
                    break

                # Check if command is supported (built-in commands or SAP commands)
                built_in_commands = ["ls", "cat", "ps", "env", "h", "help", "?"]
                if command not in built_in_commands:
                    # Check if it's an available SAP command
                    if not sap_system.is_command_available(command):
                        print("[x] Command not found")
                        print("[i] Use 'h' or 'help' to see all available SAP commands")
                        continue

                output = sap_system.execute_command(command, parameters)

                if command in ["h", "help", "?"] and output:
                    command_completer.refresh_commands()

                # Display and log output
                if output:
                    print(output)

            except KeyboardInterrupt:
                break

    except Exception as exc:
        print(f"Fatal error: {exc}")
        return
