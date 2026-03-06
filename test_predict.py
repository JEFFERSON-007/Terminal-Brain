#!/usr/bin/env python3
import asyncio
import sys

async def test_predict():
    from terminalbrain.ai import RecommendationEngine
    from terminalbrain.core import HistoryAnalyzer
    
    engine = RecommendationEngine()
    await engine.initialize()
    
    history = HistoryAnalyzer()
    history.load_history()
    
    if not history.commands:
        return
    
    current_cmd = history.commands[-1]
    predictions = await engine.predict_next(current_cmd, top_n=3)
    
    if predictions and predictions[0].confidence > 0.1:
        print(f"\033[2;36m→ Next: {predictions[0].command}\033[0m", flush=True)

if __name__ == "__main__":
    asyncio.run(test_predict())
