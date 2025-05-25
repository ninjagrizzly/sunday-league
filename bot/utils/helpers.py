from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


def calculate_team_statistics(teams: List[str], match_results: Dict[str, Dict]) -> Dict:
    """Calculate comprehensive team statistics"""
    teams_stats = {}
    
    # Initialize stats for all teams
    for team in teams:
        teams_stats[team] = {
            'points': 0,
            'played': 0,
            'won': 0,
            'drawn': 0,
            'lost': 0,
            'goals_for': 0,
            'goals_against': 0,
            'goal_difference': 0
        }
    
    # Process all match results
    for match_id, result in match_results.items():
        try:
            # Parse match_id to extract teams: "R1_TeamA_vs_TeamB"
            parts = match_id.split('_')
            if len(parts) < 4:
                continue
                
            home_team = parts[1]
            away_team = parts[3]
            
            if home_team not in teams_stats or away_team not in teams_stats:
                continue
            
            home_score = result['home_score']
            away_score = result['away_score']
            
            # Update match count
            teams_stats[home_team]['played'] += 1
            teams_stats[away_team]['played'] += 1
            
            # Update goals
            teams_stats[home_team]['goals_for'] += home_score
            teams_stats[home_team]['goals_against'] += away_score
            teams_stats[away_team]['goals_for'] += away_score
            teams_stats[away_team]['goals_against'] += home_score
            
            # Update points and match results
            if home_score > away_score:  # Home team wins
                teams_stats[home_team]['points'] += 3
                teams_stats[home_team]['won'] += 1
                teams_stats[away_team]['lost'] += 1
            elif home_score < away_score:  # Away team wins
                teams_stats[away_team]['points'] += 3
                teams_stats[away_team]['won'] += 1
                teams_stats[home_team]['lost'] += 1
            else:  # Draw
                teams_stats[home_team]['points'] += 1
                teams_stats[away_team]['points'] += 1
                teams_stats[home_team]['drawn'] += 1
                teams_stats[away_team]['drawn'] += 1
        except (KeyError, IndexError, ValueError) as e:
            logger.error(f"Error processing match {match_id}: {e}")
    
    # Calculate goal difference
    for team in teams_stats:
        teams_stats[team]['goal_difference'] = (
            teams_stats[team]['goals_for'] - teams_stats[team]['goals_against']
        )
    
    return teams_stats


def format_tournament_table(teams_stats: Dict) -> Tuple[str, List]:
    """Format tournament table as string"""
    # Sort teams by points (descending), then by goal difference, then by goals for
    sorted_teams = sorted(
        teams_stats.items(),
        key=lambda x: (x[1]['points'], x[1]['goal_difference'], x[1]['goals_for']),
        reverse=True
    )
    
    table_text = "🏆 **Tournament Table**\n\n"
    table_text += "```"
    table_text += f"{'Pos':<3} {'Team':<12} {'P':<2} {'W':<2} {'D':<2} {'L':<2} {'GF':<3} {'GA':<3} {'GD':<4} {'Pts':<3}\n"
    table_text += "-" * 65 + "\n"
    
    for pos, (team, stats) in enumerate(sorted_teams, 1):
        gd_str = f"+{stats['goal_difference']}" if stats['goal_difference'] > 0 else str(stats['goal_difference'])
        table_text += f"{pos:<3} {team[:12]:<12} {stats['played']:<2} {stats['won']:<2} {stats['drawn']:<2} {stats['lost']:<2} "
        table_text += f"{stats['goals_for']:<3} {stats['goals_against']:<3} {gd_str:<4} {stats['points']:<3}\n"
    
    table_text += "```\n"
    
    return table_text, sorted_teams


def format_detailed_stats(teams_stats: Dict, tournament_rounds: Dict) -> str:
    """Format detailed tournament statistics"""
    stats_text = "📊 **Detailed Tournament Statistics**\n\n"
    
    # Top scorers (by goals for)
    top_scorers = sorted(teams_stats.items(), key=lambda x: x[1]['goals_for'], reverse=True)
    stats_text += "⚽ **Top Scoring Teams:**\n"
    for i, (team, stats) in enumerate(top_scorers[:5], 1):
        stats_text += f"{i}. {team}: {stats['goals_for']} goals\n"
    
    # Best defense (by goals against)
    best_defense = sorted(teams_stats.items(), key=lambda x: x[1]['goals_against'])
    stats_text += "\n🛡️ **Best Defensive Teams:**\n"
    for i, (team, stats) in enumerate(best_defense[:5], 1):
        stats_text += f"{i}. {team}: {stats['goals_against']} goals conceded\n"
    
    # Most wins
    most_wins = sorted(teams_stats.items(), key=lambda x: x[1]['won'], reverse=True)
    stats_text += "\n🏆 **Most Wins:**\n"
    for i, (team, stats) in enumerate(most_wins[:5], 1):
        stats_text += f"{i}. {team}: {stats['won']} wins\n"
    
    # Calculate total goals and matches
    total_goals = sum(stats['goals_for'] for stats in teams_stats.values()) // 2
    total_matches = sum(stats['played'] for stats in teams_stats.values()) // 2
    
    stats_text += f"\n📈 **Tournament Overview:**\n"
    stats_text += f"Total Matches Played: {total_matches}\n"
    stats_text += f"Total Goals Scored: {total_goals}\n"
    if total_matches > 0:
        stats_text += f"Average Goals per Match: {total_goals/total_matches:.2f}\n"
    
    # Round-by-round breakdown
    stats_text += f"\n📅 **Round Breakdown:**\n"
    total_rounds = len(tournament_rounds)
    for round_num in range(1, total_rounds + 1):
        if round_num in tournament_rounds:
            status = "✅ Complete" if tournament_rounds[round_num]['completed'] else "⏳ In Progress"
            matches_in_round = len(tournament_rounds[round_num]['matches'])
            completed_in_round = sum(1 for home, away in tournament_rounds[round_num]['matches'] 
                                   if f"R{round_num}_{home}_vs_{away}".replace(" ", "_") in tournament_rounds)
            stats_text += f"Round {round_num}: {completed_in_round}/{matches_in_round} matches - {status}\n"
    
    return stats_text
