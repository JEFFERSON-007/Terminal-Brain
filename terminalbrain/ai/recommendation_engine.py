"""
Command recommendation engine combining multiple sources
"""

import asyncio
from typing import List, Dict, Any, Optional
from terminalbrain.ai.llm_engine import LLMEngine
from terminalbrain.ai.ml_predictor import MLPredictor
from terminalbrain.core.ranking_engine import Suggestion, RankingEngine
from terminalbrain.core.history_analyzer import HistoryAnalyzer
from terminalbrain.core.context_analyzer import ContextAnalyzer


class RecommendationEngine:
    """
    AI recommendation engine combining:
    - LLM inference
    - ML prediction
    - Command history
    - Rule-based suggestions
    """

    def __init__(self, llm_backend: str = "ollama", model: str = "mistral"):
        self.llm_engine = LLMEngine(backend_type=llm_backend, model=model)
        self.ml_predictor = MLPredictor()
        self.history_analyzer = HistoryAnalyzer()
        self.ranking_engine = RankingEngine()
        self.context_analyzer = ContextAnalyzer()

    async def initialize(self) -> None:
        """Initialize recommendation engine"""
        # Load command history
        self.history_analyzer.load_history()

        # Train ML predictor
        self.ml_predictor.train(self.history_analyzer.commands)

    async def recommend(self, query: str, top_n: int = 5) -> List[Suggestion]:
        """
        Get command recommendations for a query

        Args:
            query: Natural language query or partial command
            top_n: Number of recommendations

        Returns:
            List of ranked suggestions
        """
        suggestions: List[Suggestion] = []

        # 1. Get LLM suggestions
        llm_suggestions = await self._get_llm_suggestions(query)
        suggestions.extend(llm_suggestions)

        # 2. Get history-based suggestions
        history_suggestions = self._get_history_suggestions(query)
        suggestions.extend(history_suggestions)

        # 3. Get ML predictions
        ml_suggestions = self._get_ml_suggestions(query)
        suggestions.extend(ml_suggestions)

        # 4. Deduplicate and rank
        suggestions = self.ranking_engine.deduplicate(suggestions)
        suggestions = self.ranking_engine.rank_suggestions(suggestions)

        return suggestions[:top_n]

    async def _get_llm_suggestions(self, query: str) -> List[Suggestion]:
        """Get suggestions from LLM"""
        try:
            if not await self.llm_engine.is_available():
                return []

            command = await self.llm_engine.generate_command(query)

            if command and not command.startswith("Error"):
                # Get explanation
                explanation = await self.llm_engine.explain_command(command)

                return [
                    Suggestion(
                        command=command,
                        confidence=0.85,
                        explanation=explanation[:100],
                        source="llm",
                    )
                ]
        except Exception as e:
            print(f"LLM suggestion error: {e}")

        return []

    def _get_history_suggestions(self, query: str) -> List[Suggestion]:
        """Get suggestions from command history"""
        suggestions = []

        # Find similar commands
        similar = self.history_analyzer.get_similar_commands(query, top_n=3)

        for cmd, similarity in similar:
            suggestions.append(
                Suggestion(
                    command=cmd,
                    confidence=min(similarity, 0.95),
                    explanation="From your command history",
                    source="history",
                )
            )

        return suggestions

    def _get_ml_suggestions(self, query: str) -> List[Suggestion]:
        """Get suggestions from ML predictor"""
        suggestions = []

        # Get ML predictions
        predictions = self.ml_predictor.predict(query, top_n=3)

        for cmd, probability in predictions:
            suggestions.append(
                Suggestion(
                    command=cmd,
                    confidence=probability,
                    explanation="Based on your command patterns",
                    source="ml",
                )
            )

        return suggestions

    async def predict_next(self, command: str, top_n: int = 3) -> List[Suggestion]:
        """
        Predict next command after current one

        Args:
            command: Current command
            top_n: Number of predictions

        Returns:
            List of predicted next commands
        """
        suggestions: List[Suggestion] = []

        # Get history-based predictions
        history_preds = self.history_analyzer.predict_next_command(command, top_n)
        for cmd, prob in history_preds:
            suggestions.append(
                Suggestion(
                    command=cmd,
                    confidence=prob,
                    explanation="Frequently follows this command",
                    source="history",
                )
            )

        # Get ML predictions
        ml_preds = self.ml_predictor.predict(command, top_n)
        for cmd, prob in ml_preds:
            suggestions.append(
                Suggestion(
                    command=cmd,
                    confidence=prob,
                    explanation="Predicted by ML model",
                    source="ml",
                )
            )

        # Rank and deduplicate
        suggestions = self.ranking_engine.deduplicate(suggestions)
        suggestions = self.ranking_engine.rank_suggestions(suggestions)

        return suggestions[:top_n]

    async def explain_command(self, command: str) -> str:
        """Get explanation for a command"""
        if await self.llm_engine.is_available():
            return await self.llm_engine.explain_command(command)
        return "Explanation not available"

    async def fix_command_error(self, command: str, error: str) -> List[Suggestion]:
        """
        Get suggestions to fix a broken command

        Args:
            command: The command that failed
            error: The error message

        Returns:
            List of fix suggestions
        """
        suggestions = []

        # Get LLM fix suggestions
        if await self.llm_engine.is_available():
            fixed = await self.llm_engine.fix_command(command, error)
            if fixed and not fixed.startswith("Error"):
                suggestions.append(
                    Suggestion(
                        command=fixed,
                        confidence=0.9,
                        explanation="AI-suggested fix",
                        source="llm",
                    )
                )

        # Try common fixes
        common_fixes = self._get_common_fixes(command, error)
        suggestions.extend(common_fixes)

        return suggestions

    def _get_common_fixes(self, command: str, error: str) -> List[Suggestion]:
        """Get common command fixes"""
        suggestions = []

        # Typo fixes
        if "command not found" in error.lower():
            # Try common misspellings
            typo_fixes = {
                "gti": "git",
                "pytohn": "python",
                "nmp": "npm",
                "dcoker": "docker",
            }
            for typo, correct in typo_fixes.items():
                if typo in command:
                    fixed_cmd = command.replace(typo, correct)
                    suggestions.append(
                        Suggestion(
                            command=fixed_cmd,
                            confidence=0.8,
                            explanation="Fixed typo",
                            source="rule",
                        )
                    )

        return suggestions

    async def generate_script(self, description: str) -> str:
        """Generate a shell script from description"""
        if await self.llm_engine.is_available():
            return await self.llm_engine.generate_script(description)
        return ""

    def suggest_aliases(self) -> Dict[str, str]:
        """Suggest useful aliases based on history"""
        return self.history_analyzer.suggest_aliases(min_frequency=5)
