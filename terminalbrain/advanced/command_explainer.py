"""Command Explanation Engine - Explains Linux commands from man pages and tldr."""

import subprocess
import re
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple
from pathlib import Path


@dataclass
class FlagExplanation:
    """Explanation of a command flag."""

    flag: str
    short_form: Optional[str]
    long_form: Optional[str]
    description: str


@dataclass
class CommandExplanation:
    """Complete explanation of a Linux command."""

    command: str
    description: str
    syntax: str
    flags: List[FlagExplanation] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    related_commands: List[str] = field(default_factory=list)
    source: str = "man"  # 'man' or 'tldr'


class CommandExplainer:
    """Explains Linux commands by parsing man pages and tldr documentation."""

    def __init__(self):
        """Initialize Command Explainer."""
        self.cache: Dict[str, CommandExplanation] = {}
        self.common_commands = self._load_common_commands()

    def _load_common_commands(self) -> Dict[str, str]:
        """Load descriptions of common commands."""
        return {
            "ls": "list directory contents",
            "grep": "search for patterns in files",
            "find": "search for files in a directory tree",
            "git": "version control system",
            "tar": "archive files",
            "curl": "transfer data using URLs",
            "pip": "Python package installer",
            "docker": "container platform",
            "apt": "Debian package manager",
            "chmod": "change file permissions",
            "chown": "change file owner",
            "mkdir": "create directories",
            "rm": "remove files",
            "cp": "copy files",
            "mv": "move/rename files",
            "cat": "concatenate and display files",
            "sed": "stream editor",
            "awk": "text processing language",
            "gcc": "C compiler",
            "make": "build automation",
        }

    def explain(self, command: str) -> Optional[CommandExplanation]:
        """
        Explain a Linux command.

        Args:
            command: Command name or command line

        Returns:
            CommandExplanation or None if not found
        """
        # Extract base command
        base_cmd = self._extract_base_command(command)

        # Check cache
        if base_cmd in self.cache:
            return self.cache[base_cmd]

        # Try man page first
        explanation = self._explain_from_man(base_cmd)

        # Fall back to built-in
        if not explanation:
            explanation = self._explain_from_builtins(command)

        if explanation:
            self.cache[base_cmd] = explanation

        return explanation

    def explain_flags(self, command: str) -> List[FlagExplanation]:
        """
        Explain the flags in a command.

        Args:
            command: Full command with flags

        Returns:
            List of flag explanations
        """
        explanation = self.explain(self._extract_base_command(command))
        if not explanation:
            return []

        # Extract flags from command
        flags = re.findall(r"-+\w+", command)
        matching_flags = [
            f for f in explanation.flags if f.flag in flags or f.short_form in flags
        ]

        return matching_flags

    def explain_command_parts(self, command: str) -> Dict[str, str]:
        """
        Break down and explain each part of a command.

        Example:
        >>> explainer.explain_command_parts("tar -czvf backup.tar.gz folder")
        Returns:
            Dictionary mapping each part to its explanation
        """
        parts = command.split()
        explanation = {}

        for i, part in enumerate(parts):
            if part.startswith("-"):
                # Flag
                exp = self.explain(parts[0]) if i == 0 else None
                if exp:
                    flag_exp = next(
                        (f for f in exp.flags if f.flag == part or f.short_form == part),
                        None,
                    )
                    if flag_exp:
                        explanation[part] = flag_exp.description
                else:
                    explanation[part] = "command option/flag"
            else:
                # Argument
                if i == 0:
                    # Command itself
                    cmd_exp = self.explain(part)
                    explanation[part] = (
                        cmd_exp.description if cmd_exp else "command"
                    )
                else:
                    # Parameter - context dependent
                    explanation[part] = "parameter/argument"

        return explanation

    def _extract_base_command(self, command: str) -> str:
        """Extract base command name from full command string."""
        parts = command.strip().split()
        if not parts:
            return ""

        base = parts[0]
        if base.startswith("sudo"):
            base = parts[1] if len(parts) > 1 else "sudo"

        # Remove path
        if "/" in base:
            base = base.split("/")[-1]

        return base.lower()

    def _explain_from_man(self, command: str) -> Optional[CommandExplanation]:
        """Try to get explanation from man pages."""
        try:
            # Get man page
            result = subprocess.run(
                ["man", command],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0:
                man_content = result.stdout
                return self._parse_man_page(command, man_content)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return None

    def _parse_man_page(self, command: str, content: str) -> Optional[CommandExplanation]:
        """Parse man page to extract information."""
        lines = content.split("\n")

        # Extract description
        description = ""
        for i, line in enumerate(lines):
            if "DESCRIPTION" in line or "NAME" in line:
                if i + 1 < len(lines):
                    description = lines[i + 1].strip()
                break

        if not description:
            return None

        # Extract synopsis
        syntax = ""
        for i, line in enumerate(lines):
            if "SYNOPSIS" in line:
                if i + 1 < len(lines):
                    syntax = lines[i + 1].strip()
                break

        # Simple flag extraction
        flags = self._extract_flags_from_man(lines)

        return CommandExplanation(
            command=command,
            description=description,
            syntax=syntax or f"{command} [OPTIONS]",
            flags=flags,
            source="man",
        )

    def _extract_flags_from_man(self, lines: List[str]) -> List[FlagExplanation]:
        """Extract flag explanations from man page content."""
        flags = []

        for i, line in enumerate(lines):
            # Look for flag patterns like "-f, --flag"
            match = re.match(r"\s*(-\w),\s*(--[\w-]+)?\s+(.*)", line)
            if match:
                short = match.group(1)
                long = match.group(2)
                desc = match.group(3)
                flags.append(
                    FlagExplanation(
                        flag=long or short, short_form=short, long_form=long, description=desc
                    )
                )

        return flags[:10]  # Limit to first 10 flags

    def _explain_from_builtins(self, command: str) -> Optional[CommandExplanation]:
        """Provide built-in explanations for common commands."""
        base = self._extract_base_command(command)

        if base not in self.common_commands:
            return None

        description = self.common_commands[base]

        # Build basic explanation
        flags = self._get_common_flags(base)

        return CommandExplanation(
            command=base,
            description=description,
            syntax=f"{base} [OPTIONS] [ARGUMENTS]",
            flags=flags,
            examples=self._get_common_examples(base),
            source="builtin",
        )

    def _get_common_flags(self, command: str) -> List[FlagExplanation]:
        """Get common flags for well-known commands."""
        common_flags = {
            "ls": [
                FlagExplanation(
                    flag="-l", short_form="-l", long_form="", description="long format"
                ),
                FlagExplanation(
                    flag="-a",
                    short_form="-a",
                    long_form="",
                    description="show hidden files",
                ),
                FlagExplanation(
                    flag="-h",
                    short_form="-h",
                    long_form="",
                    description="human-readable sizes",
                ),
            ],
            "grep": [
                FlagExplanation(
                    flag="-r",
                    short_form="-r",
                    long_form="",
                    description="recursive search",
                ),
                FlagExplanation(
                    flag="-i",
                    short_form="-i",
                    long_form="",
                    description="case-insensitive",
                ),
                FlagExplanation(
                    flag="-n",
                    short_form="-n",
                    long_form="",
                    description="show line numbers",
                ),
            ],
            "tar": [
                FlagExplanation(
                    flag="-c",
                    short_form="-c",
                    long_form="",
                    description="create archive",
                ),
                FlagExplanation(
                    flag="-x",
                    short_form="-x",
                    long_form="",
                    description="extract archive",
                ),
                FlagExplanation(
                    flag="-v",
                    short_form="-v",
                    long_form="",
                    description="verbose output",
                ),
                FlagExplanation(
                    flag="-z",
                    short_form="-z",
                    long_form="",
                    description="gzip compression",
                ),
                FlagExplanation(
                    flag="-f",
                    short_form="-f",
                    long_form="",
                    description="file name",
                ),
            ],
        }

        return common_flags.get(command, [])

    def _get_common_examples(self, command: str) -> List[str]:
        """Get common usage examples."""
        examples = {
            "ls": ["ls -la", "ls -h", "ls -ltr"],
            "grep": ["grep 'pattern' file", "grep -r 'text' .", "grep -i 'case' file"],
            "tar": [
                "tar -czf archive.tar.gz folder",
                "tar -xzf archive.tar.gz",
                "tar -tf archive.tar.gz",
            ],
            "find": [
                "find . -name '*.txt'",
                "find . -type f -size +100M",
                "find . -mtime -7",
            ],
            "git": [
                "git add .",
                "git commit -m 'message'",
                "git push origin main",
            ],
        }

        return examples.get(command, [])
