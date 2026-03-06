"""
Plugin system for Terminal Brain.

Plugins extend Terminal Brain with optional features like local LLMs, 
ML prediction, voice commands, and workflow automation.

Architecture:

- Plugin directory: ~/.terminalbrain/plugins/
- Each plugin is a self-contained directory with __init__.py
- Plugins define metadata, dependencies, and entry points
- Plugin manager handles installation, loading, and lifecycle

"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any, List
import json
import subprocess
import sys


class PluginStatus(Enum):
    """Plugin installation and runtime status."""
    NOT_INSTALLED = "not_installed"
    INSTALLED = "installed"
    ENABLED = "enabled"
    DISABLED = "disabled"
    ERROR = "error"


@dataclass
class PluginMetadata:
    """Plugin metadata."""
    name: str
    version: str
    description: str
    author: str
    dependencies: List[str]
    optional_dependencies: List[str]
    entry_point: str  # e.g., "terminalbrain_llm:init"
    config_schema: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_dict(cls, data: Dict) -> "PluginMetadata":
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "dependencies": self.dependencies,
            "optional_dependencies": self.optional_dependencies,
            "entry_point": self.entry_point,
            "config_schema": self.config_schema,
        }


class PluginManager:
    """Manages plugin lifecycle and execution."""
    
    def __init__(self, plugin_dir: Optional[Path] = None):
        self.plugin_dir = plugin_dir or self._get_default_plugin_dir()
        self.plugin_dir.mkdir(parents=True, exist_ok=True)
        self._plugins: Dict[str, PluginMetadata] = {}
        self._load_plugin_registry()
    
    @staticmethod
    def _get_default_plugin_dir() -> Path:
        """Get default plugin directory."""
        config_dir = Path.home() / ".terminalbrain"
        return config_dir / "plugins"
    
    def _load_plugin_registry(self) -> None:
        """Load installed plugins from registry."""
        registry_file = self.plugin_dir / ".registry.json"
        if registry_file.exists():
            with open(registry_file) as f:
                data = json.load(f)
                for name, metadata in data.items():
                    self._plugins[name] = PluginMetadata.from_dict(metadata)
    
    def _save_plugin_registry(self) -> None:
        """Save plugin registry to disk."""
        registry_file = self.plugin_dir / ".registry.json"
        data = {name: meta.to_dict() for name, meta in self._plugins.items()}
        with open(registry_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def get_plugin_status(self, name: str) -> PluginStatus:
        """Get plugin status."""
        if name not in self._plugins:
            return PluginStatus.NOT_INSTALLED
        
        plugin_path = self.plugin_dir / name
        if not plugin_path.exists():
            return PluginStatus.ERROR
        
        # Check if enabled in config
        config_file = plugin_path / "config.json"
        if config_file.exists():
            with open(config_file) as f:
                config = json.load(f)
                enabled = config.get("enabled", False)
                return PluginStatus.ENABLED if enabled else PluginStatus.DISABLED
        
        return PluginStatus.INSTALLED
    
    def install_module(self, module_name: str) -> bool:
        """Install an optional module.
        
        Modules available:
        - llm: Local LLM support (Ollama, llama.cpp)
        - prediction: ML-based command prediction
        - knowledgebase: Local knowledge base with RAG
        - voice: Speech-to-text voice commands
        - workflows: Advanced workflow automation
        
        """
        module_installers = {
            "llm": self._install_llm_module,
            "prediction": self._install_prediction_module,
            "knowledgebase": self._install_kb_module,
            "voice": self._install_voice_module,
            "workflows": self._install_workflows_module,
        }
        
        if module_name not in module_installers:
            print(f"Unknown module: {module_name}")
            print(f"Available modules: {', '.join(module_installers.keys())}")
            return False
        
        installer = module_installers[module_name]
        return installer()
    
    def _install_llm_module(self) -> bool:
        """Install local LLM support module."""
        metadata = PluginMetadata(
            name="llm",
            version="1.0.0",
            description="Local LLM support via Ollama and llama.cpp",
            author="Terminal Brain Team",
            dependencies=[],
            optional_dependencies=["ollama>=0.0.11"],
            entry_point="terminalbrain.plugins.llm:init",
            config_schema={
                "runtime": {"type": "string", "enum": ["ollama", "llamacpp"]},
                "model": {"type": "string"},
                "api_base": {"type": "string"},
            }
        )
        return self._create_plugin("llm", metadata)
    
    def _install_prediction_module(self) -> bool:
        """Install ML prediction module."""
        metadata = PluginMetadata(
            name="prediction",
            version="1.0.0",
            description="ML-based command prediction using scikit-learn",
            author="Terminal Brain Team",
            dependencies=[],
            optional_dependencies=["scikit-learn>=1.3.0", "numpy>=1.24.0"],
            entry_point="terminalbrain.plugins.prediction:init",
        )
        return self._create_plugin("prediction", metadata)
    
    def _install_kb_module(self) -> bool:
        """Install knowledge base module."""
        metadata = PluginMetadata(
            name="knowledgebase",
            version="1.0.0",
            description="Local knowledge base with semantic search",
            author="Terminal Brain Team",
            dependencies=[],
            optional_dependencies=["faiss-cpu>=1.7.4", "sentence-transformers>=2.2.0"],
            entry_point="terminalbrain.plugins.knowledgebase:init",
        )
        return self._create_plugin("knowledgebase", metadata)
    
    def _install_voice_module(self) -> bool:
        """Install voice command module."""
        metadata = PluginMetadata(
            name="voice",
            version="1.0.0",
            description="Speech-to-text voice commands for Terminal Brain",
            author="Terminal Brain Team",
            dependencies=[],
            optional_dependencies=[],  # Would use system tools like PulseAudio
            entry_point="terminalbrain.plugins.voice:init",
        )
        return self._create_plugin("voice", metadata)
    
    def _install_workflows_module(self) -> bool:
        """Install workflow automation module."""
        metadata = PluginMetadata(
            name="workflows",
            version="1.0.0",
            description="Advanced workflow detection and automation",
            author="Terminal Brain Team",
            dependencies=[],
            optional_dependencies=["pyyaml>=6.0"],
            entry_point="terminalbrain.plugins.workflows:init",
        )
        return self._create_plugin("workflows", metadata)
    
    def _create_plugin(self, name: str, metadata: PluginMetadata) -> bool:
        """Create plugin directory structure and install dependencies."""
        plugin_path = self.plugin_dir / name
        plugin_path.mkdir(parents=True, exist_ok=True)
        
        # Save metadata
        metadata_file = plugin_path / "metadata.json"
        with open(metadata_file, "w") as f:
            json.dump(metadata.to_dict(), f, indent=2)
        
        # Create config file
        config_file = plugin_path / "config.json"
        with open(config_file, "w") as f:
            json.dump({"enabled": True}, f, indent=2)
        
        # Install dependencies
        all_deps = metadata.dependencies + metadata.optional_dependencies
        if all_deps:
            print(f"Installing dependencies for {name}...")
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install"] + all_deps,
                    check=True,
                    capture_output=True
                )
                print(f"✓ Dependencies installed for {name}")
            except subprocess.CalledProcessError as e:
                print(f"✗ Failed to install dependencies: {e.stderr.decode()}")
                return False
        
        # Register plugin
        self._plugins[name] = metadata
        self._save_plugin_registry()
        
        print(f"✓ Plugin '{name}' installed successfully")
        return True
    
    def uninstall_module(self, module_name: str) -> bool:
        """Uninstall an optional module."""
        if module_name not in self._plugins:
            print(f"Plugin not installed: {module_name}")
            return False
        
        plugin_path = self.plugin_dir / module_name
        import shutil
        shutil.rmtree(plugin_path)
        
        del self._plugins[module_name]
        self._save_plugin_registry()
        
        print(f"✓ Plugin '{module_name}' uninstalled")
        return True
    
    def list_plugins(self) -> Dict[str, PluginStatus]:
        """List all plugins and their status."""
        available = {
            "llm": "Local LLM support",
            "prediction": "ML command prediction",
            "knowledgebase": "Vector search knowledge base",
            "voice": "Voice commands",
            "workflows": "Workflow automation",
        }
        
        status = {}
        for name in available.keys():
            status[name] = self.get_plugin_status(name)
        
        return status
    
    def load_plugin(self, name: str):
        """Load and initialize a plugin."""
        if name not in self._plugins:
            raise ValueError(f"Plugin not installed: {name}")
        
        metadata = self._plugins[name]
        if self.get_plugin_status(name) != PluginStatus.ENABLED:
            raise ValueError(f"Plugin not enabled: {name}")
        
        # Dynamic import from entry point
        module_path, func_name = metadata.entry_point.rsplit(":", 1)
        module = __import__(module_path, fromlist=[func_name])
        init_func = getattr(module, func_name)
        
        return init_func()
