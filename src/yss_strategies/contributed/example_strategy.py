"""
Example Strategy for YSS Community

This is a simple example strategy that demonstrates the basic
structure and requirements for YSS community strategies.
"""

from typing import Dict, Any, Optional, Union
from ..base import CommunityStrategy


class ExampleStrategy(CommunityStrategy):
    """
    Simple example strategy using basic progression on red bets.
    
    This strategy demonstrates the minimum required structure for YSS
    community strategies. It implements a simple Martingale-style
    progression on red bets with safety limits.
    
    The strategy doubles the bet after each loss and resets to the
    base bet after a win. It includes safety mechanisms to prevent
    excessive losses.
    
    Example:
        strategy = ExampleStrategy()
        defaults = strategy.get_defaults()
        bet = strategy.place_bet(game_state)
    """
    
    def _initialize_state(self):
        """Initialize strategy state."""
        self.consecutive_losses = 0
        self.last_bet_amount = 0
    
    @classmethod
    def get_defaults(cls) -> Dict[str, Any]:
        """Return default configuration parameters."""
        return {
            "contributor_name": "YSS Team",
            "strategy_description": "Simple Martingale progression on red",
            "bankroll": 1000,
            "base_bet": 10,
            "target_profit": 100,
            "max_consecutive_losses": 6,
            "progression_multiplier": 2.0
        }
    
    def place_bet(self, game_state) -> Optional[Union[Dict[str, float], int, float]]:
        """
        Place bet using Martingale progression on red.
        
        Args:
            game_state: Current game state
            
        Returns:
            dict: Betting positions or None for no bet
        """
        base_bet = self.config["base_bet"]
        max_losses = self.config["max_consecutive_losses"]
        
        # First bet
        if len(game_state.history) < 1:
            self.last_bet_amount = base_bet
            return {"red": base_bet}
        
        # Check last result
        last_result = game_state.last_result
        red_numbers = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
        last_bet_won = last_result in red_numbers
        
        if last_bet_won:
            # Win: Reset progression
            self.consecutive_losses = 0
            self.last_bet_amount = base_bet
            bet_amount = base_bet
        else:
            # Loss: Increase bet
            self.consecutive_losses += 1
            
            if self.consecutive_losses >= max_losses:
                return None  # Stop betting
            
            multiplier = self.config["progression_multiplier"]
            bet_amount = int(self.last_bet_amount * multiplier)
            self.last_bet_amount = bet_amount
        
        # Safety checks
        if bet_amount > game_state.current_balance:
            return None
        
        max_bet = self.config["bankroll"] * 0.25
        if bet_amount > max_bet:
            return None
        
        return {"red": bet_amount}
