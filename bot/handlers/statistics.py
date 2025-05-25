from telegram import Update
from telegram.ext import ContextTypes
from bot.models.tournament import tournament
from bot.utils.keyboards import Keyboards
from bot.utils.helpers import calculate_team_statistics, format_tournament_table, format_detailed_stats
import logging

logger = logging.getLogger(__name__)


async def view_tournament_table(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display comprehensive tournament table"""
    if not tournament.match_results:
        await update.message.reply_text("❌ No match results available yet.")
        return
    
    teams_stats = calculate_team_statistics(tournament.teams, tournament.match_results)
    progress = tournament.get_tournament_progress()
    
    table_text, sorted_teams = format_tournament_table(teams_stats)
    
    table_text += "\n**Legend:** P=Played, W=Won, D=Drawn, L=Lost, GF=Goals For, GA=Goals Against, GD=Goal Difference, Pts=Points"
    
    # Add tournament progress
    table_text += f"\n\n**Tournament Progress:**"
    table_text += f"\n• Rounds: {progress['completed_rounds']}/{progress['total_rounds']} completed"
    table_text += f"\n• Matches: {progress['completed_matches']}/{progress['total_matches']} played"
    table_text += f"\n• Current Round: {tournament.current_round} {'✅' if progress['current_round_complete'] else '⏳'}"
    
    if tournament.tournament_finished:
        table_text += "\n🏁 **Tournament Status:** FINISHED"
        if sorted_teams:
            winner = sorted_teams[0][0]
            table_text += f"\n🥇 **Champion:** {winner}"
    
    await update.message.reply_text(
        table_text, 
        reply_markup=Keyboards.tournament_table(), 
        parse_mode='Markdown'
    )


async def view_detailed_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display detailed team statistics"""
    if not tournament.match_results:
        await update.message.reply_text("❌ No match results available yet.")
        return
    
    teams_stats = calculate_team_statistics(tournament.teams, tournament.match_results)
    stats_text = format_detailed_stats(teams_stats, tournament.rounds)
    
    await update.message.reply_text(
        stats_text, 
        reply_markup=Keyboards.detailed_stats(), 
        parse_mode='Markdown'
    )
