"""Workflow Detection Engine - Detects and stores frequently repeated command sequences."""

import json
import yaml
from collections import defaultdict
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


@dataclass
class WorkflowPattern:
    """Represents a detected workflow pattern."""

    name: str
    commands: List[str]
    frequency: int
    last_used: str
    description: str = ""
    tags: List[str] = field(default_factory=list)
    created: str = field(default_factory=lambda: datetime.now().isoformat())


class WorkflowDetector:
    """Detects frequently repeated command sequences and suggests automation."""

    def __init__(self, min_frequency: int = 3, min_sequence_length: int = 2):
        """
        Initialize Workflow Detector.

        Args:
            min_frequency: Minimum occurrences to consider a pattern
            min_sequence_length: Minimum commands in a sequence
        """
        self.min_frequency = min_frequency
        self.min_sequence_length = min_sequence_length
        self.patterns: Dict[str, WorkflowPattern] = {}
        self.sequence_history: List[List[str]] = []

    def analyze_history(self, command_history: List[str]) -> Dict[str, WorkflowPattern]:
        """
        Analyze command history to detect workflow patterns.

        Args:
            command_history: List of commands in execution order

        Returns:
            Dictionary of detected workflow patterns
        """
        detected = {}

        # Look for sequences of varying lengths
        for seq_len in range(
            self.min_sequence_length, min(6, len(command_history) // 2)
        ):
            sequences = self._find_sequences(command_history, seq_len)

            for cmd_sequence, occurrences in sequences.items():
                if len(occurrences) >= self.min_frequency:
                    # Generate workflow name
                    name = self._suggest_workflow_name(list(cmd_sequence))

                    pattern = WorkflowPattern(
                        name=name,
                        commands=list(cmd_sequence),
                        frequency=len(occurrences),
                        last_used=str(max(occurrences)),
                        tags=self._extract_tags(list(cmd_sequence)),
                    )

                    detected[name] = pattern
                    self.patterns[name] = pattern

        return detected

    def _find_sequences(
        self, history: List[str], length: int
    ) -> Dict[tuple, List[int]]:
        """
        Find all sequences of given length in history.

        Returns:
            Dictionary mapping command sequences to list of occurrence indices
        """
        sequences = defaultdict(list)

        for i in range(len(history) - length + 1):
            # Normalize commands
            seq = tuple(self._normalize(cmd) for cmd in history[i : i + length])
            sequences[seq].append(i)

        return sequences

    def _normalize(self, cmd: str) -> str:
        """Normalize command by extracting base command and key arguments."""
        parts = cmd.strip().split()
        if not parts:
            return ""

        # Extract base command
        if parts[0].startswith("sudo"):
            base = parts[1] if len(parts) > 1 else "sudo"
            parts = parts[1:]
        else:
            base = parts[0]

        # For common commands, include first argument
        if base in ["git", "docker", "npm", "pip"] and len(parts) > 1:
            return f"{base} {parts[1]}"

        return base.lower()

    def _suggest_workflow_name(self, commands: List[str]) -> str:
        """Suggest a descriptive name for a workflow."""
        # Look for common patterns
        cmd_str = " ".join(commands)

        patterns = {
            "git pull": "sync",
            "git add": "git_commit",
            "git push": "git_sync",
            "docker build": "docker_deploy",
            "npm run": "npm_build",
            "find": "search",
        }

        for pattern, name in patterns.items():
            if pattern in cmd_str:
                return name

        # Fall back to combining first characters
        name = "_".join(cmd[0] for cmd in commands)
        return f"workflow_{name}"

    def _extract_tags(self, commands: List[str]) -> List[str]:
        """Extract tags from commands."""
        tags = set()

        for cmd in commands:
            if "git" in cmd:
                tags.add("git")
            if "docker" in cmd:
                tags.add("docker")
            if "python" in cmd or "pip" in cmd:
                tags.add("python")
            if "npm" in cmd or "node" in cmd:
                tags.add("nodejs")
            if "build" in cmd or "make" in cmd:
                tags.add("build")
            if "deploy" in cmd:
                tags.add("deploy")

        return list(tags)

    def get_workflow(self, name: str) -> Optional[WorkflowPattern]:
        """Get a detected workflow by name."""
        return self.patterns.get(name)

    def list_workflows(self) -> List[WorkflowPattern]:
        """List all detected workflows, sorted by frequency."""
        return sorted(
            self.patterns.values(), key=lambda p: p.frequency, reverse=True
        )

    def save_workflow(self, name: str, filepath: Path) -> None:
        """
        Save a workflow to YAML file.

        Args:
            name: Workflow name
            filepath: Path to save YAML file
        """
        if name not in self.patterns:
            raise ValueError(f"Workflow '{name}' not found")

        pattern = self.patterns[name]
        workflow_data = {
            "name": pattern.name,
            "description": pattern.description,
            "commands": pattern.commands,
            "frequency": pattern.frequency,
            "tags": pattern.tags,
            "created": pattern.created,
        }

        # Create workflows directory if needed
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "w") as f:
            yaml.dump(workflow_data, f, default_flow_style=False, sort_keys=False)

    def save_all_workflows(self, workflows_dir: Path) -> None:
        """Save all workflows to directory."""
        workflows_dir.mkdir(parents=True, exist_ok=True)

        for name, pattern in self.patterns.items():
            filepath = workflows_dir / f"{pattern.name}.yaml"
            self.save_workflow(pattern.name, filepath)

    def load_workflow(self, filepath: Path) -> Optional[WorkflowPattern]:
        """Load a workflow from YAML file."""
        if not filepath.exists():
            return None

        with open(filepath, "r") as f:
            data = yaml.safe_load(f)

        pattern = WorkflowPattern(
            name=data.get("name", ""),
            commands=data.get("commands", []),
            frequency=data.get("frequency", 1),
            last_used=data.get("last_used", datetime.now().isoformat()),
            description=data.get("description", ""),
            tags=data.get("tags", []),
            created=data.get("created", datetime.now().isoformat()),
        )

        self.patterns[pattern.name] = pattern
        return pattern

    def load_all_workflows(self, workflows_dir: Path) -> Dict[str, WorkflowPattern]:
        """Load all workflows from directory."""
        workflows = {}

        if not workflows_dir.exists():
            return workflows

        for yaml_file in workflows_dir.glob("*.yaml"):
            pattern = self.load_workflow(yaml_file)
            if pattern:
                workflows[pattern.name] = pattern

        return workflows

    def execute_workflow(self, name: str) -> List[str]:
        """Get commands for workflow execution."""
        if name not in self.patterns:
            raise ValueError(f"Workflow '{name}' not found")

        return self.patterns[name].commands

    def get_workflow_stats(self) -> Dict[str, any]:
        """Get statistics about detected workflows."""
        if not self.patterns:
            return {
                "total_workflows": 0,
                "total_commands": 0,
                "most_frequent": None,
                "average_frequency": 0,
            }

        frequencies = [p.frequency for p in self.patterns.values()]
        commands = [len(p.commands) for p in self.patterns.values()]

        return {
            "total_workflows": len(self.patterns),
            "total_sequences": sum(frequencies),
            "average_sequence_length": sum(commands) / len(commands),
            "average_frequency": sum(frequencies) / len(frequencies),
            "most_frequent": max(self.patterns.values(), key=lambda p: p.frequency).name,
            "most_frequent_count": max(frequencies),
        }
