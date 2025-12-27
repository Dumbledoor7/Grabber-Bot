"""
Configuration file - Edit your texts and settings here
"""

# ============== BOT SETTINGS ==============
BOT_TOKEN = "8262223594:AAGLuQHUWPDPMNj6KF9fvqjNW63xMu_HOTo"
ADMIN_IDS = [8081806690]

# ============== CONTACT ==============
OWNER_CONTACT = "@YourUsername"  # Change this to your Telegram username

# ============== TEXTS ==============
# Edit these however you like. Use {variables} where shown.

TEXTS = {
    # Start command
    "start": """Welcome to Grabber Bot!

Send me a link and I'll grab all images + info as a ZIP file.

Supported:
- kleinanzeigen.de

Contact: {owner}""",

    # Help command  
    "help": """How to use:
1. Copy a listing link
2. Send it here
3. Get ZIP with all images + info

Contact: {owner}""",

    # Processing messages
    "loading": "Loading listing...",
    "downloading": "Downloading {count} images...",
    "creating_zip": "Creating ZIP file...",
    
    # Success
    "success": "Done! {count} images",
    
    # Errors
    "error_invalid_link": "Invalid link. Send a kleinanzeigen.de listing link.",
    "error_load_failed": "Could not load listing. Try again later.",
    "error_no_images": "No images found.",
    "error_unknown": "Something went wrong. Contact {owner}",
}

# ============== SUPPORTED PLATFORMS ==============
PLATFORMS = {
    "kleinanzeigen": {
        "name": "Kleinanzeigen.de",
        "patterns": [
            r"kleinanzeigen\.de/s-anzeige/",
        ],
        "enabled": True,
    },
    # Add more platforms later:
    # "willhaben": {
    #     "name": "Willhaben.at", 
    #     "patterns": [r"willhaben\.at/"],
    #     "enabled": False,
    # },
}