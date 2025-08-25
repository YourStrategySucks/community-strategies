---
name: 🎲 Strategy Submission
about: Submit a new roulette strategy to the community collection
title: 'feat(strategy): add [strategy name]'
labels: ['strategy-submission', 'community']
assignees: []
---

## Strategy Information

**Strategy Name:** 
<!-- Provide a clear, descriptive name for your strategy -->

**Your Name/Handle:** 
<!-- How would you like to be credited as the contributor? -->

**Strategy Description:** 
<!-- Provide a detailed description of how your strategy works -->

## Strategy Details

**Strategy Type:** 
<!-- e.g., Martingale, Progressive, Flat Betting, Custom -->

**Risk Level:** 
<!-- Low / Medium / High -->

**Default Parameters:**
- **Bankroll:** $
- **Base Bet:** $
- **Target Profit:** $

**Special Features:**
<!-- Any unique aspects of your strategy (loss limits, win streaks, etc.) -->

## Implementation

**Strategy File:** 
<!-- What will you name your strategy file? (e.g., my_martingale.py) -->

**Dependencies:** 
<!-- Any special imports or dependencies beyond the core framework -->

**Testing:** 
<!-- Have you tested this strategy? What were the results? -->

## Code Preview
```python
# Paste a preview of your strategy's place_bet method or key logic
def place_bet(self, game_state):
    # Your implementation here
    pass
```

## Checklist

Before submitting, please ensure:

- [ ] I have read the [Contributing Guidelines](../CONTRIBUTING.md)
- [ ] I have tested my strategy with the core framework
- [ ] My strategy includes proper error handling
- [ ] I have provided clear documentation in docstrings
- [ ] My strategy follows the [Strategy Development Guide](../docs/strategy-development.md)
- [ ] I have included appropriate default values in `get_defaults()`
- [ ] My code follows the project's coding standards
- [ ] I am willing to maintain this strategy and respond to issues

## Additional Context

<!-- Add any other context, screenshots, or examples about the strategy here -->

---

**Note:** After creating this issue, you'll need to submit a Pull Request with your strategy implementation. See our [Contributing Guidelines](../CONTRIBUTING.md) for detailed instructions.
