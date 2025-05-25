from telegram import Update
from telegram.ext import ContextTypes
from bot.models.tournament import tournament
from bot.utils.keyboards import Keyboards
from bot.handlers.matches import (
    setup_tournament, start_tournament_setup, add_rounds_setup,
    enter_results, finalize_tournament
)
from bot.handlers.statistics import view_tournament_table, view_detailed_stats
from bot.handlers.matches import view_current_round
import logging

logger = logging.getLogger(__name__)


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = update.effective_user.id
    logger.info(f"User {user_id} clicked button: {data}")
    
    try:
        if data == "add_team":
            await handle_add_team(query, context)
        elif data == "clear_teams":
            await handle_clear_teams(query, context)
        elif data == "start_tournament":
            await start_tournament_setup(query, context)
        elif data == "add_rounds":
            await add_rounds_setup(query, context)
        elif data.startswith("rounds_"):
            await handle_rounds_selection(query, context, data)
        elif data.startswith("add_rounds_"):
            await handle_add_rounds_selection(query, context, data)
        elif data.startswith("finish_round_"):
            await handle_finish_round(query, context, data)
        elif data == "enter_results":
            await enter_results(query, context)
        elif data == "advance_round":
            await handle_advance_round(query, context)
        elif data == "finish_tournament":
            await handle_finish_tournament(query, context)
        elif data == "force_finish":
            await finalize_tournament(query, context)
        elif data == "view_table":
            await view_tournament_table(query, context)
        elif data == "detailed_stats":
            await view_detailed_stats(query, context)
        elif data == "view_current_round":
            await view_current_round(query, context)
        elif data.startswith("view_round_"):
            await handle_view_round(query, context, data)
        elif data.startswith("result_"):
            await handle_result_input(query, context, data)
        elif data == "cancel":
            await handle_cancel(query, context)
        else:
            logger.warning(f"Unknown callback data: {data}")
            
    except Exception as e:
        logger.error(f"Error handling callback {data}: {e}")
        await query.edit_message_text("❌ An error occurred. Please try again.")


async def handle_add_team(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle add team button"""
    await query.edit_message_text(
        "Please enter the team name:",
        reply_markup=Keyboards.cancel()
    )
    context.user_data['waiting_for'] = 'team_name'


async def handle_clear_teams(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle clear teams button"""
    tournament.teams = []
    tournament.reset_tournament()
    await query.edit_message_text("🗑️ All teams cleared and tournament reset!")
    await setup_tournament(query, context)


async def handle_rounds_selection(query, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
    """Handle rounds selection"""
    if data == "rounds_custom":
        await query.edit_message_text(
            f"Please enter the number of rounds (1-{tournament.config.max_rounds}):",
            reply_markup=Keyboards.cancel()
        )
        context.user_data['waiting_for'] = 'custom_rounds'
    else:
        rounds = int(data.split("_")[1])
        if tournament.create_tournament_structure(rounds):
            await query.edit_message_text(
                f"✅ Tournament created!\n\n"
                f"**Rounds:** {rounds}\n"
                f"**Teams:** {len(tournament.teams)}\n"
                f"**Matches per Round:** {len(tournament.rounds[1]['matches'])}\n"
                f"**Total Matches:** {len(tournament.rounds[1]['matches']) * rounds}"
            )
        else:
            await query.edit_message_text("❌ Failed to create tournament!")


async def handle_add_rounds_selection(query, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
    """Handle add rounds selection"""
    if data == "add_rounds_custom":
        await query.edit_message_text(
            f"Please enter the number of additional rounds (1-{tournament.config.max_additional_rounds}):",
            reply_markup=Keyboards.cancel()
        )
        context.user_data['waiting_for'] = 'custom_add_rounds'
    else:
        additional_rounds = int(data.split("_")[2])
        if tournament.add_additional_rounds(additional_rounds):
            await query.edit_message_text(
                f"✅ Added {additional_rounds} additional rounds!\n\n"
                f"**Total Rounds:** {tournament.total_rounds}\n"
                f"**Current Round:** {tournament.current_round}\n"
                f"**New Total Matches:** {len(tournament.rounds[1]['matches']) * tournament.total_rounds}"
            )
        else:
            await query.edit_message_text("❌ Failed to add rounds!")


async def handle_finish_round(query, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
    """Handle finish round button"""
    round_num = int(data.split("_")[2])
    if tournament.is_round_complete(round_num):
        tournament.complete_round(round_num)
        await query.edit_message_text(f"🏁 Round {round_num} finished successfully!")
    else:
        await query.edit_message_text(f"❌ Cannot finish Round {round_num} - not all matches completed!")


async def handle_advance_round(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle advance round button"""
    if tournament.advance_to_next_round():
        await query.edit_message_text(f"🔄 Advanced to Round {tournament.current_round}!")
    else:
        await query.edit_message_text("❌ Cannot advance to next round!")


async def handle_finish_tournament(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle finish tournament button"""
    from football_bot.handlers.matches import finish_tournament_command
    await finish_tournament_command(query, context)


async def handle_view_round(query, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
    """Handle view round button"""
    round_num = int(data.split("_")[2])
    old_round = tournament.current_round
    tournament.current_round = round_num
    await view_current_round(query, context)
    tournament.current_round = old_round  # Restore current round


async def handle_result_input(query, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
    """Handle result input button"""
    match_id = data[7:]  # Remove "result_" prefix
    context.user_data['current_match'] = match_id
    context.user_data['waiting_for'] = 'match_result'
    
    # Parse match info
    parts = match_id.split("_")
    round_num = parts[0][1:]  # Remove 'R'
    home_team = parts[1]
    away_team = parts[3]
    
    await query.edit_message_text(
        f"🏆 **Enter Result**\n\n**Round {round_num}**\n{home_team} vs {away_team}\n\nPlease enter the result in format: home_score-away_score\nExample: 2-1",
        reply_markup=Keyboards.cancel()
    )


async def handle_cancel(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle cancel button"""
    context.user_data.clear()
    await query.edit_message_text("❌ Operation cancelled.")
