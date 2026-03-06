"""
Command error detection and debugging
"""

from typing import List, Dict, Optional, Tuple
from terminalbrain.core.command_parser import CommandParser


class ErrorDebugger:
    """Detect and debug command errors"""

    # Common error patterns
    ERROR_PATTERNS = {
        "not found": "command_not_found",
        "permission denied": "permission_denied",
        "no such file": "file_not_found",
        "invalid option": "invalid_option",
        "broken pipe": "broken_pipe",
        "killed": "killed_signal",
        "segmentation fault": "segfault",
        "bus error": "bus_error",
        "connection refused": "connection_refused",
        "timed out": "timeout",
    }

    def __init__(self):
        self.parser = CommandParser()

    def categorize_error(self, error_message: str) -> Optional[str]:
        """Categorize error by type"""
        error_lower = error_message.lower()

        for pattern, category in self.ERROR_PATTERNS.items():
            if pattern in error_lower:
                return category

        return None

    def detect_common_mistakes(self, command: str) -> List[Dict[str, str]]:
        """
        Detect common command mistakes

        Args:
            command: Command string

        Returns:
            List of detected issues with suggestions
        """
        issues = []
        parsed = self.parser.parse(command)

        # Check for common typos
        typo_fixes = self._check_typos(parsed.command)
        if typo_fixes:
            for fix in typo_fixes:
                issues.append(fix)

        # Check for missing flags
        missing_flags = self._check_missing_flags(parsed)
        if missing_flags:
            for flag in missing_flags:
                issues.append(flag)

        # Check for argument issues
        arg_issues = self._check_arguments(parsed)
        if arg_issues:
            for issue in arg_issues:
                issues.append(issue)

        return issues

    def _check_typos(self, command: str) -> List[Dict[str, str]]:
        """Check for common typos"""
        issues = []

        typos = {
            "gti": "git",
            "pytohn": "python",
            "nmp": "npm",
            "dcoker": "docker",
            "systemctl": "systemctl",
            "servive": "service",
            "instlal": "install",
        }

        for typo, correct in typos.items():
            if typo in command:
                issues.append(
                    {
                        "type": "typo",
                        "detected": typo,
                        "suggestion": correct,
                        "message": f"Did you mean '{correct}'?",
                    }
                )

        return issues

    def _check_missing_flags(self, parsed) -> List[Dict[str, str]]:
        """Check for potentially missing flags"""
        issues = []

        # Commands that usually need flags
        flag_suggestions = {
            "find": ["-name", "-type", "-size"],
            "grep": ["-r", "-n", "-i"],
            "chmod": ["-R"],
            "cp": ["-r"],
            "rm": ["-rf"],
            "ls": ["-la"],
        }

        if parsed.command in flag_suggestions and not parsed.flags:
            issues.append(
                {
                    "type": "missing_flag",
                    "command": parsed.command,
                    "suggestion": f"Consider adding flags like: {', '.join(flag_suggestions[parsed.command])}",
                    "message": f"{parsed.command} often needs flags",
                }
            )

        return issues

    def _check_arguments(self, parsed) -> List[Dict[str, str]]:
        """Check for argument issues"""
        issues = []

        # Commands that require arguments
        required_args = ["cd", "cp", "mv", "mkdir", "rmdir", "chmod", "chown"]

        if parsed.command in required_args and not parsed.args:
            issues.append(
                {
                    "type": "missing_argument",
                    "command": parsed.command,
                    "message": f"{parsed.command} requires arguments",
                }
            )

        return issues

    def suggest_alternatives(self, failed_command: str) -> List[str]:
        """
        Suggest alternative commands

        Args:
            failed_command: The command that failed

        Returns:
            List of alternative commands
        """
        alternatives = []
        parsed = self.parser.parse(failed_command)

        # Alternative for common tasks
        alternatives_map = {
            "python": ["python3"],
            "pip": ["pip3", "python3 -m pip"],
            "npm": ["yarn", "pnpm"],
            "apt": ["apt-get"],
            "yum": ["dnf"],
            "which": ["whereis", "command -v"],
        }

        if parsed.command in alternatives_map:
            alternatives = alternatives_map[parsed.command]

        return alternatives

    def get_help_command(self, command: str) -> List[str]:
        """Get help commands for a given command"""
        help_variants = [
            f"man {command}",
            f"{command} --help",
            f"{command} -h",
            f"tldr {command}",
            f"info {command}",
        ]
        return help_variants
