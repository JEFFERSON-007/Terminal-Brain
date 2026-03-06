# Terminal Brain - Quick Start Guide

Welcome to **Terminal Brain**, your AI-powered terminal assistant!

## What is Terminal Brain?

Terminal Brain is an intelligent terminal assistant that:
- 🤖 Recommends Linux commands using AI/ML
- 🔮 Predicts your next command
- 🐛 Detects and fixes command errors
- 📊 Monitors system resources in real-time
- 🎯 Learns from your command history
- 🔒 Prevents dangerous commands

## Installation (2 minutes)

### Step 1: Install Terminal Brain
```bash
cd "Terminal Brain"
bash scripts/install.sh
```

The script will:
- ✅ Check Python 3.10+
- ✅ Create virtual environment
- ✅ Install dependencies
- ✅ Setup shell integration
- ✅ Create configuration

### Step 2: Reload Your Shell
```bash
source ~/.bashrc
# Or for Zsh:
source ~/.zshrc
```

### Step 3: Verify Installation
```bash
tb version
# Output: Terminal Brain v0.1.0
```

## Basic Usage

### Ask for Command Suggestions
```bash
# Get recommendations for your task
tb ask "find large files"

# Output shows:
# 1. find / -type f -size +100M (92% | llm)
# 2. find . -type f -size +100M (85% | history)
# 3. du -sh /* (78% | history)
```

### Predict Next Command
```bash
# After "git add .", what comes next?
tb predict "git add ."

# Output:
# 1. git commit (85%)
# 2. git push (10%)
# 3. git status (5%)
```

### View System Dashboard
```bash
# See real-time system metrics
tb dashboard

# Shows: CPU, RAM, Disk, Battery, Top Processes
# Updates every 2 seconds
```

### Analyze Your Command History
```bash
# Learn from your past commands
tb analyze

# Shows: Total commands, unique commands, most used
# Suggests useful aliases
```

### Generate Shell Scripts
```bash
# Generate a backup script
tb generate "backup home folder daily"

# Shows the generated script
# Option to save to file: --save --output backup.sh
```

## Handy Aliases

Terminal Brain creates these aliases automatically:
```bash
ask "find files"          # Same as: tb ask "find files"
tb "compress folder"      # Quick suggestion
tbdash                    # Show dashboard
```

## Features by Task

### Finding Files
```bash
ask "find python files"
ask "find large files"
ask "find recently modified files"
```

### Version Control
```bash
ask "add and commit changes"
ask "create a git branch"
ask "revert last commit"
```

### Docker & Containers
```bash
ask "list running containers"
ask "build docker image"
ask "deploy docker container"
```

### File Operations
```bash
ask "compress this folder"
ask "extract tar file"
ask "backup files"
```

### System Administration
```bash
ask "check disk space"
ask "monitor processes"
ask "check system performance"
```

## With Local AI (Recommended)

For the best experience, install Ollama for local AI:

```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh

# Download a model (choose one)
ollama pull mistral        # Fast, general purpose (4GB)
ollama pull neural-chat    # Code-focused (4GB)
ollama pull codellama      # Programming specialist (7GB)

# Verify it's running
ollama list

# Terminal Brain automatically detects it!
tb ask "find large files"
# Much faster with local model!
```

## Configuration

Edit your configuration:
```bash
# View current config
tb config show

# Edit in text editor
tb config edit

# Reset to defaults
tb config reset
```

Configuration file: `~/.config/terminalbrain/terminalbrain.toml`

### Key Settings:
```toml
[ai]
backend = "ollama"     # or "openai", "local"
model = "mistral"      # Model to use
temperature = 0.7      # Creativity level (0-1)

[ui]
show_dashboard = true  # Show system metrics
show_battery = true    # Show battery status
refresh_interval = 2000 # Update every 2 seconds

[security]
require_confirmation = true  # Confirm risky commands
```

## Common Workflows

### Workflow 1: Find and Compress Large Files
```bash
ask "find large files"
# Copy the suggested command and run it
# Then:
ask "compress these files"
```

### Workflow 2: Git Workflow
```bash
git add .
# Terminal Brain predicts:
tb predict "git add ."
# → suggests: git commit

git commit -m "changes"
# → suggests: git push
```

### Workflow 3: Backup
```bash
ask "backup home folder"
# Get suggestions
tb generate "daily backup script" --save --output backup.sh
chmod +x backup.sh
./backup.sh
```

## Troubleshooting

### "tb: command not found"
```bash
# Shell integration not loaded
source ~/.bashrc
# Or restart terminal
```

### "LLM not available" / Slow responses
```bash
# Install Ollama for local AI
curl https://ollama.ai/install.sh | sh
ollama pull mistral
# Restart Terminal Brain
```

### Want to use OpenAI instead?
```bash
# Edit config
tb config edit

# Change to:
[ai]
backend = "openai"
model = "gpt-4"
openai_api_key = "sk-..."
```

## Tips & Tricks

### 1. Learn Your Patterns
```bash
# Analyze what commands you use most
tb analyze
# Creates aliases for frequent commands
alias ga="git add"
alias ll="ls -la"
```

### 2. Keyboard Shortcuts
```bash
# In your shell, use Tab completion with Terminal Brain suggestions
ask "find "<TAB>
# Shows suggestions as you type
```

### 3. Pipe with Terminal Brain
```bash
# Use suggestions in pipes
CMD=$(tb ask "find large files" --top 1 | grep "^[0-9]" | cut -d' ' -f2-)
eval "$CMD"
```

### 4. Check Your History
```bash
# See what Terminal Brain learned
tb analyze
# Shows: top commands, suggested aliases, patterns
```

## API Usage (Python)

For developers integrating Terminal Brain:

```python
from terminalbrain.ai import RecommendationEngine
import asyncio

async def main():
    engine = RecommendationEngine()
    await engine.initialize()
    
    # Get suggestions
    suggestions = await engine.recommend("find large files")
    for s in suggestions:
        print(f"{s.command}: {s.confidence:.0%}")

asyncio.run(main())
```

## Getting Help

```bash
# Show all Terminal Brain commands
tb --help

# Get help on specific command
tb ask --help
tb predict --help
tb generate --help
```

## Documentation

- **Quick Start**: This file
- **Complete Guide**: [README.md](README.md)
- **API Reference**: [docs/API.md](docs/API.md)
- **Examples**: [docs/EXAMPLES.md](docs/EXAMPLES.md)
- **Architecture**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

## System Requirements

- Python 3.10+
- Linux-based OS (Ubuntu, Debian, Fedora, etc.)
- ~100MB disk space
- ~150MB RAM (with dashboard active)

## Performance

- **Startup**: <200ms
- **Suggestion Latency**: 50ms (ML) to 500ms (LLM)
- **Memory**: 50-120MB depending on features
- **CPU**: <5% idle

## What's Next?

1. ✅ Install Terminal Brain
2. ✅ Try: `tb ask "list files"`
3. ✅ View: `tb dashboard`
4. ✅ Analyze: `tb analyze`
5. ✅ Configure: `tb config edit`
6. ✅ Learn more: Read [README.md](README.md)

## Questions or Issues?

- Check [TROUBLESHOOTING](#troubleshooting) above
- Read [docs/EXAMPLES.md](docs/EXAMPLES.md)
- Review [docs/API.md](docs/API.md)
- See [CONTRIBUTING.md](CONTRIBUTING.md)

---

**Terminal Brain: Your AI brain inside the terminal.**

*Making Linux commands intelligent and accessible to everyone.*

Happy commanding! 🚀
