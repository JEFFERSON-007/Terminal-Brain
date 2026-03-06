"""
Ranking engine for suggestions
"""

from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, field


@dataclass
class Suggestion:
    """A command suggestion"""
    command: str
    confidence: float
    explanation: str
    source: str  # "llm", "ml", "history", "rule"
    complexity: str = "moderate"
    score: float = field(default=0.0)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "command": self.command,
            "confidence": round(self.confidence, 2),
            "explanation": self.explanation,
            "source": self.source,
            "complexity": self.complexity,
        }


class RankingEngine:
    """Rank and prioritize suggestions"""

    def __init__(self):
        self.weights = {
            "llm": 0.35,
            "ml": 0.25,
            "history": 0.25,
            "rule": 0.15,
        }

    def rank_suggestions(self, suggestions: List[Suggestion]) -> List[Suggestion]:
        """
        Rank suggestions by various factors

        Args:
            suggestions: List of suggestions to rank

        Returns:
            Sorted list of suggestions by score
        """
        for suggestion in suggestions:
            suggestion.score = self._calculate_score(suggestion)

        # Sort by score descending
        return sorted(suggestions, key=lambda s: s.score, reverse=True)

    def _calculate_score(self, suggestion: Suggestion) -> float:
        """Calculate composite score for a suggestion"""
        base_score = suggestion.confidence
        source_weight = self.weights.get(suggestion.source, 0.1)

        # Adjust for complexity (prefer simpler commands)
        complexity_factor = 1.0
        if suggestion.complexity == "simple":
            complexity_factor = 1.2
        elif suggestion.complexity == "complex":
            complexity_factor = 0.8

        return base_score * source_weight * complexity_factor

    def deduplicate(self, suggestions: List[Suggestion]) -> List[Suggestion]:
        """Remove duplicate commands, keeping highest scoring"""
        seen = {}
        for suggestion in suggestions:
            cmd = suggestion.command
            if cmd not in seen or suggestion.score > seen[cmd].score:
                seen[cmd] = suggestion

        return list(seen.values())

    def filter_by_confidence(
        self,
        suggestions: List[Suggestion],
        min_confidence: float = 0.3,
    ) -> List[Suggestion]:
        """Filter suggestions by minimum confidence"""
        return [s for s in suggestions if s.confidence >= min_confidence]

    def get_top_suggestions(
        self,
        suggestions: List[Suggestion],
        n: int = 5,
    ) -> List[Suggestion]:
        """Get top N suggestions"""
        ranked = self.rank_suggestions(suggestions)
        return ranked[:n]
