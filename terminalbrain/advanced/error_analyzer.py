"""AI Terminal Debugger - Automatic error detection and fix suggestion system."""

import json
import re
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple
from pathlib import Path


@dataclass
class ErrorPattern:
    """Represents a detectable error pattern."""

    pattern: str  # Regex pattern to match error
    category: str  # Error category (missing_dep, permission, etc.)
    description: str  # Human-readable description
    fixes: List[str] = field(default_factory=list)  # Suggested fixes
    confidence: float = 0.8  # Confidence level (0-1)


@dataclass
class ErrorSuggestion:
    """Error analysis result with suggestions."""

    error_detected: bool
    category: str
    message: str
    fixes: List[str]
    confidence: float
    additional_info: Dict[str, str] = field(default_factory=dict)


class ErrorAnalyzer:
    """Detects and analyzes terminal errors with AI-powered fix suggestions."""

    def __init__(self, knowledge_base: Optional[Dict] = None):
        """
        Initialize Error Analyzer.

        Args:
            knowledge_base: Optional knowledge base with error patterns and fixes
        """
        self.knowledge_base = knowledge_base or {}
        self.error_patterns = self._initialize_patterns()
        self.error_history: List[Tuple[str, str, str]] = []  # (cmd, stderr, category)

    def _initialize_patterns(self) -> List[ErrorPattern]:
        """Initialize common error patterns with fixes."""
        return [
            ErrorPattern(
                pattern=r"command not found",
                category="missing_command",
                description="Command is not installed or not in PATH",
                fixes=[
                    "Check if the program is installed: which <command>",
                    "Install using package manager: apt install <program>",
                    "Check PATH variable: echo $PATH",
                    "Use full path to command: /usr/bin/<command>",
                ],
                confidence=0.95,
            ),
            ErrorPattern(
                pattern=r"pip.*not found",
                category="missing_pip",
                description="pip is not installed",
                fixes=[
                    "sudo apt install python3-pip",
                    "python3 -m ensurepip",
                    "python3 -m pip install --upgrade pip",
                ],
                confidence=0.95,
            ),
            ErrorPattern(
                pattern=r"Permission denied",
                category="permission_denied",
                description="Insufficient permissions to access resource",
                fixes=[
                    "Use sudo: sudo <command>",
                    "Change permissions: chmod +x <file>",
                    "Check file ownership: ls -l <file>",
                    "Use chown: sudo chown $USER <file>",
                ],
                confidence=0.90,
            ),
            ErrorPattern(
                pattern=r"not a git repository",
                category="not_git_repo",
                description="Not in a git repository directory",
                fixes=[
                    "Initialize git: git init",
                    "Navigate to git repo: cd <repo>",
                    "Clone repository: git clone <url>",
                ],
                confidence=0.92,
            ),
            ErrorPattern(
                pattern=r"fatal: unable to access.*401",
                category="auth_failed",
                description="Authentication failed (401 Unauthorized)",
                fixes=[
                    "Check credentials: git config --global user.name",
                    "Generate SSH key: ssh-keygen -t ed25519",
                    "Set git credentials: git config --global credential.helper store",
                    "Use personal access token instead of password",
                ],
                confidence=0.88,
            ),
            ErrorPattern(
                pattern=r"ModuleNotFoundError|ImportError",
                category="missing_module",
                description="Python module not found",
                fixes=[
                    "Install package: pip install <module_name>",
                    "Check Python version: python --version",
                    "Use virtual environment: python -m venv venv",
                ],
                confidence=0.93,
            ),
            ErrorPattern(
                pattern=r"No such file or directory",
                category="file_not_found",
                description="File or directory does not exist",
                fixes=[
                    "Check path: ls -la <path>",
                    "List directory: ls <directory>",
                    "Find file: find ~ -name <filename>",
                    "Check current directory: pwd",
                ],
                confidence=0.91,
            ),
            ErrorPattern(
                pattern=r"Connection refused",
                category="connection_refused",
                description="Cannot connect to server/service",
                fixes=[
                    "Check if service is running: systemctl status <service>",
                    "Start service: sudo systemctl start <service>",
                    "Check port: netstat -tlnp | grep <port>",
                    "Check firewall: sudo ufw status",
                ],
                confidence=0.87,
            ),
            ErrorPattern(
                pattern=r"ENOENT|No such file",
                category="path_error",
                description="Path does not exist",
                fixes=[
                    "Create directory: mkdir -p <path>",
                    "Check path exists: test -d <path>",
                    "List parent directory: ls -la",
                ],
                confidence=0.89,
            ),
            ErrorPattern(
                pattern=r"Illegal instruction",
                category="illegal_instruction",
                description="CPU instruction not supported",
                fixes=[
                    "Check system architecture: uname -m",
                    "Download correct binary for architecture",
                    "Check CPU capabilities: cat /proc/cpuinfo | grep flags",
                ],
                confidence=0.82,
            ),
            ErrorPattern(
                pattern=r"Address already in use",
                category="port_in_use",
                description="Port is already bound to another process",
                fixes=[
                    "Find process using port: lsof -i :<port>",
                    "Kill process: kill -9 <pid>",
                    "Use different port: <command> --port <new_port>",
                ],
                confidence=0.90,
            ),
            ErrorPattern(
                pattern=r"Disk quota exceeded",
                category="disk_quota",
                description="Storage quota exceeded",
                fixes=[
                    "Check disk usage: df -h",
                    "Find large files: du -ah | sort -rh | head",
                    "Clean up: rm -rf <large_files>",
                    "Request quota increase from admin",
                ],
                confidence=0.85,
            ),
        ]

    def analyze(
        self, command: str, stderr: str, exit_code: int = 0
    ) -> ErrorSuggestion:
        """
        Analyze command execution for errors.

        Args:
            command: The executed command
            stderr: Standard error output
            exit_code: Command exit code

        Returns:
            ErrorSuggestion with detected errors and fixes
        """
        if exit_code == 0 and not stderr:
            return ErrorSuggestion(
                error_detected=False,
                category="success",
                message="Command executed successfully",
                fixes=[],
                confidence=1.0,
            )

        # Match error patterns
        matches = []
        for pattern in self.error_patterns:
            if re.search(pattern.pattern, stderr, re.IGNORECASE):
                matches.append(pattern)

        if not matches:
            # Generic error handling
            return ErrorSuggestion(
                error_detected=True,
                category="unknown_error",
                message=f"Error occurred (exit code: {exit_code})",
                fixes=[
                    f"Check error message: {stderr[:100]}",
                    f"Search error online: '{stderr.split()[0]}'",
                    f"Run with verbose flags: {command} -v",
                ],
                confidence=0.5,
                additional_info={"stderr": stderr, "exit_code": str(exit_code)},
            )

        # Use highest confidence match
        best_match = max(matches, key=lambda p: p.confidence)

        # Store in history
        self.error_history.append((command, stderr, best_match.category))

        return ErrorSuggestion(
            error_detected=True,
            category=best_match.category,
            message=best_match.description,
            fixes=best_match.fixes,
            confidence=best_match.confidence,
            additional_info={
                "command": command,
                "stderr_snippet": stderr[:200],
                "exit_code": str(exit_code),
            },
        )

    def suggest_commands(self, error_category: str) -> List[str]:
        """
        Suggest commands to resolve an error category.

        Args:
            error_category: The error category

        Returns:
            List of suggested commands to fix the error
        """
        for pattern in self.error_patterns:
            if pattern.category == error_category:
                return pattern.fixes
        return []

    def learn_from_fix(self, error_category: str, successful_fix: str) -> None:
        """
        Learn from user-confirmed fixes.

        Args:
            error_category: The error category
            successful_fix: The fix command that worked
        """
        for pattern in self.error_patterns:
            if pattern.category == error_category:
                # Add successful fix to front of list
                if successful_fix not in pattern.fixes:
                    pattern.fixes.insert(0, successful_fix)
                # Slightly increase confidence
                pattern.confidence = min(1.0, pattern.confidence + 0.02)
                break

    def get_error_statistics(self) -> Dict[str, int]:
        """
        Get statistics on encountered errors.

        Returns:
            Dictionary of error categories and occurrence counts
        """
        stats = {}
        for _, _, category in self.error_history:
            stats[category] = stats.get(category, 0) + 1
        return dict(sorted(stats.items(), key=lambda x: x[1], reverse=True))

    def save_patterns(self, filepath: Path) -> None:
        """Save error patterns to JSON file."""
        data = [
            {
                "pattern": p.pattern,
                "category": p.category,
                "description": p.description,
                "fixes": p.fixes,
                "confidence": p.confidence,
            }
            for p in self.error_patterns
        ]
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def load_patterns(self, filepath: Path) -> None:
        """Load error patterns from JSON file."""
        with open(filepath, "r") as f:
            data = json.load(f)
        self.error_patterns = [
            ErrorPattern(
                pattern=d["pattern"],
                category=d["category"],
                description=d["description"],
                fixes=d["fixes"],
                confidence=d.get("confidence", 0.8),
            )
            for d in data
        ]
