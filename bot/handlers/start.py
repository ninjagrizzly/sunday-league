from telegram import Update
from telegram.ext import ContextTypes
from bot.utils.keyboards import Keyboards
import logging

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command with main menu"""
    user_id = update.effective_user.id
    logger.info(f"User {user_id} started the bot")
    
    welcome_text = """
🏆 **Football Tournament Assistant** ⚽

**Enhanced Features:**
✅ **Finish Round** - Complete rounds manually
✅ **Add Rounds** - Extend tournament dynamically

**Tournament Structure:**
• Each round contains ALL possible matches between teams
• Every team plays every other team in each round
• Complete a round before advancing to the next
• Add more rounds anytime during tournament

**Available Commands:**
⚽ **Setup Tournament** - Add teams
🎯 **Start Tournament** - Begin with specified rounds
📅 **View Round** - See current round matches
🏆 **Enter Results** - Record match scores
📊 **View Table** - Tournament standings
📈 **Detailed Stats** - Team statistics
🔄 **Next Round** - Advance to next round
➕ **Add Rounds** - Add more rounds to tournament
🏁 **Finish Tournament** - End tournament
ℹ️ **Tournament Info** - View status
🔄 **Reset Tournament** - Start over

Ready to manage your professional tournament!
    """
    
    await update.message.reply_text(
        welcome_text, 
        reply_markup=Keyboards.main_menu(), 
        parse_mode='Markdown'
    )
