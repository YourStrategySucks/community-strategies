# Contributing to YSS Community Strategies 🎯

Thank you for your interest in contributing to the YSS Community Strategies project! This guide will help you get started with contributing strategies, improvements, and fixes.

## 🚀 Quick Contribution Guide

### 1. Fork & Clone
```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/yss-community-strategies.git
cd yss-community-strategies
```

### 2. Set Up Development Environment
```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run validation tools to ensure everything works
python scripts/validate_strategy_metadata.py
python scripts/check_strategy_requirements.py
```

### 3. Create Your Strategy
```bash
# Create a new branch for your strategy
git checkout -b feature/my-awesome-strategy

# Copy the template
cp docs/STRATEGY_TEMPLATE.py src/yss_strategies/contributed/my_strategy.py

# Edit your strategy file
code src/yss_strategies/contributed/my_strategy.py
```

### 4. Test & Validate
```bash
# Validate your strategy
python scripts/validate_strategy_metadata.py --strategies-dir src/yss_strategies/contributed

# Check requirements
python scripts/check_strategy_requirements.py --strategies-dir src/yss_strategies/contributed

# Benchmark performance
python scripts/benchmark_strategies.py --strategies-dir src/yss_strategies/contributed

# Run unit tests
python -m pytest tests/ -v
```

### 5. Submit Pull Request
```bash
# Commit your changes
git add src/yss_strategies/contributed/my_strategy.py
git commit -m "Add MyStrategy: Brief description of the strategy"

# Push to your fork
git push origin feature/my-awesome-strategy

# Create PR on GitHub
```

## 📋 Strategy Development Guidelines

### Inheritance Pattern

All strategies must inherit from the `CommunityStrategy` base class and follow these patterns:

```python
from yss_strategies.base import CommunityStrategy

class YourStrategy(CommunityStrategy):
    """Your strategy description."""
    
    def _initialize_state(self):
        """Initialize strategy-specific state variables."""
        # Set up your instance variables here
        self.consecutive_losses = 0
        self.custom_state = {}
    
    @classmethod
    def get_defaults(cls) -> Dict[str, Any]:
        """Return default configuration as classmethod."""
        return {
            "contributor_name": "Your Name",
            "strategy_description": "Brief description",
            # ... other parameters
        }
    
    def place_bet(self, game_state):
        """Implement your betting logic."""
        # Access configuration via self.config
        base_bet = self.config["base_bet"]
        return {"red": base_bet}
```

**Key points:**

- ✅ Inherit from `CommunityStrategy`
- ✅ Use `@classmethod` for `get_defaults(cls)`
- ✅ Access configuration via `self.config` (not calling `get_defaults()`)
- ✅ Override `_initialize_state()` for custom state variables

### Required Structure

Every strategy must follow this structure:

```python
class YourStrategy:
    """
    Brief one-line description of your strategy.
    
    Detailed explanation of how the strategy works, its mathematical
    foundation, and any special considerations or parameters.
    
    Example:
        strategy = YourStrategy()
        defaults = strategy.get_defaults()
        bet = strategy.place_bet(game_state)
    """
    
    def get_defaults(self):
        """Return default configuration parameters."""
        return {
            # Required metadata
            "contributor_name": "Your Name or GitHub Username",
            "strategy_description": "One-line description for the UI",
            
            # Recommended parameters
            "bankroll": 1000,
            "base_bet": 10,
            "target_profit": 100,
            
            # Your custom parameters
            "custom_param": "value"
        }
    
    def place_bet(self, game_state):
        """
        Determine betting action based on current game state.
        
        Args:
            game_state: Object with properties:
                - history: List of previous spin results
                - last_result: Most recent spin result
                - current_balance: Current player balance
                - total_bet: Total amount bet so far
                - spin_count: Number of spins played
        
        Returns:
            dict: Betting positions {"red": 10, "black": 5, "0": 1}
            int/float: Single bet amount (placed on red by default)
            None: Skip this round
        """
        # Your betting logic here
        return {"red": 10}
```

### Metadata Requirements

Your `get_defaults()` method must include:

- **`contributor_name`**: Your name or GitHub username
- **`strategy_description`**: One-line description shown in the UI
- **Standard parameters**: `bankroll`, `base_bet`, etc. (recommended)
- **Custom parameters**: Any strategy-specific configuration

### Betting Return Types

The `place_bet()` method can return:

1. **Dictionary**: Multiple bets `{"red": 10, "odd": 5, "1-12": 20}`
2. **Number**: Single bet amount (placed on red)
3. **None**: Skip this round

### Available Bet Types

```python
# Color bets
{"red": amount, "black": amount}

# Even/Odd bets
{"even": amount, "odd": amount}

# High/Low bets
{"high": amount, "low": amount}  # high=19-36, low=1-18

# Dozen bets
{"1-12": amount, "13-24": amount, "25-36": amount}

# Column bets
{"col1": amount, "col2": amount, "col3": amount}

# Straight up bets
{"0": amount, "1": amount, "2": amount, ..., "36": amount}

# Split, street, corner bets (advanced)
{"split_1_2": amount, "street_1_2_3": amount, "corner_1_2_4_5": amount}
```

## 🧪 Testing Your Strategy

### Local Validation

Run all validation checks before submitting:

```bash
# Check strategy structure and metadata
python scripts/validate_strategy_metadata.py

# Verify dependencies and requirements
python scripts/check_strategy_requirements.py

# Performance benchmarking
python scripts/benchmark_strategies.py --spins 1000

# Unit tests
python -m pytest tests/test_strategies.py -v
```

### Writing Tests

Add tests for your strategy in `tests/test_strategies.py`:

```python
def test_my_strategy():
    """Test MyStrategy implementation."""
    from yss_strategies.contributed.my_strategy import MyStrategy
    
    strategy = MyStrategy()
    
    # Test defaults
    defaults = strategy.get_defaults()
    assert "contributor_name" in defaults
    assert "strategy_description" in defaults
    assert defaults["contributor_name"] != ""
    
    # Test betting logic
    from tests.mock_game_state import MockGameState
    game_state = MockGameState()
    
    bet = strategy.place_bet(game_state)
    assert bet is None or isinstance(bet, (dict, int, float))
    
    # Test with history
    game_state.add_results([1, 2, 3, 4, 5])
    bet = strategy.place_bet(game_state)
    assert bet is None or isinstance(bet, (dict, int, float))
```

### Performance Expectations

Your strategy should meet these performance criteria:

- **Execution Time**: < 10 seconds for 1000 spins
- **Memory Usage**: < 100MB during execution
- **Error Rate**: < 1% of betting calls
- **File Size**: < 100KB source code

## 🛡️ Security & Safety Guidelines

### Allowed Dependencies

✅ **Standard Library**
```python
import math
import random
import itertools
import collections
import datetime
import statistics
from typing import Dict, List, Optional
```

✅ **Approved Third-Party**
```python
import numpy as np
import pandas as pd
import scipy.stats
import matplotlib.pyplot as plt  # For visualization only
```

### Forbidden Operations

❌ **File System Access**
```python
# Don't do this
open("file.txt", "r")
with open("data.csv") as f:
    content = f.read()
```

❌ **Network Access**
```python
# Don't do this
import requests
import urllib
import socket
```

❌ **System Operations**
```python
# Don't do this
import os
import sys
import subprocess
os.system("command")
```

❌ **Dangerous Functions**
```python
# Don't do this
eval("code")
exec("code")
__import__("module")
```

### Safe Practices

✅ **Use Configuration**
```python
def get_defaults(self):
    return {
        "data_source": "built_in",  # Not external file
        "api_key": None,  # No external APIs
        "cache_size": 100  # Reasonable limits
    }
```

✅ **Handle Errors Gracefully**
```python
def place_bet(self, game_state):
    try:
        # Your betting logic
        return {"red": 10}
    except Exception as e:
        # Log error and return safe default
        return None
```

## 📊 Documentation Standards

### Code Documentation

```python
class MyStrategy:
    """
    Strategy implementing the Martingale betting system with modifications.
    
    This strategy doubles the bet after each loss and resets to the base bet
    after a win. It includes safety mechanisms to prevent excessive losses.
    
    Mathematical Foundation:
        The Martingale system is based on the probability that a losing streak
        cannot continue indefinitely. However, it requires careful bankroll
        management due to exponential bet growth.
    
    Parameters:
        base_bet (int): Starting bet amount
        max_bet (int): Maximum allowed bet to prevent excessive losses
        reset_on_profit (bool): Whether to reset progression when profitable
    
    Example:
        >>> strategy = MyStrategy()
        >>> defaults = strategy.get_defaults()
        >>> defaults["base_bet"]
        10
    """
    
    def place_bet(self, game_state):
        """
        Place bet using modified Martingale progression.
        
        Args:
            game_state (GameState): Current game state containing:
                - history: List of previous results
                - current_balance: Available funds
                - last_result: Most recent spin outcome
        
        Returns:
            dict: Betting positions, e.g., {"red": 20}
            None: If no bet should be placed
        
        Note:
            The strategy will not bet if the required amount exceeds
            the maximum bet limit or available balance.
        """
        # Implementation details...
```

### README Updates

If your strategy introduces new concepts, update documentation:

1. Add to the "Featured Strategies" table
2. Include in examples if it demonstrates important patterns
3. Update the API reference if you add new methods

## 🔄 Pull Request Process

### Before Submitting

- [ ] Strategy passes all validation scripts
- [ ] Tests added and passing
- [ ] Documentation is complete
- [ ] No forbidden dependencies or operations
- [ ] Performance meets benchmarks
- [ ] Code follows style guidelines

### PR Description Template

```markdown
## Strategy Description
Brief description of what your strategy does and its unique approach.

## Mathematical Foundation
Explain the mathematical or logical basis for your strategy.

## Testing Results
```
✅ Validation passed
✅ Requirements check passed  
✅ Performance benchmark: X bets/second
✅ Unit tests: X/X passing
```

## Example Usage
```python
from yss_strategies.contributed.my_strategy import MyStrategy
strategy = MyStrategy()
# Example of how to use your strategy
```

## Checklist
- [ ] Follows required structure
- [ ] Includes proper metadata
- [ ] Has comprehensive docstrings
- [ ] Passes all validation tests
- [ ] Includes unit tests
- [ ] Performance meets requirements
```

### Review Process

1. **Automated Checks**: GitHub Actions run validation automatically
2. **Code Review**: Maintainers review code quality and safety
3. **Performance Review**: Strategy is benchmarked for performance
4. **Community Feedback**: Other contributors may provide feedback
5. **Approval**: Once approved, your strategy will be merged

### After Approval

- Your strategy becomes part of the community collection
- Attribution is maintained in all displays and documentation
- You'll be added to the contributors list
- Performance metrics are tracked in the dashboard

## 🏆 Recognition System

### Contributor Levels

- **🌱 New Contributor**: First strategy merged
- **🌿 Regular Contributor**: 3+ strategies merged
- **🌳 Core Contributor**: 10+ strategies or significant improvements
- **⭐ Strategy Master**: Exceptional strategies with high community adoption

### Achievement Badges

- **🎯 Performance Pro**: Strategy in top 10% for performance
- **📚 Documentation Star**: Excellent documentation and examples
- **🧪 Testing Champion**: Comprehensive test coverage
- **🔧 Bug Hunter**: Finding and fixing issues
- **💡 Innovation Award**: Novel or creative approaches

## 💬 Getting Help

### Before Asking

1. Check the [FAQ](docs/FAQ.md)
2. Search existing [issues](../../issues)
3. Review [strategy examples](docs/EXAMPLES.md)
4. Run validation tools for specific error details

### Where to Get Help

- **💭 General Questions**: [GitHub Discussions](../../discussions)
- **🐛 Bug Reports**: [GitHub Issues](../../issues/new?template=bug-report.md)
- **💡 Feature Ideas**: [GitHub Issues](../../issues/new?template=feature-request.md)
- **📧 Private Questions**: support@yss-strategies.com

### How to Ask Good Questions

1. **Be Specific**: Include exact error messages and steps to reproduce
2. **Provide Context**: Share your strategy code (if not sensitive)
3. **Show Effort**: Explain what you've already tried
4. **Include Environment**: Python version, OS, package versions

Example good question:
```
I'm getting a validation error "Missing required metadata field: contributor_name" 
but I have this in my get_defaults():

```python
def get_defaults(self):
    return {
        "contributor_name": "John Doe",
        # ... rest of config
    }
```

I'm running Python 3.9 on Windows. The validation script output is:
[paste full output here]
```

## 🎉 Thank You!

Every contribution makes the YSS community stronger. Whether you're adding a new strategy, fixing bugs, improving documentation, or helping other contributors, your efforts are appreciated!

Happy coding! 🚀
