# 🤖 Bideruibot - AI Video Generation Bot

## 🚀 Features
- 🎬 AI-powered video generation from text prompts
- 📱 User-friendly interface with inline buttons
- 🔄 Conversation flow for guided generation
- 📊 Usage tracking and daily limits
- ⚡ Fast and responsive commands
- 🔒 Secure token management via environment variables

## 🛠️ Tech Stack
- Python 3.11
- python-telegram-bot 20.7
- Railway (Hosting)
- GitHub (Version Control)

## 📦 Installation

### Local Development
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set environment variable: `TELEGRAM_BOT_TOKEN=your_token_here`
4. Run the bot: `python main.py`

### Deployment to Railway
1. Push code to GitHub
2. Create new project on Railway
3. Deploy from GitHub repository
4. Add environment variable: `TELEGRAM_BOT_TOKEN`
5. Deploy!

## 🔧 Environment Variables
| Variable | Description |
|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Your bot token from @BotFather |

## 🎯 Commands
- `/start` - Welcome message
- `/help` - Help menu
- `/generate` - Start video generation
- `/status` - Check bot status
- `/about` - Bot information
- `/cancel` - Cancel current operation

## 📝 License
MIT License - Free to use and modify
