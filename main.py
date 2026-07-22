import os
import logging
import asyncio
import requests
import json
from datetime import datetime
from typing import Optional, Dict, Any
from io import BytesIO
import tempfile
import shutil
import traceback

# Telegram imports
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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

BOT_USERNAME = "bideruibot"
VERSION = "2.0.0"

# Conversation states
WAITING_FOR_IMAGE = 1
WAITING_FOR_PROMPT = 2
WAITING_FOR_DURATION = 3

# ============ USER DATA ============
user_data_store: Dict[int, Dict[str, Any]] = {}

# ============ MESSAGES ============
START_MESSAGE = """
🎬 *Welcome to Bideruibot v2.0!*

I can turn your images into dancing/singing videos! ✨

*What I can do:*
• 🎭 Animate your photos to dance
• 🎵 Make images sing with audio
• 🎬 Create videos from text prompts

*How to use:*
1. Click "Generate Video" below
2. Upload a photo
3. Describe what you want
4. I'll create your video!

💡 *Example:* "Make her dance like a pop star"
"""

HELP_MESSAGE = """
📚 *Available Commands*

/start - Welcome message
/help - Show this help
/generate - Start image-to-video generation
/status - Check bot status
/about - Bot information
/cancel - Cancel current operation

📸 *Image Requirements:*
• Format: JPG, PNG
• Max size: 20MB
• Clear face/body preferred
"""

# ============ VIDEO GENERATION FUNCTIONS ============

class VideoGenerator:
    """Handles all video generation operations"""
    
    @staticmethod
    async def generate_dancing_video(image_data: bytes, prompt: str, duration: int = 10) -> Optional[str]:
        """
        Generate a dancing video from image
        """
        try:
            logger.info(f"Generating dancing video for prompt: {prompt[:50]}...")
            
            # For testing, return a sample video
            # In production, replace with actual API call
            await asyncio.sleep(3)  # Simulate processing
            
            # Sample video URLs (these work)
            sample_videos = [
                "https://sample-videos.com/video321/mp4/720/big_buck_bunny_720p_1mb.mp4",
                "https://sample-videos.com/video321/mp4/720/big_buck_bunny_720p_2mb.mp4",
            ]
            import random
            return random.choice(sample_videos)
                
        except Exception as e:
            logger.error(f"Video generation error: {str(e)}")
            logger.error(traceback.format_exc())
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
        [InlineKeyboardButton("🎬 Generate Video", callback_data="generate")],
        [InlineKeyboardButton("📸 Image to Video", callback_data="image_to_video")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"👋 Hi {user.first_name}!\n\n{START_MESSAGE}",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    keyboard = [
        [InlineKeyboardButton("🎬 Generate Now", callback_data="generate")],
        [InlineKeyboardButton("📸 Image to Video", callback_data="image_to_video")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        HELP_MESSAGE,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /about command"""
    await update.message.reply_text(
        f"""
🎬 *Bideruibot v{VERSION}*

Advanced AI bot for image-to-video generation.

*Features:*
• 🎭 Dancing animations
• 🎵 Singing avatars
• 🎨 Style transfer
• ⚡ Fast processing

*Tech Stack:*
• Python 3.11
• python-telegram-bot
• AI animation models
• Railway hosting

Made with ❤️ for creators
""",
        parse_mode='Markdown'
    )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command"""
    user_id = update.effective_user.id
    user_data = user_data_store.get(user_id, {'generations_used': 0})
    
    status_text = f"""
🟢 *Bot Status: Online*

📊 *Your Stats:*
• Today's Generations: {user_data.get('generations_used', 0)}/10
• Total Generations: {user_data.get('total_generations', 0)}
• Joined: {user_data.get('joined', datetime.now()).strftime('%Y-%m-%d')}

🎯 *Features Available:*
• Image to video: ✅
• Dancing animation: ✅
• Singing avatars: ✅

⚡ *Status: Ready to generate!*
"""
    
    await update.message.reply_text(
        status_text,
        parse_mode='Markdown'
    )

async def generate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /generate command"""
    keyboard = [
        [InlineKeyboardButton("📸 Image to Dancing Video", callback_data="image_to_video")],
        [InlineKeyboardButton("🎵 Image to Singing Video", callback_data="singing_video")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎬 *Video Generation*\n\n"
        "Please choose what you want to generate:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /cancel command"""
    # Clear conversation state
    if 'conversation' in context.user_data:
        context.user_data['conversation'] = None
    if 'state' in context.user_data:
        context.user_data['state'] = None
    
    await update.message.reply_text(
        "✅ *Operation Cancelled*\n\n"
        "You can start a new generation anytime with /generate",
        parse_mode='Markdown'
    )

# ============ IMAGE HANDLING ============

async def image_to_video_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start image to video process"""
    query = update.callback_query
    await query.answer()
    
    # Set conversation state
    context.user_data['state'] = WAITING_FOR_IMAGE
    context.user_data['generation_type'] = 'dancing'
    
    await query.edit_message_text(
        "📸 *Image to Video Generation*\n\n"
        "1️⃣ *Send me a photo* of a person or character\n"
        "2️⃣ I'll make them dance and sing!\n\n"
        "📤 *Please send your image now:*\n"
        "• Format: JPG, PNG\n"
        "• Max size: 20MB\n"
        "• Clear face/body required\n\n"
        "🔄 Send /cancel to cancel",
        parse_mode='Markdown'
    )

async def singing_video_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start singing video process"""
    query = update.callback_query
    await query.answer()
    
    # Set conversation state
    context.user_data['state'] = WAITING_FOR_IMAGE
    context.user_data['generation_type'] = 'singing'
    
    await query.edit_message_text(
        "🎵 *Singing Video Generation*\n\n"
        "1️⃣ *Send me a photo* of a person\n"
        "2️⃣ Describe what you want them to sing\n"
        "3️⃣ I'll create a singing avatar!\n\n"
        "📤 *Please send your image now:*\n"
        "• Clear face photo\n"
        "• JPG or PNG format\n\n"
        "🔄 Send /cancel to cancel",
        parse_mode='Markdown'
    )

async def handle_image_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle image upload for video generation"""
    user_id = update.effective_user.id
    
    logger.info(f"Image received from user {user_id}")
    
    # Check if we're expecting an image
    state = context.user_data.get('state')
    logger.info(f"Current state: {state}")
    
    if state != WAITING_FOR_IMAGE:
        logger.info("Not in WAITING_FOR_IMAGE state, sending help")
        await update.message.reply_text(
            "🤔 Use /generate to start a new video creation!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎬 Generate Video", callback_data="generate")]
            ])
        )
        return
    
    try:
        # Get the image
        photo = update.message.photo[-1]  # Get largest size
        file = await photo.get_file()
        
        logger.info(f"Downloading image: {file.file_id}")
        image_bytes = await file.download_as_bytearray()
        
        # Save image data in context
        context.user_data['image_data'] = image_bytes
        
        # Update state to wait for prompt
        context.user_data['state'] = WAITING_FOR_PROMPT
        generation_type = context.user_data.get('generation_type', 'dancing')
        
        # Ask for prompt
        if generation_type == 'dancing':
            await update.message.reply_text(
                "✅ *Image Received!*\n\n"
                "Now describe how you want them to dance:\n\n"
                "💃 *Examples:*\n"
                "• 'Dance like a pop star'\n"
                "• 'Breakdance moves'\n"
                "• 'Ballet dancing elegantly'\n\n"
                "⌨️ Send your description now:",
                parse_mode='Markdown'
            )
        else:  # singing
            await update.message.reply_text(
                "✅ *Image Received!*\n\n"
                "Now describe what you want them to sing:\n\n"
                "🎵 *Examples:*\n"
                "• 'Sing a pop song'\n"
                "• 'Sing happy birthday'\n"
                "• 'Sing a romantic ballad'\n\n"
                "⌨️ Send your description now:",
                parse_mode='Markdown'
            )
            
    except Exception as e:
        logger.error(f"Error handling image: {str(e)}")
        logger.error(traceback.format_exc())
        await update.message.reply_text(
            "❌ *Error Processing Image*\n\n"
            "Please try again with a different image.\n"
            "Make sure it's a JPG or PNG file under 20MB.",
            parse_mode='Markdown'
        )

async def handle_prompt_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the prompt for video generation"""
    user_id = update.effective_user.id
    prompt = update.message.text
    
    logger.info(f"Prompt received from user {user_id}: {prompt[:50]}...")
    
    # Check if we're expecting a prompt
    state = context.user_data.get('state')
    if state != WAITING_FOR_PROMPT:
        await update.message.reply_text(
            "🤔 Use /generate to start a new video creation!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎬 Generate Video", callback_data="generate")]
            ])
        )
        return
    
    if len(prompt.strip()) < 3:
        await update.message.reply_text(
            "⚠️ Please provide a more detailed description (at least 3 characters)!",
            parse_mode='Markdown'
        )
        return
    
    # Get generation type and image
    generation_type = context.user_data.get('generation_type', 'dancing')
    image_data = context.user_data.get('image_data')
    
    if not image_data:
        await update.message.reply_text(
            "❌ *Image data not found*\n\n"
            "Please start over with /generate",
            parse_mode='Markdown'
        )
        context.user_data['state'] = None
        return
    
    # Clear state immediately to prevent duplicate processing
    context.user_data['state'] = None
    context.user_data['processing'] = True
    
    # Show processing message
    processing_msg = await update.message.reply_text(
        f"🎬 *Generating Video...*\n\n"
        f"Type: {'Dancing' if generation_type == 'dancing' else 'Singing'}\n"
        f"Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}\n\n"
        "⏳ This will take 30-60 seconds...\n"
        "Please wait while I create your masterpiece!",
        parse_mode='Markdown'
    )
    
    try:
        # Show typing indicator
        await update.message.chat.send_action(action="upload_video")
        
        # Generate video
        video_url = await VideoGenerator.generate_dancing_video(
            image_data, 
            prompt, 
            duration=10
        )
        
        if video_url:
            # Update user data
            if user_id not in user_data_store:
                user_data_store[user_id] = {'generations_used': 0, 'total_generations': 0}
            
            user_data_store[user_id]['generations_used'] += 1
            user_data_store[user_id]['total_generations'] += 1
            
            # Send the video
            keyboard = [
                [InlineKeyboardButton("🎬 Generate Another", callback_data="generate")],
                [InlineKeyboardButton("📊 Check Status", callback_data="status")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_video(
                video=video_url,
                caption=f"✅ *Video Generated Successfully!*\n\n"
                        f"🎯 {generation_type.title()} animation\n"
                        f"📝 Prompt: {prompt[:200]}{'...' if len(prompt) > 200 else ''}\n\n"
                        f"📊 {user_data_store[user_id]['generations_used']}/10 free generations used today",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            await processing_msg.delete()
            
        else:
            await processing_msg.edit_text(
                "❌ *Generation Failed*\n\n"
                "I couldn't generate the video at this moment.\n\n"
                "🔧 *Possible reasons:*\n"
                "• Service temporarily unavailable\n"
                "• Try again with a different image\n"
                "• Try a different prompt\n\n"
                "🔄 Use /generate to try again.",
                parse_mode='Markdown'
            )
            
    except Exception as e:
        logger.error(f"Video generation error: {str(e)}")
        logger.error(traceback.format_exc())
        await processing_msg.edit_text(
            "⚠️ *An Error Occurred*\n\n"
            "Please try again later or use /help for assistance.\n\n"
            "🔄 Use /generate to start over.",
            parse_mode='Markdown'
        )
    
    finally:
        # Clear processing flag
        context.user_data['processing'] = False
        # Clear image data to free memory
        context.user_data['image_data'] = None

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle general text messages"""
    message_text = update.message.text
    
    # Check if in generation flow
    state = context.user_data.get('state')
    if state == WAITING_FOR_PROMPT:
        # This is handled by the conversation handler
        return await handle_prompt_received(update, context)
    
    # Check if processing
    if context.user_data.get('processing', False):
        await update.message.reply_text(
            "⏳ *Please wait...*\n\n"
            "I'm currently generating a video for you.\n"
            "It will be ready in a few moments!",
            parse_mode='Markdown'
        )
        return
    
    # Generic response with buttons
    keyboard = [
        [InlineKeyboardButton("🎬 Generate Video", callback_data="generate")],
        [InlineKeyboardButton("📸 Image to Video", callback_data="image_to_video")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🤔 I received: *{message_text[:50]}{'...' if len(message_text) > 50 else ''}*\n\n"
        "💡 Try these commands:\n"
        "• /generate - Create a video\n"
        "• /status - Check your limits\n\n"
        "Or use the buttons below!",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# ============ BUTTON HANDLERS ============

async def handle_button_press(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard button presses"""
    query = update.callback_query
    await query.answer()
    
    try:
        if query.data == "generate":
            await generate_command(update, context)
            
        elif query.data == "image_to_video":
            await image_to_video_start(update, context)
            
        elif query.data == "singing_video":
            await singing_video_start(update, context)
            
        elif query.data == "help":
            await help_command(update, context)
            
        elif query.data == "status":
            await status_command(update, context)
            
        elif query.data == "cancel":
            context.user_data['state'] = None
            context.user_data['image_data'] = None
            await query.edit_message_text(
                "✅ *Operation Cancelled*\n\n"
                "You can start a new generation anytime with /generate",
                parse_mode='Markdown'
            )
            
    except Exception as e:
        logger.error(f"Button handler error: {str(e)}")
        logger.error(traceback.format_exc())
        await query.edit_message_text(
            "❌ *Error*\n\n"
            "Something went wrong. Please try /start again.",
            parse_mode='Markdown'
        )

# ============ ERROR HANDLER ============

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error: {context.error}")
    logger.error(traceback.format_exc())
    
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "⚠️ *Something went wrong!*\n\n"
                "Please try again or use /help for assistance.\n\n"
                "🔄 Use /start to restart the bot.",
                parse_mode='Markdown'
            )
    except Exception as e:
        logger.error(f"Error in error handler: {e}")

# ============ MAIN FUNCTION ============

def main():
    """Start the bot"""
    logger.info("🚀 Starting Bideruibot v2.0...")
    
    # Create application
    application = Application.builder().token(TOKEN).build()
    
    # Create conversation handler
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('generate', generate_command),
            CallbackQueryHandler(image_to_video_start, pattern='^image_to_video$'),
            CallbackQueryHandler(singing_video_start, pattern='^singing_video$'),
        ],
        states={
            WAITING_FOR_IMAGE: [
                MessageHandler(filters.PHOTO, handle_image_received),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text),
            ],
            WAITING_FOR_PROMPT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_prompt_received),
            ],
        },
        fallbacks=[
            CommandHandler('cancel', cancel_command),
            CommandHandler('start', start_command),
            CommandHandler('help', help_command),
            CallbackQueryHandler(lambda u, c: None, pattern='^cancel$'),
        ],
        per_message=False,
        allow_reentry=True
    )
    
    application.add_handler(conv_handler)
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("cancel", cancel_command))
    
    # Add message handlers for non-conversation states
    application.add_handler(MessageHandler(
        filters.PHOTO, 
        handle_image_received
    ))
    
    # Add button handler for all callback queries
    application.add_handler(CallbackQueryHandler(handle_button_press))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start bot
    logger.info("✅ Bideruibot is running! Waiting for users...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
