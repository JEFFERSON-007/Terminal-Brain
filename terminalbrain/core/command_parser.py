"""
Command parser and analyzer
"""

import re
import shlex
from dataclasses import dataclass
from typing import List, Dict, Optional, Any


@dataclass
class ParsedCommand:
    """Parsed command structure"""
    command: str
    args: List[str]
    flags: Dict[str, Optional[str]]
    pipes: List[str]
    redirects: Dict[str, str]
    background: bool
    raw: str

    def __str__(self) -> str:
        return self.raw

    def get_flag(self, flag: str) -> Optional[str]:
        """Get flag value"""
        return self.flags.get(flag)

    def has_flag(self, flag: str) -> bool:
        """Check if flag exists"""
        return flag in self.flags


class CommandParser:
    """Parse and analyze shell commands"""

    def __init__(self):
        self.pipe_pattern = re.compile(r'\s*\|\s*')
        self.redirect_pattern = re.compile(r'([<>]{1,2}|&>)\s*')
        self.flag_pattern = re.compile(r'^-+')

    def parse(self, command_str: str) -> ParsedCommand:
        """
        Parse a command string into components

        Args:
            command_str: Raw command string

        Returns:
            ParsedCommand with parsed components
        """
        raw = command_str.strip()
        if not raw:
            return ParsedCommand("", [], {}, [], {}, False, "")

        # Check for background execution
        background = raw.endswith("&")
        if background:
            raw = raw[:-1].strip()

        # Split by pipes
        pipes = self.pipe_pattern.split(raw)

        # Parse first command
        first_cmd = pipes[0].strip()

        # Split into tokens
        try:
            tokens = shlex.split(first_cmd)
        except ValueError:
            tokens = first_cmd.split()

        if not tokens:
            return ParsedCommand("", [], {}, pipes[1:], {}, background, raw)

        # Extract command
        command = tokens[0]
        remaining = tokens[1:]

        # Parse flags and args
        args = []
        flags = {}

        for token in remaining:
            if self.flag_pattern.match(token):
                # Flag
                if "=" in token:
                    flag, value = token.split("=", 1)
                    flags[flag] = value
                else:
                    flags[token] = None
            else:
                args.append(token)

        # Parse redirects
        redirects = {}
        redirect_matches = list(self.redirect_pattern.finditer(first_cmd))
        for match in redirect_matches:
            operator = match.group()
            redirects[operator] = ""  # Would need more parsing for full values

        return ParsedCommand(
            command=command,
            args=args,
            flags=flags,
            pipes=pipes[1:],
            redirects=redirects,
            background=background,
            raw=raw,
        )

    def extract_subcommands(self, command_str: str) -> List[str]:
        """Extract all subcommands from a piped command"""
        parsed = self.parse(command_str)
        subcommands = [parsed.command]
        for pipe_cmd in parsed.pipes:
            try:
                tokens = shlex.split(pipe_cmd.strip())
                if tokens:
                    subcommands.append(tokens[0])
            except ValueError:
                pass
        return subcommands

    def is_dangerous(self, command_str: str, dangerous_patterns: List[str]) -> bool:
        """Check if command matches dangerous patterns"""
        cmd_lower = command_str.lower()
        for pattern in dangerous_patterns:
            if pattern.lower() in cmd_lower:
                return True
        return False

    def get_command_info(self, command_str: str) -> Dict[str, Any]:
        """Get detailed command information"""
        parsed = self.parse(command_str)
        return {
            "command": parsed.command,
            "args_count": len(parsed.args),
            "flags_count": len(parsed.flags),
            "has_pipes": len(parsed.pipes) > 0,
            "is_background": parsed.background,
            "has_redirects": len(parsed.redirects) > 0,
            "complexity": self._calculate_complexity(parsed),
        }

    def _calculate_complexity(self, parsed: ParsedCommand) -> str:
        """Calculate command complexity"""
        score = 0
        score += len(parsed.args)
        score += len(parsed.flags) * 2
        score += len(parsed.pipes) * 3
        score += len(parsed.redirects) * 2

        if score <= 2:
            return "simple"
        elif score <= 5:
            return "moderate"
        else:
            return "complex"
