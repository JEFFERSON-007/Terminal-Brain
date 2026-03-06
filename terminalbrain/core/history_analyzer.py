"""
Command history analyzer and learning system
"""

import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import json


class HistoryAnalyzer:
    """Analyze command history and learn user patterns"""

    def __init__(self):
        self.commands: List[str] = []
        self.command_freq: Counter = Counter()
        self.command_sequences: List[Tuple[str, str]] = []
        self.time_patterns: Dict[str, List[str]] = defaultdict(list)

    def load_bash_history(self) -> List[str]:
        """Load bash history from ~/.bash_history"""
        history_file = Path.home() / ".bash_history"
        commands = []

        if history_file.exists():
            try:
                with open(history_file, "r", errors="ignore") as f:
                    commands = [line.strip() for line in f if line.strip()]
            except Exception as e:
                print(f"Warning: Could not read bash history: {e}")

        self.commands = commands
        self._analyze_commands()
        return commands

    def load_zsh_history(self) -> List[str]:
        """Load zsh history from ~/.zsh_history"""
        history_file = Path.home() / ".zsh_history"
        commands = []

        if history_file.exists():
            try:
                with open(history_file, "r", errors="ignore") as f:
                    for line in f:
                        # ZSH history format: : <timestamp>:0;<command>
                        if ";" in line:
                            parts = line.split(";", 1)
                            if len(parts) > 1:
                                cmd = parts[1].strip()
                                if cmd:
                                    commands.append(cmd)
                        elif line.strip():
                            commands.append(line.strip())
            except Exception as e:
                print(f"Warning: Could not read zsh history: {e}")

        self.commands = commands
        self._analyze_commands()
        return commands

    def load_history(self) -> List[str]:
        """Load history from available shell history files"""
        # Try bash first, then zsh
        bash_history = Path.home() / ".bash_history"
        zsh_history = Path.home() / ".zsh_history"

        if bash_history.exists():
            return self.load_bash_history()
        elif zsh_history.exists():
            return self.load_zsh_history()
        else:
            return []

    def _analyze_commands(self) -> None:
        """Analyze loaded commands for patterns"""
        if not self.commands:
            return

        # Count frequency
        self.command_freq = Counter()
        for cmd in self.commands:
            # Extract main command
            main_cmd = cmd.split()[0] if cmd.split() else cmd
            self.command_freq[main_cmd] += 1

        # Find sequences
        self.command_sequences = []
        for i in range(len(self.commands) - 1):
            if self.commands[i] and self.commands[i + 1]:
                main1 = self.commands[i].split()[0]
                main2 = self.commands[i + 1].split()[0]
                if main1 != main2:  # Skip repeats
                    self.command_sequences.append((main1, main2))

    def get_most_common(self, n: int = 10) -> List[Tuple[str, int]]:
        """Get most frequently used commands"""
        return self.command_freq.most_common(n)

    def get_command_patterns(self) -> Dict[str, int]:
        """Get command patterns and their frequencies"""
        patterns = Counter()
        for cmd in self.commands:
            parts = cmd.split()
            if parts:
                # Pattern: main command
                patterns[parts[0]] += 1
                # Pattern: main + first arg
                if len(parts) > 1:
                    patterns[f"{parts[0]} {parts[1]}"] += 1
        return dict(patterns)

    def predict_next_command(self, current_cmd: str, top_n: int = 3) -> List[Tuple[str, float]]:
        """Predict next command based on sequence frequency"""
        main_cmd = current_cmd.split()[0] if current_cmd.split() else current_cmd

        # Count transitions from current command
        transitions = Counter()
        for prev, next_cmd in self.command_sequences:
            if prev == main_cmd:
                transitions[next_cmd] += 1

        if not transitions:
            # If no transitions found, return most common commands
            return [
                (cmd, count / len(self.commands))
                for cmd, count in self.command_freq.most_common(top_n)
                if cmd != main_cmd
            ]

        # Convert to probabilities
        total = sum(transitions.values())
        results = [
            (cmd, count / total) for cmd, count in transitions.most_common(top_n)
        ]
        return results

    def get_similar_commands(self, cmd: str, top_n: int = 5) -> List[Tuple[str, float]]:
        """Find similar commands using simple similarity"""
        cmd_tokens = set(cmd.split())
        similarities = []

        for history_cmd in self.commands:
            hist_tokens = set(history_cmd.split())
            # Jaccard similarity
            if cmd_tokens or hist_tokens:
                intersection = len(cmd_tokens & hist_tokens)
                union = len(cmd_tokens | hist_tokens)
                similarity = intersection / union if union > 0 else 0
                if similarity > 0:
                    similarities.append((history_cmd, similarity))

        # Sort by similarity and return top N
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_n]

    def suggest_aliases(self, min_frequency: int = 5) -> Dict[str, str]:
        """Suggest useful aliases for frequently used commands"""
        aliases = {}

        for cmd, freq in self.command_freq.most_common():
            if freq >= min_frequency:
                parts = cmd.split()
                if len(parts) > 1:
                    # Multi-word commands are good candidates
                    main_cmd = parts[0]
                    # Create alias from first letters
                    alias = "".join([p[0] for p in parts])
                    if len(alias) > 1 and alias not in aliases:
                        aliases[alias] = cmd

        return aliases

    def get_statistics(self) -> Dict[str, any]:
        """Get overall history statistics"""
        if not self.commands:
            return {}

        unique_commands = len(set(self.commands))
        most_common = self.command_freq.most_common(1)

        return {
            "total_commands": len(self.commands),
            "unique_commands": unique_commands,
            "command_diversity": unique_commands / len(self.commands) if self.commands else 0,
            "most_used_command": most_common[0][0] if most_common else None,
            "most_used_frequency": most_common[0][1] if most_common else 0,
            "unique_sequences": len(set(self.command_sequences)),
        }

    def export_statistics(self, filepath: Path) -> None:
        """Export statistics to JSON"""
        stats = self.get_statistics()
        stats["most_common"] = dict(self.command_freq.most_common(20))
        stats["suggested_aliases"] = self.suggest_aliases()

        with open(filepath, "w") as f:
            json.dump(stats, f, indent=2)
