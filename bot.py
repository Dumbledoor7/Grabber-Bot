"""
Grabber Bot - Main file
"""

import io
import re
import zipfile
import logging
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from config import BOT_TOKEN, ADMIN_IDS, OWNER_CONTACT, TEXTS, PLATFORMS
from scrapers import kleinanzeigen

# Logging (minimal)
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def get_text(key: str, **kwargs) -> str:
    """Get text from config and format it"""
    text = TEXTS.get(key, "")
    kwargs["owner"] = OWNER_CONTACT
    return text.format(**kwargs)


def detect_platform(url: str) -> str:
    """Detect which platform a URL belongs to"""
    for platform_id, platform in PLATFORMS.items():
        if not platform.get("enabled"):
            continue
        for pattern in platform.get("patterns", []):
            if re.search(pattern, url):
                return platform_id
    return None

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start"""
    keyboard = [
        [InlineKeyboardButton("How to use", callback_data="help")],
        [InlineKeyboardButton("Contact", callback_data="contact")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(get_text("start"), reply_markup=reply_markup)


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "help":
        await query.message.reply_text(get_text("help"))
    elif query.data == "contact":
        await query.message.reply_text(f"Contact: {OWNER_CONTACT}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help"""
    await update.message.reply_text(get_text("help"))


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages"""
    text = update.message.text
    user = update.effective_user
    
    # Find URL in message
    url_match = re.search(r"https?://[^\s]+", text)
    if not url_match:
        await update.message.reply_text(get_text("error_invalid_link"))
        return
    
    url = url_match.group()
    
    # Detect platform
    platform = detect_platform(url)
    if not platform:
        await update.message.reply_text(get_text("error_invalid_link"))
        return
    
    # Send loading message
    loading_msg = await update.message.reply_text(get_text("loading"))
    
    # Scrape based on platform
    try:
        if platform == "kleinanzeigen":
            data = kleinanzeigen.scrape(url)
        else:
            data = None
        
        if not data:
            await loading_msg.edit_text(get_text("error_load_failed"))
            return
        
        # Check for images
        if not data["images"]:
            await loading_msg.edit_text(get_text("error_no_images"))
            return
        
        # Update status
        await loading_msg.edit_text(get_text("downloading", count=len(data["images"])))
        
        # Create ZIP file
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
# Add info.txt
            info_text = f"""Titel: {data['title']}
Preis: {data['price']}
Datum: {data['date']}

Beschreibung:
{data['description']}

URL: {data['url']}

Downloaded with @TGPythonBot on Telegram
"""
            zf.writestr("info.txt", info_text)
            
            # Download and add images
            for i, img_url in enumerate(data["images"], 1):
                img_data = kleinanzeigen.download_image(img_url)
                if img_data:
                    zf.writestr(f"image_{i:02d}.jpg", img_data)
        
        zip_buffer.seek(0)
        
        # Send ZIP
        filename = re.sub(r"[^\w\s-]", "", data["title"])[:30] or "listing"
        filename = f"{filename}.zip"
        
        await loading_msg.edit_text(get_text("creating_zip"))
        await update.message.reply_document(
            document=zip_buffer,
            filename=filename,
            caption=get_text("success", count=len(data["images"]))
        )
        await loading_msg.delete()
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await loading_msg.edit_text(get_text("error_unknown"))


def main():
    """Start the bot"""
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    from telegram.ext import CallbackQueryHandler
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot starting...")
    app.run_polling()


if __name__ == "__main__":
    main()