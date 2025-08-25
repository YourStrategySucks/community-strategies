"""
Base classes for YSS community strategies.

This module provides the base interface that community strategies should implement
to be compatible with the YSS framework.
"""

from typing import Dict, Any, Optional, Union
from abc import ABC, abstractmethod


class CommunityStrategy(ABC):
    """
    Base class for community-contributed strategies.
    
    All community strategies should inherit from this class and implement
    the required abstract methods.
    """
    
    def __init__(self, **kwargs):
        """
        Initialize the strategy with configuration parameters.
        
        Args:
            **kwargs: Configuration parameters that override defaults
        """
        defaults = self.get_defaults()
        self.config = {**defaults, **kwargs}  # kwargs override defaults
        
        # Extract common configuration
        self.contributor_name = self.config['contributor_name']
        self.strategy_description = self.config['strategy_description']
        self.bankroll = self.config.get('bankroll', 1000)
        self.base_bet = self.config.get('base_bet', 10)
        
        # Initialize strategy state
        self._initialize_state()
    
    def _initialize_state(self):
        """Initialize strategy-specific state variables."""
        # Override in subclasses to set up state tracking
        pass
    
    @classmethod
    @abstractmethod
    def get_defaults(cls) -> Dict[str, Any]:
        """
        Return default configuration parameters for this strategy.
        
        Must include at minimum:
        - contributor_name: Name or GitHub username of contributor
        - strategy_description: Brief description of the strategy
        
        Returns:
            dict: Default configuration parameters
        """
        pass
    
    @abstractmethod
    def place_bet(self, game_state) -> Optional[Union[Dict[str, float], int, float]]:
        """
        Determine betting action based on current game state.
        
        Args:
            game_state: Object containing game information with attributes:
                - history: List of previous spin results [0-36]
                - last_result: Most recent spin result
                - current_balance: Current player balance
                - total_bet: Total amount bet in this session
                - spin_count: Number of spins played
        
        Returns:
            dict: Betting positions {"bet_type": amount, ...}
            int/float: Single bet amount (placed on red by default)
            None: Skip this round
        """
        pass
    
    def reset(self):
        """Reset strategy state to initial conditions."""
        self._initialize_state()
    
    def get_info(self) -> Dict[str, Any]:
        """Get strategy information for display purposes."""
        return {
            'name': self.__class__.__name__,
            'contributor_name': self.contributor_name,
            'strategy_description': self.strategy_description,
            'config': self.config.copy()
        }
