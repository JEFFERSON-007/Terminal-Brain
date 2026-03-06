"""Script Generator - Generates shell scripts from natural language descriptions."""

import re
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from datetime import datetime


@dataclass
class GeneratedScript:
    """Generated shell script."""

    name: str
    description: str
    content: str
    language: str = "bash"
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    requires: List[str] = field(default_factory=list)  # Required tools/packages
    safety_level: str = "medium"  # low, medium, high


class ScriptGenerator:
    """Generates shell scripts from natural language descriptions using AI patterns."""

    def __init__(self):
        """Initialize Script Generator."""
        self.script_templates = self._load_templates()
        self.safety_checks = self._load_safety_checks()

    def _load_templates(self) -> Dict[str, str]:
        """Load common script templates."""
        return {
            "backup": """#!/bin/bash
# Backup script - {description}
set -e

BACKUP_DIR="$HOME/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="{backup_name}_$TIMESTAMP.tar.gz"

mkdir -p "$BACKUP_DIR"
echo "Creating backup: $BACKUP_NAME"

tar -czf "$BACKUP_DIR/$BACKUP_NAME" {target}

echo "Backup completed: $BACKUP_DIR/$BACKUP_NAME"
""",
            "deploy": """#!/bin/bash
# Deployment script - {description}
set -e

echo "Starting deployment..."

# Pull latest changes
git pull origin {branch}

# Build
{build_command}

# Deploy
{deploy_command}

echo "Deployment completed!"
""",
            "cleanup": """#!/bin/bash
# Cleanup script - {description}
set -e

echo "Cleaning up..."

{cleanup_commands}

echo "Cleanup completed!"
""",
            "install": """#!/bin/bash
# Installation script - {description}
set -e

echo "Installing {package}..."

{install_commands}

echo "Installation completed!"
""",
        }

    def _load_safety_checks(self) -> Dict[str, str]:
        """Load safety check patterns."""
        return {
            "rm -rf": "DANGER: Recursive file deletion",
            "dd": "DANGER: Direct disk writing",
            "mkfs": "DANGER: Filesystem formatting",
            "://:": "DANGER: Infinite loop pattern",
            "chmod 777": "WARNING: Overly permissive permissions",
        }

    def generate(self, description: str) -> GeneratedScript:
        """
        Generate a shell script from natural language description.

        Args:
            description: Natural language script description

        Returns:
            GeneratedScript with generated content
        """
        # Detect script type
        script_type = self._detect_script_type(description)

        # Generate appropriate script
        if script_type == "backup":
            script = self._generate_backup_script(description)
        elif script_type == "deploy":
            script = self._generate_deploy_script(description)
        elif script_type == "cleanup":
            script = self._generate_cleanup_script(description)
        elif script_type == "install":
            script = self._generate_install_script(description)
        else:
            script = self._generate_generic_script(description)

        # Check safety
        safety_level = self._check_safety(script.content)
        script.safety_level = safety_level

        return script

    def _detect_script_type(self, description: str) -> str:
        """Detect what type of script is needed."""
        desc_lower = description.lower()

        if any(word in desc_lower for word in ["backup", "archive", "copy"]):
            return "backup"
        elif any(word in desc_lower for word in ["deploy", "release", "push"]):
            return "deploy"
        elif any(word in desc_lower for word in ["clean", "cleanup", "remove"]):
            return "cleanup"
        elif any(word in desc_lower for word in ["install", "setup", "configure"]):
            return "install"
        else:
            return "generic"

    def _generate_backup_script(self, description: str) -> GeneratedScript:
        """Generate a backup script."""
        # Extract target from description
        target = self._extract_path(description) or "/home/$USER"
        name = self._extract_name(description) or "backup"

        content = self.script_templates["backup"].format(
            description=description, backup_name=name, target=target
        )

        return GeneratedScript(
            name=f"{name}_backup.sh",
            description=f"Backup script: {description}",
            content=content,
            requires=["tar", "gzip"],
            safety_level="low",
        )

    def _generate_deploy_script(self, description: str) -> GeneratedScript:
        """Generate a deployment script."""
        branch = self._extract_branch(description) or "main"
        name = self._extract_name(description) or "deploy"

        build_cmd = "echo 'Building...' && npm run build"
        deploy_cmd = "echo 'Deploying...' && npm run start"

        if "docker" in description.lower():
            build_cmd = "docker build -t app ."
            deploy_cmd = "docker compose up -d"

        content = self.script_templates["deploy"].format(
            description=description,
            branch=branch,
            build_command=build_cmd,
            deploy_command=deploy_cmd,
        )

        return GeneratedScript(
            name=f"{name}_deploy.sh",
            description=f"Deployment script: {description}",
            content=content,
            requires=["git", "docker"] if "docker" in description else ["git"],
            safety_level="high",
        )

    def _generate_cleanup_script(self, description: str) -> GeneratedScript:
        """Generate a cleanup script."""
        name = self._extract_name(description) or "cleanup"

        # Generate cleanup commands based on description
        cleanup_cmds = self._generate_cleanup_commands(description)

        content = self.script_templates["cleanup"].format(
            description=description, cleanup_commands=cleanup_cmds
        )

        return GeneratedScript(
            name=f"{name}_cleanup.sh",
            description=f"Cleanup script: {description}",
            content=content,
            safety_level="medium",
        )

    def _generate_install_script(self, description: str) -> GeneratedScript:
        """Generate an installation script."""
        name = self._extract_name(description) or "install"
        package = name

        install_cmds = self._generate_install_commands(description)

        content = self.script_templates["install"].format(
            description=description, package=package, install_commands=install_cmds
        )

        return GeneratedScript(
            name=f"{name}_install.sh",
            description=f"Installation script: {description}",
            content=content,
            safety_level="low",
        )

    def _generate_generic_script(self, description: str) -> GeneratedScript:
        """Generate a generic script."""
        name = self._extract_name(description) or "script"

        # Create basic script with comments
        content = f"""#!/bin/bash
# Script: {description}
set -e

echo "Running: {description}"

# Add your commands here
# {description}

echo "Done!"
"""

        return GeneratedScript(
            name=f"{name}.sh",
            description=description,
            content=content,
            safety_level="medium",
        )

    def _generate_cleanup_commands(self, description: str) -> str:
        """Generate cleanup commands from description."""
        commands = []

        if "cache" in description.lower():
            commands.append("rm -rf ~/.cache/*")
        if "temp" in description.lower() or "tmp" in description.lower():
            commands.append("rm -rf /tmp/*")
        if "log" in description.lower():
            commands.append("rm -rf ~/.local/share/*/logs")
        if "docker" in description.lower():
            commands.append("docker system prune -f")
        if "npm" in description.lower():
            commands.append("npm cache clean --force")

        if not commands:
            commands.append("# Add cleanup commands here")

        return "\n".join(commands)

    def _generate_install_commands(self, description: str) -> str:
        """Generate install commands from description."""
        commands = []

        if "python" in description.lower():
            commands.append("pip install {package}")
        if "npm" in description.lower() or "node" in description.lower():
            commands.append("npm install {package}")
        if "apt" in description.lower() or "ubuntu" in description.lower():
            commands.append("sudo apt update && sudo apt install {package}")

        if not commands:
            commands.append("# Add installation commands for {package}")

        return "\n".join(commands)

    def _extract_path(self, text: str) -> Optional[str]:
        """Extract file path from text."""
        match = re.search(r"(/[\w/.-]*|\$\{?\w+\}?)", text)
        return match.group(1) if match else None

    def _extract_name(self, text: str) -> Optional[str]:
        """Extract name from description."""
        words = text.lower().split()
        if words:
            return words[0]
        return None

    def _extract_branch(self, text: str) -> Optional[str]:
        """Extract git branch from text."""
        match = re.search(r"(main|master|develop|dev|branch\s+(\w+))", text.lower())
        if match:
            return match.group(2) if match.group(2) else match.group(1)
        return None

    def _check_safety(self, script_content: str) -> str:
        """Check script for dangerous operations."""
        dangers = 0
        warnings = 0

        for pattern, description in self.safety_checks.items():
            if pattern in script_content:
                if "DANGER" in description:
                    dangers += 1
                else:
                    warnings += 1

        if dangers > 0:
            return "high"
        elif warnings > 0:
            return "medium"
        else:
            return "low"

    def add_safety_header(self, script: GeneratedScript) -> str:
        """Add safety headers and checks to script."""
        if script.safety_level == "high":
            warning = (
                f"\n# ⚠️ WARNING: This script contains potentially dangerous operations\n"
                f"# Please review carefully before running\n\n"
            )
            return warning + script.content
        elif script.safety_level == "medium":
            return script.content
        else:
            return script.content
