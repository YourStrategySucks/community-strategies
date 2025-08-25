"""
Test suite for YSS community strategies.

This module provides comprehensive testing for all community-contributed
strategies to ensure they meet the required interface and quality standards.
"""

import pytest
import importlib
import inspect
from pathlib import Path
from typing import Dict, Any
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# Mock game state for testing
class MockGameState:
    """Mock game state for strategy testing."""
    
    def __init__(self):
        self.history = []
        self.last_result = None
        self.current_balance = 1000
        self.total_bet = 0
        self.spin_count = 0
    
    def add_result(self, result):
        """Add a spin result to history."""
        self.history.append(result)
        self.last_result = result
        self.spin_count += 1
    
    def add_results(self, results):
        """Add multiple results to history."""
        for result in results:
            self.add_result(result)

def get_strategy_classes_from_contributed():
    """Dynamically discover all strategy classes in the contributed folder."""
    import importlib.util
    import os
    import sys
    import types
    strategy_classes = []
    contributed_dir = os.path.join(os.path.dirname(__file__), '..', 'src', 'yss_strategies', 'contributed')
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
    
    for fname in os.listdir(contributed_dir):
        if fname.endswith('.py') and not fname.startswith('_'):
            modname = fname[:-3]
            spec = importlib.util.spec_from_file_location(f"yss_strategies.contributed.{modname}", os.path.join(contributed_dir, fname))
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                for name, obj in vars(module).items():
                    if (inspect.isclass(obj)
                        and name.endswith('Strategy')
                        and hasattr(obj, 'place_bet')
                        and hasattr(obj, 'get_defaults')
                        and obj.__module__ == module.__name__):  # Ensure it's defined in this module
                        strategy_classes.append(obj)
    return strategy_classes

import pytest

@pytest.mark.parametrize("strategy_class", get_strategy_classes_from_contributed())
def test_strategy_interface(strategy_class):
    """Test that each strategy implements the required interface and metadata."""
    # Import the base class for inheritance checking
    from yss_strategies.base import CommunityStrategy
    
    # Test inheritance
    assert issubclass(strategy_class, CommunityStrategy), f"Strategy {strategy_class.__name__} must inherit from CommunityStrategy"
    
    # Test class-level requirements
    assert hasattr(strategy_class, 'get_defaults'), "Strategy class must have get_defaults classmethod"
    assert hasattr(strategy_class, 'place_bet'), "Strategy class must have place_bet method"
    
    # Verify get_defaults is a classmethod
    assert isinstance(inspect.getattr_static(strategy_class, 'get_defaults'), classmethod), "get_defaults must be a classmethod"
    
    # Test method signatures - check unbound methods from class to include 'self'/'cls'
    place_bet_sig = inspect.signature(strategy_class.place_bet)
    assert len(place_bet_sig.parameters) == 2, f"place_bet must take (self, game_state), got {list(place_bet_sig.parameters.keys())}"
    
    # For classmethods, we need to check the unbound method or verify it's a classmethod
    if isinstance(inspect.getattr_static(strategy_class, 'get_defaults'), classmethod):
        # It's a classmethod - the signature will be empty when called on the class
        get_defaults_sig = inspect.signature(strategy_class.get_defaults)
        assert len(get_defaults_sig.parameters) == 0, f"get_defaults classmethod should have no visible parameters, got {list(get_defaults_sig.parameters.keys())}"
    else:
        # Regular method - should have cls parameter
        get_defaults_sig = inspect.signature(strategy_class.get_defaults)
        assert len(get_defaults_sig.parameters) == 1, f"get_defaults must take (cls), got {list(get_defaults_sig.parameters.keys())}"
    
    # Test instantiation
    strategy = strategy_class()
    
    # Test metadata from classmethod
    defaults = strategy_class.get_defaults()
    assert isinstance(defaults, dict), "get_defaults must return dictionary"
    
    required_fields = ["contributor_name", "strategy_description"]
    for field in required_fields:
        assert field in defaults, f"Missing required field: {field}"
        assert isinstance(defaults[field], str), f"{field} must be string"
        assert defaults[field].strip() != "", f"{field} cannot be empty"
    
    recommended_fields = ["bankroll", "base_bet"]
    for field in recommended_fields:
        if field in defaults:
            assert isinstance(defaults[field], (int, float)), f"{field} must be numeric"
            assert defaults[field] > 0, f"{field} must be positive"

@pytest.mark.parametrize("strategy_class", get_strategy_classes_from_contributed())
def test_strategy_betting(strategy_class):
    """Test betting logic for each strategy."""
    strategy = strategy_class()
    game_state = MockGameState()
    bet = strategy.place_bet(game_state)
    assert bet is not None, "Strategy should place initial bet"
    assert isinstance(bet, (dict, int, float)), "Bet must be dict, int, or float"
    if isinstance(bet, dict):
        assert all(isinstance(v, (int, float)) for v in bet.values()), "Bet amounts must be numeric"
        assert all(v >= 0 for v in bet.values()), "Bet amounts must be non-negative"
    elif isinstance(bet, (int, float)):
        assert bet >= 0, "Bet amount must be non-negative"
    # Test betting with history
    game_state.add_results([1, 2, 3, 4, 5])
    bet = strategy.place_bet(game_state)
    if bet is not None:
        assert isinstance(bet, (dict, int, float)), "Bet must be dict, int, float, or None"

@pytest.mark.parametrize("strategy_class", get_strategy_classes_from_contributed())
def test_strategy_safety(strategy_class):
    """Test that strategies don't violate safety constraints."""
    strategy = strategy_class()
    game_state = MockGameState()
    game_state.current_balance = 100  # Limited balance
    for i in range(50):
        game_state.add_result(i % 37)
        bet = strategy.place_bet(game_state)
        if bet is not None:
            if isinstance(bet, dict):
                total_bet = sum(bet.values())
            elif isinstance(bet, (int, float)):
                total_bet = bet
            else:
                total_bet = 0
            assert total_bet <= game_state.current_balance, f"Strategy bet {total_bet} exceeds balance {game_state.current_balance}"

@pytest.mark.parametrize("strategy_class", get_strategy_classes_from_contributed())
def test_strategy_performance(strategy_class):
    """Test strategy performance characteristics."""
    import time
    strategy = strategy_class()
    game_state = MockGameState()
    start_time = time.time()
    for i in range(1000):
        game_state.add_result(i % 37)
        bet = strategy.place_bet(game_state)
    end_time = time.time()
    execution_time = end_time - start_time
    bets_per_second = 1000 / execution_time
    assert bets_per_second > 100, f"Strategy too slow: {bets_per_second:.1f} bets/sec"

@pytest.mark.parametrize("strategy_class", get_strategy_classes_from_contributed())
def test_strategy_consistency(strategy_class):
    """Test that strategy produces consistent results."""
    def run_sequence():
        strategy = strategy_class()
        game_state = MockGameState()
        results = []
        for i in range(20):
            game_state.add_result(i % 37)
            bet = strategy.place_bet(game_state)
            results.append(bet)
        return results
    results1 = run_sequence()
    results2 = run_sequence()
    assert results1 == results2, "Strategy should be deterministic"

def test_strategy_discovery():
    """Test that at least one strategy is discovered in contributed folder."""
    strategy_classes = get_strategy_classes_from_contributed()
    assert len(strategy_classes) > 0, "No strategies discovered in contributed folder"
    for strategy_class in strategy_classes:
        assert hasattr(strategy_class, 'place_bet'), "Discovered class should have place_bet"
        assert hasattr(strategy_class, 'get_defaults'), "Discovered class should have get_defaults"

# Utility functions for strategy testing
if __name__ == "__main__":
    # Run tests when executed directly
    pytest.main([__file__, "-v"])
