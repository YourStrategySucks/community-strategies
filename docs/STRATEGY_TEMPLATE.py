"""
Strategy Template for YSS Community Contributions

This template provides the basic structure for creating a new strategy
for the YSS (Yet Another Simulation System) platform.

Copy this file and modify it to create your own strategy.
"""

from typing import Dict, Any, Optional, Union
from yss_strategies.base import CommunityStrategy


class TemplateStrategy(CommunityStrategy):
    """
    Template strategy demonstrating the required structure and best practices.
    
    This is a template strategy that shows how to implement the required
    methods and structure for YSS community strategies. Replace this
    docstring with a description of your actual strategy.
    
    Your strategy description should include:
    - Brief explanation of the betting approach
    - Mathematical foundation (if applicable)
    - Key parameters and their effects
    - Example usage
    
    Example:
        strategy = TemplateStrategy()
        defaults = strategy.get_defaults()
        bet = strategy.place_bet(game_state)
    """
    
    def _initialize_state(self):
        """
        Initialize strategy-specific state variables.
        
        Override this method to set up any instance variables your strategy
        needs to maintain state between betting rounds.
        """
        # Example state variables
        self.consecutive_losses = 0
        self.last_bet_amount = 0
        self.total_profit = 0
        
        # You can add your own state variables here
        # self.custom_state = {}
    
    @classmethod
    def get_defaults(cls) -> Dict[str, Any]:
        """
        Return default configuration parameters for this strategy.
        
        This method MUST be implemented and MUST return a dictionary
        containing at least the required metadata fields.
        
        Required fields:
            contributor_name (str): Your name or GitHub username
            strategy_description (str): One-line description for the UI
        
        Recommended fields:
            bankroll (int): Starting bankroll amount
            base_bet (int): Base betting amount
            target_profit (int): Profit target for the session
        
        Returns:
            dict: Configuration parameters
        """
        return {
            # REQUIRED: Replace with your information
            "contributor_name": "Your Name",
            "strategy_description": "Template strategy demonstrating basic structure",
            
            # RECOMMENDED: Standard parameters
            "bankroll": 1000,
            "base_bet": 10,
            "target_profit": 100,
            
            # CUSTOM: Add your strategy-specific parameters here
            "max_consecutive_losses": 5,
            "progression_multiplier": 2.0,
            "reset_on_win": True,
            
            # Example of different parameter types
            "use_progression": True,
            "stop_loss_percentage": 0.5,
            "preferred_bet_types": ["red", "black"],
        }
    
    def place_bet(self, game_state) -> Optional[Union[Dict[str, float], int, float]]:
        """
        Determine betting action based on current game state.
        
        This method MUST be implemented. It receives the current game
        state and should return betting instructions.
        
        Args:
            game_state: Object containing game information with attributes:
                - history (list): Previous spin results [0-36]
                - last_result (int): Most recent spin result
                - current_balance (float): Current player balance
                - total_bet (float): Total amount bet in this session
                - spin_count (int): Number of spins played
        
        Returns:
            dict: Betting positions {"bet_type": amount, ...}
                  Valid bet types: "red", "black", "even", "odd", "high", "low",
                  "1-12", "13-24", "25-36", "col1", "col2", "col3",
                  "0", "1", "2", ..., "36"
            
            int/float: Single bet amount (will be placed on red by default)
            
            None: Skip this round (no bet)
        
        Example returns:
            {"red": 10, "odd": 5}  # Multiple bets
            20                      # Single bet on red
            None                    # No bet this round
        """
        # Get configuration from self.config instead of calling get_defaults()
        base_bet = self.config["base_bet"]
        max_losses = self.config["max_consecutive_losses"]
        
        # Example strategy logic: Simple progression on red
        
        # Check if we have enough history to make decisions
        if len(game_state.history) < 1:
            # First spin or no history - place base bet
            self.last_bet_amount = base_bet
            return {"red": base_bet}
        
        # Check the last result
        last_result = game_state.last_result
        
        # Determine if last bet won (assuming we bet on red)
        # Red numbers: 1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36
        red_numbers = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
        last_bet_won = last_result in red_numbers
        
        if last_bet_won:
            # Win: Reset progression
            self.consecutive_losses = 0
            self.last_bet_amount = base_bet
            bet_amount = base_bet
        else:
            # Loss: Increase progression
            self.consecutive_losses += 1
            
            # Check if we've hit maximum consecutive losses
            if self.consecutive_losses >= max_losses:
                # Stop betting or reset
                return None
            
            # Double the bet (Martingale-style progression)
            multiplier = self.config["progression_multiplier"]
            bet_amount = int(self.last_bet_amount * multiplier)
            self.last_bet_amount = bet_amount
        
        # Safety check: Don't bet more than we have
        if bet_amount > game_state.current_balance:
            return None
        
        # Safety check: Don't bet more than a reasonable amount
        max_bet = self.config["bankroll"] * 0.25  # Max 25% of bankroll
        if bet_amount > max_bet:
            return None
        
        # Place the bet on red
        return {"red": bet_amount}
    
    # OPTIONAL: You can add helper methods for your strategy
    def _analyze_pattern(self, history, pattern_length=5):
        """
        Example helper method to analyze recent patterns.
        
        Args:
            history (list): List of recent spin results
            pattern_length (int): How many spins to analyze
        
        Returns:
            dict: Pattern analysis results
        """
        if len(history) < pattern_length:
            return {"insufficient_data": True}
        
        recent = history[-pattern_length:]
        red_numbers = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
        
        red_count = sum(1 for num in recent if num in red_numbers)
        black_count = sum(1 for num in recent if num != 0 and num not in red_numbers)
        zero_count = sum(1 for num in recent if num == 0)
        
        return {
            "red_ratio": red_count / pattern_length,
            "black_ratio": black_count / pattern_length,
            "zero_ratio": zero_count / pattern_length,
            "red_streak": self._count_streak(recent, red_numbers),
            "black_streak": self._count_streak(recent, red_numbers, invert=True)
        }
    
    def _count_streak(self, results, target_set, invert=False):
        """
        Count consecutive occurrences at the end of results.
        
        Args:
            results (list): List of spin results
            target_set (set): Set of numbers to count
            invert (bool): If True, count numbers NOT in target_set
        
        Returns:
            int: Length of current streak
        """
        if not results:
            return 0
        
        streak = 0
        for result in reversed(results):
            if invert:
                if result != 0 and result not in target_set:
                    streak += 1
                else:
                    break
            else:
                if result in target_set:
                    streak += 1
                else:
                    break
        
        return streak
    
    # OPTIONAL: Add validation method for your parameters
    def validate_config(self, config):
        """
        Validate strategy configuration parameters.
        
        Args:
            config (dict): Configuration to validate
        
        Returns:
            tuple: (is_valid, error_message)
        """
        required_fields = ["contributor_name", "strategy_description"]
        
        for field in required_fields:
            if field not in config:
                return False, f"Missing required field: {field}"
            if not config[field] or not config[field].strip():
                return False, f"Empty required field: {field}"
        
        # Validate numeric parameters
        numeric_fields = ["bankroll", "base_bet", "target_profit"]
        for field in numeric_fields:
            if field in config:
                if not isinstance(config[field], (int, float)) or config[field] <= 0:
                    return False, f"Invalid {field}: must be positive number"
        
        # Custom validation for your parameters
        if "max_consecutive_losses" in config:
            if config["max_consecutive_losses"] < 1:
                return False, "max_consecutive_losses must be at least 1"
        
        if "progression_multiplier" in config:
            if config["progression_multiplier"] < 1.0:
                return False, "progression_multiplier must be at least 1.0"
        
        return True, ""

# Example of how to test your strategy locally
if __name__ == "__main__":
    # This code will run when you execute the file directly
    # Use it for testing your strategy during development
    
    print("Testing TemplateStrategy...")
    
    # Create strategy instance
    strategy = TemplateStrategy()
    
    # Test get_defaults
    defaults = strategy.get_defaults()
    print(f"Defaults: {defaults}")
    
    # Test validation
    is_valid, error = strategy.validate_config(defaults)
    print(f"Validation: {is_valid}, {error}")
    
    # Create mock game state for testing
    class MockGameState:
        def __init__(self):
            self.history = []
            self.last_result = None
            self.current_balance = 1000
            self.total_bet = 0
            self.spin_count = 0
        
        def add_result(self, result):
            self.history.append(result)
            self.last_result = result
            self.spin_count += 1
    
    # Test betting logic
    game_state = MockGameState()
    
    # Test initial bet
    bet = strategy.place_bet(game_state)
    print(f"Initial bet: {bet}")
    
    # Simulate some spins
    test_results = [12, 5, 0, 23, 8]  # Mix of red, black, zero
    for result in test_results:
        game_state.add_result(result)
        bet = strategy.place_bet(game_state)
        print(f"After {result}: bet = {bet}")
    
    print("Strategy test completed!")
