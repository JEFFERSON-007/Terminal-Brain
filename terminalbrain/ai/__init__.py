"""
AI and recommendation modules
"""

from terminalbrain.ai.llm_engine import LLMEngine
from terminalbrain.ai.ml_predictor import MLPredictor
from terminalbrain.ai.recommendation_engine import RecommendationEngine
from terminalbrain.ai.error_debugger import ErrorDebugger

__all__ = [
    "LLMEngine",
    "MLPredictor",
    "RecommendationEngine",
    "ErrorDebugger",
]
