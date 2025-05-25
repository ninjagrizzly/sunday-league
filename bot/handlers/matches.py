from telegram import Update
from telegram.ext import ContextTypes
from bot.models.tournament import tournament
from bot.utils.keyboards import Keyboards
from bot.utils.helpers import calculate_team_statistics
import logging

logger = logging.getLogger(__name__)


async def setup_tournament(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Setup tournament by adding teams"""
    teams_text = "**Current Teams:**\n"
    if tournament.teams:
        for i, team in enumerate(tournament.teams, 1):
            teams_text += f"{i}. {team}\n"
        
        # Calculate matches per round
        num_teams = len(tournament.teams)
        matches_per_round = (num_teams * (num_teams - 1)) // 2
        teams_text += f"\n**Total Teams:** {num_teams}"
        teams_text += f"\n**Matches per Round:** {matches_per_round}"
    else:
        teams_text += "No teams added yet.\n"
    
    await update.message.reply_text(
        teams_text, 
        reply_markup=Keyboards.setup_tournament(), 
        parse_mode='Markdown'
    )


async def start_tournament_setup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start tournament setup with round selection"""
    if len(tournament.teams) < 2:
        await update.message.reply_text("❌ Need at least 2 teams to start tournament!")
        return
    
    num_teams = len(tournament.teams)
    matches_per_round = (num_teams * (num_teams - 1)) // 2
    
    setup_text = f"""
🎯 **Start Tournament**

**Teams:** {num_teams}
**Matches per Round:** {matches_per_round}

Each round will contain ALL possible matches:
"""
    
    for i in range(len(tournament.teams)):
        for j in range(i + 1, len(tournament.teams)):
            setup_text += f"• {tournament.teams[i]} vs {tournament.teams[j]}\n"
    
    setup_text += "\nSelect number of rounds:"
    
    await update.message.reply_text(
        setup_text, 
        reply_markup=Keyboards.rounds_selection(), 
        parse_mode='Markdown'
    )


async def add_rounds_setup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Setup for adding additional rounds"""
    if not tournament.tournament_started:
        await update.message.reply_text("❌ No tournament started yet! Start a tournament first.")
        return
    
    progress = tournament.get_tournament_progress()
    
    add_text = f"""
➕ **Add Additional Rounds**

**Current Tournament Status:**
• Current Rounds: {tournament.total_rounds}
• Current Round: {tournament.current_round}
• Completed Rounds: {progress['completed_rounds']}
• Matches per Round: {len(tournament.rounds.get(1, {}).get('matches', []))}

**Note:** New rounds will have the same match structure as existing rounds.

How many rounds would you like to add?
    """
    
    await update.message.reply_text(
        add_text, 
        reply_markup=Keyboards.add_rounds_selection(), 
        parse_mode='Markdown'
    )


async def view_current_round(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """View current round matches and status"""
    if not tournament.tournament_started:
        await update.message.reply_text("❌ No tournament started yet. Please start a tournament first.")
        return
    
    current_round = tournament.current_round
    if current_round not in tournament.rounds:
        await update.message.reply_text("❌ No matches for current round.")
        return
    
    matches = tournament.rounds[current_round]['matches']
    round_complete = tournament.is_round_complete(current_round)
    round_marked_complete = tournament.rounds[current_round]['completed']
    
    round_text = f"📅 **Round {current_round} of {tournament.total_rounds}**\n"
    
    if round_marked_complete:
        round_text += f"**Status:** ✅ Completed\n\n"
    elif round_complete:
        round_text += f"**Status:** 🎯 Ready to Finish\n\n"
    else:
        round_text += f"**Status:** ⏳ In Progress\n\n"
    
    completed_matches = 0
    for i, (home, away) in enumerate(matches, 1):
        match_id = tournament.create_match_id(current_round, home, away)
        result = tournament.match_results.get(match_id, {})
        
        if result:
            round_text += f"{i}. {home} {result['home_score']}-{result['away_score']} {away} ✅\n"
            completed_matches += 1
        else:
            round_text += f"{i}. {home} vs {away} ⏳\n"
    
    round_text += f"\n**Progress:** {completed_matches}/{len(matches)} matches completed"
    
    reply_markup = Keyboards.round_navigation(
        current_round, tournament.total_rounds, round_complete, round_marked_complete
    )
    
    await update.message.reply_text(round_text, reply_markup=reply_markup, parse_mode='Markdown')


async def enter_results(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Enter match results for current round"""
    if not tournament.tournament_started:
        await update.message.reply_text("❌ No tournament started yet.")
        return
    
    current_round = tournament.current_round
    if current_round not in tournament.rounds:
        await update.message.reply_text("❌ No matches for current round.")
        return
    
    matches = tournament.rounds[current_round]['matches']
    
    # Add Finish Round button if all matches are completed
    round_complete = tournament.is_round_complete(current_round)
    round_marked_complete = tournament.rounds[current_round]['completed']
    
    status_text = ""
    additional_buttons = []
    if round_complete and not round_marked_complete:
        status_text = "\n\n✅ **All matches completed! You can now finish this round.**"
        # Add finish round button to keyboard
        additional_buttons.append([{"text": "🏁 Finish Round", "callback_data": f"finish_round_{current_round}"}])
    elif round_marked_complete:
        status_text = "\n\n🎯 **Round completed and finished!**"

    reply_markup = Keyboards.match_results(matches, current_round, tournament.match_results, additional_buttons)
    
    await update.message.reply_text(
        f"🏆 **Enter Results - Round {current_round}**\n\nSelect a match to enter/edit the result:{status_text}",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def finish_tournament_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Finish the tournament"""
    if tournament.tournament_finished:
        await update.message.reply_text("🏁 Tournament is already finished!")
        return
    
    if not tournament.tournament_started:
        await update.message.reply_text("❌ No tournament started yet!")
        return
    
    progress = tournament.get_tournament_progress()
    
    if progress['completed_matches'] < progress['total_matches']:
        from bot.utils.keyboards import Keyboards
        keyboard = [
            [{"text": "✅ Yes, Finish Now", "callback_data": "force_finish"}],
            [{"text": "❌ No, Continue", "callback_data": "cancel"}]
        ]
        reply_markup = {"inline_keyboard": keyboard}
        
        await update.message.reply_text(
            f"⚠️ **Warning:** Tournament is not complete!\n\n"
            f"**Progress:** {progress['completed_matches']}/{progress['total_matches']} matches played\n"
            f"**Rounds:** {progress['completed_rounds']}/{progress['total_rounds']} completed\n\n"
            f"Are you sure you want to finish the tournament?",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await finalize_tournament(update, context)


async def finalize_tournament(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Finalize tournament and show results"""
    tournament.finish_tournament()
    teams_stats = calculate_team_statistics(tournament.teams, tournament.match_results)
    sorted_teams = sorted(
        teams_stats.items(),
        key=lambda x: (x[1]['points'], x[1]['goal_difference'], x[1]['goals_for']),
        reverse=True
    )
    
    finish_text = "🏁 **Tournament Finished!**\n\n"
    
    if sorted_teams:
        finish_text += "🏆 **Final Standings:**\n"
        finish_text += f"🥇 **Champion:** {sorted_teams[0][0]} ({sorted_teams[0][1]['points']} pts)\n"
        
        if len(sorted_teams) > 1:
            finish_text += f"🥈 **Runner-up:** {sorted_teams[1][0]} ({sorted_teams[1][1]['points']} pts)\n"
        if len(sorted_teams) > 2:
            finish_text += f"🥉 **Third Place:** {sorted_teams[2][0]} ({sorted_teams[2][1]['points']} pts)\n"
        
        # Tournament statistics
        total_goals = sum(stats['goals_for'] for stats in teams_stats.values()) // 2
        total_matches = sum(stats['played'] for stats in teams_stats.values()) // 2
        
        finish_text += f"\n📊 **Tournament Statistics:**\n"
        finish_text += f"• Total Rounds: {tournament.total_rounds}\n"
        finish_text += f"• Total Matches: {total_matches}\n"
        finish_text += f"• Total Goals: {total_goals}\n"
        if total_matches > 0:
            finish_text += f"• Average Goals/Match: {total_goals/total_matches:.2f}\n"
    
    await update.message.reply_text(finish_text, parse_mode='Markdown')


async def tournament_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display comprehensive tournament information"""
    info_text = f"""
ℹ️ **Tournament Information**

**Setup:**
• Teams: {len(tournament.teams)}
• Tournament Started: {'Yes' if tournament.tournament_started else 'No'}
• Tournament Finished: {'Yes' if tournament.tournament_finished else 'No'}

**Structure:**
• Total Rounds: {tournament.total_rounds}
• Current Round: {tournament.current_round}
• Matches per Round: {len(tournament.rounds.get(1, {}).get('matches', []))}

**Teams List:**
"""
    
    for i, team in enumerate(tournament.teams, 1):
        info_text += f"{i}. {team}\n"
    
    if not tournament.teams:
        info_text += "No teams added yet."
    
    if tournament.tournament_started:
        progress = tournament.get_tournament_progress()
        info_text += f"\n**Progress:**\n"
        info_text += f"• Completed Rounds: {progress['completed_rounds']}/{progress['total_rounds']}\n"
        info_text += f"• Completed Matches: {progress['completed_matches']}/{progress['total_matches']}\n"
        info_text += f"• Current Round Complete: {'Yes' if progress['current_round_complete'] else 'No'}\n"
    
    await update.message.reply_text(info_text, parse_mode='Markdown')
