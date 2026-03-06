"""
Knowledge base and RAG pipeline
"""

from typing import List, Dict, Optional
import json
from pathlib import Path


class KnowledgeBase:
    """Command knowledge base"""

    # Built-in Linux command database
    COMMAND_DB = {
        "find": {
            "description": "Search for files",
            "syntax": "find [path] [options]",
            "examples": [
                "find . -name '*.txt'",
                "find / -type f -size +100M",
                "find . -mtime -7",
            ],
            "tags": ["file-operation", "search"],
        },
        "grep": {
            "description": "Search text patterns",
            "syntax": "grep [options] pattern [file]",
            "examples": [
                "grep 'error' logfile.txt",
                "grep -r 'TODO' src/",
                "grep -i 'case' file.txt",
            ],
            "tags": ["search", "text-processing"],
        },
        "ls": {
            "description": "List directory contents",
            "syntax": "ls [options] [path]",
            "examples": [
                "ls -la",
                "ls -lh",
                "ls -lt",
            ],
            "tags": ["file-operation", "directory"],
        },
        "git": {
            "description": "Version control system",
            "syntax": "git [command]",
            "examples": [
                "git add .",
                "git commit -m 'message'",
                "git push origin main",
            ],
            "tags": ["vcs", "version-control"],
        },
        "docker": {
            "description": "Container management",
            "syntax": "docker [command]",
            "examples": [
                "docker ps",
                "docker build -t app .",
                "docker run -d app",
            ],
            "tags": ["container", "deployment"],
        },
        "tar": {
            "description": "Archive files",
            "syntax": "tar [options] [archive] [files]",
            "examples": [
                "tar -czf archive.tar.gz folder/",
                "tar -xzf archive.tar.gz",
            ],
            "tags": ["compression", "archive"],
        },
        "ssh": {
            "description": "Remote secure shell",
            "syntax": "ssh [options] user@host",
            "examples": [
                "ssh user@example.com",
                "ssh -i key.pem user@host",
            ],
            "tags": ["networking", "remote"],
        },
        "curl": {
            "description": "Download web content",
            "syntax": "curl [options] url",
            "examples": [
                "curl https://example.com",
                "curl -X POST -d 'data' url",
            ],
            "tags": ["networking", "http"],
        },
        "pip": {
            "description": "Python package manager",
            "syntax": "pip [command]",
            "examples": [
                "pip install package",
                "pip list",
                "pip freeze > requirements.txt",
            ],
            "tags": ["python", "package-manager"],
        },
        "npm": {
            "description": "Node.js package manager",
            "syntax": "npm [command]",
            "examples": [
                "npm install package",
                "npm run build",
                "npm test",
            ],
            "tags": ["nodejs", "package-manager"],
        },
    }

    def __init__(self):
        self.commands = self.COMMAND_DB.copy()
        self.embeddings = {}

    def get_command_info(self, command: str) -> Optional[Dict]:
        """Get information about a command"""
        return self.commands.get(command)

    def search_commands(self, query: str) -> List[Dict]:
        """Search knowledge base by description or tags"""
        query_lower = query.lower()
        results = []

        for cmd, info in self.commands.items():
            if (
                query_lower in info["description"].lower()
                or any(tag in query_lower for tag in info.get("tags", []))
                or query_lower in cmd.lower()
            ):
                results.append({"command": cmd, "info": info})

        return results

    def get_examples(self, command: str) -> List[str]:
        """Get usage examples for a command"""
        info = self.get_command_info(command)
        if info:
            return info.get("examples", [])
        return []

    def get_similar_commands(self, command: str) -> List[str]:
        """Get similar commands by tags"""
        info = self.get_command_info(command)
        if not info:
            return []

        tags = set(info.get("tags", []))
        similar = []

        for cmd, cmd_info in self.commands.items():
            if cmd == command:
                continue

            cmd_tags = set(cmd_info.get("tags", []))
            if tags & cmd_tags:  # Has common tags
                similar.append(cmd)

        return similar

    def export_to_json(self, filepath: Path) -> None:
        """Export knowledge base to JSON"""
        with open(filepath, "w") as f:
            json.dump(self.commands, f, indent=2)

    def import_from_json(self, filepath: Path) -> None:
        """Import knowledge base from JSON"""
        with open(filepath, "r") as f:
            self.commands.update(json.load(f))


class RAGPipeline:
    """Retrieval-Augmented Generation pipeline"""

    def __init__(self):
        self.kb = KnowledgeBase()
        self.embedding_model = None
        self.index = None

    def index_knowledge_base(self) -> None:
        """Index knowledge base for retrieval"""
        try:
            from sentence_transformers import SentenceTransformer

            # Load embedding model
            self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

            # Embed all commands
            for cmd, info in self.kb.commands.items():
                text = f"{cmd} {info['description']} {' '.join(info.get('examples', []))}"
                embedding = self.embedding_model.encode(text)
                self.kb.embeddings[cmd] = embedding

        except ImportError:
            print("sentence-transformers not installed, RAG unavailable")

    def retrieve(self, query: str, top_k: int = 5) -> List[str]:
        """
        Retrieve most relevant commands for a query

        Args:
            query: Natural language query
            top_k: Number of results

        Returns:
            List of relevant commands
        """
        if not self.embedding_model:
            # Fallback to simple search
            results = self.kb.search_commands(query)
            return [r["command"] for r in results[:top_k]]

        try:
            from sklearn.metrics.pairwise import cosine_similarity
            import numpy as np

            query_embedding = self.embedding_model.encode(query)

            # Calculate similarity
            similarities = {}
            for cmd, embedding in self.kb.embeddings.items():
                sim = cosine_similarity([query_embedding], [embedding])[0][0]
                similarities[cmd] = sim

            # Sort by similarity
            ranked = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
            return [cmd for cmd, _ in ranked[:top_k]]

        except Exception:
            return []

    def augment_with_context(self, query: str, retrieved_commands: List[str]) -> str:
        """
        Augment prompt with retrieved context

        Args:
            query: Original query
            retrieved_commands: Retrieved relevant commands

        Returns:
            Augmented prompt for LLM
        """
        context = "Relevant commands:\n"
        for cmd in retrieved_commands:
            info = self.kb.get_command_info(cmd)
            if info:
                context += f"- {cmd}: {info['description']}\n"

        return f"""{context}

User query: {query}

Based on the relevant commands above, suggest the best command to use."""
