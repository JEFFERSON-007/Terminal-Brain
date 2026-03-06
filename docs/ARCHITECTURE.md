# System Architecture

## Overview

Terminal Brain is an AI-powered terminal assistant composed of modular, specialized components that work together to provide intelligent command recommendations, predictions, and system monitoring.

```
┌─────────────────────────────────────────────────────────────────┐
│                    Terminal Brain Architecture                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Shell Integration Layer (Bash, Zsh, Fish)              │   │
│  │  - Command hooks                                         │   │
│  │  - History integration                                   │   │
│  │  - Function aliases                                      │   │
│  └──────────────────────────────────────────────────────────┘   │
│                            ↓                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  CLI Interface (Typer)                                   │   │
│  │  - ask, predict, generate, dashboard, config            │   │
│  └──────────────────────────────────────────────────────────┘   │
│                            ↓                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Core Processing Layer                                   │   │
│  │  ├─ Command Parser (parse & analyze commands)            │   │
│  │  ├─ History Analyzer (learn from history)                │   │
│  │  ├─ Context Analyzer (understand environment)            │   │
│  │  └─ Ranking Engine (prioritize suggestions)              │   │
│  └──────────────────────────────────────────────────────────┘   │
│                            ↓                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  AI & ML Layer                                           │   │
│  │  ├─ LLM Engine (Ollama, OpenAI, etc.)                   │   │
│  │  ├─ ML Predictor (scikit-learn models)                  │   │
│  │  ├─ Recommendation Engine (combines sources)             │   │
│  │  └─ Error Debugger (error detection & fixes)            │   │
│  └──────────────────────────────────────────────────────────┘   │
│                            ↓                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Data Sources                                            │   │
│  │  ├─ Knowledge Base (commands, examples, docs)            │   │
│  │  ├─ Command History (bash/zsh history)                   │   │
│  │  ├─ System Metrics (CPU, RAM, Disk, Battery)             │   │
│  │  └─ RAG Pipeline (semantic search)                       │   │
│  └──────────────────────────────────────────────────────────┘   │
│                            ↓                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Terminal UI (Textual)                                   │   │
│  │  - Dashboard with live metrics                           │   │
│  │  - Interactive suggestions                               │   │
│  │  - Real-time updates                                     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Shell Integration Layer

**Location:** `terminalbrain/shell/`

- **bash_integration.sh**: Bash-specific hooks and functions
- **zsh_integration.sh**: Zsh-specific hooks and functions

**Responsibilities:**
- Capture user commands
- Provide shell aliases (`ask`, `tb`, `tbdash`)
- Enable quick access to Terminal Brain functions
- Maintain shell compatibility

### 2. CLI Interface

**Location:** `terminalbrain/cli.py`

**Commands:**
- `ask <query>` - Get command suggestions
- `predict` - Predict next command
- `dashboard` - Show system metrics
- `generate <description>` - Generate shell scripts
- `config <action>` - Manage configuration
- `analyze` - Analyze command history
- `knowledge` - Browse knowledge base
- `version` - Show version info

**Technology:** Typer framework for clean CLI

### 3. Core Processing

**Location:** `terminalbrain/core/`

#### CommandParser
- Parses shell command syntax
- Extracts commands, args, flags, pipes, redirects
- Calculates command complexity
- Detects dangerous commands

#### HistoryAnalyzer
- Loads bash/zsh history files
- Analyzes command patterns
- Finds most common commands
- Detects command sequences
- Suggests aliases

#### ContextAnalyzer
- Current working directory
- Files and directories in cwd
- Git repository status
- Running processes
- Environment variables
- Installed tools

#### RankingEngine
- Scores suggestions
- Deduplicates results
- Filters by confidence
- Combines multiple sources

### 4. AI & ML Layer

**Location:** `terminalbrain/ai/`

#### LLMEngine
- **OllamaBackend**: Local models via Ollama
- **OpenAIBackend**: API-based models
- **LocalMLBackend**: Custom local models

Features:
- Generate commands from natural language
- Explain what commands do
- Debug command errors
- Generate shell scripts

#### MLPredictor
- RandomForest classifier
- Learns from command history
- Predicts next commands
- Feature extraction from commands

#### RecommendationEngine
- Combines LLM + ML + History sources
- Ranks by confidence and source weight
- Deduplicates suggestions
- Caches predictions

#### ErrorDebugger
- Categorizes error types
- Detects common mistakes
- Suggests fixes
- Provides help commands

### 5. Knowledge Base & RAG

**Location:** `terminalbrain/knowledge/`

#### KnowledgeBase
- 100+ built-in command documentation
- Examples for each command
- Command tags and categories
- Similar command suggestions

#### RAGPipeline
- Semantic search using embeddings
- Sentence transformers for context
- FAISS for similarity search
- Augments LLM prompts with context

### 6. System Monitoring

**Location:** `terminalbrain/monitor/`

#### SystemMonitor
- CPU usage percentage
- RAM usage and available memory
- Disk usage and free space
- Battery percentage and charging status
- System uptime

#### NetworkMonitor
- Internet connectivity check
- Latency measurement (ping)
- Speed testing via speedtest-cli
- WiFi signal strength

#### ProcessMonitor
- Top processes by CPU/memory
- Find processes by name
- Process tree
- Kill processes
- Thread information

### 7. Terminal UI

**Technology:** Textual (Rich for rendering)

**Features:**
- Real-time metric updates
- Live system dashboard
- Interactive suggestion display
- Customizable widgets
- Color themes

## Data Flow

### Command Recommendation Flow

```
User Query
    ↓
Parse & Validate
    ↓
├─→ LLM Engine → AI suggestions
├─→ ML Predictor → ML suggestions  
└─→ History Analyzer → History-based
    ↓
Ranking Engine
    ↓
Deduplicate & Filter
    ↓
Sort by Score
    ↓
Display to User
```

### Learning Flow

```
Shell History File
    ↓
HistoryAnalyzer
    ├─→ Frequency analysis
    ├─→ Sequence learning
    └─→ Pattern extraction
    ↓
MLPredictor
    ├─→ Feature extraction
    ├─→ Model training
    └─→ Prediction capability
```

## Technology Stack

| Component | Technology |
|-----------|-----------|
| **Language** | Python 3.10+ |
| **CLI** | Typer |
| **Terminal UI** | Textual, Rich |
| **AI/ML** | scikit-learn, PyTorch |
| **LLM** | Ollama, OpenAI |
| **Embeddings** | sentence-transformers |
| **Vector DB** | FAISS |
| **System** | psutil, subprocess |
| **Config** | TOML, Pydantic |
| **Async** | asyncio |

## Performance Targets

| Metric | Target | Status |
|--------|--------|--------|
| Startup time | < 200ms | ✓ |
| LLM suggestion latency | < 300ms | ✓ |
| ML prediction latency | < 50ms | ✓ |
| Memory footprint | < 150MB | ✓ |
| CPU usage (idle) | < 5% | ✓ |

## Security Measures

1. **Dangerous Command Detection**
   - Pattern matching for risky commands
   - Requires explicit confirmation
   - Whitelist/blacklist support

2. **API Key Management**
   - Stored in config file (~/.config/terminalbrain/)
   - Not logged or cached
   - Support for multiple backends

3. **History Privacy**
   - Local processing only
   - No telemetry by default
   - Optional opt-in analytics

## Scalability & Extensibility

### Plugin Architecture
- Custom AI backends
- Custom command sources
- Custom UI widgets
- Custom suggestion sources

### Configuration
- TOML-based configuration
- Per-user settings
- Environment variable overrides
- Hot-reloadable

## Configuration

See `config/terminalbrain.toml` for complete configuration options.

Key settings:
- AI backend selection (ollama, openai, local)
- Model selection
- UI preferences
- Security settings
- Knowledge base source
- Suggestion behavior

## Testing & Quality

- Unit tests for all modules
- Integration tests
- Type checking with mypy
- Linting with ruff
- Code formatting with black

## Future Enhancements

- Voice command support
- Cross-device sync
- Plugin marketplace
- Advanced visualization
- Terminal multiplexer integration
- IDE plugin support
