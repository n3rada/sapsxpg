

def check_nwrfc_sdk():
    """Check if NWRFCSDK is properly installed"""
    try:
        from pyrfc import Connection
        return True
    except ImportError:
        print("⚠️ NWRFCSDK not found. Please download from:")
        print("https://support.sap.com/en/product/connectors/nwrfcsdk.html")
        print("https://community.sap.com/t5/technology-blog-posts-by-members/connecting-python-with-sap-step-by-step-guide/ba-p/13452893")
        return False


def banner() -> str:
    """Return the application banner."""
    return r"""
     _____  ___    ____ 
    /  ___|/ _ \  |  _ \  
    \ `--./ /_\ \ | |_) | 
     `--. \  _  | |  __/ 
    /\__/ / | | | | |    
    \____/\_| |_/ |_|   SXPG_CALL_SYSTEM
    """