from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from typing import List, Tuple, Dict


class Keyboards:
    @staticmethod
    def main_menu() -> ReplyKeyboardMarkup:
        """Create main menu keyboard"""
        keyboard = [
            [KeyboardButton("⚽ Setup Tournament"), KeyboardButton("🎯 Start Tournament")],
            [KeyboardButton("📅 View Round"), KeyboardButton("🏆 Enter Results")],
            [KeyboardButton("📊 View Table"), KeyboardButton("📈 Detailed Stats")],
            [KeyboardButton("🔄 Next Round"), KeyboardButton("➕ Add Rounds")],
            [KeyboardButton("🏁 Finish Tournament"), KeyboardButton("ℹ️ Tournament Info")],
            [KeyboardButton("🔄 Reset Tournament")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    @staticmethod
    def setup_tournament() -> InlineKeyboardMarkup:
        """Create setup tournament keyboard"""
        keyboard = [
            [InlineKeyboardButton("➕ Add Team", callback_data="add_team")],
            [InlineKeyboardButton("🗑️ Clear Teams", callback_data="clear_teams")],
            [InlineKeyboardButton("🎯 Start Tournament", callback_data="start_tournament")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def rounds_selection() -> InlineKeyboardMarkup:
        """Create rounds selection keyboard"""
        keyboard = [
            [InlineKeyboardButton("1 Round", callback_data="rounds_1")],
            [InlineKeyboardButton("2 Rounds", callback_data="rounds_2")],
            [InlineKeyboardButton("3 Rounds", callback_data="rounds_3")],
            [InlineKeyboardButton("4 Rounds", callback_data="rounds_4")],
            [InlineKeyboardButton("5 Rounds", callback_data="rounds_5")],
            [InlineKeyboardButton("🔢 Custom", callback_data="rounds_custom")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def add_rounds_selection() -> InlineKeyboardMarkup:
        """Create add rounds selection keyboard"""
        keyboard = [
            [InlineKeyboardButton("1 Round", callback_data="add_rounds_1")],
            [InlineKeyboardButton("2 Rounds", callback_data="add_rounds_2")],
            [InlineKeyboardButton("3 Rounds", callback_data="add_rounds_3")],
            [InlineKeyboardButton("5 Rounds", callback_data="add_rounds_5")],
            [InlineKeyboardButton("🔢 Custom", callback_data="add_rounds_custom")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def cancel() -> InlineKeyboardMarkup:
        """Create cancel keyboard"""
        return InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="cancel")]])
    
    @staticmethod
    def match_results(matches: List[Tuple[str, str]], round_num: int, match_results: Dict) -> InlineKeyboardMarkup:
        """Create match results keyboard"""
        keyboard = []
        
        for i, (home, away) in enumerate(matches):
            match_id = f"R{round_num}_{home}_vs_{away}".replace(" ", "_")
            result = match_results.get(match_id, {})
            
            if result:
                button_text = f"✅ {home} {result['home_score']}-{result['away_score']} {away}"
            else:
                button_text = f"⏳ {home} vs {away}"
            
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"result_{match_id}")])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def round_navigation(current_round: int, total_rounds: int, round_complete: bool, round_marked_complete: bool) -> InlineKeyboardMarkup:
        """Create round navigation keyboard"""
        keyboard = []
        
        # Round navigation
        nav_row = []
        if current_round > 1:
            nav_row.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"view_round_{current_round-1}"))
        if current_round < total_rounds:
            nav_row.append(InlineKeyboardButton("➡️ Next", callback_data=f"view_round_{current_round+1}"))
        if nav_row:
            keyboard.append(nav_row)
        
        # Action buttons
        keyboard.append([InlineKeyboardButton("🏆 Enter Results", callback_data="enter_results")])
        
        # Finish Round button (only if round is complete but not marked as finished)
        if round_complete and not round_marked_complete:
            keyboard.append([InlineKeyboardButton("🏁 Finish Round", callback_data=f"finish_round_{current_round}")])
        
        if round_marked_complete and current_round < total_rounds:
            keyboard.append([InlineKeyboardButton("🔄 Advance to Next Round", callback_data="advance_round")])
        elif round_marked_complete and current_round == total_rounds:
            keyboard.append([InlineKeyboardButton("🏁 Finish Tournament", callback_data="finish_tournament")])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def tournament_table() -> InlineKeyboardMarkup:
        """Create tournament table keyboard"""
        keyboard = [
            [InlineKeyboardButton("📊 Detailed Stats", callback_data="detailed_stats")],
            [InlineKeyboardButton("📅 View Round", callback_data="view_current_round")],
            [InlineKeyboardButton("➕ Add Rounds", callback_data="add_rounds")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def detailed_stats() -> InlineKeyboardMarkup:
        """Create detailed stats keyboard"""
        keyboard = [
            [InlineKeyboardButton("🏆 Back to Table", callback_data="view_table")],
            [InlineKeyboardButton("📅 View Round", callback_data="view_current_round")]
        ]
        return InlineKeyboardMarkup(keyboard)
