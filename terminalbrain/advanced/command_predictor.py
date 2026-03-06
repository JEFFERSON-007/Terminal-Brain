"""Command Prediction Engine - Predicts next commands using n-grams and Markov chains."""

import json
from collections import defaultdict
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from pathlib import Path


@dataclass
class CommandSequence:
    """Represents a sequence of commands."""

    commands: List[str]
    frequency: int = 1
    last_used: str = ""


@dataclass
class PredictionResult:
    """Result from command prediction."""

    predictions: List[Tuple[str, float]]  # (command, confidence)
    based_on: str  # What the prediction was based on
    explanation: Optional[str] = None


class CommandPredictor:
    """
    Predicts next commands using n-gram and Markov chain models.

    Uses:
    - Bigrams (2-command sequences)
    - Trigrams (3-command sequences)
    - Markov chains with variable order
    """

    def __init__(self, n: int = 3):
        """
        Initialize Command Predictor.

        Args:
            n: Maximum n-gram size (default: 3)
        """
        self.n = n
        self.bigrams: Dict[str, Dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )
        self.trigrams: Dict[Tuple[str, str], Dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )
        self.unigrams: Dict[str, int] = defaultdict(int)
        self.command_sequences: List[CommandSequence] = []
        self.history_length = 0

    def train(self, command_history: List[str]) -> None:
        """
        Train the predictor on command history.

        Args:
            command_history: List of commands in execution order
        """
        self.history_length = len(command_history)

        # Build unigram model (single commands)
        for cmd in command_history:
            cmd_base = self._normalize_command(cmd)
            self.unigrams[cmd_base] += 1

        # Build bigram model (2-command sequences)
        for i in range(len(command_history) - 1):
            cmd1 = self._normalize_command(command_history[i])
            cmd2 = self._normalize_command(command_history[i + 1])
            self.bigrams[cmd1][cmd2] += 1

        # Build trigram model (3-command sequences)
        if self.n >= 3:
            for i in range(len(command_history) - 2):
                cmd1 = self._normalize_command(command_history[i])
                cmd2 = self._normalize_command(command_history[i + 1])
                cmd3 = self._normalize_command(command_history[i + 2])
                self.trigrams[(cmd1, cmd2)][cmd3] += 1

    def predict_next(
        self, recent_commands: List[str], top_k: int = 5
    ) -> PredictionResult:
        """
        Predict next command given recent command history.

        Args:
            recent_commands: Recent command history (last 1-3 commands)
            top_k: Number of predictions to return

        Returns:
            PredictionResult with ranked command predictions
        """
        if not recent_commands:
            return PredictionResult(
                predictions=[],
                based_on="empty_history",
                explanation="No command history provided",
            )

        normalized = [self._normalize_command(cmd) for cmd in recent_commands]

        # Try trigram prediction if we have 2 recent commands
        if len(normalized) >= 2 and self.n >= 3:
            key = (normalized[-2], normalized[-1])
            if key in self.trigrams and self.trigrams[key]:
                predictions = self._rank_predictions(self.trigrams[key], top_k)
                return PredictionResult(
                    predictions=predictions,
                    based_on="trigram_model",
                    explanation=f"Based on sequence: {normalized[-2]} → {normalized[-1]} → ?",
                )

        # Fall back to bigram prediction
        if normalized:
            last_cmd = normalized[-1]
            if last_cmd in self.bigrams and self.bigrams[last_cmd]:
                predictions = self._rank_predictions(self.bigrams[last_cmd], top_k)
                return PredictionResult(
                    predictions=predictions,
                    based_on="bigram_model",
                    explanation=f"Based on command: {last_cmd} → ?",
                )

        # Fall back to frequency-based prediction
        if self.unigrams:
            predictions = self._rank_predictions(self.unigrams, top_k)
            return PredictionResult(
                predictions=predictions,
                based_on="frequency_model",
                explanation="Based on overall command frequency",
            )

        return PredictionResult(
            predictions=[],
            based_on="no_data",
            explanation="No training data available",
        )

    def predict_workflow(self, workflow_start: List[str]) -> List[str]:
        """
        Predict a complete workflow (sequence of commands).

        Args:
            workflow_start: Starting command(s)

        Returns:
            Predicted workflow sequence
        """
        workflow = [self._normalize_command(cmd) for cmd in workflow_start]
        max_length = 10

        while len(workflow) < max_length:
            prediction = self.predict_next(workflow)
            if not prediction.predictions:
                break
            next_cmd = prediction.predictions[0][0]
            workflow.append(next_cmd)

            # Stop if we return to a command we've already seen (loop)
            if workflow.count(next_cmd) > 1:
                break

        return workflow

    def get_workflow_patterns(self, min_frequency: int = 3) -> List[CommandSequence]:
        """
        Get frequently occurring command sequences.

        Args:
            min_frequency: Minimum frequency to consider significant

        Returns:
            List of frequently occurring workflows
        """
        patterns = []

        # Find frequent bigrams
        for cmd1, next_cmds in self.bigrams.items():
            for cmd2, freq in next_cmds.items():
                if freq >= min_frequency:
                    patterns.append(
                        CommandSequence(commands=[cmd1, cmd2], frequency=freq)
                    )

        # Find frequent trigrams
        if self.n >= 3:
            for (cmd1, cmd2), next_cmds in self.trigrams.items():
                for cmd3, freq in next_cmds.items():
                    if freq >= min_frequency:
                        patterns.append(
                            CommandSequence(
                                commands=[cmd1, cmd2, cmd3], frequency=freq
                            )
                        )

        # Sort by frequency
        return sorted(patterns, key=lambda p: p.frequency, reverse=True)

    def _normalize_command(self, cmd: str) -> str:
        """
        Normalize command by extracting base command.

        Args:
            cmd: Full command string

        Returns:
            Normalized command
        """
        # Remove arguments, keep only base command
        parts = cmd.strip().split()
        if not parts:
            return ""

        base = parts[0]

        # Handle common patterns
        if base.startswith("sudo"):
            base = parts[1] if len(parts) > 1 else "sudo"
        elif base.startswith("python"):
            base = "python"
        elif "/" in base:
            base = base.split("/")[-1]

        return base.lower()

    def _rank_predictions(
        self, predictions_dict: Dict[str, int], top_k: int
    ) -> List[Tuple[str, float]]:
        """
        Rank predictions by frequency and return confidence scores.

        Args:
            predictions_dict: Dictionary of {command: frequency}
            top_k: Number of top predictions to return

        Returns:
            List of (command, confidence) tuples
        """
        if not predictions_dict:
            return []

        total = sum(predictions_dict.values())
        ranked = sorted(predictions_dict.items(), key=lambda x: x[1], reverse=True)[
            :top_k
        ]

        return [(cmd, freq / total) for cmd, freq in ranked]

    def save_model(self, filepath: Path) -> None:
        """Save the model to JSON."""
        model_data = {
            "unigrams": self.unigrams,
            "bigrams": {
                cmd1: dict(cmds) for cmd1, cmds in self.bigrams.items()
            },
            "trigrams": {
                str(key): dict(cmds) for key, cmds in self.trigrams.items()
            },
            "history_length": self.history_length,
            "n": self.n,
        }
        with open(filepath, "w") as f:
            json.dump(model_data, f, indent=2)

    def load_model(self, filepath: Path) -> None:
        """Load the model from JSON."""
        with open(filepath, "r") as f:
            model_data = json.load(f)

        self.unigrams = defaultdict(int, model_data.get("unigrams", {}))
        self.bigrams = defaultdict(lambda: defaultdict(int))
        for cmd1, cmds in model_data.get("bigrams", {}).items():
            self.bigrams[cmd1] = defaultdict(int, cmds)

        self.trigrams = defaultdict(lambda: defaultdict(int))
        for key_str, cmds in model_data.get("trigrams", {}).items():
            cmd1, cmd2 = eval(key_str)
            self.trigrams[(cmd1, cmd2)] = defaultdict(int, cmds)

        self.history_length = model_data.get("history_length", 0)
        self.n = model_data.get("n", 3)
