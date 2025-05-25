import json
import logging
from typing import Dict, List, Tuple
from bot.config.settings import settings

logger = logging.getLogger(__name__)


class FootballTournament:
    def __init__(self, data_file: str = "tournament_data.json"):
        self.teams: List[str] = []
        self.rounds: Dict[int, Dict] = {}
        self.current_round: int = 1
        self.total_rounds: int = 0
        self.match_results: Dict[str, Dict] = {}
        self.tournament_finished: bool = False
        self.tournament_started: bool = False
        
        self.data_file = settings.data_dir / data_file
        self.load_data()
    
    def generate_single_round_matches(self) -> List[Tuple[str, str]]:
        """Generate all possible matches for one round"""
        matches = []
        for i in range(len(self.teams)):
            for j in range(i + 1, len(self.teams)):
                matches.append((self.teams[i], self.teams[j]))
        return matches
    
    def create_tournament_structure(self, num_rounds: int) -> bool:
        """Create tournament structure with specified number of rounds"""
        if len(self.teams) < 2 or num_rounds > settings.max_rounds:
            logger.warning(f"Cannot create tournament: teams={len(self.teams)}, rounds={num_rounds}")
            return False
        
        self.total_rounds = num_rounds
        self.rounds = {}
        
        round_matches = self.generate_single_round_matches()
        
        for round_num in range(1, num_rounds + 1):
            self.rounds[round_num] = {
                'matches': round_matches.copy(),
                'completed': False
            }
        
        self.current_round = 1
        self.tournament_started = True
        self.tournament_finished = False
        self.match_results = {}
        self.save_data()
        logger.info(f"Tournament created with {num_rounds} rounds and {len(self.teams)} teams")
        return True
    
    def add_additional_rounds(self, additional_rounds: int) -> bool:
        """Add additional rounds to existing tournament"""
        if not self.tournament_started or additional_rounds <= 0:
            return False
        
        if additional_rounds > settings.max_additional_rounds:
            logger.warning(f"Cannot add {additional_rounds} rounds, max allowed: {settings.max_additional_rounds}")
            return False
        
        round_matches = self.generate_single_round_matches()
        
        for round_num in range(self.total_rounds + 1, self.total_rounds + additional_rounds + 1):
            self.rounds[round_num] = {
                'matches': round_matches.copy(),
                'completed': False
            }
        
        self.total_rounds += additional_rounds
        self.save_data()
        logger.info(f"Added {additional_rounds} additional rounds")
        return True
    
    def is_round_complete(self, round_num: int) -> bool:
        """Check if all matches in a round are completed"""
        if round_num not in self.rounds:
            return False
        
        matches = self.rounds[round_num]['matches']
        for home, away in matches:
            match_id = self.create_match_id(round_num, home, away)
            if match_id not in self.match_results:
                return False
        return True
    
    def complete_round(self, round_num: int) -> None:
        """Mark a round as completed"""
        if round_num in self.rounds:
            self.rounds[round_num]['completed'] = True
            self.save_data()
            logger.info(f"Round {round_num} marked as completed")
    
    def can_advance_to_next_round(self) -> bool:
        """Check if current round is complete and can advance"""
        return self.is_round_complete(self.current_round)
    
    def advance_to_next_round(self) -> bool:
        """Advance to next round if possible"""
        if self.current_round < self.total_rounds:
            if self.can_advance_to_next_round():
                self.complete_round(self.current_round)
            self.current_round += 1
            self.save_data()
            logger.info(f"Advanced to round {self.current_round}")
            return True
        return False
    
    def finish_tournament(self) -> None:
        """Mark tournament as finished"""
        self.tournament_finished = True
        if self.can_advance_to_next_round():
            self.complete_round(self.current_round)
        self.save_data()
        logger.info("Tournament finished")
    
    def reset_tournament(self) -> None:
        """Reset tournament to start fresh"""
        self.rounds = {}
        self.current_round = 1
        self.total_rounds = 0
        self.match_results = {}
        self.tournament_finished = False
        self.tournament_started = False
        self.save_data()
        logger.info("Tournament reset")
    
    def create_match_id(self, round_num: int, home_team: str, away_team: str) -> str:
        """Create unique match ID"""
        return f"R{round_num}_{home_team}_vs_{away_team}".replace(" ", "_")
    
    def get_tournament_progress(self) -> Dict:
        """Get overall tournament progress"""
        completed_rounds = sum(1 for r in self.rounds.values() if r['completed'])
        total_matches = len(self.rounds.get(1, {}).get('matches', [])) * self.total_rounds
        completed_matches = len(self.match_results)
        
        return {
            'completed_rounds': completed_rounds,
            'total_rounds': self.total_rounds,
            'completed_matches': completed_matches,
            'total_matches': total_matches,
            'current_round_complete': self.is_round_complete(self.current_round)
        }
    
    def save_data(self) -> None:
        """Save bot data to file"""
        try:
            data = {
                'teams': self.teams,
                'rounds': self.rounds,
                'current_round': self.current_round,
                'total_rounds': self.total_rounds,
                'match_results': self.match_results,
                'tournament_finished': self.tournament_finished,
                'tournament_started': self.tournament_started
            }
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug("Tournament data saved successfully")
        except Exception as e:
            logger.error(f"Failed to save tournament data: {e}")
    
    def load_data(self) -> None:
        """Load bot data from file"""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.teams = data.get('teams', [])
                    self.rounds = {int(k): v for k, v in data.get('rounds', {}).items()}
                    self.current_round = data.get('current_round', 1)
                    self.total_rounds = data.get('total_rounds', 0)
                    self.match_results = data.get('match_results', {})
                    self.tournament_finished = data.get('tournament_finished', False)
                    self.tournament_started = data.get('tournament_started', False)
                logger.info("Tournament data loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load tournament data: {e}")
