"""
Context analyzer for terminal environment
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class TerminalContext:
    """Current terminal context"""
    cwd: str
    user: str
    hostname: str
    shell: str
    files_in_cwd: List[str]
    directories_in_cwd: List[str]
    env_vars: Dict[str, str]
    running_processes: List[str]
    git_branch: Optional[str]
    git_repo: bool


class ContextAnalyzer:
    """Analyze current terminal context"""

    @staticmethod
    def get_context() -> TerminalContext:
        """Get current terminal context"""
        cwd = os.getcwd()
        user = os.getenv("USER", "unknown")
        hostname = os.getenv("HOSTNAME", "localhost")
        shell = os.getenv("SHELL", "/bin/bash").split("/")[-1]

        # List files and directories
        files = []
        directories = []
        try:
            for item in os.listdir(cwd):
                if os.path.isdir(os.path.join(cwd, item)):
                    directories.append(item)
                else:
                    files.append(item)
        except PermissionError:
            pass

        # Get environment variables
        env_vars = dict(os.environ)

        # Get running processes (simplified)
        running_processes = ContextAnalyzer._get_running_processes()

        # Check git status
        git_branch = ContextAnalyzer._get_git_branch(cwd)
        git_repo = git_branch is not None

        return TerminalContext(
            cwd=cwd,
            user=user,
            hostname=hostname,
            shell=shell,
            files_in_cwd=files[:20],  # Limit to 20
            directories_in_cwd=directories[:20],
            env_vars=env_vars,
            running_processes=running_processes[:10],  # Top 10
            git_branch=git_branch,
            git_repo=git_repo,
        )

    @staticmethod
    def _get_git_branch(cwd: str) -> Optional[str]:
        """Get current git branch if in repo"""
        try:
            result = subprocess.run(
                ["git", "-C", cwd, "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                timeout=1,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None

    @staticmethod
    def _get_running_processes() -> List[str]:
        """Get top running processes"""
        try:
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True,
                timeout=2,
            )
            processes = []
            for line in result.stdout.split("\n")[1:11]:  # Skip header, get top 10
                parts = line.split()
                if len(parts) > 10:
                    processes.append(parts[10])
            return processes
        except Exception:
            return []

    @staticmethod
    def analyze_cwd() -> Dict[str, Any]:
        """Analyze current working directory"""
        cwd = Path.cwd()

        return {
            "path": str(cwd),
            "is_git_repo": (cwd / ".git").exists(),
            "is_python_project": (cwd / "pyproject.toml").exists() or (cwd / "setup.py").exists(),
            "is_node_project": (cwd / "package.json").exists(),
            "is_rust_project": (cwd / "Cargo.toml").exists(),
            "has_docker": (cwd / "Dockerfile").exists(),
            "has_makefile": (cwd / "Makefile").exists(),
            "file_count": len(list(cwd.glob("*"))),
        }

    @staticmethod
    def check_tool_installed(tool: str) -> bool:
        """Check if a tool is installed"""
        try:
            subprocess.run(
                ["which", tool],
                capture_output=True,
                timeout=1,
                check=True,
            )
            return True
        except Exception:
            return False

    @staticmethod
    def get_installed_tools() -> List[str]:
        """Get list of common installed tools"""
        tools = [
            "git",
            "docker",
            "python",
            "python3",
            "node",
            "npm",
            "cargo",
            "ruby",
            "go",
            "gcc",
            "make",
            "curl",
            "wget",
            "vim",
            "nano",
            "tmux",
            "screen",
        ]

        installed = []
        for tool in tools:
            if ContextAnalyzer.check_tool_installed(tool):
                installed.append(tool)

        return installed
