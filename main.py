import os
import logging
import asyncio
import requests
import json
from datetime import datetime
from typing import Optional, Dict, Any
import tempfile
import traceback
import random
import base64

# Telegram imports
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============ CONFIGURATION ============
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    logger.error("❌ TELEGRAM_BOT_TOKEN not found in environment variables!")
    exit(1)

# Conversation states
WAITING_FOR_IMAGE = 1
WAITING_FOR_PROMPT = 2

# ============ USER DATA ============
user_data_store: Dict[int, Dict[str, Any]] = {}

# ============ VIDEO GENERATION ============

class VideoGenerator:
    """Handles all video generation operations"""
    
    @staticmethod
    async def generate_video_with_text(image_data: bytes, text_prompt: str) -> Optional[bytes]:
        """
        Generate a video with text overlay and animation
        This creates a simple video with the text overlaid
        """
        try:
            logger.info(f"Generating video with text: {text_prompt[:50]}...")
            
            # For now, we'll create a simple response
            # In production, integrate with actual AI APIs
            
            # Simulate processing
            await asyncio.sleep(5)
            
            # For demo purposes, return None to show we're working on it
            # This will trigger the "Coming soon" message
            return None
            
        except Exception as e:
            logger.error(f"Video generation error: {str(e)}")
            logger.error(traceback.format_exc())
            return None

    @staticmethod
    async def generate_dancing_video(image_data: bytes, prompt: str) -> Optional[bytes]:
        """
        Generate dancing video from image
        Placeholder for actual AI integration
        """
        try:
            logger.info(f"Generating dancing video with prompt: {prompt[:50]}...")
            
            # Simulate processing
            await asyncio.sleep(3)
            
            # For demo, return None
            return None
            
        except Exception as e:
            logger.error(f"Dancing video error: {str(e)}")
            return None

# ============ COMMAND HANDLERS ============

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    
    # Initialize user data
    user_id = user.id
    if user_id not in user_data_store:
        user_data_store[user_id] = {
            'joined': datetime.now(),
            'generations_used': 0,
            'total_generations': 0
        }
    
    keyboard = [
        [InlineKeyboardButton("🎬 Create Video", callback_data="create_video")],
        [InlineKeyboardButton("📸 Image to Video", callback_data="image_to_video")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"👋 *Hi {user.first_name}!* Welcome to Bideruibot! 🎬\n\n"
        "I can turn your images into amazing videos!\n\n"
        "*What I can do:*\n"
        "• 🎭 Animate your photos\n"
        "• 🎵 Make images speak\n"
        "• 🎬 Add text overlays\n"
        "• 💃 Dancing animations\n\n"
        "*How to use:*\n"
        "1. Click 'Create Video' below\n"
        "2. Upload your image\n"
        "3. Tell me what to do\n"
        "4. I'll create your video!\n\n"
        "✨ *Try it now!*",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    keyboard = [
        [InlineKeyboardButton("🎬 Create Video", callback_data="create_video")],
        [InlineKeyboardButton("📊 Status", callback_data="status")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📚 *Bideruibot Help*\n\n"
        "*Commands:*\n"
        "• /start - Welcome & menu\n"
        "• /help - Show this help\n"
        "• /create - Start video creation\n"
        "• /status - Check your usage\n"
        "• /cancel - Cancel operation\n\n"
        "*How to create a video:*\n"
        "1️⃣ Send /create or click 'Create Video'\n"
        "2️⃣ Upload a photo (JPG/PNG)\n"
        "3️⃣ Describe what you want\n"
        "4️⃣ Wait for your video!\n\n"
        "*Example prompts:*\n"
        "• 'Make her dance like a pop star'\n"
        "• 'Say my name is Ayomide, I'm 40 years old'\n"
        "• 'Dance to a happy beat'\n\n"
        "🎯 *Tips:* Be specific for best results!",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command"""
    user_id = update.effective_user.id
    user_data = user_data_store.get(user_id, {'generations_used': 0, 'total_generations': 0})
    
    await update.message.reply_text(
        f"📊 *Your Statistics*\n\n"
        f"• Today's Generations: {user_data.get('generations_used', 0)}/10\n"
        f"• Total Generations: {user_data.get('total_generations', 0)}\n"
        f"• Joined: {user_data.get('joined', datetime.now()).strftime('%Y-%m-%d')}\n\n"
        f"🟢 Bot Status: *Online*\n"
        f"⚡ Ready to create videos!",
        parse_mode='Markdown'
    )

async def create_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /create command"""
    await update.message.reply_text(
        "🎬 *Let's Create Your Video!*\n\n"
        "📤 *Step 1:* Please send me a photo\n"
        "• Format: JPG or PNG\n"
        "• Max size: 20MB\n"
        "• Clear face/body preferred\n\n"
        "🔄 Send /cancel to cancel",
        parse_mode='Markdown'
    )
    context.user_data['state'] = WAITING_FOR_IMAGE

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /cancel command"""
    context.user_data['state'] = None
    context.user_data['image_data'] = None
    context.user_data['prompt'] = None
    
    await update.message.reply_text(
        "✅ *Cancelled!*\n\n"
        "You can start a new video anytime with /create",
        parse_mode='Markdown'
    )

# ============ IMAGE HANDLING ============

async def handle_image_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle image upload"""
    user_id = update.effective_user.id
    
    logger.info(f"📸 Image received from user {user_id}")
    
    # Check state
    state = context.user_data.get('state')
    if state != WAITING_FOR_IMAGE:
        await update.message.reply_text(
            "🤔 Please use /create to start a new video!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎬 Create Video", callback_data="create_video")]
            ])
        )
        return
    
    try:
        # Get image
        photo = update.message.photo[-1]
        file = await photo.get_file()
        
        # Download image
        logger.info(f"⬇️ Downloading image: {file.file_id}")
        image_bytes = await file.download_as_bytearray()
        
        # Store image
        context.user_data['image_data'] = image_bytes
        
        # Ask for prompt
        context.user_data['state'] = WAITING_FOR_PROMPT
        
        await update.message.reply_text(
            "✅ *Image Received!*\n\n"
            "📝 *Step 2:* Now tell me what you want!\n\n"
            "*Examples:*\n"
            "• 'Make her say: My name is Ayomide, I'm 40 years old'\n"
            "• 'Dance like a pop star'\n"
            "• 'Sing a happy song'\n"
            "• 'Create a funny video with this image'\n\n"
            "✏️ Send your description now:",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"❌ Error handling image: {str(e)}")
        logger.error(traceback.format_exc())
        await update.message.reply_text(
            "❌ *Error!*\n\n"
            "Couldn't process your image. Please try again.\n"
            "Make sure it's a valid JPG or PNG file.",
            parse_mode='Markdown'
        )

async def handle_prompt_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text prompt"""
    user_id = update.effective_user.id
    prompt = update.message.text
    
    logger.info(f"📝 Prompt received from user {user_id}: {prompt[:50]}...")
    
    # Check state
    state = context.user_data.get('state')
    if state != WAITING_FOR_PROMPT:
        await update.message.reply_text(
            "🤔 Please use /create to start a new video!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎬 Create Video", callback_data="create_video")]
            ])
        )
        return
    
    if len(prompt.strip()) < 3:
        await update.message.reply_text(
            "⚠️ Please provide a longer description (at least 3 characters)!",
            parse_mode='Markdown'
        )
        return
    
    # Get image
    image_data = context.user_data.get('image_data')
    if not image_data:
        await update.message.reply_text(
            "❌ *Error!*\n\n"
            "Image data not found. Please start over with /create.",
            parse_mode='Markdown'
        )
        context.user_data['state'] = None
        return
    
    # Clear state
    context.user_data['state'] = None
    
    # Show processing
    processing_msg = await update.message.reply_text(
        f"🎬 *Creating Your Video...*\n\n"
        f"📝 *Prompt:* {prompt[:100]}{'...' if len(prompt) > 100 else ''}\n\n"
        "⏳ *Step 3:* Generating...\n"
        "This will take 30-60 seconds.\n"
        "Please wait! 🎥",
        parse_mode='Markdown'
    )
    
    try:
        # Show typing
        await update.message.chat.send_action(action="upload_video")
        
        # Generate video
        logger.info(f"🎬 Generating video for prompt: {prompt[:50]}...")
        
        # For now, we'll send a message explaining the feature
        await processing_msg.edit_text(
            "🎬 *Video Generation Feature*\n\n"
            "I'm currently being upgraded to support full video generation!\n\n"
            "✨ *Coming Soon:*\n"
            "• Real dancing animations\n"
            "• Voice synthesis\n"
            "• Text-to-speech with your custom text\n"
            "• Professional video editing\n\n"
            "For now, let me show you what I can do with your image! 🎨",
            parse_mode='Markdown'
        )
        
        # Send a placeholder video or GIF
        await update.message.reply_text(
            "🎨 *Preview Mode*\n\n"
            "Here's a preview of what's coming:\n"
            f"📸 Your image will be animated with:\n"
            f"• Text: {prompt[:100]}{'...' if len(prompt) > 100 else ''}\n\n"
            "🚀 *Full video generation coming soon!*\n"
            "Stay tuned for exciting updates! 🎬",
            parse_mode='Markdown'
        )
        
        # Update user data
        if user_id not in user_data_store:
            user_data_store[user_id] = {'generations_used': 0, 'total_generations': 0}
        
        user_data_store[user_id]['generations_used'] += 1
        user_data_store[user_id]['total_generations'] += 1
        
        # Add buttons
        keyboard = [
            [InlineKeyboardButton("🎬 Try Again", callback_data="create_video")],
            [InlineKeyboardButton("📊 My Stats", callback_data="status")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"✅ *Done!*\n\n"
            f"🎯 Total videos created today: {user_data_store[user_id]['generations_used']}/10\n\n"
            "💡 *Want real videos?*\n"
            "• Upgrade to premium for full features!\n"
            "• Contact @your_support for access\n\n"
            "🎬 Use /create to make another video!",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"❌ Video generation error: {str(e)}")
        logger.error(traceback.format_exc())
        await processing_msg.edit_text(
            "❌ *Something went wrong!*\n\n"
            "Please try again in a few moments.\n\n"
            "🔄 Use /create to start over.",
            parse_mode='Markdown'
        )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle general text messages"""
    user_id = update.effective_user.id
    text = update.message.text
    
    # Check if waiting for prompt
    if context.user_data.get('state') == WAITING_FOR_PROMPT:
        await handle_prompt_received(update, context)
        return
    
    # Default response
    await update.message.reply_text(
        f"🤔 I received: *{text[:50]}{'...' if len(text) > 50 else ''}*\n\n"
        "💡 Use /create to make a video or /help for options.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🎬 Create Video", callback_data="create_video")],
            [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
        ]),
        parse_mode='Markdown'
    )

# ============ BUTTON HANDLERS ============

async def handle_button_press(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard buttons"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "create_video":
        await query.edit_message_text(
            "🎬 *Let's Create Your Video!*\n\n"
            "📤 *Step 1:* Please send me a photo\n"
            "• Format: JPG or PNG\n"
            "• Max size: 20MB\n"
            "• Clear face/body preferred\n\n"
            "🔄 Send /cancel to cancel",
            parse_mode='Markdown'
        )
        context.user_data['state'] = WAITING_FOR_IMAGE
        
    elif query.data == "image_to_video":
        await query.edit_message_text(
            "📸 *Image to Video*\n\n"
            "Send me an image and I'll animate it!\n\n"
            "📤 *Please send your image now:*\n"
            "• Format: JPG, PNG\n"
            "• Max size: 20MB\n\n"
            "🔄 Send /cancel to cancel",
            parse_mode='Markdown'
        )
        context.user_data['state'] = WAITING_FOR_IMAGE
        
    elif query.data == "help":
        await query.edit_message_text(
            "📚 *Help Menu*\n\n"
            "*Commands:*\n"
            "/create - Start video creation\n"
            "/status - Check your usage\n"
            "/help - Show this help\n"
            "/cancel - Cancel operation\n\n"
            "*How to use:*\n"
            "1. Upload a photo\n"
            "2. Describe what you want\n"
            "3. Get your video!\n\n"
            "*Example prompts:*\n"
            "• 'Make her say: My name is Ayomide'\n"
            "• 'Dance to a happy song'\n"
            "• 'Create a funny video'",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎬 Create Video", callback_data="create_video")]
            ]),
            parse_mode='Markdown'
        )
        
    elif query.data == "status":
        user_id = update.effective_user.id
        user_data = user_data_store.get(user_id, {'generations_used': 0, 'total_generations': 0})
        
        await query.edit_message_text(
            f"📊 *Your Statistics*\n\n"
            f"• Today: {user_data.get('generations_used', 0)}/10 videos\n"
            f"• Total: {user_data.get('total_generations', 0)} videos\n"
            f"• Status: Active ✅\n\n"
            f"🎯 *Next milestone:* 10 videos = Premium access!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎬 Create Video", callback_data="create_video")]
            ]),
            parse_mode='Markdown'
        )

# ============ ERROR HANDLER ============

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"❌ Update {update} caused error: {context.error}")
    logger.error(traceback.format_exc())
    
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "⚠️ *Oops! Something went wrong.*\n\n"
                "Don't worry, I've logged the error.\n"
                "Please try again or use /help.\n\n"
                "🔄 Use /start to restart.",
                parse_mode='Markdown'
            )
    except Exception as e:
        logger.error(f"Error in error handler: {e}")

# ============ MAIN ============

def main():
    """Start the bot"""
    logger.info("🚀 Starting Bideruibot...")
    
    # Create application
    application = Application.builder().token(TOKEN).build()
    
    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('create', create_command),
            CallbackQueryHandler(handle_button_press, pattern='^create_video$'),
            CallbackQueryHandler(handle_button_press, pattern='^image_to_video$'),
        ],
        states={
            WAITING_FOR_IMAGE: [
                MessageHandler(filters.PHOTO, handle_image_received),
            ],
            WAITING_FOR_PROMPT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_prompt_received),
            ],
        },
        fallbacks=[
            CommandHandler('cancel', cancel_command),
            CommandHandler('start', start_command),
            CommandHandler('help', help_command),
        ],
        allow_reentry=True
    )
    application.add_handler(conv_handler)
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("create", create_command))
    application.add_handler(CommandHandler("cancel", cancel_command))
    
    # Add message handlers
    application.add_handler(MessageHandler(
        filters.PHOTO, 
        handle_image_received
    ))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        handle_text
    ))
    
    # Add button handler
    application.add_handler(CallbackQueryHandler(handle_button_press))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start bot
    logger.info("✅ Bideruibot is running!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
