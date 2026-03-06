"""Learning Feedback Loop - Incorporates user feedback to improve suggestions."""

import json
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
from enum import Enum


class FeedbackType(Enum):
    """Types of user feedback."""

    ACCEPTED = "accepted"  # User accepted the suggestion
    REJECTED = "rejected"  # User rejected the suggestion
    MODIFIED = "modified"  # User modified the suggestion
    HELPFUL = "helpful"  # User marked as helpful
    NOT_HELPFUL = "not_helpful"  # User marked as not helpful


@dataclass
class FeedbackEntry:
    """A feedback entry for learning."""

    suggestion: str  # The suggested command/fix
    feedback_type: str  # Type of feedback
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    user_modification: Optional[str] = None  # What user changed it to
    context: Dict[str, str] = field(default_factory=dict)  # Context info
    confidence_before: float = 0.0
    confidence_after: float = 0.0


class LearningFeedback:
    """System for learning from user feedback to improve suggestions."""

    def __init__(self, history_file: Optional[Path] = None):
        """
        Initialize Learning Feedback system.

        Args:
            history_file: Path to feedback history file
        """
        self.history_file = history_file
        self.feedback_history: List[FeedbackEntry] = []
        self.suggestion_scores: Dict[str, float] = {}  # Score adjustments per suggestion
        self.accepted_patterns: Dict[str, int] = {}  # Pattern -> acceptance count

        if history_file and history_file.exists():
            self.load_history(history_file)

    def record_feedback(
        self,
        suggestion: str,
        feedback_type: FeedbackType,
        user_modification: Optional[str] = None,
        context: Optional[Dict[str, str]] = None,
        confidence_before: float = 0.5,
    ) -> FeedbackEntry:
        """
        Record user feedback on a suggestion.

        Args:
            suggestion: The suggested command
            feedback_type: Type of feedback
            user_modification: If modified, what the user changed it to
            context: Context information (e.g., command type, error type)
            confidence_before: Model's confidence in suggestion

        Returns:
            FeedbackEntry that was recorded
        """
        entry = FeedbackEntry(
            suggestion=suggestion,
            feedback_type=feedback_type.value,
            user_modification=user_modification,
            context=context or {},
            confidence_before=confidence_before,
        )

        self.feedback_history.append(entry)

        # Update scores based on feedback
        self._update_suggestion_score(suggestion, feedback_type, confidence_before)

        # Update patterns
        self._update_patterns(suggestion, feedback_type)

        return entry

    def _update_suggestion_score(
        self, suggestion: str, feedback_type: FeedbackType, confidence: float
    ) -> None:
        """Update the score/weight of a suggestion based on feedback."""
        if suggestion not in self.suggestion_scores:
            self.suggestion_scores[suggestion] = confidence

        current_score = self.suggestion_scores[suggestion]

        # Adjust score based on feedback type
        if feedback_type == FeedbackType.ACCEPTED:
            # User accepted: increase score
            adjustment = 0.05
            self.suggestion_scores[suggestion] = min(1.0, current_score + adjustment)

        elif feedback_type == FeedbackType.REJECTED:
            # User rejected: decrease score
            adjustment = 0.1
            self.suggestion_scores[suggestion] = max(0.0, current_score - adjustment)

        elif feedback_type == FeedbackType.MODIFIED:
            # User modified: neutral to slightly negative
            adjustment = 0.02
            self.suggestion_scores[suggestion] = max(0.0, current_score - adjustment)

        elif feedback_type == FeedbackType.HELPFUL:
            # User marked helpful: boost score
            adjustment = 0.08
            self.suggestion_scores[suggestion] = min(1.0, current_score + adjustment)

        elif feedback_type == FeedbackType.NOT_HELPFUL:
            # User marked unhelpful: reduce score
            adjustment = 0.15
            self.suggestion_scores[suggestion] = max(0.0, current_score - adjustment)

    def _update_patterns(
        self, suggestion: str, feedback_type: FeedbackType
    ) -> None:
        """Extract and update command patterns from feedback."""
        if feedback_type == FeedbackType.ACCEPTED:
            # Extract base command
            base_cmd = suggestion.split()[0] if suggestion.split() else suggestion

            if base_cmd not in self.accepted_patterns:
                self.accepted_patterns[base_cmd] = 0
            self.accepted_patterns[base_cmd] += 1

    def get_suggestion_score(self, suggestion: str) -> float:
        """Get the learned score for a suggestion."""
        return self.suggestion_scores.get(suggestion, 0.5)

    def get_statistics(self) -> Dict[str, any]:
        """Get feedback statistics."""
        if not self.feedback_history:
            return {
                "total_feedback": 0,
                "acceptance_rate": 0.0,
                "rejection_rate": 0.0,
                "modification_rate": 0.0,
            }

        total = len(self.feedback_history)
        accepted = sum(1 for f in self.feedback_history if f.feedback_type == "accepted")
        rejected = sum(1 for f in self.feedback_history if f.feedback_type == "rejected")
        modified = sum(1 for f in self.feedback_history if f.feedback_type == "modified")

        return {
            "total_feedback": total,
            "acceptance_rate": accepted / total if total > 0 else 0.0,
            "rejection_rate": rejected / total if total > 0 else 0.0,
            "modification_rate": modified / total if total > 0 else 0.0,
            "helpful_rate": sum(
                1 for f in self.feedback_history if f.feedback_type == "helpful"
            )
            / total
            if total > 0
            else 0.0,
            "most_accepted_pattern": max(
                self.accepted_patterns.items(), key=lambda x: x[1], default=(None, 0)
            )[0],
        }

    def get_best_suggestions(self, top_k: int = 10) -> List[tuple]:
        """Get top-scored suggestions."""
        sorted_suggestions = sorted(
            self.suggestion_scores.items(), key=lambda x: x[1], reverse=True
        )
        return sorted_suggestions[:top_k]

    def get_worst_suggestions(self, top_k: int = 10) -> List[tuple]:
        """Get lowest-scored suggestions."""
        sorted_suggestions = sorted(
            self.suggestion_scores.items(), key=lambda x: x[1]
        )
        return sorted_suggestions[:top_k]

    def get_feedback_for_context(self, context: str) -> List[FeedbackEntry]:
        """Get feedback entries matching a context."""
        return [f for f in self.feedback_history if context in str(f.context)]

    def export_insights(self) -> Dict[str, any]:
        """Export learning insights for improvement."""
        return {
            "statistics": self.get_statistics(),
            "best_suggestions": [
                {"suggestion": s, "score": score}
                for s, score in self.get_best_suggestions(5)
            ],
            "worst_suggestions": [
                {"suggestion": s, "score": score}
                for s, score in self.get_worst_suggestions(5)
            ],
            "total_patterns": len(self.accepted_patterns),
            "feedback_entries": len(self.feedback_history),
        }

    def save_history(self, filepath: Path) -> None:
        """Save feedback history to JSON file."""
        filepath.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "feedback_history": [asdict(entry) for entry in self.feedback_history],
            "suggestion_scores": self.suggestion_scores,
            "accepted_patterns": self.accepted_patterns,
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def load_history(self, filepath: Path) -> None:
        """Load feedback history from JSON file."""
        if not filepath.exists():
            return

        with open(filepath, "r") as f:
            data = json.load(f)

        self.feedback_history = [
            FeedbackEntry(**entry) for entry in data.get("feedback_history", [])
        ]
        self.suggestion_scores = data.get("suggestion_scores", {})
        self.accepted_patterns = data.get("accepted_patterns", {})

    def recommend_model_improvements(self) -> List[str]:
        """Based on feedback, suggest areas for improvement."""
        recommendations = []
        stats = self.get_statistics()

        if stats["rejection_rate"] > 0.3:
            recommendations.append("Model has high rejection rate - consider retraining")

        if stats["acceptance_rate"] < 0.5:
            recommendations.append("Acceptance rate below 50% - improve suggestion quality")

        if stats["modification_rate"] > 0.4:
            recommendations.append("Many suggestions are modified - suggestions may be incomplete")

        worst = self.get_worst_suggestions(1)
        if worst and worst[0][1] < 0.2:
            recommendations.append(f"Remove low-scoring suggestion: {worst[0][0]}")

        return recommendations
