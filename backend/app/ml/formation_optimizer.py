import numpy as np
from typing import List, Dict, Tuple, Any
from itertools import combinations

class FormationOptimizer:
    """
    Optimizes player formations based on predicted performance and formation constraints.
    Uses a greedy algorithm with constraints to find the optimal lineup.
    """
    
    def __init__(self):
        # Valid formations in Serie A Fantacalcio
        self.valid_formations = {
            '3-4-3': {'DEF': 3, 'MID': 4, 'FWD': 3},
            '3-5-2': {'DEF': 3, 'MID': 5, 'FWD': 2},
            '4-3-3': {'DEF': 4, 'MID': 3, 'FWD': 3},
            '4-4-2': {'DEF': 4, 'MID': 4, 'FWD': 2},
            '4-5-1': {'DEF': 4, 'MID': 5, 'FWD': 1},
            '5-3-2': {'DEF': 5, 'MID': 3, 'FWD': 2},
            '5-4-1': {'DEF': 5, 'MID': 4, 'FWD': 1}
        }
    
    def optimize_lineup(self, 
                        squad: List[Dict[str, Any]], 
                        formation: str = None, 
                        matchday: int = None) -> Dict[str, Any]:
        """
        Optimizes the lineup based on player predictions for a given matchday.
        
        Args:
            squad: List of player dictionaries with role, prediction, and other attributes
            formation: Specific formation to use (if None, will find the best formation)
            matchday: The matchday to optimize for (affects predictions)
            
        Returns:
            Dictionary with optimized lineup and bench players
        """
        # Group players by role
        players_by_role = {
            'GK': [p for p in squad if p['role'] == 'GK'],
            'DEF': [p for p in squad if p['role'] == 'DEF'],
            'MID': [p for p in squad if p['role'] == 'MID'],
            'FWD': [p for p in squad if p['role'] == 'FWD']
        }
        
        # Sort players by prediction (descending)
        for role in players_by_role:
            players_by_role[role] = sorted(
                players_by_role[role], 
                key=lambda p: p.get('prediction', 0), 
                reverse=True
            )
        
        # If formation is specified, optimize for that formation
        if formation and formation in self.valid_formations:
            return self._create_lineup_for_formation(players_by_role, formation)
        
        # Otherwise, find the best formation
        best_formation = None
        best_score = -1
        best_lineup = None
        
        for form in self.valid_formations:
            lineup = self._create_lineup_for_formation(players_by_role, form)
            score = self._calculate_lineup_score(lineup)
            
            if score > best_score:
                best_score = score
                best_formation = form
                best_lineup = lineup
        
        if best_lineup:
            best_lineup['formation'] = best_formation
            best_lineup['score'] = best_score
            
        return best_lineup
    
    def _create_lineup_for_formation(self, 
                                    players_by_role: Dict[str, List[Dict[str, Any]]], 
                                    formation: str) -> Dict[str, Any]:
        """
        Creates the best possible lineup for a given formation.
        
        Args:
            players_by_role: Dictionary of players grouped by role
            formation: Formation string (e.g., '3-4-3')
            
        Returns:
            Dictionary with lineup and bench players
        """
        # Get formation requirements
        requirements = self.valid_formations[formation]
        
        # Always select the best goalkeeper
        gk = players_by_role['GK'][0] if players_by_role['GK'] else None
        
        # Select the best players for each position based on formation
        lineup = {
            'GK': [gk] if gk else [],
            'DEF': players_by_role['DEF'][:requirements['DEF']] if len(players_by_role['DEF']) >= requirements['DEF'] else players_by_role['DEF'],
            'MID': players_by_role['MID'][:requirements['MID']] if len(players_by_role['MID']) >= requirements['MID'] else players_by_role['MID'],
            'FWD': players_by_role['FWD'][:requirements['FWD']] if len(players_by_role['FWD']) >= requirements['FWD'] else players_by_role['FWD']
        }
        
        # Create bench (remaining players)
        starters = [p for role in lineup for p in lineup[role]]
        bench = [p for role in players_by_role for p in players_by_role[role] if p not in starters]
        
        return {
            'lineup': lineup,
            'bench': bench,
            'formation': formation
        }
    
    def _calculate_lineup_score(self, lineup_data: Dict[str, Any]) -> float:
        """
        Calculates the total predicted score for a lineup.
        
        Args:
            lineup_data: Dictionary with lineup and bench players
            
        Returns:
            Total predicted score
        """
        lineup = lineup_data['lineup']
        total_score = sum(
            player.get('prediction', 0) 
            for role in lineup 
            for player in lineup[role]
        )
        return total_score
    
    def recommend_transfers(self, 
                           squad: List[Dict[str, Any]], 
                           available_players: List[Dict[str, Any]], 
                           budget: float = 0,
                           max_transfers: int = 2) -> List[Dict[str, Any]]:
        """
        Recommends optimal player transfers based on predictions and budget.
        
        Args:
            squad: Current squad players
            available_players: Available players for transfer
            budget: Available transfer budget
            max_transfers: Maximum number of transfers to recommend
            
        Returns:
            List of recommended transfers (player to sell, player to buy)
        """
        # Group players by role
        squad_by_role = {
            'GK': [p for p in squad if p['role'] == 'GK'],
            'DEF': [p for p in squad if p['role'] == 'DEF'],
            'MID': [p for p in squad if p['role'] == 'MID'],
            'FWD': [p for p in squad if p['role'] == 'FWD']
        }
        
        available_by_role = {
            'GK': [p for p in available_players if p['role'] == 'GK'],
            'DEF': [p for p in available_players if p['role'] == 'DEF'],
            'MID': [p for p in available_players if p['role'] == 'MID'],
            'FWD': [p for p in available_players if p['role'] == 'FWD']
        }
        
        # Sort by prediction
        for role in squad_by_role:
            squad_by_role[role] = sorted(
                squad_by_role[role], 
                key=lambda p: p.get('prediction', 0)
            )
            
            available_by_role[role] = sorted(
                available_by_role[role], 
                key=lambda p: p.get('prediction', 0),
                reverse=True
            )
        
        recommendations = []
        remaining_budget = budget
        
        # For each role, find potential upgrades
        for role in ['GK', 'DEF', 'MID', 'FWD']:
            # Skip if no players in this role or no available players
            if not squad_by_role[role] or not available_by_role[role]:
                continue
                
            # Consider worst performers in squad for replacement
            candidates_to_sell = squad_by_role[role][:3]  # Consider worst 3 players
            
            for player_to_sell in candidates_to_sell:
                # Find better players available
                better_players = [
                    p for p in available_by_role[role] 
                    if p.get('prediction', 0) > player_to_sell.get('prediction', 0) + 0.5  # Significant improvement
                ]
                
                for player_to_buy in better_players:
                    # Check if we can afford this transfer
                    transfer_cost = player_to_buy.get('price', 0) - player_to_sell.get('price', 0)
                    
                    if transfer_cost <= remaining_budget:
                        # Calculate improvement
                        improvement = player_to_buy.get('prediction', 0) - player_to_sell.get('prediction', 0)
                        
                        recommendations.append({
                            'sell': player_to_sell,
                            'buy': player_to_buy,
                            'cost': transfer_cost,
                            'improvement': improvement,
                            'score': improvement / (transfer_cost if transfer_cost > 0 else 0.1)  # Value for money
                        })
        
        # Sort recommendations by score (best value first)
        recommendations = sorted(recommendations, key=lambda r: r['score'], reverse=True)
        
        # Return top recommendations within max_transfers limit
        return recommendations[:max_transfers]
    
    def optimize_for_next_n_matchdays(self, 
                                     squad: List[Dict[str, Any]], 
                                     n_matchdays: int = 5) -> Dict[str, Any]:
        """
        Optimizes lineup considering predictions for the next N matchdays.
        Useful for longer-term planning.
        
        Args:
            squad: List of player dictionaries
            n_matchdays: Number of future matchdays to consider
            
        Returns:
            Dictionary with optimized lineup and formation
        """
        # For each player, calculate average prediction over next N matchdays
        for player in squad:
            future_predictions = [
                player.get(f'prediction_matchday_{i}', player.get('prediction', 0)) 
                for i in range(1, n_matchdays + 1)
            ]
            player['avg_future_prediction'] = sum(future_predictions) / len(future_predictions)
        
        # Create a copy of squad with avg_future_prediction as the main prediction
        future_squad = []
        for player in squad:
            player_copy = player.copy()
            player_copy['prediction'] = player.get('avg_future_prediction', 0)
            future_squad.append(player_copy)
        
        # Use the regular optimization with the modified predictions
        return self.optimize_lineup(future_squad)