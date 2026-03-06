# Terminal Brain Examples

## Installation & Setup

### Quick Start

```bash
# 1. Clone and enter directory
cd "Terminal Brain"

# 2. Run installation script
bash scripts/install.sh

# 3. Reload shell
source ~/.bashrc  # or ~/.zshrc

# 4. Test installation
tb ask "list files"
```

### Manual Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install package
pip install -e .

# Setup shell integration
bash scripts/setup_hooks.sh
```

### Setup Local LLM (Optional but Recommended)

```bash
# Install Ollama from https://ollama.ai

# Download a model
ollama pull mistral    # ~4GB, good general model
ollama pull neural-chat # ~4GB, good for code
ollama pull codellama  # ~7GB, specialized for coding

# Verify installation
ollama list

# Test in Terminal Brain
tb ask "find large files"
```

## Command Examples

### 1. Get Command Suggestions

```bash
# Natural language query
tb ask "find large files"
# Output:
# 1. find / -type f -size +100M (92% | llm)
# 2. find . -type f -size +100M (85% | history)
# 3. du -sh /* (78% | history)

# With explanations
tb ask "compress this folder" --explain
# Shows detailed explanations for each suggestion

# Get more suggestions
tb ask "find log files" --top 10
```

### 2. Predict Next Command

```bash
# Predict after current history
tb predict

# Predict after specific command
tb predict "git add ."
# Output:
# 1. git commit (85% probability)
# 2. git push (10% probability)
# 3. git status (5% probability)
```

### 3. System Dashboard

```bash
# Show real-time system metrics
tb dashboard

# Output:
# Terminal Brain Dashboard
# CPU Usage: 27%
# Memory: 5.1 GB / 16 GB (32%)
# Disk: 240 GB / 512 GB (47%)
# Battery: 82% (Charging)
# Top Processes (CPU):
# - python: 12.5%
# - firefox: 8.3%
```

### 4. Generate Scripts

```bash
# Generate a backup script
tb generate "backup home folder daily"
# Displays generated bash script with explanation

# Generate and save to file
tb generate "deploy docker container" --save --output deploy.sh

# The script is created, explained, and made executable
chmod +x deploy.sh
./deploy.sh
```

### 5. Analyze History

```bash
# Analyze your command history
tb analyze

# Output shows:
# - Total commands used
# - Unique commands
# - Most used commands
# - Most used command sequences
# - Suggested aliases based on frequency
```

### 6. Browse Knowledge Base

```bash
# See all available commands in knowledge base
tb knowledge

# Output shows table of:
# Command | Description | Tags
# find    | Search for files | file-operation, search
# grep    | Search text patterns | search, text-processing
# ...
```

### 7. Configuration Management

```bash
# View current configuration
tb config show

# Edit configuration (opens in $EDITOR)
tb config edit

# Reset to defaults
tb config reset

# Edit the TOML directly
~/.config/terminalbrain/terminalbrain.toml
```

## Shell Integration Examples

### Using Terminal Brain Functions

```bash
# Ask command suggestions (aliased)
ask "find python files"
tb "find python files"

# Shorthand aliases
alias ll="ls -la"          # Set up by Terminal Brain
alias ga="git add"         # Suggested by Terminal Brain

# View dashboard
tbdash

# Generate and run script directly
tb generate "setup python project" --save
bash script.sh
```

### In Shell Scripts

```bash
#!/bin/bash

# Use TB recommendation engine in scripts
if command -v tb &> /dev/null; then
    # Get suggestion for file backup
    BACKUP_CMD=$(tb ask "backup files" --top 1 | grep "^[0-9]" | cut -d' ' -f2-)
    eval "$BACKUP_CMD"
fi
```

## Python API Examples

### Example 1: Get Command Recommendations

```python
from terminalbrain.ai import RecommendationEngine
import asyncio

async def main():
    # Create engine
    engine = RecommendationEngine(llm_backend="ollama", model="mistral")
    
    # Initialize (loads history, trains ML model)
    await engine.initialize()
    
    # Get recommendations
    suggestions = await engine.recommend("find large files", top_n=5)
    
    # Display results
    for i, suggestion in enumerate(suggestions, 1):
        print(f"{i}. {suggestion.command}")
        print(f"   Confidence: {suggestion.confidence:.0%}")
        print(f"   Source: {suggestion.source}")
        print(f"   Info: {suggestion.explanation}\n")

# Run
asyncio.run(main())
```

### Example 2: Analyze Command History

```python
from terminalbrain.core import HistoryAnalyzer

# Load and analyze history
analyzer = HistoryAnalyzer()
analyzer.load_history()

# Get statistics
stats = analyzer.get_statistics()
print(f"Total commands: {stats['total_commands']}")
print(f"Unique commands: {stats['unique_commands']}")
print(f"Most used: {stats['most_used_command']}")

# Show top commands
print("\nTop 10 commands:")
for cmd, count in analyzer.get_most_common(10):
    print(f"  {cmd}: {count} times")

# Get alias suggestions
print("\nSuggested aliases:")
for alias, command in analyzer.suggest_aliases(min_frequency=3).items():
    print(f"  alias {alias}='{command}'")
```

### Example 3: Command Prediction

```python
from terminalbrain.ai import RecommendationEngine
import asyncio

async def predict_workflow():
    engine = RecommendationEngine()
    await engine.initialize()
    
    # Common workflow
    workflow = [
        "cd project",
        "git status",
        "git add .",
        "git commit -m 'changes'",
    ]
    
    print("Workflow analysis:")
    for cmd in workflow:
        predictions = await engine.predict_next(cmd, top_n=2)
        print(f"\nAfter: {cmd}")
        for pred in predictions:
            print(f"  → {pred.command} ({pred.confidence:.0%})")

asyncio.run(predict_workflow())
```

### Example 4: Monitor System

```python
from terminalbrain.monitor import SystemMonitor, ProcessMonitor
import time

# Get current metrics
metrics = SystemMonitor.get_metrics()
print(f"CPU: {metrics.cpu_percent:.1f}%")
print(f"RAM: {metrics.ram_used_gb:.1f}GB / {metrics.ram_total_gb:.1f}GB")
print(f"Disk: {metrics.disk_used_gb:.0f}GB / {metrics.disk_total_gb:.0f}GB")

if metrics.battery_percent:
    print(f"Battery: {metrics.battery_percent:.0f}%")

# Get top processes
print("\nTop 5 processes by CPU:")
for proc in ProcessMonitor.get_top_processes(5, sort_by="cpu"):
    print(f"  {proc.name}: {proc.cpu_percent:.1f}%")
```

### Example 5: Error Handling

```python
from terminalbrain.ai import ErrorDebugger

debugger = ErrorDebugger()

# User tries command and gets error
broken_cmd = "pytohn script.py"
error_msg = "command not found: pytohn"

# Get debugging info
mistakes = debugger.detect_common_mistakes(broken_cmd)
for mistake in mistakes:
    print(f"Issue: {mistake['type']}")
    print(f"Suggestion: {mistake.get('suggestion', mistake.get('message'))}")

# Get help
help_cmds = debugger.get_help_command("python")
print(f"\nHelp commands:")
for cmd in help_cmds:
    print(f"  {cmd}")
```

### Example 6: Knowledge Base Search

```python
from terminalbrain.knowledge import KnowledgeBase, RAGPipeline

# Search knowledge base
kb = KnowledgeBase()

# Get info about a command
find_info = kb.get_command_info("find")
print(f"find: {find_info['description']}")
print(f"Syntax: {find_info['syntax']}")
print(f"Examples:")
for ex in find_info['examples']:
    print(f"  {ex}")

# Search for commands
results = kb.search_commands("search file")
for result in results:
    print(f"\n{result['command']}: {result['info']['description']}")

# Use RAG for semantic search
rag = RAGPipeline()
relevant = rag.retrieve("find large files", top_k=3)
print(f"\nSemantically relevant commands: {relevant}")
```

## Advanced Workflows

### Workflow 1: Smart Directory Navigation

```bash
#!/bin/bash

# Use Terminal Brain to suggest directory operations
suggest_dir_cmd() {
    local desc="$1"
    tb ask "$desc" --top 1 | grep "^\." | head -1
}

# Navigate to project
cd $(suggest_dir_cmd "find python projects")
ls -la

# Or combine with Terminal Brain predictions
cd project
# Terminal Brain suggests: git status, git add, etc.
```

### Workflow 2: Automated Backup

```python
from terminalbrain.ai import RecommendationEngine
import asyncio
import subprocess

async def smart_backup():
    engine = RecommendationEngine()
    await engine.initialize()
    
    # Get best backup command for current directory
    suggestions = await engine.recommend(
        "backup current directory",
        top_n=1
    )
    
    if suggestions:
        cmd = suggestions[0].command
        print(f"Executing: {cmd}")
        subprocess.run(cmd, shell=True)

# Run daily
# Add to crontab:
# 0 2 * * * python3 /path/to/smart_backup.py

asyncio.run(smart_backup())
```

### Workflow 3: Learning Custom Commands

```python
from terminalbrain.core import HistoryAnalyzer

# Periodically analyze history to learn patterns
analyzer = HistoryAnalyzer()
analyzer.load_history()

# Find command sequences specific to your workflow
sequences = analyzer.command_sequences[-100:]  # Last 100 sequences

print("Your command patterns:")
from collections import Counter
seq_freq = Counter(sequences)
for (cmd1, cmd2), count in seq_freq.most_common(5):
    print(f"  {cmd1} → {cmd2}: {count} times")

# Create aliases for frequent sequences
aliases = analyzer.suggest_aliases(min_frequency=10)
print("\nCreate these aliases:")
for alias, cmd in aliases.items():
    print(f"  alias {alias}='{cmd}'")
```

### Workflow 4: Error Recovery Pipeline

```bash
#!/bin/bash

# Wrap command execution with Terminal Brain error handling

run_with_recovery() {
    local cmd="$1"
    
    # Try to run command
    if ! eval "$cmd"; then
        local error_msg="$?"
        
        # Get TB suggestions for error
        echo "Command failed. Getting suggestions..."
        
        # Terminal Brain would analyze the error
        echo "Suggestions for: $cmd"
        
        # User can choose from suggestions
        tb ask "fix: $cmd" --top 3
    fi
}

# Usage
run_with_recovery "find large files"
run_with_recovery "python script.py"
```

## Configuration Examples

### Example 1: Using OpenAI Backend

```toml
# ~/.config/terminalbrain/terminalbrain.toml

[ai]
backend = "openai"
model = "gpt-4"
openai_api_key = "sk-..."
temperature = 0.7
max_suggestions = 5
```

### Example 2: Minimal Resources

```toml
[ai]
backend = "local"  # No API calls, local models only
temperature = 0.5  # Faster, less creative

[ui]
show_dashboard = false
refresh_interval = 5000  # Update less frequently

[knowledge]
cache_embeddings = true  # Cache for fast reuse
```

### Example 3: Development Machine

```toml
[ai]
backend = "ollama"
model = "codellama"  # Better for code
temperature = 0.8

[ui]
show_dashboard = true
show_processes = true
refresh_interval = 1000

[security]
require_confirmation = true

[knowledge]
knowledge_source = "both"  # tldr + man pages
```

## Troubleshooting

### "command not found: tb"

```bash
# Make sure shell integration was sourced
source ~/.bashrc  # or ~/.zshrc

# Or manually source it
source /path/to/terminalbrain/shell/bash_integration.sh
```

### "LLM not available"

```bash
# Install and run Ollama
curl https://ollama.ai/install.sh | sh
ollama pull mistral

# Verify it's running
curl http://localhost:11434/api/tags
```

### "Permission denied" for script generation

```bash
# Make sure scripts are executable
chmod +x script.sh

# Or run with bash explicitly
bash script.sh
```

## Tips & Tricks

1. **Alias Creation**: Use `tb analyze` to find frequent commands and create aliases
2. **Prediction Practice**: Use `tb predict` after commands to see patterns Terminal Brain learns
3. **History Export**: Export history analysis with `tb analyze > analysis.json`
4. **Quick Help**: Type `tb --help` for command reference
5. **Configuration Backup**: Save your `~/.config/terminalbrain/` directory
6. **Shell Integration**: Add Terminal Brain to your dotfiles for consistency across machines

## Performance Optimization

```bash
# Reduce LLM suggestions latency
# Use faster model:
# mistral (4GB) - fast, general
# neural-chat (4GB) - fast, focused
# llama2 (7GB) - slower, more capable

# Cache knowledge base embeddings
# Edit config: cache_embeddings = true

# Disable features you don't need
# In config: show_battery = false, show_network_speed = false

# Use local models only (no API calls)
# Set backend = "ollama" (not "openai")
```

---

For more information, see [API.md](API.md) and [ARCHITECTURE.md](ARCHITECTURE.md)
