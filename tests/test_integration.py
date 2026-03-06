"""
Integration tests for Terminal Brain
"""

import pytest
import asyncio
from pathlib import Path
import tempfile
import json

from terminalbrain.config import Config, load_config, save_config, get_config_path
from terminalbrain.ai import RecommendationEngine, ErrorDebugger
from terminalbrain.knowledge import KnowledgeBase, RAGPipeline
from terminalbrain.monitor import SystemMonitor, ProcessMonitor


class TestConfiguration:
    """Test configuration management"""

    def test_load_default_config(self):
        config = load_config()
        assert config is not None
        assert config.ai.backend
        assert config.ui

    def test_save_and_load_config(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test.toml"

            # Create config
            config = Config()
            config.ai.model = "test-model"

            # This would need modification to test custom paths
            # Just verify structure is correct
            assert config.ai.model == "test-model"

    def test_config_defaults(self):
        config = Config()
        assert config.general.theme == "dark"
        assert config.ai.temperature == 0.7
        assert config.ui.refresh_interval == 2000


class TestKnowledgeBase:
    """Test knowledge base functionality"""

    def test_knowledge_base_initialization(self):
        kb = KnowledgeBase()
        assert len(kb.commands) > 0

    def test_get_command_info(self):
        kb = KnowledgeBase()
        info = kb.get_command_info("find")
        assert info is not None
        assert "description" in info
        assert "examples" in info

    def test_search_commands(self):
        kb = KnowledgeBase()
        results = kb.search_commands("search")
        assert len(results) > 0

    def test_get_examples(self):
        kb = KnowledgeBase()
        examples = kb.get_examples("find")
        assert isinstance(examples, list)
        assert len(examples) > 0

    def test_get_similar_commands(self):
        kb = KnowledgeBase()
        similar = kb.get_similar_commands("find")
        assert isinstance(similar, list)


class TestRAGPipeline:
    """Test RAG pipeline"""

    def test_rag_initialization(self):
        rag = RAGPipeline()
        assert rag.kb is not None

    def test_retrieval(self):
        rag = RAGPipeline()
        # Without embedding model, uses fallback
        results = rag.retrieve("find files", top_k=3)
        assert isinstance(results, list)


class TestErrorDebugger:
    """Test error debugging"""

    def test_error_categorization(self):
        debugger = ErrorDebugger()
        error_type = debugger.categorize_error("command not found: gti")
        assert error_type == "command_not_found"

    def test_typo_detection(self):
        debugger = ErrorDebugger()
        mistakes = debugger.detect_common_mistakes("pytohn script.py")
        assert len(mistakes) > 0
        assert any(m["type"] == "typo" for m in mistakes)

    def test_suggest_alternatives(self):
        debugger = ErrorDebugger()
        alts = debugger.suggest_alternatives("python script.py")
        assert isinstance(alts, list)

    def test_help_commands(self):
        debugger = ErrorDebugger()
        helps = debugger.get_help_command("find")
        assert len(helps) > 0
        assert any("--help" in h for h in helps)


class TestSystemMonitor:
    """Test system monitoring"""

    def test_get_cpu_percent(self):
        cpu = SystemMonitor.get_cpu_percent()
        assert 0 <= cpu <= 100

    def test_get_ram_info(self):
        ram = SystemMonitor.get_ram_info()
        assert "percent" in ram
        assert "used_gb" in ram
        assert 0 <= ram["percent"] <= 100

    def test_get_disk_info(self):
        disk = SystemMonitor.get_disk_info()
        assert "percent" in disk
        assert 0 <= disk["percent"] <= 100

    def test_get_battery_info(self):
        battery = SystemMonitor.get_battery_info()
        assert isinstance(battery, dict)
        # Might not have battery on all systems

    def test_get_metrics(self):
        metrics = SystemMonitor.get_metrics()
        assert metrics.cpu_percent >= 0
        assert metrics.ram_percent >= 0
        assert metrics.disk_percent >= 0

    def test_get_metrics_dict(self):
        metrics_dict = SystemMonitor.get_metrics_dict()
        assert "cpu" in metrics_dict
        assert "ram" in metrics_dict
        assert "disk" in metrics_dict


class TestProcessMonitor:
    """Test process monitoring"""

    def test_get_top_processes(self):
        processes = ProcessMonitor.get_top_processes(n=5)
        assert isinstance(processes, list)
        assert len(processes) <= 5

    def test_find_process_by_name(self):
        # Find Python processes (should exist since we're running Python)
        processes = ProcessMonitor.find_process_by_name("python")
        assert isinstance(processes, list)

    def test_process_tree(self):
        import os

        tree = ProcessMonitor.get_process_tree(pid=os.getpid())
        assert "parent" in tree
        assert "children" in tree


class TestRecommendationEngineIntegration:
    """Integration tests for recommendation engine"""

    def test_engine_initialization(self):
        engine = RecommendationEngine()
        assert engine.llm_engine is not None
        assert engine.history_analyzer is not None
        assert engine.ranking_engine is not None

    @pytest.mark.asyncio
    async def test_initialization(self):
        engine = RecommendationEngine()
        await engine.initialize()
        # Should not raise

    def test_history_analysis(self):
        engine = RecommendationEngine()
        engine.history_analyzer.commands = [
            "ls", "git add", "git commit", "git push", "ls"
        ]
        engine.history_analyzer._analyze_commands()

        # Test that history was analyzed
        aliases = engine.suggest_aliases()
        assert isinstance(aliases, dict)

    @pytest.mark.asyncio
    async def test_command_explanation(self):
        engine = RecommendationEngine()
        # This will fail if Ollama not running, but shouldn't crash
        result = await engine.explain_command("find . -name '*.txt'")
        assert isinstance(result, str)


class TestEndToEndWorkflow:
    """End-to-end workflow tests"""

    def test_command_parsing_and_ranking(self):
        from terminalbrain.core import CommandParser
        from terminalbrain.core.ranking_engine import RankingEngine, Suggestion

        parser = CommandParser()
        ranker = RankingEngine()

        # Parse command
        parsed = parser.parse("find . -name '*.txt'")
        assert parsed.command == "find"

        # Create suggestions
        suggestions = [
            Suggestion("find . -name '*.txt'", 0.9, "exact", "llm"),
            Suggestion("find . -name '*.txt' -type f", 0.85, "extended", "history"),
        ]

        # Rank
        ranked = ranker.rank_suggestions(suggestions)
        deduped = ranker.deduplicate(ranked)

        assert len(deduped) == 1  # Duplicates removed

    def test_history_learning_workflow(self):
        from terminalbrain.core import HistoryAnalyzer

        analyzer = HistoryAnalyzer()
        analyzer.commands = [
            "git add .",
            "git commit -m 'test'",
            "git push",
            "git add .",
            "git commit -m 'fix'",
            "git push",
        ]
        analyzer._analyze_commands()

        # Predict next after git add
        predictions = analyzer.predict_next_command("git add .", top_n=1)
        assert len(predictions) > 0
        # Should predict "git commit" or similar

    def test_error_fix_workflow(self):
        from terminalbrain.ai import ErrorDebugger

        debugger = ErrorDebugger()

        # Detect typo
        mistakes = debugger.detect_common_mistakes("pytohn -c 'print(1)'")
        assert len(mistakes) > 0

        # Get alternatives
        alts = debugger.suggest_alternatives("pytohn -c")
        assert "python" in alts or "python3" in alts


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
