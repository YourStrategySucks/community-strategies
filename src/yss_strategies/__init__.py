"""
YSS Community Strategies Package

This package contains community-contributed strategies for the YSS 
(Yet Another Simulation System) roulette simulator.
"""

__version__ = "1.0.0"
__author__ = "YSS Community"
__email__ = "yourstrategysucks@gmail.com"

from .contributed import *

# Package metadata
__all__ = [
    # Re-export contributed strategies
    "contributed",
]
