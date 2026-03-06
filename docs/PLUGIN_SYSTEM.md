# Plugin System Architecture

Terminal Brain uses a modular plugin system to keep the base installation lightweight while supporting advanced features.

## Plugin Directory Structure

```
~/.terminalbrain/
├── plugins/
│   ├── .registry.json          # Plugin registry metadata
│   ├── llm/
│   │   ├── metadata.json       # Plugin metadata
│   │   ├── config.json         # Runtime configuration
│   │   └── data/               # Plugin-specific data
│   ├── prediction/
│   │   ├── metadata.json
│   │   ├── config.json
│   │   └── models/
│   ├── knowledgebase/
│   │   ├── metadata.json
│   │   ├── config.json
│   │   └── vectors/            # FAISS indexes
│   ├── voice/
│   │   ├── metadata.json
│   │   └── config.json
│   └── workflows/
│       ├── metadata.json
│       ├── config.json
│       └── definitions/
```

## Available Modules

### LLM Module (`terminal-brain install llm`)

**Dependencies**: `ollama`, `llama-cpp-python`

Provides local LLM inference using:
- Ollama (easy setup, auto-downloads models)
- llama.cpp (lightweight, pure CPU)

**Configuration**:
```toml
[advanced.llm]
backend = "ollama"           # or "llamacpp"
model = "mistral"            # Ollama model name
api_base = "http://localhost:11434"  # Ollama endpoint
model_path = "/path/to/gguf"  # For llama.cpp
```

**Usage in code**:
```python
from terminalbrain.plugins.llm import OllamaBackend

backend = OllamaBackend(model="mistral")
response = await backend.infer("Find large files")
```

---

### Prediction Module (`terminal-brain install prediction`)

**Dependencies**: `numpy`, `scikit-learn`

ML-based command prediction using RandomForest and Gradient Boosting.

**Configuration**:
```toml
[advanced.prediction]
model = "random_forest"      # or "gradient_boosting"
min_frequency = 2            # Min command occurrences
```

**Usage in code**:
```python
from terminalbrain.plugins.prediction import MLPredictor

predictor = MLPredictor()
predictor.train(command_history)
next_commands = predictor.predict(history)
```

---

### Knowledge Base Module (`terminal-brain install knowledgebase`)

**Dependencies**: `faiss-cpu`, `sentence-transformers`

Local vector search knowledge base with semantic search.

**Configuration**:
```toml
[advanced.knowledgebase]
embedding_model = "all-MiniLM-L6-v2"
similarity_threshold = 0.7
max_results = 5
```

**Usage in code**:
```python
from terminalbrain.plugins.knowledgebase import KnowledgeBase

kb = KnowledgeBase()
kb.build_index(documents)
results = kb.search("find large files", top_k=5)
```

---

### Voice Module (`terminal-brain install voice`)

**Dependencies**: None (uses system audio APIs)

Speech-to-text voice command input.

**Usage**:
```bash
terminal-brain voice listen   # Record voice command
```

---

### Workflows Module (`terminal-brain install workflows`)

**Dependencies**: `pyyaml`

Advanced workflow detection and automation.

**Configuration**:
```toml
[advanced.workflows]
min_frequency = 3             # Min sequence occurrences
auto_detect = true            # Auto-detect patterns
```

**Usage in code**:
```python
from terminalbrain.plugins.workflows import WorkflowEngine

engine = WorkflowEngine()
workflows = engine.detect_workflow(commands)
engine.save_workflow("backup", commands, path)
```

---

## Plugin Manager API

### Installation

```python
from terminalbrain.plugins import PluginManager

manager = PluginManager()

# Install a module
manager.install_module("llm")

# List all plugins
status = manager.list_plugins()

# Check plugin status
status = manager.get_plugin_status("llm")

# Load a plugin
llm = manager.load_plugin("llm")
```

### CLI Commands

```bash
# List available modules
terminal-brain modules

# Install a module
terminal-brain install llm
terminal-brain install prediction

# Uninstall a module
terminal-brain uninstall llm

# Check installation status
terminal-brain modules
```

---

## Plugin Metadata Format

Each plugin has a `metadata.json`:

```json
{
  "name": "llm",
  "version": "1.0.0",
  "description": "Local LLM support via Ollama and llama.cpp",
  "author": "Terminal Brain Team",
  "dependencies": [],
  "optional_dependencies": [
    "ollama>=0.0.11",
    "llama-cpp-python>=0.2.0"
  ],
  "entry_point": "terminalbrain.plugins.llm:init",
  "config_schema": {
    "backend": {
      "type": "string",
      "enum": ["ollama", "llamacpp"]
    },
    "model": {
      "type": "string"
    }
  }
}
```

---

## Plugin Security Model

### Sandboxing

Plugins are loaded dynamically but execute in the same process. 

**Security measures**:
1. Plugins stored in user home directory (`~/.terminalbrain/plugins/`)
2. Registry file `.registry.json` tracks installed plugins
3. Configuration files limit plugin behavior
4. Plugins can only access their own data directory

### Trust Model

- Only install plugins from trusted sources
- Each plugin's dependencies are explicitly declared
- Plugin permissions are limited to configuration options

---

## Creating Custom Plugins

To create a custom plugin:

1. Create plugin directory:
```bash
mkdir -p ~/.terminalbrain/plugins/myplugin
```

2. Create `metadata.json`:
```json
{
  "name": "myplugin",
  "version": "1.0.0",
  "description": "My custom plugin",
  "author": "Your Name",
  "dependencies": [],
  "optional_dependencies": [],
  "entry_point": "my_plugin:init"
}
```

3. Create `config.json`:
```json
{
  "enabled": true,
  "option1": "value1"
}
```

4. Install your module:
```python
from terminalbrain.plugins import PluginManager

manager = PluginManager()
manager.install_module("myplugin")
```

---

## Performance Notes

**Base Installation (no plugins)**:
- ~10 MB disk space
- ~50 MB memory idle
- Startup time: <500ms

**With LLM module** (Ollama):
- Requires 4-8 GB for model download
- First inference: 2-5 seconds
- Subsequent: <1 second

**With Prediction module**:
- ~200 MB additional memory
- Model training: 1-10 seconds depending on history size
- Prediction: <50ms

**With Knowledge Base module**:
- Depends on documentation size
- Typical: 500 MB - 2 GB
- Search: <100ms

---

## Module Dependency Resolution

When installing a module, the plugin manager:

1. Reads `metadata.json`
2. Extracts `optional_dependencies` list
3. Runs `pip install <dependencies>`
4. Stores plugin metadata in registry
5. Creates plugin configuration file

Failed dependency installs will fail the module installation gracefully.

