"""
Unit tests for Terminal Brain core modules
"""

import pytest
from pathlib import Path
from terminalbrain.core import CommandParser, HistoryAnalyzer
from terminalbrain.core.ranking_engine import Suggestion, RankingEngine
from terminalbrain.core.context_analyzer import ContextAnalyzer


class TestCommandParser:
    """Test CommandParser functionality"""

    def setup_method(self):
        self.parser = CommandParser()

    def test_parse_simple_command(self):
        parsed = self.parser.parse("ls -la")
        assert parsed.command == "ls"
        assert "-la" in parsed.flags
        assert not parsed.background
        assert not parsed.pipes

    def test_parse_command_with_args(self):
        parsed = self.parser.parse("find . -name '*.txt'")
        assert parsed.command == "find"
        assert "." in parsed.args
        assert "-name" in parsed.flags

    def test_parse_piped_command(self):
        parsed = self.parser.parse("find . -name '*.txt' | grep error")
        assert parsed.command == "find"
        assert len(parsed.pipes) > 0

    def test_parse_background_command(self):
        parsed = self.parser.parse("long_command &")
        assert parsed.background

    def test_extract_subcommands(self):
        subcommands = self.parser.extract_subcommands("git add . && git commit")
        assert "git" in subcommands

    def test_dangerous_command_detection(self):
        assert self.parser.is_dangerous("rm -rf /", ["rm -rf"])
        assert not self.parser.is_dangerous("ls -la", ["rm -rf"])

    def test_command_complexity(self):
        simple = self.parser.parse("ls")
        assert simple.raw  # Just verify parsing works

        complex_cmd = self.parser.parse("find . -name '*.txt' -size +100M -type f | xargs grep -l 'error' > results.txt")
        info = self.parser.get_command_info(complex_cmd.raw)
        assert info["complexity"] == "complex"


class TestHistoryAnalyzer:
    """Test HistoryAnalyzer functionality"""

    def setup_method(self):
        self.analyzer = HistoryAnalyzer()
        # Create sample history
        self.analyzer.commands = [
            "ls",
            "cd /tmp",
            "ls -la",
            "git add .",
            "git commit -m 'test'",
            "git push",
            "ls",
            "ls -la",
            "git status",
            "git log",
        ]
        self.analyzer._analyze_commands()

    def test_most_common_commands(self):
        most_common = self.analyzer.get_most_common(3)
        assert len(most_common) <= 3
        assert most_common[0][0] in ["ls", "git"]  # Should be most common

    def test_command_patterns(self):
        patterns = self.analyzer.get_command_patterns()
        assert "ls" in patterns
        assert "git" in patterns

    def test_predict_next_command(self):
        predictions = self.analyzer.predict_next_command("git add", top_n=2)
        assert len(predictions) <= 2
        # Should predict git commit or git push

    def test_similar_commands(self):
        similar = self.analyzer.get_similar_commands("ls -la /tmp", top_n=3)
        assert len(similar) <= 3

    def test_suggest_aliases(self):
        aliases = self.analyzer.suggest_aliases(min_frequency=2)
        assert isinstance(aliases, dict)

    def test_statistics(self):
        stats = self.analyzer.get_statistics()
        assert stats["total_commands"] == 10
        assert stats["unique_commands"] <= 10
        assert "most_used_command" in stats


class TestRankingEngine:
    """Test RankingEngine functionality"""

    def setup_method(self):
        self.engine = RankingEngine()

    def test_rank_suggestions(self):
        suggestions = [
            Suggestion("cmd1", 0.9, "explanation", "llm"),
            Suggestion("cmd2", 0.8, "explanation", "history"),
            Suggestion("cmd3", 0.7, "explanation", "ml"),
        ]

        ranked = self.engine.rank_suggestions(suggestions)
        assert len(ranked) == 3
        assert ranked[0].score >= ranked[1].score

    def test_deduplicate_suggestions(self):
        suggestions = [
            Suggestion("find . -name '*.txt'", 0.9, "exp1", "llm"),
            Suggestion("find . -name '*.txt'", 0.8, "exp2", "history"),
            Suggestion("grep -r pattern .", 0.7, "exp3", "ml"),
        ]

        deduped = self.engine.deduplicate(suggestions)
        commands = [s.command for s in deduped]
        assert commands.count("find . -name '*.txt'") == 1

    def test_filter_by_confidence(self):
        suggestions = [
            Suggestion("cmd1", 0.9, "exp", "llm"),
            Suggestion("cmd2", 0.5, "exp", "history"),
            Suggestion("cmd3", 0.2, "exp", "ml"),
        ]

        filtered = self.engine.filter_by_confidence(suggestions, min_confidence=0.5)
        assert len(filtered) == 2

    def test_get_top_suggestions(self):
        suggestions = [
            Suggestion(f"cmd{i}", 0.9 - i*0.1, "exp", "llm")
            for i in range(10)
        ]

        top = self.engine.get_top_suggestions(suggestions, n=3)
        assert len(top) == 3


class TestContextAnalyzer:
    """Test ContextAnalyzer functionality"""

    def test_get_context(self):
        context = ContextAnalyzer.get_context()
        assert context.cwd
        assert context.user
        assert context.shell
        assert isinstance(context.files_in_cwd, list)

    def test_analyze_cwd(self):
        analysis = ContextAnalyzer.analyze_cwd()
        assert "path" in analysis
        assert "is_git_repo" in analysis

    def test_check_tool_installed(self):
        # Most systems have these
        assert ContextAnalyzer.check_tool_installed("python3")
        assert not ContextAnalyzer.check_tool_installed("nonexistent_tool_xyz")

    def test_get_installed_tools(self):
        tools = ContextAnalyzer.get_installed_tools()
        assert isinstance(tools, list)
        assert len(tools) > 0  # Should have at least python3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
