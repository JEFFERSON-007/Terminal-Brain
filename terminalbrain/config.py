"""
Configuration management for Terminal Brain
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
import toml
from pydantic import BaseModel, Field


class GeneralConfig(BaseModel):
    """General configuration settings"""
    theme: str = "dark"
    startup_message: bool = True
    suggestion_frequency: int = 3


class AIConfig(BaseModel):
    """AI and model configuration"""
    backend: str = "ollama"  # "ollama", "openai", "local"
    model: str = "mistral"
    temperature: float = 0.7
    max_suggestions: int = 5
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None


class UIConfig(BaseModel):
    """Terminal UI configuration"""
    show_dashboard: bool = True
    show_battery: bool = True
    show_network_speed: bool = True
    show_processes: bool = True
    refresh_interval: int = 2000  # milliseconds


class SecurityConfig(BaseModel):
    """Security settings"""
    dangerous_commands: list = Field(
        default_factory=lambda: ["rm -rf", "mkfs", "dd", ":|", "> /dev"]
    )
    require_confirmation: bool = True


class KnowledgeConfig(BaseModel):
    """Knowledge base configuration"""
    enable_rag: bool = True
    knowledge_source: str = "tldr"  # "tldr", "man", "both"
    cache_embeddings: bool = True


class AdvancedFeaturesConfig(BaseModel):
    """Advanced features configuration"""
    # Error Analysis
    error_analysis_enabled: bool = True
    auto_fix_suggestions: bool = True
    
    # Command Prediction
    prediction_enabled: bool = True
    prediction_confidence_threshold: float = 0.6
    
    # Workflow Detection
    workflow_detection_enabled: bool = True
    workflow_min_frequency: int = 3
    workflow_storage_dir: str = "~/.terminalbrain/workflows"
    
    # Command Explanation
    explain_commands: bool = True
    use_man_pages: bool = True
    
    # Script Generation
    script_generation_enabled: bool = True
    script_safety_checks: bool = True
    
    # Alias Suggestions
    alias_suggestions_enabled: bool = True
    min_alias_frequency: int = 3
    min_char_savings: int = 3
    
    # Learning Feedback
    learning_enabled: bool = True
    feedback_history_file: str = "~/.terminalbrain/feedback.json"
    
    # Safety
    safety_level: str = "high"  # "low", "medium", "high"
    require_command_confirmation: bool = True
    dangerous_command_patterns: list = Field(
        default_factory=lambda: ["rm -rf /", "dd if=", "mkfs", ":/:", "chmod 777"]
    )


class Config(BaseModel):
    """Complete Terminal Brain configuration"""
    general: GeneralConfig = Field(default_factory=GeneralConfig)
    ai: AIConfig = Field(default_factory=AIConfig)
    ui: UIConfig = Field(default_factory=UIConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    knowledge: KnowledgeConfig = Field(default_factory=KnowledgeConfig)
    advanced: AdvancedFeaturesConfig = Field(default_factory=AdvancedFeaturesConfig)

    class Config:
        extra = "allow"


def get_config_path() -> Path:
    """Get the configuration file path"""
    config_dir = Path.home() / ".config" / "terminalbrain"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "terminalbrain.toml"


def load_config() -> Config:
    """Load configuration from file or create defaults"""
    config_path = get_config_path()

    if config_path.exists():
        try:
            data = toml.load(config_path)
            return Config(**data)
        except Exception as e:
            print(f"Warning: Could not load config from {config_path}: {e}")
            return Config()
    else:
        # Create default config file
        config = Config()
        save_config(config)
        return config


def save_config(config: Config) -> None:
    """Save configuration to file"""
    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)

    data = config.model_dump()
    with open(config_path, "w") as f:
        toml.dump(data, f)


def get_default_config_toml() -> str:
    """Get default configuration as TOML string"""
    return """
# Terminal Brain Configuration

[general]
theme = "dark"
startup_message = true
suggestion_frequency = 3

[ai]
backend = "ollama"  # "ollama", "openai", "local"
model = "mistral"
temperature = 0.7
max_suggestions = 5
# openai_api_key = "sk-..."
# anthropic_api_key = "..."

[ui]
show_dashboard = true
show_battery = true
show_network_speed = true
show_processes = true
refresh_interval = 2000  # milliseconds

[security]
dangerous_commands = ["rm -rf", "mkfs", "dd", ":|", "> /dev"]
require_confirmation = true

[knowledge]
enable_rag = true
knowledge_source = "tldr"  # "tldr", "man", "both"
cache_embeddings = true

[advanced]
# Error Analysis Engine
error_analysis_enabled = true
auto_fix_suggestions = true

# Command Prediction Engine
prediction_enabled = true
prediction_confidence_threshold = 0.6

# Workflow Detection
workflow_detection_enabled = true
workflow_min_frequency = 3
workflow_storage_dir = "~/.terminalbrain/workflows"

# Command Explanation
explain_commands = true
use_man_pages = true

# Script Generation
script_generation_enabled = true
script_safety_checks = true

# Alias Suggestions
alias_suggestions_enabled = true
min_alias_frequency = 3
min_char_savings = 3

# Learning Feedback Loop
learning_enabled = true
feedback_history_file = "~/.terminalbrain/feedback.json"

# Safety & Security
safety_level = "high"  # "low", "medium", "high"
require_command_confirmation = true
dangerous_command_patterns = ["rm -rf /", "dd if=", "mkfs", ":/:", "chmod 777"]
"""
