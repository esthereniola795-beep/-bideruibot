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

BOT_USERNAME = "bideruibot"
VERSION = "2.0.0"

# Conversation states
WAITING_FOR_IMAGE = 1
WAITING_FOR_PROMPT = 2
WAITING_FOR_DURATION = 3

# API Keys (Optional - for actual video generation)
KLING_API_KEY = os.environ.get('KLING_API_KEY', '')
RUNWAY_API_KEY = os.environ.get('RUNWAY_API_KEY', '')
REPLICATE_API_TOKEN = os.environ.get('REPLICATE_API_TOKEN', '')

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
• 🎨 AI-powered video generation

*How to use:*
1. Send /generate to start
2. Upload a photo
3. Describe what you want
4. I'll create your video!

💡 *Example:* "Make her dance and sing"
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
• Format: JPG, PNG, GIF
• Max size: 20MB
• Resolution: Minimum 512x512

🎬 *Features:*
• Image animation
• Dancing effects
• Singing/voice sync
• Custom duration

💡 *Pro Tip:* Be specific in your prompts!
"""

ABOUT_MESSAGE = f"""
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
"""

# ============ VIDEO GENERATION FUNCTIONS ============

class VideoGenerator:
    """Handles all video generation operations"""
    
    @staticmethod
    async def generate_dancing_video(image_data: bytes, prompt: str, duration: int = 10) -> Optional[str]:
        """
        Generate a dancing video from image
        Replace this with actual API integration
        """
        try:
            logger.info(f"Generating dancing video for prompt: {prompt[:50]}...")
            
            # Option 1: Use Kling AI API
            if KLING_API_KEY:
                return await VideoGenerator._kling_image_to_video(image_data, prompt, duration)
            
            # Option 2: Use Replicate API
            elif REPLICATE_API_TOKEN:
                return await VideoGenerator._replicate_image_to_video(image_data, prompt, duration)
            
            # Option 3: Use Runway API
            elif RUNWAY_API_KEY:
                return await VideoGenerator._runway_image_to_video(image_data, prompt, duration)
            
            # Fallback: Simulate generation (for testing)
            else:
                # For testing, return a sample dancing video
                sample_videos = [
                    "https://sample-videos.com/video321/mp4/720/big_buck_bunny_720p_1mb.mp4",
                    "https://sample-videos.com/video321/mp4/720/big_buck_bunny_720p_2mb.mp4",
                ]
                import random
                await asyncio.sleep(5)  # Simulate processing
                return random.choice(sample_videos)
                
        except Exception as e:
            logger.error(f"Video generation error: {str(e)}")
            return None

    @staticmethod
    async def _kling_image_to_video(image_data: bytes, prompt: str, duration: int) -> Optional[str]:
        """Generate video using Kling AI API"""
        try:
            import requests
            import base64
            
            # Encode image to base64
            img_b64 = base64.b64encode(image_data).decode('utf-8')
            
            # Kling API endpoint
            url = "https://api.klingai.com/v1/videos/image-to-video"
            
            headers = {
                "Authorization": f"Bearer {KLING_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "image": img_b64,
                "prompt": prompt,
                "duration": duration,
                "style": "dancing",
                "motion": "animate"
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=120)
            
            if response.status_code == 200:
                data = response.json()
                video_url = data.get('data', {}).get('video_url')
                if video_url:
                    return video_url
            
            logger.error(f"Kling API error: {response.status_code} - {response.text}")
            return None
            
        except Exception as e:
            logger.error(f"Kling API error: {str(e)}")
            return None

    @staticmethod
    async def _replicate_image_to_video(image_data: bytes, prompt: str, duration: int) -> Optional[str]:
        """Generate video using Replicate API"""
        try:
            import requests
            import base64
            
            img_b64 = base64.b64encode(image_data).decode('utf-8')
            
            # Replicate API endpoint for image-to-video
            url = "https://api.replicate.com/v1/predictions"
            
            headers = {
                "Authorization": f"Token {REPLICATE_API_TOKEN}",
                "Content-Type": "application/json"
            }
            
            # Use a popular image-to-video model on Replicate
            payload = {
                "version": "stability-ai/stable-video-diffusion",
                "input": {
                    "image": f"data:image/jpeg;base64,{img_b64}",
                    "prompt": prompt,
                    "motion_bucket_id": 127,
                    "frames_per_second": 6,
                    "num_frames": 25
                }
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            
            if response.status_code == 201:
                data = response.json()
                prediction_id = data.get('id')
                
                # Poll for completion
                status_url = f"https://api.replicate.com/v1/predictions/{prediction_id}"
                
                for _ in range(30):  # Wait up to 2 minutes
                    await asyncio.sleep(4)
                    status_response = requests.get(status_url, headers=headers)
                    status_data = status_response.json()
                    
                    if status_data.get('status') == 'succeeded':
                        video_url = status_data.get('output', {}).get('video')
                        return video_url
                    elif status_data.get('status') == 'failed':
                        logger.error(f"Replicate prediction failed: {status_data}")
                        return None
            
            return None
            
        except Exception as e:
            logger.error(f"Replicate API error: {str(e)}")
            return None

    @staticmethod
    async def _runway_image_to_video(image_data: bytes, prompt: str, duration: int) -> Optional[str]:
        """Generate video using Runway API"""
        try:
            import requests
            import base64
            
            img_b64 = base64.b64encode(image_data).decode('utf-8')
            
            url = "https://api.runwayml.com/v1/image_to_video"
            
            headers = {
                "Authorization": f"Bearer {RUNWAY_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "image": img_b64,
                "prompt": f"{prompt}, dancing, singing, animated",
                "duration": duration
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=120)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('video_url')
            
            return None
            
        except Exception as e:
            logger.error(f"Runway API error: {str(e)}")
            return None

    @staticmethod
    async def generate_singing_video(image_data: bytes, song_prompt: str, duration: int = 10) -> Optional[str]:
        """
        Generate video with singing/animated lipsync
        """
        try:
            logger.info(f"Generating singing video with prompt: {song_prompt[:50]}...")
            
            # Combine singing prompt with dancing
            full_prompt = f"{song_prompt}, singing, lip sync, expressive, animated, dancing"
            
            # Use the same generation function with singing prompt
            return await VideoGenerator.generate_dancing_video(image_data, full_prompt, duration)
            
        except Exception as e:
            logger.error(f"Singing video error: {str(e)}")
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
        ABOUT_MESSAGE,
        parse_mode='Markdown'
    )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command"""
    user_id = update.effective_user.id
    user_data = user_data_store.get(user_id, {'generations_used': 0})
    
    status_text = f"""
🟢 *Bot Status: Online*

📊 *Your Stats:*
• Today's Generations: {user_data['generations_used']}/10
• Total Generations: {user_data['total_generations']}
• Joined: {user_data.get('joined', datetime.now()).strftime('%Y-%m-%d')}

🎯 *Features:*
• Image to video: ✅
• Dancing animation: ✅
• Singing avatars: ✅
• Text to video: ✅

⚡ *API Status:*
• Kling AI: {'✅' if KLING_API_KEY else '❌'}
• Replicate: {'✅' if REPLICATE_API_TOKEN else '❌'}
• Runway: {'✅' if RUNWAY_API_KEY else '❌'}
"""
    
    await update.message.reply_text(
        status_text,
        parse_mode='Markdown'
    )

async def generate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /generate command"""
    await update.message.reply_text(
        "🎬 *Video Generation*\n\n"
        "Please choose what you want to generate:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📸 Image to Dancing Video", callback_data="image_to_video")],
            [InlineKeyboardButton("🎵 Image to Singing Video", callback_data="singing_video")],
            [InlineKeyboardButton("🎨 Text to Video", callback_data="text_to_video")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
        ]),
        parse_mode='Markdown'
    )

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /cancel command"""
    if context.user_data.get('state'):
        context.user_data['state'] = None
        await update.message.reply_text(
            "✅ *Operation Cancelled*\n\n"
            "You can start a new generation anytime with /generate",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "ℹ️ No active operation to cancel."
        )

# ============ IMAGE HANDLING ============

async def handle_image_to_video_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start image to video process"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "📸 *Image to Video Generation*\n\n"
        "1. Send me a photo of a person or character\n"
        "2. I'll make them dance and sing!\n\n"
        "📤 *Please send your image:*\n"
        "• Format: JPG, PNG\n"
        "• Max size: 20MB\n"
        "• Clear face/body required\n\n"
        "🔄 Send /cancel to cancel",
        parse_mode='Markdown'
    )
    
    context.user_data['state'] = WAITING_FOR_IMAGE
    context.user_data['generation_type'] = 'dancing'

async def handle_singing_video_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start singing video process"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "🎵 *Singing Video Generation*\n\n"
        "1. Send me a photo\n"
        "2. Describe what you want them to sing\n"
        "3. I'll create a singing avatar!\n\n"
        "📤 *Send your image first:*\n"
        "• Clear face photo\n"
        "• JPG or PNG format\n\n"
        "🔄 Send /cancel to cancel",
        parse_mode='Markdown'
    )
    
    context.user_data['state'] = WAITING_FOR_IMAGE
    context.user_data['generation_type'] = 'singing'

async def handle_text_to_video_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start text to video process"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "🎨 *Text to Video Generation*\n\n"
        "Describe what video you want to create!\n\n"
        "📝 *Example:*\n"
        '"A beautiful sunset over a futuristic city with flying cars"\n\n'
        "💡 Be specific for best results!\n"
        "• Include style, mood, colors\n"
        "• Add movement descriptions\n\n"
        "🔄 Send /cancel to cancel",
        parse_mode='Markdown'
    )
    
    context.user_data['state'] = WAITING_FOR_PROMPT
    context.user_data['generation_type'] = 'text'

async def handle_image_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle image upload for video generation"""
    user_id = update.effective_user.id
    state = context.user_data.get('state')
    
    if state != WAITING_FOR_IMAGE:
        await update.message.reply_text(
            "🤔 Use /generate to start a new video creation!"
        )
        return
    
    # Check daily limit
    if user_data_store[user_id]['generations_used'] >= 10:
        await update.message.reply_text(
            "⚠️ *Daily Limit Reached*\n\n"
            "You've used all 10 free generations today.\n"
            "Please try again tomorrow!",
            parse_mode='Markdown'
        )
        context.user_data['state'] = None
        return
    
    # Get the image
    photo = update.message.photo[-1]  # Get largest size
    file = await photo.get_file()
    
    # Download image
    image_bytes = await file.download_as_bytearray()
    
    # Save image for processing
    temp_dir = tempfile.mkdtemp()
    image_path = os.path.join(temp_dir, f"{user_id}_image.jpg")
    
    with open(image_path, 'wb') as f:
        f.write(image_bytes)
    
    # Ask for prompt/duration
    generation_type = context.user_data.get('generation_type', 'dancing')
    
    if generation_type == 'dancing':
        await update.message.reply_text(
            "✅ *Image Received!*\n\n"
            "Now describe how you want them to dance:\n\n"
            "💃 *Examples:*\n"
            "• 'Dance like a pop star'\n"
            "• 'Breakdance moves'\n"
            "• 'Ballet dancing elegantly'\n\n"
            "⌨️ Send your description",
            parse_mode='Markdown'
        )
        context.user_data['image_data'] = image_bytes
        context.user_data['state'] = WAITING_FOR_PROMPT
        context.user_data['image_path'] = image_path
        
    elif generation_type == 'singing':
        await update.message.reply_text(
            "✅ *Image Received!*\n\n"
            "Now describe what song or lyrics you want them to sing:\n\n"
            "🎵 *Examples:*\n"
            "• 'Sing a pop song'\n"
            "• 'Sing happy birthday'\n"
            "• 'Sing a romantic ballad'\n\n"
            "⌨️ Send your description",
            parse_mode='Markdown'
        )
        context.user_data['image_data'] = image_bytes
        context.user_data['state'] = WAITING_FOR_PROMPT
        context.user_data['image_path'] = image_path

async def handle_prompt_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the prompt for video generation"""
    user_id = update.effective_user.id
    prompt = update.message.text
    
    if len(prompt.strip()) < 3:
        await update.message.reply_text(
            "⚠️ Please provide a more detailed description!",
            parse_mode='Markdown'
        )
        return WAITING_FOR_PROMPT
    
    # Get generation type and image
    generation_type = context.user_data.get('generation_type', 'dancing')
    image_data = context.user_data.get('image_data')
    image_path = context.user_data.get('image_path')
    
    # Clear state
    context.user_data['state'] = None
    
    # Show processing
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
        video_url = None
        
        if generation_type == 'dancing':
            video_url = await VideoGenerator.generate_dancing_video(
                image_data, 
                prompt, 
                duration=10
            )
        elif generation_type == 'singing':
            video_url = await VideoGenerator.generate_singing_video(
                image_data, 
                prompt, 
                duration=10
            )
        elif generation_type == 'text':
            # Text to video
            video_url = await VideoGenerator.generate_dancing_video(
                b"",  # No image
                prompt,
                duration=10
            )
        
        # Clean up temp file
        if image_path and os.path.exists(image_path):
            os.remove(image_path)
        if image_path:
            os.rmdir(os.path.dirname(image_path))
        
        if video_url:
            # Update user data
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
                        f"📊 {user_data_store[user_id]['generations_used']}/10 free generations used",
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
                "• API key not configured\n"
                "• Invalid image format\n\n"
                "🔄 Try again with a different image or prompt.",
                parse_mode='Markdown'
            )
            
    except Exception as e:
        logger.error(f"Video generation error: {str(e)}")
        await processing_msg.edit_text(
            "⚠️ *An Error Occurred*\n\n"
            "Please try again later or use /help for assistance.",
            parse_mode='Markdown'
        )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle general text messages"""
    message_text = update.message.text
    
    # Check if in generation flow
    state = context.user_data.get('state')
    if state == WAITING_FOR_PROMPT:
        return await handle_prompt_received(update, context)
    
    # Generic response
    keyboard = [
        [InlineKeyboardButton("🎬 Generate Video", callback_data="generate")],
        [InlineKeyboardButton("📸 Image to Video", callback_data="image_to_video")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🤔 I received: *{message_text[:50]}{'...' if len(message_text) > 50 else ''}*\n\n"
        "I'm not sure what you want me to do with that.\n\n"
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
    
    if query.data == "generate":
        await generate_command(update, context)
        
    elif query.data == "image_to_video":
        await handle_image_to_video_start(update, context)
        
    elif query.data == "singing_video":
        await handle_singing_video_start(update, context)
        
    elif query.data == "text_to_video":
        await handle_text_to_video_start(update, context)
        
    elif query.data == "help":
        await help_command(update, context)
        
    elif query.data == "status":
        await status_command(update, context)
        
    elif query.data == "cancel":
        context.user_data['state'] = None
        await query.edit_message_text(
            "✅ *Operation Cancelled*\n\n"
            "You can start a new generation anytime with /generate",
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
                "Please try again or use /help for assistance.",
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
    
    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('generate', generate_command),
            CallbackQueryHandler(handle_button_press, pattern='^(generate|image_to_video|singing_video|text_to_video)$')
        ],
        states={
            WAITING_FOR_IMAGE: [
                MessageHandler(filters.PHOTO, handle_image_received)
            ],
            WAITING_FOR_PROMPT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_prompt_received)
            ],
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
    application.add_handler(CommandHandler("generate", generate_command))
    
    # Add message handlers
    application.add_handler(MessageHandler(
        filters.PHOTO & ~filters.COMMAND, 
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
