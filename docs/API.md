# API Documentation

## Core Module APIs

### CommandParser

```python
from terminalbrain.core import CommandParser

parser = CommandParser()

# Parse a command
parsed = parser.parse("find . -name '*.txt' | grep error")
print(parsed.command)           # 'find'
print(parsed.args)             # ['.', '*.txt']
print(parsed.flags)            # {'-name': None}
print(parsed.pipes)            # ['grep error']

# Extract subcommands
subcmds = parser.extract_subcommands("git add . && git commit -m 'test'")
# Returns: ['git', 'git']

# Check if dangerous
is_dangerous = parser.is_dangerous("rm -rf /", ["rm -rf", "mkfs"])
# Returns: True

# Get command info
info = parser.get_command_info("ls -la /tmp")
# Returns: {'command': 'ls', 'args_count': 2, 'flags_count': 1, ...}
```

### HistoryAnalyzer

```python
from terminalbrain.core import HistoryAnalyzer

analyzer = HistoryAnalyzer()

# Load command history
commands = analyzer.load_history()  # Loads from .bash_history or .zsh_history

# Get most common commands
top_10 = analyzer.get_most_common(10)
# Returns: [('git', 150), ('ls', 120), ...]

# Predict next command
predictions = analyzer.predict_next_command("git add", top_n=3)
# Returns: [('git commit', 0.85), ('git push', 0.10), ...]

# Find similar commands
similar = analyzer.get_similar_commands("find large files")
# Returns: [(command, similarity_score), ...]

# Get statistics
stats = analyzer.get_statistics()
# Returns: {'total_commands': 5000, 'unique_commands': 250, ...}

# Suggest aliases
aliases = analyzer.suggest_aliases(min_frequency=5)
# Returns: {'ga': 'git add', 'll': 'ls -la', ...}
```

### ContextAnalyzer

```python
from terminalbrain.core import ContextAnalyzer

# Get current terminal context
context = ContextAnalyzer.get_context()
print(context.cwd)              # Current directory
print(context.git_repo)         # Is git repository?
print(context.running_processes) # List of running processes
print(context.git_branch)       # Current git branch

# Analyze current directory
analysis = ContextAnalyzer.analyze_cwd()
# Returns: {'is_git_repo': True, 'is_python_project': True, ...}

# Check if tool is installed
if ContextAnalyzer.check_tool_installed("docker"):
    print("Docker is installed")

# Get installed tools
tools = ContextAnalyzer.get_installed_tools()
# Returns: ['git', 'docker', 'python3', 'npm', ...]
```

### RankingEngine

```python
from terminalbrain.core.ranking_engine import RankingEngine, Suggestion

engine = RankingEngine()

# Create suggestions from different sources
suggestions = [
    Suggestion(command="find . -name '*.txt'", confidence=0.9, 
               explanation="LLM suggestion", source="llm"),
    Suggestion(command="grep -r 'pattern' .", confidence=0.85,
               explanation="From history", source="history"),
]

# Rank suggestions
ranked = engine.rank_suggestions(suggestions)
# Sorted by composite score (confidence × source weight × complexity factor)

# Deduplicate
deduped = engine.deduplicate(suggestions)
# Removes duplicates, keeps highest scoring

# Get top N
top_5 = engine.get_top_suggestions(suggestions, n=5)
```

## AI Module APIs

### LLMEngine

```python
from terminalbrain.ai import LLMEngine
import asyncio

# Initialize with Ollama backend
engine = LLMEngine(backend_type="ollama", model="mistral")

# Or with OpenAI
engine = LLMEngine(backend_type="openai", model="gpt-3.5-turbo",
                   api_key="sk-...")

# Check if available
async def main():
    available = await engine.is_available()
    
    # Generate command from description
    cmd = await engine.generate_command("find large files")
    # Returns: "find / -type f -size +100M"
    
    # Explain a command
    explanation = await engine.explain_command("find . -name '*.txt'")
    # Returns: "Search current directory recursively for files ending in .txt"
    
    # Fix a broken command
    fix = await engine.fix_command("pytohn --version", "command not found")
    # Returns: "python3 --version"
    
    # Generate script
    script = await engine.generate_script("backup home folder daily")
    # Returns: shell script code

asyncio.run(main())
```

### RecommendationEngine

```python
from terminalbrain.ai import RecommendationEngine
import asyncio

engine = RecommendationEngine(llm_backend="ollama", model="mistral")

async def main():
    # Initialize
    await engine.initialize()
    
    # Get recommendations
    suggestions = await engine.recommend("find large files", top_n=5)
    for s in suggestions:
        print(f"{s.command}: {s.confidence:.0%} ({s.source})")
    
    # Predict next command
    predictions = await engine.predict_next("git add .", top_n=3)
    
    # Get explanation
    explain = await engine.explain_command("find . -name '*.py'")
    
    # Fix errors
    fixes = await engine.fix_command_error("find large files", 
                                            "command not found")
    
    # Generate script
    script = await engine.generate_script("deploy docker project")
    
    # Get alias suggestions
    aliases = engine.suggest_aliases()

asyncio.run(main())
```

### ErrorDebugger

```python
from terminalbrain.ai import ErrorDebugger

debugger = ErrorDebugger()

# Categorize error
error_type = debugger.categorize_error("command not found: gti")
# Returns: "command_not_found"

# Detect common mistakes
mistakes = debugger.detect_common_mistakes("pytohn script.py")
# Returns: [{'type': 'typo', 'detected': 'pytohn', 
#            'suggestion': 'python', 'message': "Did you mean 'python'?"}]

# Get alternative commands
alts = debugger.suggest_alternatives("pip install package")
# Returns: ["pip3", "python3 -m pip"]

# Get help commands
help_cmds = debugger.get_help_command("find")
# Returns: ["man find", "find --help", "find -h", ...]
```

## Monitoring APIs

### SystemMonitor

```python
from terminalbrain.monitor import SystemMonitor

# Get individual metrics
cpu = SystemMonitor.get_cpu_percent()           # 23.5
ram = SystemMonitor.get_ram_info()              # {'percent': 45.2, ...}
disk = SystemMonitor.get_disk_info("/")         # {'percent': 72.1, ...}
battery = SystemMonitor.get_battery_info()      # {'percent': 82, 'charging': True}
uptime = SystemMonitor.get_uptime()             # Seconds since boot

# Get all metrics at once
metrics = SystemMonitor.get_metrics()
# Returns SystemMetrics object with all data

# Get as dictionary
metrics_dict = SystemMonitor.get_metrics_dict()
# Returns: {'cpu': 23.5, 'ram': {...}, 'disk': {...}, ...}
```

### NetworkMonitor

```python
from terminalbrain.monitor import NetworkMonitor

# Check connectivity
online = NetworkMonitor.check_connectivity()    # True/False

# Get latency
latency = NetworkMonitor.get_latency()          # ~45.2 ms

# Measure speed (slower operation)
speed = NetworkMonitor.measure_speed()
# Returns: {'download_mbps': 150.5, 'upload_mbps': 45.2, ...}

# Get WiFi signal
signal = NetworkMonitor.get_wifi_signal_strength()  # 0-100
```

### ProcessMonitor

```python
from terminalbrain.monitor import ProcessMonitor

# Get top processes
top_procs = ProcessMonitor.get_top_processes(n=10, sort_by="cpu")
# Returns: List[ProcessInfo]

for proc in top_procs:
    print(f"{proc.name}: CPU {proc.cpu_percent}%, MEM {proc.memory_mb}MB")

# Get specific process
proc = ProcessMonitor.get_process_info(pid=1234)

# Find by name
firefox_procs = ProcessMonitor.find_process_by_name("firefox")

# Get process tree
tree = ProcessMonitor.get_process_tree(pid=1234)

# Kill process
ProcessMonitor.kill_process(pid=1234, force=False)
```

## Knowledge Base API

```python
from terminalbrain.knowledge import KnowledgeBase, RAGPipeline

# Create knowledge base
kb = KnowledgeBase()

# Get command info
info = kb.get_command_info("find")
# Returns: {'description': '...', 'syntax': '...', 'examples': [...], ...}

# Search knowledge base
results = kb.search_commands("search for files")
# Returns: [{'command': 'find', 'info': {...}}, ...]

# Get examples
examples = kb.get_examples("git")
# Returns: ["git add .", "git commit -m 'msg'", ...]

# Get similar commands
similar = kb.get_similar_commands("find")
# Returns: ["grep", "ls", ...] (by tags)

# RAG Pipeline
rag = RAGPipeline()
rag.index_knowledge_base()  # Build embeddings

# Retrieve relevant commands
relevant = rag.retrieve("find large files", top_k=5)
# Returns: ['find', 'ls', 'du', ...]

# Augment prompt with context
augmented_prompt = rag.augment_with_context(
    "find large files",
    relevant[:3]
)
```

## Configuration API

```python
from terminalbrain.config import load_config, save_config, Config

# Load config (creates defaults if needed)
config = load_config()

# Access settings
print(config.ai.backend)        # 'ollama'
print(config.ui.show_dashboard) # True
print(config.security.dangerous_commands)

# Modify and save
config.ai.model = "neural-chat"
save_config(config)

# Create custom config
custom_config = Config(
    ai=AIConfig(backend="openai", model="gpt-4"),
    ui=UIConfig(show_battery=False)
)
save_config(custom_config)
```

## CLI Examples

```bash
# Ask for command suggestions
tb ask "find large files"
tb ask "compress this folder" --top 3 --explain

# Predict next command
tb predict
tb predict "git add ."

# Show dashboard
tb dashboard

# Generate scripts
tb generate "backup home folder daily" --save --output backup.sh

# Manage configuration
tb config show
tb config edit
tb config reset

# Analyze history
tb analyze

# Browse knowledge base
tb knowledge

# Show version
tb version
```

## Example Workflows

### Workflow: Learn from History and Predict

```python
from terminalbrain.core import HistoryAnalyzer
from terminalbrain.ai import MLPredictor

# Load and analyze history
history = HistoryAnalyzer()
history.load_history()

# Train ML model
predictor = MLPredictor()
predictor.train(history.commands)

# Make predictions
predictions = predictor.predict("git add .", top_n=3)
for cmd, prob in predictions:
    print(f"{cmd}: {prob:.0%}")
```

### Workflow: Complete Recommendation Pipeline

```python
from terminalbrain.ai import RecommendationEngine
import asyncio

async def complete_workflow():
    # Create engine
    engine = RecommendationEngine(llm_backend="ollama")
    await engine.initialize()
    
    # Get recommendations
    query = "backup my home directory"
    suggestions = await engine.recommend(query, top_n=5)
    
    # Display results
    for i, s in enumerate(suggestions, 1):
        print(f"{i}. {s.command}")
        print(f"   Confidence: {s.confidence:.0%}")
        print(f"   Source: {s.source}")
        print(f"   {s.explanation}\n")
    
    # Generate a script
    script = await engine.generate_script(query)
    print("Generated script:")
    print(script)

asyncio.run(complete_workflow())
```

## Error Handling

All APIs follow consistent error handling:

```python
try:
    suggestions = await engine.recommend("find files")
except ConnectionError:
    print("Cannot connect to LLM backend")
except ValueError as e:
    print(f"Invalid input: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Async Operations

LLM-related operations are async:

```python
import asyncio

async def main():
    engine = RecommendationEngine()
    results = await engine.recommend("query")
    return results

# Run async code
results = asyncio.run(main())
```

## Rate Limiting & Caching

- ML predictions are cached per command
- LLM requests are rate-limited by backend
- Knowledge base queries are instant (in-memory)

## Thread Safety

- History analyzer is thread-safe
- System monitor is thread-safe
- LLM engine queues requests
