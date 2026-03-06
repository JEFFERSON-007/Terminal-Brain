"""Workflow Recommender - Suggests intelligent command pipelines for common tasks."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable
from datetime import datetime


@dataclass
class WorkflowRecommendation:
    """Recommendation for a command workflow/pipeline."""

    task: str  # What the user wants to accomplish
    pipeline: str  # The suggested command pipeline
    explanation: str  # Why this pipeline is recommended
    alternative_pipelines: List[str] = field(default_factory=list)
    tools_required: List[str] = field(default_factory=list)
    estimated_time: str = "quick"  # quick, moderate, slow


class WorkflowRecommender:
    """Recommends intelligent command pipelines for common tasks."""

    def __init__(self):
        """Initialize Workflow Recommender."""
        self.pipeline_db = self._build_pipeline_database()
        self.custom_pipelines: Dict[str, str] = {}

    def _build_pipeline_database(self) -> Dict[str, List[Dict]]:
        """Build database of common pipelines."""
        return {
            "find_large_files": [
                {
                    "pipeline": "du -ah | sort -rh | head -20",
                    "explanation": "Show top 20 largest files/directories",
                    "tools": ["du", "sort", "head"],
                    "time": "quick",
                },
                {
                    "pipeline": "find . -type f -size +100M -exec ls -lh {} \\;",
                    "explanation": "Find all files larger than 100MB",
                    "tools": ["find", "ls"],
                    "time": "moderate",
                },
            ],
            "find_recently_modified": [
                {
                    "pipeline": "find . -type f -mtime -7 -ls | sort -k10 -r",
                    "explanation": "Files modified in last 7 days",
                    "tools": ["find", "sort"],
                    "time": "quick",
                },
                {
                    "pipeline": "find . -type f -mmin -60 | head -20",
                    "explanation": "Files modified in last hour",
                    "tools": ["find", "head"],
                    "time": "quick",
                },
            ],
            "search_in_files": [
                {
                    "pipeline": "grep -r 'pattern' . --include='*.py' -n",
                    "explanation": "Search for pattern in Python files with line numbers",
                    "tools": ["grep"],
                    "time": "quick",
                },
                {
                    "pipeline": "find . -name '*.txt' -exec grep -l 'pattern' {} \\;",
                    "explanation": "Find text files containing pattern",
                    "tools": ["find", "grep"],
                    "time": "moderate",
                },
            ],
            "monitor_system": [
                {
                    "pipeline": "watch -n 1 'ps aux | head -20'",
                    "explanation": "Monitor top 20 processes every second",
                    "tools": ["watch", "ps", "head"],
                    "time": "quick",
                },
                {
                    "pipeline": "top -b -n 1 | head -30",
                    "explanation": "Single snapshot of top processes",
                    "tools": ["top", "head"],
                    "time": "quick",
                },
            ],
            "cleanup_old_files": [
                {
                    "pipeline": "find . -type f -mtime +30 -delete",
                    "explanation": "Delete files older than 30 days (DANGEROUS)",
                    "tools": ["find"],
                    "time": "quick",
                },
                {
                    "pipeline": "find . -type f -mtime +30",
                    "explanation": "Find files older than 30 days (safe preview)",
                    "tools": ["find"],
                    "time": "quick",
                },
            ],
            "compress_files": [
                {
                    "pipeline": "tar -czf archive.tar.gz folder/",
                    "explanation": "Create gzipped tar archive",
                    "tools": ["tar", "gzip"],
                    "time": "moderate",
                },
                {
                    "pipeline": "zip -r archive.zip folder/",
                    "explanation": "Create zip archive",
                    "tools": ["zip"],
                    "time": "moderate",
                },
            ],
            "batch_rename_files": [
                {
                    "pipeline": "for f in *.old; do mv \"$f\" \"${f%.old}.new\"; done",
                    "explanation": "Rename all .old files to .new",
                    "tools": ["mv"],
                    "time": "quick",
                },
                {
                    "pipeline": "rename 's/old/new/' *.txt",
                    "explanation": "Use rename tool to change files (if available)",
                    "tools": ["rename"],
                    "time": "quick",
                },
            ],
            "count_lines": [
                {
                    "pipeline": "wc -l *.py | tail -1",
                    "explanation": "Total lines in all Python files",
                    "tools": ["wc", "tail"],
                    "time": "quick",
                },
                {
                    "pipeline": "find . -name '*.py' -exec wc -l {} + | tail -1",
                    "explanation": "Total lines in Python files (recursive)",
                    "tools": ["find", "wc"],
                    "time": "quick",
                },
            ],
            "backup_system": [
                {
                    "pipeline": "tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz ~/",
                    "explanation": "Create timestamped backup of home directory",
                    "tools": ["tar", "gzip", "date"],
                    "time": "slow",
                },
                {
                    "pipeline": "rsync -av --delete ~/ /backup/home/",
                    "explanation": "Sync home to backup location",
                    "tools": ["rsync"],
                    "time": "moderate",
                },
            ],
            "convert_images": [
                {
                    "pipeline": "for f in *.jpg; do convert \"$f\" \"${f%.jpg}.png\"; done",
                    "explanation": "Convert all JPG to PNG",
                    "tools": ["convert", "ImageMagick"],
                    "time": "moderate",
                },
                {
                    "pipeline": "mogrify -format png *.jpg",
                    "explanation": "Batch convert JPG to PNG with ImageMagick",
                    "tools": ["mogrify", "ImageMagick"],
                    "time": "moderate",
                },
            ],
            "list_installed_packages": [
                {
                    "pipeline": "apt list --installed | wc -l",
                    "explanation": "Count installed Debian packages",
                    "tools": ["apt", "wc"],
                    "time": "quick",
                },
                {
                    "pipeline": "pip list | grep -c '^'",
                    "explanation": "Count installed Python packages",
                    "tools": ["pip", "grep", "wc"],
                    "time": "quick",
                },
            ],
            "check_disk_usage": [
                {
                    "pipeline": "df -h | grep -v '^Filesystem'",
                    "explanation": "Show disk usage for all drives",
                    "tools": ["df", "grep"],
                    "time": "quick",
                },
                {
                    "pipeline": "du -sh /*",
                    "explanation": "Show disk usage by directory",
                    "tools": ["du"],
                    "time": "quick",
                },
            ],
        }

    def recommend(self, task: str) -> Optional[WorkflowRecommendation]:
        """
        Recommend a workflow for a given task.

        Args:
            task: Description of what user wants to accomplish

        Returns:
            WorkflowRecommendation or None if no match found
        """
        # Normalize task
        task_lower = task.lower()

        # Check custom pipelines first
        for key, pipeline in self.custom_pipelines.items():
            if key.lower() in task_lower:
                return WorkflowRecommendation(
                    task=task,
                    pipeline=pipeline,
                    explanation="Custom pipeline",
                    tools_required=[],
                )

        # Search pipeline database
        for task_key, pipelines in self.pipeline_db.items():
            if task_key.replace("_", " ") in task_lower or task_lower in task_key:
                if pipelines:
                    main = pipelines[0]
                    alternatives = [p["pipeline"] for p in pipelines[1:]]

                    return WorkflowRecommendation(
                        task=task,
                        pipeline=main["pipeline"],
                        explanation=main["explanation"],
                        alternative_pipelines=alternatives,
                        tools_required=main.get("tools", []),
                        estimated_time=main.get("time", "quick"),
                    )

        return None

    def list_available_workflows(self) -> List[str]:
        """List all available workflow categories."""
        return list(self.pipeline_db.keys()) + list(self.custom_pipelines.keys())

    def add_custom_pipeline(
        self, task_name: str, pipeline: str, explanation: str = ""
    ) -> None:
        """Add a custom pipeline recommendation."""
        self.custom_pipelines[task_name] = {
            "pipeline": pipeline,
            "explanation": explanation or f"Custom: {task_name}",
        }

    def get_similar_workflows(self, task: str) -> List[str]:
        """Get workflows similar to requested task."""
        task_lower = task.lower()
        similar = []

        for key in self.pipeline_db.keys():
            key_normalized = key.replace("_", " ")
            # Simple similarity check
            if any(
                word in task_lower for word in key_normalized.split()
            ) or any(word in key_normalized for word in task_lower.split()):
                similar.append(key)

        return similar

    def explain_pipeline(self, pipeline: str) -> str:
        """Explain what a pipeline does."""
        # Parse common patterns
        explanations = []

        if "|" in pipeline:
            parts = pipeline.split("|")
            explanations.append(f"Pipeline with {len(parts)} steps:")
            for i, part in enumerate(parts, 1):
                explanations.append(f"  {i}. {part.strip()}")
        else:
            explanations.append(f"Single command: {pipeline}")

        return "\n".join(explanations)
