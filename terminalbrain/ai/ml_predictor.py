"""
Machine learning predictor for command suggestion
"""

from typing import List, Tuple, Optional, Dict, Any
import json
from pathlib import Path
from collections import Counter


class MLPredictor:
    """ML-based command predictor"""

    def __init__(self):
        self.model = None
        self.feature_extractor = CommandFeatureExtractor()
        self.is_trained = False

    def train(self, command_history: List[str]) -> None:
        """
        Train predictor on command history

        Args:
            command_history: List of historical commands
        """
        if len(command_history) < 10:
            self.is_trained = False
            return

        try:
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.preprocessing import LabelEncoder

            # Extract features from history
            X = []
            y = []

            for i in range(len(command_history) - 1):
                features = self.feature_extractor.extract(command_history[i])
                next_cmd = command_history[i + 1].split()[0]

                X.append(features)
                y.append(next_cmd)

            if not X or not y:
                return

            # Train model
            self.model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)

            # Convert features to numeric
            X_numeric = self._convert_to_numeric(X)
            self.model.fit(X_numeric, y)
            self.is_trained = True

        except ImportError:
            print("scikit-learn not installed, ML predictor unavailable")

    def predict(self, command: str, top_n: int = 3) -> List[Tuple[str, float]]:
        """
        Predict next command

        Args:
            command: Current command
            top_n: Number of predictions

        Returns:
            List of (command, probability) tuples
        """
        if not self.is_trained or not self.model:
            return []

        try:
            features = self.feature_extractor.extract(command)
            X_numeric = self._convert_to_numeric([features])

            # Get predictions
            probabilities = self.model.predict_proba(X_numeric)[0]
            classes = self.model.classes_

            # Get top predictions
            results = []
            for class_idx, prob in enumerate(probabilities):
                if prob > 0.1:  # Only include > 10% probability
                    results.append((classes[class_idx], float(prob)))

            results.sort(key=lambda x: x[1], reverse=True)
            return results[:top_n]

        except Exception as e:
            print(f"Prediction error: {e}")
            return []

    def _convert_to_numeric(self, feature_list: List[List[Any]]) -> List[List[float]]:
        """Convert features to numeric format"""
        numeric = []
        for features in feature_list:
            # Convert boolean/int features to floats
            row = [float(f) if isinstance(f, (int, bool)) else 0.0 for f in features]
            numeric.append(row)
        return numeric

    def save(self, filepath: Path) -> None:
        """Save model to disk"""
        if not self.is_trained:
            return

        try:
            import joblib

            joblib.dump(self.model, filepath)
        except ImportError:
            print("joblib not installed, cannot save model")

    def load(self, filepath: Path) -> None:
        """Load model from disk"""
        try:
            import joblib

            self.model = joblib.load(filepath)
            self.is_trained = True
        except ImportError:
            print("joblib not installed, cannot load model")


class CommandFeatureExtractor:
    """Extract features from commands for ML"""

    def extract(self, command: str) -> List[Any]:
        """
        Extract features from a command

        Args:
            command: Command string

        Returns:
            List of features
        """
        features = []

        # Basic features
        parts = command.split()
        main_cmd = parts[0] if parts else ""

        features.append(len(parts))  # Number of parts
        features.append(len(command))  # Command length
        features.append("--" in command)  # Has long flags
        features.append("-" in command)  # Has short flags
        features.append("|" in command)  # Has pipes
        features.append(">" in command)  # Has redirects
        features.append("&&" in command)  # Has command chaining
        features.append(";" in command)  # Has semicolon

        # Command-specific features
        features.append(self._is_git_command(main_cmd))
        features.append(self._is_docker_command(main_cmd))
        features.append(self._is_file_operation(main_cmd))
        features.append(self._is_process_command(main_cmd))

        # Argument features
        features.append(len([p for p in parts if p.startswith("-")]))  # Flag count

        return features

    def _is_git_command(self, cmd: str) -> int:
        return 1 if cmd in ["git", "g"] else 0

    def _is_docker_command(self, cmd: str) -> int:
        return 1 if cmd in ["docker", "docker-compose"] else 0

    def _is_file_operation(self, cmd: str) -> int:
        return 1 if cmd in ["ls", "cd", "cp", "mv", "rm", "mkdir", "find", "grep"] else 0

    def _is_process_command(self, cmd: str) -> int:
        return 1 if cmd in ["ps", "kill", "top", "htop", "systemctl"] else 0
