"""
Terminal Brain - AI-powered terminal assistant
"""

__version__ = "0.1.0"
__author__ = "Terminal Brain Team"
__license__ = "MIT"

from terminalbrain.config import Config, load_config
from terminalbrain.core import CommandParser, HistoryAnalyzer
from terminalbrain.ai import RecommendationEngine

__all__ = [
    "Config",
    "load_config",
    "CommandParser",
    "HistoryAnalyzer",
    "RecommendationEngine",
]
