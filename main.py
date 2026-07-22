import os
import logging
import sys
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any

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

# Bot configuration
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    logger.error("❌ TELEGRAM_BOT_TOKEN not found in environment variables!")
    sys.exit(1)

BOT_USERNAME = "bideruibot"
VERSION = "1.0.0"

# Conversation states
WAITING_FOR_PROMPT = 1

# Default messages
START_MESSAGE = """
🎬 *Welcome to Bideruibot!*

Your AI-powered video generation assistant. I can help you create amazing videos from text descriptions.

✨ *What I can do:*
• 🎥 Generate videos from text prompts
• 🎨 Create AI art and animations
• 📹 Convert images to video
• ✂️ Edit and enhance existing content

💡 *Quick Start:* Just send me a description of what you want to create!

*Example:* "A futuristic city at sunset with flying cars and neon lights"

---

🤖 *Commands:* /help to see all options
"""

HELP_MESSAGE = """
📚 *Available Commands*

/start - Welcome message and introduction
/help - Show this help menu
/generate - Start video generation
/status - Check bot status and usage limits
/about - Learn more about this bot
/cancel - Cancel current operation

🔧 *How to use:*
1. Send /generate
2. Describe your video in detail
3. Wait for generation (30-60 seconds)
4. Download your video!

💡 *Tips for better results:*
• Be specific in your descriptions
• Include style preferences (cinematic, anime, realistic)
• Mention colors, mood, and atmosphere
• Keep prompts between 10-100 words

📊 *Daily Limits:* 10 free generations
"""

ABOUT_MESSAGE = f"""
🎬 *Bideruibot v{VERSION}*

An intelligent Telegram bot that creates stunning videos using cutting-edge AI technology.

🛠️ *Technical Stack:*
• Python 3.11 with python-telegram-bot
• Railway for hosting and deployment
• GitHub for version control
• AI video generation models

👨‍💻 *Developer:* Your Name Here
📧 *Support:* support@bideruibot.com
🌐 *Website:* https://bideruibot.com

💖 *Made with love for content creators worldwide*
"""

STATUS_MESSAGE = """
🟢 *Bot Status: Online*

📊 *System Information:*
• Version: {version}
• Uptime: {uptime}
• Active Users: {users}

🎯 *Daily Limits:*
• Free Generations: {free_gens_used}/{free_gens_max}
• Premium Generations: {premium_gens_used}/{premium_gens_max}

⚡ *Performance:*
• Average Response Time: {avg_time}ms
• Success Rate: {success_rate}%

🔒 *Security:* All data encrypted in transit
"""

# Track user data (in production, use a database)
user_data_store: Dict[int, Dict[str, Any]] = {}

class VideoGenerator:
    """Handles video generation logic"""
    
    @staticmethod
    async def generate_from_prompt(prompt: str) -> Optional[str]:
        """
        Generate video from text prompt.
        Replace this with actual AI API integration.
        """
        try:
            logger.info(f"Generating video for prompt: {prompt[:50]}...")
            
            # Simulate processing time
            await asyncio.sleep(3)
            
            # Placeholder: In production, call your AI API here
            # Example: return await call_kling_api(prompt)
            
            # For testing, return a sample video URL
            sample_videos = [
                "https://sample-videos.com/video321/mp4/720/big_buck_bunny_720p_1mb.mp4",
                "https://sample-videos.com/video321/mp4/720/big_buck_bunny_720p_2mb.mp4",
                "https://sample-videos.com/video321/mp4/720/big_buck_bunny_720p_5mb.mp4"
            ]
            
            import random
            return random.choice(sample_videos)
            
        except Exception as e:
            logger.error(f"Video generation error: {str(e)}")
            return None

    @staticmethod
    async def call_kling_api(prompt: str) -> Optional[str]:
        """Example: Integration with Kling AI API"""
        import requests
        import json
        
        api_key = os.environ.get('KLING_API_KEY')
        if not api_key:
            logger.warning("KLING_API_KEY not set, using fallback")
            return None
            
        try:
            response = requests.post(
                "https://api.klingai.com/v1/videos/generations",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "prompt": prompt,
                    "duration": 5,
                    "aspect_ratio": "16:9",
                    "style": "cinematic"
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', {}).get('video_url')
            else:
                logger.error(f"API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"API call error: {str(e)}")
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
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")],
        [InlineKeyboardButton("📊 Status", callback_data="status")]
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
        [InlineKeyboardButton("📊 Check Status", callback_data="status")]
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
        ABOUT_MESSAGE,
        parse_mode='Markdown'
    )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command"""
    user_id = update.effective_user.id
    user_data = user_data_store.get(user_id, {'generations_used': 0})
    
    status_text = STATUS_MESSAGE.format(
        version=VERSION,
        uptime="3h 45m",  # In production, track actual uptime
        users=len(user_data_store),
        free_gens_used=user_data['generations_used'],
        free_gens_max=10,
        premium_gens_used=0,
        premium_gens_max=0,
        avg_time="450",
        success_rate="98.5%"
    )
    
    await update.message.reply_text(
        status_text,
        parse_mode='Markdown'
    )

async def generate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /generate command - start video generation flow"""
    user_id = update.effective_user.id
    
    # Check limits
    user_data = user_data_store.get(user_id, {})
    if user_data.get('generations_used', 0) >= 10:
        await update.message.reply_text(
            "⚠️ *Daily Limit Reached*\n\n"
            "You've used all 10 free generations for today.\n"
            "Please try again tomorrow or contact us for premium access.\n\n"
            "🔄 Premium features coming soon!",
            parse_mode='Markdown'
        )
        return
    
    await update.message.reply_text(
        "🎬 *Let's Create Your Video!*\n\n"
        "Please describe the video you want to create in detail.\n\n"
        "📝 *Include these details for best results:*\n"
        "• Main subject or scene\n"
        "• Style (cinematic, anime, realistic)\n"
        "• Mood or atmosphere\n"
        "• Colors and lighting\n\n"
        "✨ *Example:* 'A cinematic sunset over a futuristic cyberpunk city with flying cars, neon lights reflecting on wet streets, dramatic lighting'\n\n"
        "⏱️ Generation takes 30-60 seconds\n"
        "🔄 Type /cancel to cancel",
        parse_mode='Markdown'
    )
    
    # Set conversation state
    context.user_data['state'] = WAITING_FOR_PROMPT
    return WAITING_FOR_PROMPT

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /cancel command"""
    if context.user_data.get('state') == WAITING_FOR_PROMPT:
        context.user_data['state'] = None
        await update.message.reply_text(
            "✅ *Operation Cancelled*\n\n"
            "You can start a new generation anytime with /generate",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "ℹ️ No active operation to cancel.\n"
            "Use /generate to create a video!"
        )

# ============ MESSAGE HANDLERS ============

async def handle_video_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the video prompt from user"""
    user_id = update.effective_user.id
    prompt = update.message.text
    
    # Validate prompt
    if len(prompt.strip()) < 5:
        await update.message.reply_text(
            "⚠️ *Please provide a more detailed description.*\n\n"
            "Your prompt should be at least 5 characters long.\n"
            "Try including more details about the scene, style, and mood.\n\n"
            "Type /cancel to cancel",
            parse_mode='Markdown'
        )
        return WAITING_FOR_PROMPT
    
    # Clear the state
    context.user_data['state'] = None
    
    # Send processing message
    processing_msg = await update.message.reply_text(
        f"🎬 *Generating Your Video...*\n\n"
        f"📝 *Prompt:* {prompt[:100]}{'...' if len(prompt) > 100 else ''}\n\n"
        "⏳ This will take 30-60 seconds...\n"
        "Please wait while I create your masterpiece!",
        parse_mode='Markdown'
    )
    
    try:
        # Show typing indicator
        await update.message.chat.send_action(action="upload_video")
        
        # Generate the video
        video_url = await VideoGenerator.generate_from_prompt(prompt)
        
        if video_url:
            # Update user data
            if user_id in user_data_store:
                user_data_store[user_id]['generations_used'] += 1
                user_data_store[user_id]['total_generations'] += 1
            
            # Send video
            keyboard = [
                [InlineKeyboardButton("🎬 Generate Another", callback_data="generate")],
                [InlineKeyboardButton("📊 Check Status", callback_data="status")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_video(
                video=video_url,
                caption=f"✅ *Video Generated Successfully!*\n\n"
                        f"🎯 *Prompt:* {prompt[:200]}{'...' if len(prompt) > 200 else ''}\n\n"
                        f"🎬 Enjoy your creation!\n"
                        f"📊 {user_data_store[user_id]['generations_used']}/10 free generations used today",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            await processing_msg.delete()
            
        else:
            await processing_msg.edit_text(
                "❌ *Generation Failed*\n\n"
                "I couldn't generate your video at this moment.\n\n"
                "🔧 *Possible reasons:*\n"
                "• Service temporarily unavailable\n"
                "• Invalid prompt format\n"
                "• Rate limits exceeded\n\n"
                "🔄 Try again in a few minutes or try a different prompt.\n"
                "Use /help for assistance.",
                parse_mode='Markdown'
            )
            
    except Exception as e:
        logger.error(f"Error in video generation: {str(e)}")
        await processing_msg.edit_text(
            "⚠️ *An Unexpected Error Occurred*\n\n"
            "Please try again later.\n\n"
            "If the problem persists, contact support.\n"
            "Use /help for more options.",
            parse_mode='Markdown'
        )
    
    return ConversationHandler.END

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle general text messages"""
    message_text = update.message.text
    
    # Check if in generation flow
    if context.user_data.get('state') == WAITING_FOR_PROMPT:
        return await handle_video_prompt(update, context)
    
    # Generic response
    keyboard = [
        [InlineKeyboardButton("🎬 Generate Video", callback_data="generate")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🤔 I received: *{message_text[:50]}{'...' if len(message_text) > 50 else ''}*\n\n"
        "I'm not sure what you want me to do with that.\n\n"
        "💡 Try one of these commands:\n"
        "• /generate - Create a video\n"
        "• /help - See all options\n"
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
    
    if query.data == "generate":
        await query.edit_message_text(
            "🎬 *Starting Video Generation...*\n\n"
            "Please describe what video you want to create.\n"
            "Be specific for the best results!\n\n"
            "💡 *Tips:*\n"
            "• Describe the scene in detail\n"
            "• Include style and mood\n"
            "• Mention colors and atmosphere\n\n"
            "🔄 Type /cancel to cancel",
            parse_mode='Markdown'
        )
        context.user_data['state'] = WAITING_FOR_PROMPT
        
    elif query.data == "help":
        await query.edit_message_text(
            HELP_MESSAGE,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎬 Generate Now", callback_data="generate")],
                [InlineKeyboardButton("📊 Check Status", callback_data="status")]
            ]),
            parse_mode='Markdown'
        )
        
    elif query.data == "status":
        user_id = update.effective_user.id
        user_data = user_data_store.get(user_id, {'generations_used': 0})
        
        status_text = STATUS_MESSAGE.format(
            version=VERSION,
            uptime="3h 45m",
            users=len(user_data_store),
            free_gens_used=user_data['generations_used'],
            free_gens_max=10,
            premium_gens_used=0,
            premium_gens_max=0,
            avg_time="450",
            success_rate="98.5%"
        )
        
        await query.edit_message_text(
            status_text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎬 Generate Video", callback_data="generate")],
                [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
            ]),
            parse_mode='Markdown'
        )

# ============ ERROR HANDLER ============

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error: {context.error}")
    
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "⚠️ *Something went wrong!*\n\n"
                "I've logged the error and will fix it.\n"
                "Please try again or use /help for assistance.\n\n"
                "🔄 If the problem persists, try restarting the bot.",
                parse_mode='Markdown'
            )
    except Exception as e:
        logger.error(f"Error in error handler: {e}")

# ============ MAIN FUNCTION ============

def main():
    """Start the bot"""
    logger.info("🚀 Starting Bideruibot...")
    
    # Create application
    application = Application.builder().token(TOKEN).build()
    
    # Add conversation handler for video generation
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('generate', generate_command),
            CallbackQueryHandler(handle_button_press, pattern='^generate$')
        ],
        states={
            WAITING_FOR_PROMPT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_video_prompt)
            ]
        },
        fallbacks=[
            CommandHandler('cancel', cancel_command),
            CommandHandler('start', start_command),
            CommandHandler('help', help_command)
        ],
        allow_reentry=True
    )
    application.add_handler(conv_handler)
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("cancel", cancel_command))
    
    # Add message handlers
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
