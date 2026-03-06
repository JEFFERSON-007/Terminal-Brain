# Lightweight Installation Guide

Terminal Brain v2.0+ uses a modular plugin system. The **base installation is lightweight** (~30 MB), and **advanced features are optional add-ons**.

## Installation Options

### Option 1: Minimal Base Install (Recommended for Quick Start)

```bash
pip install terminalbrain
```

Includes:
- ✅ CLI interface with `ask`, `predict`, `generate` commands
- ✅ Real-time system dashboard
- ✅ API-based AI (OpenAI, OpenRouter)
- ✅ Shell integration
- ✅ Configuration system
- ✅ System monitoring

Does **NOT** include:
- ❌ Local LLMs (Ollama, llama.cpp)
- ❌ ML models (scikit-learn, FAISS)
- ❌ Knowledge base indexing
- ❌ Voice commands

**Disk space**: ~30 MB  
**Memory**: ~50 MB idle  
**Setup time**: <1 minute

---

### Option 2: With LLM Support (Local AI)

```bash
pip install terminalbrain[llm]
```

Adds:
- Ollama support (auto-download models)
- llama.cpp support
- Local inference without API costs

**Additional disk**: 4-8 GB (model download)  
**Additional setup time**: 2-5 minutes

---

### Option 3: With ML Prediction

```bash
pip install terminalbrain[prediction]
```

Adds:
- ML-based command prediction
- scikit-learn models
- Faster predictions over time

**Additional disk**: ~200 MB  
**Additional memory**: ~200 MB

---

### Option 4: With Knowledge Base

```bash
pip install terminalbrain[knowledgebase]
```

Adds:
- Vector search knowledge base
- Semantic command search
- RAG (Retrieval Augmented Generation)

**Additional disk**: 500 MB - 2 GB  
**Additional setup time**: 5-10 minutes (indexing)

---

### Option 5: Full Installation (All Features)

```bash
pip install terminalbrain[all]
```

Includes everything.

---

## Module Management

Check what's installed:

```bash
terminal-brain modules
```

Output:
```
╭─ Terminal Brain Optional Modules ──────────╮
│ Module           Status              Desc. │
├──────────────────────────────────────────┤
│ llm              not_installed        Local LLM support │
│ prediction       not_installed        ML command pred.  │
│ knowledgebase    not_installed        Vector KB         │
│ voice            not_installed        Voice commands    │
│ workflows        not_installed        Workflow auto.    │
╰──────────────────────────────────────────╯
```

### Install Individual Module

```bash
terminal-brain install llm
terminal-brain install prediction
terminal-brain install knowledgebase
```

### Uninstall Module

```bash
terminal-brain uninstall llm
```

---

## Configuration

Default config at `~/.config/terminalbrain/terminalbrain.toml`:

```toml
[general]
theme = "dark"

[ai]
# Use API-based AI by default (fast, no setup)
backend = "openai"  # or "openrouter"
model = "gpt-3.5-turbo"
api_key = "sk-..."

[ui]
show_dashboard = true

# Optional: If you install LLM module
[advanced.llm]
# backend = "ollama"
# model = "mistral"
# api_base = "http://localhost:11434"

# Optional: If you install prediction module
[advanced.prediction]
# enabled = true
# model = "random_forest"

# Optional: If you install knowledge base module
[advanced.knowledgebase]
# enabled = true
# embedding_model = "all-MiniLM-L6-v2"
```

---

## Quick Start Examples

### Start with API AI (no setup)

```bash
# Install minimal
pip install terminalbrain

# Set API key
export OPENAI_API_KEY="sk-..."

# Use immediately
terminal-brain ask "find large files"
terminal-brain dashboard
```

### Add Local LLM Later

```bash
# Initially installed minimal, now add Ollama
terminal-brain install llm

# Download a model
ollama pull mistral

# Update config to use local LLM
# [advanced.llm]
# backend = "ollama"
# model = "mistral"

# Now uses local LLM instead of API
terminal-brain ask "find large files"
```

### Add ML Prediction

```bash
# Add prediction module
terminal-brain install prediction

# Updates config automatically
# Uses history to predict next commands
terminal-brain predict
```

---

## Bandwidth and Data Usage

### API-Based (default)

- Small requests to OpenAI/OpenRouter
- ~1-5 KB per query
- Typical monthly cost: $5-50 (depending on usage)

### Local LLM

- No bandwidth after model download
- Initial: 4-8 GB download (one-time)
- Ongoing: 0 KB (fully local)

### Knowledge Base

- Initial indexing: downloads docs (~500 MB)
- Ongoing: 0 KB (fully local)

---

## Dependency Details

### Minimal Installation

```
Python 3.10+
├── textual>=0.38.0      (terminal UI)
├── rich>=13.0.0         (colored output)
├── typer>=0.9.0         (CLI framework)
├── pydantic>=2.0.0      (data validation)
├── aiohttp>=3.9.0       (async HTTP)
├── aiofiles>=23.0.0     (async I/O)
├── toml>=0.10.0         (config parsing)
├── openai>=1.0.0        (API client)
├── psutil>=5.9.0        (system metrics)
└── requests>=2.31.0     (HTTP requests)
```

**Total**: 9 packages, ~50 MB

### + LLM Module

```
Additional:
├── ollama>=0.0.11       (local inference)
└── llama-cpp-python>=0.2.0
```

### + Prediction Module

```
Additional:
├── numpy>=1.24.0        (numerical computing)
└── scikit-learn>=1.3.0  (machine learning)
```

### + Knowledge Base Module

```
Additional:
├── faiss-cpu>=1.7.4     (vector search)
└── sentence-transformers>=2.2.0
```

### + Workflows Module

```
Additional:
└── pyyaml>=6.0          (YAML parsing)
```

---

## Storage Usage Summary

| Installation        | Disk  | Memory | Setup Time |
|-------------------|-------|--------|-----------|
| Minimal           | 30 MB | 50 MB  | <1 min    |
| + LLM             | 8 GB  | 500 MB | 5 min     |
| + Prediction      | 200 MB| 200 MB | 1 min     |
| + Knowledge Base  | 2 GB  | 500 MB | 10 min    |
| All Features      | 11 GB | 1.2 GB | 20 min    |

---

## Migration Path

**Recommended approach:**

1. **Start**: Install minimal
   ```bash
   pip install terminalbrain
   ```

2. **Try API AI**: Use with OpenAI/OpenRouter
   ```bash
   terminal-brain ask "..."
   ```

3. **Later, add local LLM** if you want privacy/cost savings
   ```bash
   terminal-brain install llm
   ```

4. **Eventually add prediction** for smarter suggestions
   ```bash
   terminal-brain install prediction
   ```

This way you start fast and add features only when needed.

