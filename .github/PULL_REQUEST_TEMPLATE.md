---
name: 🎲 Strategy Contribution
about: Submit a new roulette strategy to the community
title: 'feat(strategy): add [strategy name]'
---

## Strategy Information

**Strategy Name:** [Name of your strategy]
**Contributor:** [Your name/handle for attribution]
**Strategy Type:** [e.g., Martingale variant, Progressive, Flat betting, Custom]

## Changes Made

**New Files Added:**
- `src/yss_strategies/contributed/[strategy_name].py`
- `tests/test_contributed/test_[strategy_name].py`

**Modified Files:**
- `src/yss_strategies/contributed/__init__.py` (added strategy import)

## Strategy Description

[Provide a clear description of how your strategy works, its risk level, and any special features]

## Testing

**Local Testing Completed:**
- [ ] Strategy implements required interface methods
- [ ] Strategy includes proper error handling
- [ ] Strategy has comprehensive test coverage
- [ ] Strategy follows coding standards (black, pylint, mypy)
- [ ] Strategy includes proper docstrings and metadata

**Performance Results:**
[Include any testing results or performance characteristics you've observed]

## Implementation Details

**Key Features:**
- [List the main features of your strategy]

**Risk Management:**
- [Describe how your strategy handles losses, bankroll management, etc.]

**Dependencies:**
- [List any special dependencies beyond yss-core]

## Checklist

Please ensure your contribution meets these requirements:

- [ ] I have read and followed the [Contributing Guidelines](CONTRIBUTING.md)
- [ ] My strategy follows the [Strategy Development Guide](docs/strategy-development.md)
- [ ] I have included proper `contributor_name` and `strategy_description` in `get_defaults()`
- [ ] My code follows the project's style guidelines (black, pylint)
- [ ] I have added comprehensive tests for my strategy
- [ ] My strategy handles edge cases and errors gracefully
- [ ] I have updated the strategy imports in `__init__.py`
- [ ] My commit messages follow conventional commit format
- [ ] I am willing to maintain this strategy and respond to issues

## Breaking Changes

- [ ] This PR introduces breaking changes
- [ ] This PR is backward compatible

**If breaking changes, please describe:**
[Explain any breaking changes and migration path]

## Additional Notes

[Any additional information, context, or screenshots that would help reviewers understand your contribution]

---

**Review Guidelines for Maintainers:**

1. **Code Quality:** Ensure clean, well-documented code
2. **Testing:** Verify comprehensive test coverage
3. **Performance:** Check for any performance regressions  
4. **Documentation:** Confirm proper strategy metadata and docstrings
5. **Integration:** Test with existing framework and visualization tools

Thank you for contributing to the YSS Strategies community! 🎲
