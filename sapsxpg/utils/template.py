#!/usr/bin/env python3

try:
    from pyrfc import Connection
except ImportError:
    Connection = None  # Handle missing pyrfc gracefully


def execute(command: str, timeout: float = None) -> str:
    """Execute a command using SAP's SXPG_CALL_SYSTEM function module."""

    # Establish connection to the SAP system
    conn = Connection(
        **{
            "user": "<USERNAME>",
            "passwd": "<PASSWORD>",
            "ashost": "<HOST>",
            "group": "<GROUP>",
            "sysnr": "<SYSNR>",
            "client": "<CLIENT>",
            "trace": "3",
            "lang": "EN",
        }
    )

    prepared_command = command.replace(" ", "${IFS}")

    # Call the SXPG_CALL_SYSTEM function module
    response = conn.call(
        "SXPG_CALL_SYSTEM",
        **{
            "COMMANDNAME": "<SAP_COMMAND>",
            "ADDITIONAL_PARAMETERS": f"-c {prepared_command}",
        },
    )

    # Close connection
    conn.close()

    # Process and return the output
    results = response["EXEC_PROTOCOL"]
    result_txt = ""
    for result in results:
        result_txt = f"{result_txt}{result['MESSAGE']}\n"

    return result_txt
