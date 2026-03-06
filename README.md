# Terminal Brain

**Your AI brain inside the terminal.**

Terminal Brain transforms the Linux terminal into an AI-powered intelligent workspace capable of recommending commands, predicting next actions, generating shell scripts, debugging errors, learning from user behavior, and monitoring system performance.

## Core Capabilities

### 🤖 Natural Language → Command Generation
```bash
ask "find large files"
# Suggests: find / -type f -size +100M

ask "compress this folder"
# Suggests: tar -czvf archive.tar.gz folder/

ask "show processes using most cpu"
# Suggests: top, htop
```

### 🔮 Command Prediction Engine
Predicts the next command based on:
- Command sequences
- Usage frequency
- Machine learning models
- Context awareness

### 📝 Smart Command Autocomplete
As you type, get intelligent suggestions:
```bash
docker
# Suggests: docker ps, docker build, docker compose up
```

### 🐛 Command Error Debugging
```bash
gti status
# Suggests: git status

pip install package  # fails
# Suggests: python3 -m pip install package
```

### 🔧 AI Bash Script Generator
```bash
ask "backup home folder every day"
# Generates and explains a shell script
```

### 🎯 Real-Time Terminal Dashboard
Monitor system metrics in real-time:
- CPU & RAM usage
- Disk space
- Battery percentage
- Network speed
- Active processes

### 💾 Command History Learning
Learns from your bash/zsh history to:
- Suggest frequent commands
- Recognize patterns
- Create aliases
- Automate workflows

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│         Terminal Brain System Architecture          │
├─────────────────────────────────────────────────────┤
│  Shell Integration Layer (Bash, Zsh, Fish)         │
├─────────────────────────────────────────────────────┤
│  Command Parser & Context Analyzer                 │
├─────────────────────────────────────────────────────┤
│  History Analyzer & ML Models                       │
├─────────────────────────────────────────────────────┤
│  AI Recommendation Engine                           │
│  ├─ LLM Inference (Ollama, OpenAI, etc.)          │
│  ├─ ML Prediction Model (scikit-learn)            │
│  ├─ Rule Engine                                    │
│  └─ Semantic Search (FAISS + embeddings)          │
├─────────────────────────────────────────────────────┤
│  Knowledge Base & RAG Pipeline                      │
├─────────────────────────────────────────────────────┤
│  System Monitor (CPU, RAM, Disk, Battery)          │
├─────────────────────────────────────────────────────┤
│  Terminal UI Engine (Textual)                      │
└─────────────────────────────────────────────────────┘
```

## Project Structure

```
Terminal Brain/
├── terminalbrain/
│   ├── __init__.py
│   ├── cli.py                    # CLI entry point
│   ├── config.py                 # Configuration management
│   ├── core/
│   │   ├── command_parser.py     # Parse and analyze commands
│   │   ├── history_analyzer.py   # Learn from command history
│   │   ├── ranking_engine.py     # Rank suggestions
│   │   └── context_analyzer.py   # Context awareness
│   ├── ai/
│   │   ├── llm_engine.py         # LLM integration
│   │   ├── ml_predictor.py       # ML-based prediction
│   │   ├── recommendation_engine.py
│   │   └── error_debugger.py     # Error detection & fixes
│   ├── ui/
│   │   ├── dashboard.py          # Terminal dashboard
│   │   ├── widgets.py            # UI components
│   │   └── theme.py              # Color themes
│   ├── shell/
│   │   ├── bash_integration.sh   # Bash hooks
│   │   ├── zsh_integration.sh    # Zsh hooks
│   │   └── shell_utils.py        # Shell utilities
│   ├── knowledge/
│   │   ├── knowledge_base.py     # Knowledge storage
│   │   ├── rag_pipeline.py       # RAG implementation
│   │   └── command_db.py         # Command database
│   ├── monitor/
│   │   ├── system_monitor.py     # CPU, RAM, Disk, Battery
│   │   ├── network_monitor.py    # Network speed
│   │   └── process_monitor.py    # Process tracking
│   └── security/
│       └── command_validator.py  # Dangerous command detection
├── tests/
│   ├── test_*.py                 # Unit tests
├── config/
│   └── terminalbrain.toml        # Configuration file
├── scripts/
│   ├── install.sh                # Installation script
│   └── setup_hooks.sh            # Shell hook setup
├── docs/
│   ├── ARCHITECTURE.md           # Detailed architecture
│   ├── API.md                    # API documentation
│   └── EXAMPLES.md               # Usage examples
└── pyproject.toml                # Python project config
```

## Installation

```bash
# Clone repository
git clone <repository>
cd "Terminal Brain"

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e .

# Setup shell integration
bash scripts/setup_hooks.sh

# Install local LLM (optional)
ollama pull mistral  # or: llama2, neural-chat, etc.
```

### Install from Debian Package (.deb)

```bash
# Build package
./scripts/build_deb.sh

# Install locally with apt
sudo apt install ./dist/deb/terminal-brain.deb
```

### Install from APT Repository

```bash
echo "deb [trusted=yes] https://your-repo-url/apt stable main" | sudo tee /etc/apt/sources.list.d/terminalbrain.list
sudo apt update
sudo apt install terminal-brain
```

Full packaging/repository instructions are in [docs/packaging/APT_DISTRIBUTION.md](docs/packaging/APT_DISTRIBUTION.md).

## Quick Start

### Ask for Command Suggestions
```bash
tb ask "find large files"
# Output: Suggestions with confidence scores and explanations
```

### View Terminal Dashboard
```bash
tb dashboard
# Displays: CPU, RAM, Disk, Battery, Network, Processes
```

### Generate Shell Script
```bash
tb generate "backup home folder daily"
# Generates, explains, and optionally saves script
```

### View Predictions
```bash
tb predict
# Shows predicted next commands based on history
```

### Configure Terminal Brain
```bash
tb config edit
# Opens terminalbrain.toml in your editor
```

## Configuration (terminalbrain.toml)

```toml
[general]
theme = "dark"
startup_message = true
suggestion_frequency = 3  # suggestions per query

[ai]
backend = "ollama"  # "ollama", "openai", "local"
model = "mistral"
temperature = 0.7
max_suggestions = 5

[ui]
show_dashboard = true
show_battery = true
show_network_speed = true
show_processes = true
refresh_interval = 2000  # milliseconds

[security]
dangerous_commands = ["rm -rf", "mkfs", "dd", ":|"]
require_confirmation = true

[knowledge]
enable_rag = true
knowledge_source = "tldr"  # "tldr", "man", "both"
```

## AI Backend Support

### Local Models (Offline)
- **Ollama**: Run models like Mistral, Llama 2, Neural Chat
- **llama.cpp**: Fast inference on CPU
- **Code Llama**: Code-specific model

### API-based Models
- **OpenAI**: GPT-4, GPT-3.5-turbo
- **Anthropic**: Claude
- **OpenRouter**: Access to multiple models

### Machine Learning Models
- **scikit-learn**: Command prediction with RandomForest
- **Sentence Transformers**: Semantic command search
- **FAISS**: Fast similarity search

## Performance Targets

- **Startup time**: < 200ms
- **Suggestion latency**: < 300ms
- **Memory footprint**: < 150MB (idle)
- **CPU usage**: < 5% (idle)

## Security Features

### Dangerous Command Detection
Prevents accidental execution of:
- `rm -rf` - Recursive deletion
- `mkfs` - Filesystem formatting
- `dd` - Disk operations
- And more...

### Confirmation Required
Dangerous commands require explicit user confirmation before execution.

## Advanced Features

- 🔄 **Workflow Automation**: Convert command sequences into reusable workflows
- 📊 **Usage Analytics**: Track command patterns and create insights
- 🔌 **Plugin Architecture**: Extend with custom commands and AI models
- 🌐 **Cross-Device Sync**: Share command preferences across machines
- 🎙️ **Voice Commands**: Control terminal with natural speech
- 📈 **Command Visualization**: Graph command patterns over time

## API Examples

```python
from terminalbrain.ai import RecommendationEngine
from terminalbrain.core import CommandParser

# Create recommendation engine
engine = RecommendationEngine(model="mistral")

# Get command suggestions
suggestions = await engine.suggest("find large files")
print(f"Top suggestion: {suggestions[0]['command']}")
print(f"Confidence: {suggestions[0]['confidence']}")
print(f"Explanation: {suggestions[0]['explanation']}")

# Parse command context
parser = CommandParser()
context = parser.parse("find . -name '*.txt'")
print(f"Command: {context.command}")
print(f"Arguments: {context.args}")
print(f"Flags: {context.flags}")
```

## Technology Stack

| Component | Technology |
|-----------|-----------|
| **Language** | Python 3.10+ |
| **Terminal UI** | Textual, Rich |
| **ML/AI** | scikit-learn, PyTorch, sentence-transformers |
| **Local LLM** | Ollama, llama.cpp |
| **API LLMs** | OpenAI, Anthropic, OpenRouter |
| **Vector DB** | FAISS |
| **CLI Framework** | Typer |
| **Async** | asyncio |
| **Testing** | pytest |

## Development

```bash
# Run tests
pytest tests/

# Code formatting
black terminalbrain/

# Type checking
mypy terminalbrain/

# Linting
ruff check terminalbrain/
```

## Roadmap

- [ ] v0.2: Advanced ML prediction
- [ ] v0.3: Voice command support
- [ ] v0.4: Cross-device sync
- [ ] v0.5: Plugin marketplace
- [ ] v1.0: Production release

## Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT License - see LICENSE file

## Support

- 📖 Documentation: `/docs`
- 🐛 Issues: GitHub Issues
- 💬 Discussions: GitHub Discussions

---

**Terminal Brain**: Making the terminal intelligent, one command at a time.
