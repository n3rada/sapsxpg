## File: sapsxpg/utils/methods.py


def check_nwrfc_sdk() -> bool:
    """Check if NWRFCSDK is properly installed"""
    try:
        from pyrfc import Connection

        return True
    except ImportError:
        return False


def nwrfc_sdk_tips():

    tips = "⚠️ NWRFCSDK not found."

    tips += " Ensure that the environment variables are set correctly\n"

    tips += "For Linux:\n"
    tips += """
NWRFCSDK_PATH=$(find /home /usr/local /opt /srv -type d -path "*/nwrfcsdk" -print -quit 2>/dev/null | head -1)
export SAPNWRFC_HOME=$NWRFCSDK_PATH
export LD_LIBRARY_PATH="$NWRFCSDK_PATH/lib:"
"""

    return tips
