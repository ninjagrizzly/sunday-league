import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from bot.config.settings import settings
from bot.handlers.start import start_command
from bot.handlers.callbacks import button_callback
from bot.handlers.tournament import handle_text_input
from bot.models.tournament import FootballTournament


def setup_logging() -> None:
    """Setup logging configuration"""
    log_file = settings.log_dir / "bot.log"
    
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )


def main() -> None:
    """Start the bot"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    if not settings.bot_token:
        logger.error("BOT_TOKEN not found in environment variables")
        return
    
    # Initialize tournament instance
    tournament = FootballTournament()
    
    # Create application
    application = Application.builder().token(settings.bot_token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input))
    
    # Start the bot
    logger.info(f"🤖 {settings.bot_name} is starting in {settings.environment} mode...")
    application.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == '__main__':
    main()
