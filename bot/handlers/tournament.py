from telegram import Update
from telegram.ext import ContextTypes
from bot.models.tournament import tournament
from bot.handlers.matches import (
    setup_tournament, start_tournament_setup, add_rounds_setup,
    view_current_round, enter_results, tournament_info
)
from bot.handlers.statistics import view_tournament_table, view_detailed_stats
import logging

logger = logging.getLogger(__name__)


async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text input based on context"""
    text = update.message.text
    user_id = update.effective_user.id
    
    logger.info(f"User {user_id} sent: {text}")
    
    # Handle menu buttons
    if text in ["⚽ Setup Tournament", "Setup Tournament"]:
        await setup_tournament(update, context)
    elif text in ["🎯 Start Tournament", "Start Tournament"]:
        await start_tournament_setup(update, context)
    elif text in ["📅 View Round", "View Round"]:
        await view_current_round(update, context)
    elif text in ["🏆 Enter Results", "Enter Results"]:
        await enter_results(update, context)
    elif text in ["📊 View Table", "View Table"]:
        await view_tournament_table(update, context)
    elif text in ["📈 Detailed Stats", "Detailed Stats"]:
        await view_detailed_stats(update, context)
    elif text in ["🔄 Next Round", "Next Round"]:
        await handle_next_round(update, context)
    elif text in ["➕ Add Rounds", "Add Rounds"]:
        await add_rounds_setup(update, context)
    elif text in ["🏁 Finish Tournament", "Finish Tournament"]:
        await handle_finish_tournament(update, context)
    elif text in ["ℹ️ Tournament Info", "Tournament Info"]:
        await tournament_info(update, context)
    elif text in ["🔄 Reset Tournament", "Reset Tournament"]:
        await handle_reset_tournament(update, context)
    elif 'waiting_for' in context.user_data:
        await handle_user_input(update, context)
    else:
        await update.message.reply_text("Please use the menu buttons or commands.")


async def handle_next_round(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle next round advancement"""
    if tournament.can_advance_to_next_round():
        if tournament.advance_to_next_round():
            await update.message.reply_text(f"🔄 Advanced to Round {tournament.current_round}!")
        else:
            await update.message.reply_text("🏁 Tournament completed! All rounds finished.")
    else:
        await update.message.reply_text("❌ Current round is not complete yet!")


async def handle_finish_tournament(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle tournament finishing"""
    from football_bot.handlers.matches import finish_tournament_command
    await finish_tournament_command(update, context)


async def handle_reset_tournament(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle tournament reset"""
    tournament.reset_tournament()
    await update.message.reply_text("🔄 Tournament reset! You can now set up a new tournament.")


async def handle_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle specific user inputs"""
    waiting_for = context.user_data.get('waiting_for')
    text = update.message.text
    
    if waiting_for == 'team_name':
        await handle_team_name_input(update, context, text)
    elif waiting_for == 'custom_rounds':
        await handle_custom_rounds_input(update, context, text)
    elif waiting_for == 'custom_add_rounds':
        await handle_custom_add_rounds_input(update, context, text)
    elif waiting_for == 'match_result':
        await handle_match_result_input(update, context, text)


async def handle_team_name_input(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    """Handle team name input"""
    if text not in tournament.teams:
        tournament.teams.append(text)
        tournament.save_data()
        await update.message.reply_text(f"✅ Team '{text}' added successfully!")
    else:
        await update.message.reply_text(f"❌ Team '{text}' already exists!")
    
    context.user_data.clear()
    await setup_tournament(update, context)


async def handle_custom_rounds_input(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    """Handle custom rounds input"""
    try:
        rounds = int(text)
        if 1 <= rounds <= tournament.config.max_rounds:
            if tournament.create_tournament_structure(rounds):
                await update.message.reply_text(
                    f"✅ Tournament created!\n\n"
                    f"**Rounds:** {rounds}\n"
                    f"**Teams:** {len(tournament.teams)}\n"
                    f"**Matches per Round:** {len(tournament.rounds[1]['matches'])}\n"
                    f"**Total Matches:** {len(tournament.rounds[1]['matches']) * rounds}"
                )
            else:
                await update.message.reply_text("❌ Failed to create tournament!")
        else:
            await update.message.reply_text(f"❌ Please enter a number between 1 and {tournament.config.max_rounds}!")
    except ValueError:
        await update.message.reply_text("❌ Please enter a valid number!")
    
    context.user_data.clear()


async def handle_custom_add_rounds_input(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    """Handle custom add rounds input"""
    try:
        additional_rounds = int(text)
        if 1 <= additional_rounds <= tournament.config.max_additional_rounds:
            if tournament.add_additional_rounds(additional_rounds):
                await update.message.reply_text(
                    f"✅ Added {additional_rounds} additional rounds!\n\n"
                    f"**Total Rounds:** {tournament.total_rounds}\n"
                    f"**Current Round:** {tournament.current_round}\n"
                    f"**New Total Matches:** {len(tournament.rounds[1]['matches']) * tournament.total_rounds}"
                )
            else:
                await update.message.reply_text("❌ Failed to add rounds!")
        else:
            await update.message.reply_text(f"❌ Please enter a number between 1 and {tournament.config.max_additional_rounds}!")
    except ValueError:
        await update.message.reply_text("❌ Please enter a valid number!")
    
    context.user_data.clear()


async def handle_match_result_input(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    """Handle match result input"""
    try:
        # Parse score format: "2-1"
        if '-' in text and len(text.split('-')) == 2:
            home_score, away_score = map(int, text.split('-'))
            match_id = context.user_data['current_match']
            
            tournament.match_results[match_id] = {
                'home_score': home_score,
                'away_score': away_score
            }
            tournament.save_data()
            
            await update.message.reply_text(f"✅ Result recorded: {text}")
            context.user_data.clear()
            await enter_results(update, context)
        else:
            await update.message.reply_text("❌ Invalid format! Please use format: home_score-away_score (e.g., 2-1)")
    except ValueError:
        await update.message.reply_text("❌ Invalid scores! Please enter numbers only.")
