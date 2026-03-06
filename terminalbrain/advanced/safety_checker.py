"""Safety Checker - Detects and confirms dangerous terminal operations."""

import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class RiskLevel(Enum):
    """Risk levels for commands."""

    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SafetyRisk:
    """Detected safety risk in a command."""

    command: str
    risk_level: RiskLevel
    description: str
    affected_items: List[str]  # What will be affected
    confirmation_required: bool
    suggested_alternative: Optional[str] = None


class SafetyChecker:
    """Detects and warns about dangerous terminal operations."""

    def __init__(self):
        """Initialize Safety Checker."""
        self.dangerous_patterns = self._load_dangerous_patterns()
        self.warning_patterns = self._load_warning_patterns()

    def _load_dangerous_patterns(self) -> dict:
        """Load patterns for CRITICAL and HIGH risk commands."""
        return {
            "critical": [
                {
                    "pattern": r"rm\s+-rf\s+/",
                    "description": "Recursive deletion of root directory or system files",
                    "risk": RiskLevel.CRITICAL,
                    "alternative": "Use 'find' with -delete for targeted deletion",
                },
                {
                    "pattern": r"dd\s+if=",
                    "description": "Direct disk writing - can destroy entire filesystems",
                    "risk": RiskLevel.CRITICAL,
                    "alternative": "Use 'cp', 'dd', or 'ddrescue' with extreme caution",
                },
                {
                    "pattern": r"mkfs\.",
                    "description": "Filesystem formatting - will erase all data",
                    "risk": RiskLevel.CRITICAL,
                    "alternative": "Double-check device path before running",
                },
                {
                    "pattern": r":(){ :|:& };:",
                    "description": "Fork bomb - will crash the system",
                    "risk": RiskLevel.CRITICAL,
                    "alternative": "Never run this",
                },
            ],
            "high": [
                {
                    "pattern": r"rm\s+-rf\s+[^/\s]*",
                    "description": "Recursive file deletion",
                    "risk": RiskLevel.HIGH,
                    "alternative": "Review files first with 'ls -la' or 'find'",
                },
                {
                    "pattern": r"sudo\s+.*\s+/etc/",
                    "description": "Modification of system configuration files",
                    "risk": RiskLevel.HIGH,
                    "alternative": "Backup files before modifying",
                },
                {
                    "pattern": r"sudo\s+chown\s+-R\s+",
                    "description": "Recursive permission/ownership change",
                    "risk": RiskLevel.HIGH,
                    "alternative": "Use specific paths instead of wildcards",
                },
                {
                    "pattern": r"chmod\s+777",
                    "description": "Overly permissive file permissions",
                    "risk": RiskLevel.HIGH,
                    "alternative": "Use more restrictive permissions like 755 or 644",
                },
                {
                    "pattern": r"mysql.*drop\s+database",
                    "description": "Database deletion",
                    "risk": RiskLevel.HIGH,
                    "alternative": "Backup database first",
                },
                {
                    "pattern": r"rm\s+/tmp/",
                    "description": "Deletion from /tmp - may affect running processes",
                    "risk": RiskLevel.HIGH,
                    "alternative": "Be careful not to delete needed files",
                },
            ],
        }

    def _load_warning_patterns(self) -> dict:
        """Load patterns for MEDIUM and LOW risk commands."""
        return {
            "medium": [
                {
                    "pattern": r"apt\s+remove|apt-get\s+remove",
                    "description": "System package removal",
                    "risk": RiskLevel.MEDIUM,
                },
                {
                    "pattern": r"sudo\s+.*password",
                    "description": "May contain hardcoded password",
                    "risk": RiskLevel.MEDIUM,
                },
                {
                    "pattern": r"kill\s+-9\s+\d+",
                    "description": "Force killing a process",
                    "risk": RiskLevel.MEDIUM,
                },
            ],
            "low": [
                {
                    "pattern": r"git\s+push.*\+",
                    "description": "Force push to git repository",
                    "risk": RiskLevel.LOW,
                },
                {
                    "pattern": r"mv\s+.*\s+/",
                    "description": "Moving files to system directories",
                    "risk": RiskLevel.LOW,
                },
            ],
        }

    def check(self, command: str) -> SafetyRisk:
        """
        Check command for safety risks.

        Args:
            command: The command to check

        Returns:
            SafetyRisk object with assessment
        """
        command_lower = command.lower()

        # Check critical patterns
        for pattern_info in self.dangerous_patterns.get("critical", []):
            if re.search(pattern_info["pattern"], command_lower):
                return SafetyRisk(
                    command=command,
                    risk_level=RiskLevel.CRITICAL,
                    description=pattern_info["description"],
                    affected_items=self._extract_affected_items(command),
                    confirmation_required=True,
                    suggested_alternative=pattern_info.get("alternative"),
                )

        # Check high-risk patterns
        for pattern_info in self.dangerous_patterns.get("high", []):
            if re.search(pattern_info["pattern"], command_lower):
                return SafetyRisk(
                    command=command,
                    risk_level=RiskLevel.HIGH,
                    description=pattern_info["description"],
                    affected_items=self._extract_affected_items(command),
                    confirmation_required=True,
                    suggested_alternative=pattern_info.get("alternative"),
                )

        # Check medium-risk patterns
        for pattern_info in self.warning_patterns.get("medium", []):
            if re.search(pattern_info["pattern"], command_lower):
                return SafetyRisk(
                    command=command,
                    risk_level=RiskLevel.MEDIUM,
                    description=pattern_info["description"],
                    affected_items=self._extract_affected_items(command),
                    confirmation_required=False,
                    suggested_alternative=pattern_info.get("alternative"),
                )

        # Check low-risk patterns
        for pattern_info in self.warning_patterns.get("low", []):
            if re.search(pattern_info["pattern"], command_lower):
                return SafetyRisk(
                    command=command,
                    risk_level=RiskLevel.LOW,
                    description=pattern_info["description"],
                    affected_items=self._extract_affected_items(command),
                    confirmation_required=False,
                    suggested_alternative=pattern_info.get("alternative"),
                )

        # No risk detected
        return SafetyRisk(
            command=command,
            risk_level=RiskLevel.SAFE,
            description="Command appears safe",
            affected_items=[],
            confirmation_required=False,
        )

    def _extract_affected_items(self, command: str) -> List[str]:
        """Extract file paths and resources affected by command."""
        affected = []

        # Extract file paths
        path_matches = re.findall(r"[/~][\w/\-\.]*", command)
        affected.extend(path_matches)

        # Extract database names from SQL
        db_matches = re.findall(r"database\s+(\w+)", command)
        affected.extend(db_matches)

        # Extract process IDs
        pid_matches = re.findall(r"kill\s+(?:-\d+\s+)?(\d+)", command)
        affected.extend(pid_matches)

        return affected[:5]  # Limit to 5 items

    def should_require_confirmation(self, risk: SafetyRisk) -> bool:
        """Determine if command requires user confirmation."""
        return (
            risk.confirmation_required
            and risk.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        )

    def get_safety_score(self, command: str) -> float:
        """
        Get a safety score for a command (0=dangerous, 1=safe).

        Args:
            command: Command to score

        Returns:
            Safety score 0-1
        """
        risk = self.check(command)

        scores = {
            RiskLevel.SAFE: 1.0,
            RiskLevel.LOW: 0.7,
            RiskLevel.MEDIUM: 0.4,
            RiskLevel.HIGH: 0.1,
            RiskLevel.CRITICAL: 0.0,
        }

        return scores.get(risk.risk_level, 0.5)

    def get_confirmation_message(self, risk: SafetyRisk) -> str:
        """Generate a confirmation message for user."""
        if risk.risk_level == RiskLevel.CRITICAL:
            return f"""⚠️ CRITICAL RISK DETECTED

Command: {risk.command}

{risk.description}

This command will affect:
{chr(10).join(f"  - {item}" for item in risk.affected_items)}

{risk.suggested_alternative or ""}

Type 'YES I UNDERSTAND THE RISKS' to continue, or press Ctrl+C to cancel.
"""
        elif risk.risk_level == RiskLevel.HIGH:
            return f"""⚠️ HIGH RISK DETECTED

Command: {risk.command}

{risk.description}

{risk.suggested_alternative or ""}

Continue? (y/n)
"""
        else:
            return f"Note: {risk.description}\n"

    def whitelist_command(self, pattern: str) -> None:
        """Add a command pattern to whitelist (don't check it)."""
        # Implement whitelist in subclass if needed
        pass
