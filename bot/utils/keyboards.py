from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from typing import List, Tuple


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
    def match_results(matches: List[Tuple[str, str]], round_num: int, match_results: dict) -> InlineKeyboardMarkup:
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
