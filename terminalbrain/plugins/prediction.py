"""Optional prediction module for Terminal Brain.

Provides ML-based command prediction.
Install with: terminal-brain install prediction

"""


def init():
    """Initialize prediction module."""
    return {
        "name": "prediction",
        "models": ["random_forest", "gradient_boosting"],
        "description": "ML-based command prediction",
    }


class MLPredictor:
    """ML-based command prediction."""
    
    def __init__(self):
        self.model = None
    
    def train(self, commands: list) -> None:
        """Train ML model on command history."""
        try:
            from sklearn.ensemble import RandomForestClassifier
            import numpy as np
            
            # Simplified: use command indices as features
            X = np.arange(len(commands)).reshape(-1, 1)
            y = commands
            
            self.model = RandomForestClassifier()
            self.model.fit(X, y)
        except ImportError:
            raise RuntimeError("scikit-learn not installed. Run: terminal-brain install prediction")
    
    def predict(self, history: list, top_k: int = 3) -> list:
        """Predict next commands."""
        if not self.model:
            raise RuntimeError("Model not trained")
        
        try:
            import numpy as np
            X = np.array([[len(history)]]).reshape(1, -1)
            predictions = self.model.predict_proba(X)
            return predictions[:top_k]
        except Exception as e:
            raise RuntimeError(f"Prediction failed: {e}")
