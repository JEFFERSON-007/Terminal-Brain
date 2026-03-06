"""Advanced Terminal Brain features for intelligent terminal assistance."""

from .error_analyzer import ErrorAnalyzer, ErrorPattern, ErrorSuggestion
from .command_predictor import CommandPredictor, CommandSequence
from .workflow_detector import WorkflowDetector, WorkflowPattern
from .command_explainer import CommandExplainer, CommandExplanation
from .script_generator import ScriptGenerator, GeneratedScript
from .alias_suggester import AliasSuggester, AliasSuggestion
from .workflow_recommender import WorkflowRecommender, WorkflowRecommendation
from .learning_feedback import LearningFeedback, FeedbackEntry
from .safety_checker import SafetyChecker, SafetyRisk

__all__ = [
    "ErrorAnalyzer",
    "ErrorPattern",
    "ErrorSuggestion",
    "CommandPredictor",
    "CommandSequence",
    "WorkflowDetector",
    "WorkflowPattern",
    "CommandExplainer",
    "CommandExplanation",
    "ScriptGenerator",
    "GeneratedScript",
    "AliasSuggester",
    "AliasSuggestion",
    "WorkflowRecommender",
    "WorkflowRecommendation",
    "LearningFeedback",
    "FeedbackEntry",
    "SafetyChecker",
    "SafetyRisk",
]
