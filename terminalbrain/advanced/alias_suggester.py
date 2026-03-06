"""Alias Suggester - Analyzes usage patterns and suggests useful aliases."""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple
from collections import Counter


@dataclass
class AliasSuggestion:
    """Suggestion for a useful alias."""

    command: str  # The full command
    alias: str  # Suggested alias name
    frequency: int  # How often the command appears
    time_saved_per_use: float  # Approximate characters saved
    rationale: str  # Why this alias is suggested


class AliasSuggester:
    """Analyzes command usage and suggests useful aliases."""

    def __init__(self, min_frequency: int = 3, min_savings: int = 3):
        """
        Initialize Alias Suggester.

        Args:
            min_frequency: Minimum times a command must appear
            min_savings: Minimum characters saved by alias
        """
        self.min_frequency = min_frequency
        self.min_savings = min_savings
        self.command_frequency: Dict[str, int] = {}
        self.existing_aliases: Dict[str, str] = {}

    def analyze_history(self, command_history: List[str]) -> List[AliasSuggestion]:
        """
        Analyze command history and suggest aliases.

        Args:
            command_history: List of executed commands

        Returns:
            List of alias suggestions
        """
        # Count command frequencies
        self.command_frequency = Counter(command_history)

        suggestions = []

        for cmd, frequency in self.command_frequency.items():
            if frequency < self.min_frequency:
                continue

            # Extract base command and flags
            parts = cmd.strip().split()
            if not parts:
                continue

            base_cmd = parts[0]

            # Look for common patterns that benefit from aliases
            if len(cmd) > 15:  # Long commands worth aliasing
                alias = self._suggest_alias_name(cmd)
                savings = len(cmd) - len(alias)

                if savings > self.min_savings:
                    suggestions.append(
                        AliasSuggestion(
                            command=cmd,
                            alias=alias,
                            frequency=frequency,
                            time_saved_per_use=savings,
                            rationale=f"Used {frequency} times, saves {savings} chars per use",
                        )
                    )

        # Sort by time savings and frequency
        suggestions.sort(
            key=lambda s: (s.time_saved_per_use * s.frequency, s.frequency),
            reverse=True,
        )

        return suggestions[:20]  # Return top 20

    def _suggest_alias_name(self, command: str) -> str:
        """Suggest a good alias name for a command."""
        parts = command.strip().split()
        if not parts:
            return "cmd"

        # Common alias patterns
        patterns = {
            "ls -la": "ll",
            "ls -lh": "lh",
            "git add": "ga",
            "git commit": "gc",
            "git push": "gp",
            "git pull": "gl",
            "git status": "gs",
            "git log": "log",
            "docker ps": "dps",
            "docker build": "db",
            "npm run": "nr",
            "pip install": "pi",
            "python -m": "pm",
        }

        # Check for exact pattern
        for pattern, alias in patterns.items():
            if command.startswith(pattern):
                return alias

        # Generate from first characters of words
        first_chars = "".join(p[0] for p in parts[:3])
        return first_chars.lower() or "cmd"

    def add_existing_alias(self, alias: str, command: str) -> None:
        """Add a known alias to avoid duplicates."""
        self.existing_aliases[alias] = command

    def get_alias_script(self, suggestions: List[AliasSuggestion]) -> str:
        """
        Generate a shell script with suggested aliases.

        Args:
            suggestions: List of alias suggestions

        Returns:
            Shell script content
        """
        lines = [
            "#!/bin/bash",
            "# Auto-generated aliases from Terminal Brain",
            "# Add to your ~/.bashrc or ~/.zshrc",
            "",
        ]

        for suggestion in suggestions:
            lines.append(
                f"alias {suggestion.alias}='{suggestion.command}'  "
                f"# Saves {int(suggestion.time_saved_per_use)} chars, "
                f"used {suggestion.frequency}x"
            )

        return "\n".join(lines)

    def get_function_script(self, suggestions: List[AliasSuggestion]) -> str:
        """
        Generate shell functions instead of aliases (for complex commands).

        Args:
            suggestions: List of alias suggestions

        Returns:
            Shell function script
        """
        lines = [
            "#!/bin/bash",
            "# Auto-generated functions from Terminal Brain",
            "# Add to your ~/.bashrc or ~/.zshrc",
            "",
        ]

        for suggestion in suggestions:
            func_name = suggestion.alias
            cmd = suggestion.command

            lines.append(f"{func_name}() {{")
            lines.append(f'    {cmd} "$@"')
            lines.append("}")
            lines.append("")

        return "\n".join(lines)

    def recommend_aliases(self, max_suggestions: int = 10) -> List[AliasSuggestion]:
        """Get top recommended aliases."""
        suggestions = []

        for cmd, frequency in sorted(
            self.command_frequency.items(), key=lambda x: x[1], reverse=True
        ):
            if frequency < self.min_frequency:
                break

            alias = self._suggest_alias_name(cmd)
            if alias not in self.existing_aliases:
                savings = len(cmd) - len(alias)
                if savings > 0:
                    suggestions.append(
                        AliasSuggestion(
                            command=cmd,
                            alias=alias,
                            frequency=frequency,
                            time_saved_per_use=savings,
                            rationale=f"Frequently used ({frequency}x), saves {savings} chars",
                        )
                    )

            if len(suggestions) >= max_suggestions:
                break

        return suggestions
