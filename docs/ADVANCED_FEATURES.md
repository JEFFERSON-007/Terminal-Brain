# Advanced Features Guide for Terminal Brain

## Table of Contents
1. [Error Analysis Engine](#error-analysis-engine)
2. [Command Prediction Engine](#command-prediction-engine)
3. [Workflow Detection](#workflow-detection)
4. [Command Explanation Engine](#command-explanation-engine)
5. [Script Generation](#script-generation)
6. [Alias Suggestions](#alias-suggestions)
7. [Workflow Recommendations](#workflow-recommendations)
8. [Learning Feedback Loop](#learning-feedback-loop)
9. [Safety Checker](#safety-checker)
10. [Configuration](#configuration)

---

## Error Analysis Engine

### Overview
The Error Analysis Engine automatically detects terminal errors and suggests fixes based on error patterns and knowledge base.

### Features
- **Automatic Error Detection**: Captures and analyzes stderr output
- **Pattern Matching**: 13+ built-in error patterns with fixes
- **Smart Fix Suggestions**: Contextual solutions based on error type
- **Learning**: Improves suggestions based on user feedback

### Error Categories Detected
- `missing_command`: Command not installed or not in PATH
- `missing_pip`: pip package manager not installed
- `permission_denied`: Insufficient file/directory permissions
- `not_git_repo`: Not in a git repository
- `auth_failed`: Git authentication failures (401)
- `missing_module`: Python module/package not found
- `file_not_found`: File or directory doesn't exist
- `connection_refused`: Cannot connect to service
- `path_error`: Path/directory validation errors
- `illegal_instruction`: CPU instruction not supported
- `port_in_use`: Network port already in use
- `disk_quota`: Storage quota exceeded

### Usage

#### Python API
```python
from terminalbrain.advanced import ErrorAnalyzer

analyzer = ErrorAnalyzer()

# Analyze error from command execution
result = analyzer.analyze(
    command="pip install numpy",
    stderr="bash: pip: command not found",
    exit_code=127
)

print(f"Error: {result.message}")
print(f"Category: {result.category}")
print(f"Fixes:")
for fix in result.fixes:
    print(f"  - {fix}")

# Learn from user-confirmed fix
analyzer.learn_from_fix("missing_pip", "python3 -m ensurepip")

# Get statistics
stats = analyzer.get_error_statistics()
print(f"Most common error: {max(stats, key=stats.get)}")
```

#### CLI
```bash
# Error analysis will run automatically when commands fail
# Terminal Brain captures stderr and suggests fixes

$ tb ask "install numpy"
# If error occurs, automatic suggestions appear
```

---

## Command Prediction Engine

### Overview
Uses n-gram and Markov chain models to predict your next command before you type it.

### Features
- **Bigram Prediction**: Predicts next command from last 1 command
- **Trigram Prediction**: Uses last 2 commands for better prediction
- **Workflow Detection**: Identifies and predicts complete workflows
- **Confidence Scoring**: Ranks predictions by likelihood
- **Pattern Learning**: Learns from your command history

### Prediction Models

#### Bigram Model
```
git add . → git commit (80% confidence)
git add . → git status (15% confidence)
```

#### Trigram Model
```
git add . + git commit → git push (85% confidence)
```

### Usage

#### Python API
```python
from terminalbrain.advanced import CommandPredictor

predictor = CommandPredictor()

# Train on command history
history = [
    "git add .",
    "git commit -m 'fix'",
    "git push",
    "git add .",
    "git commit -m 'fix'",
    "git push"
]
predictor.train(history)

# Predict next command
result = predictor.predict_next(["git add ."], top_k=5)

for cmd, confidence in result.predictions:
    print(f"{cmd}: {confidence:.0%}")

# Output:
# git: 85%
# git commit: 12%
# git status: 3%

# Predict entire workflow
workflow = predictor.predict_workflow(["git add"])
print(f"Predicted workflow: {' → '.join(workflow)}")

# Get workflow patterns
patterns = predictor.get_workflow_patterns(min_frequency=3)
for pattern in patterns:
    print(f"{' → '.join(pattern.commands)}: {pattern.frequency} times")
```

#### CLI
```bash
# Prediction via CLI
$ tb predict

Analyzing recent commands...
Next likely command: git commit -m

Confidence: 85%
Based on: Last command was 'git add .'

# Or with context
$ tb predict "git add"

Suggested next commands:
1. git commit -m "..." (85%)
2. git status (10%)
3. git diff (5%)
```

---

## Workflow Detection

### Overview
Automatically detects frequently repeated command sequences and suggests converting them into reusable workflows.

### Features
- **Automatic Pattern Detection**: Finds sequences appearing 3+ times
- **Workflow Naming**: Suggests descriptive names
- **YAML Storage**: Saves workflows as YAML configuration files
- **Tag-based Organization**: Categorizes workflows by tool/purpose

### Built-in Workflows
```yaml
# git_sync.yaml
- git add .
- git commit -m "update"
- git push origin main

# docker_deploy.yaml
- git pull origin main
- docker build -t app:latest .
- docker compose up -d

# python_test_deploy.yaml
- python -m pytest tests/
- pip install -r requirements.txt
- python setup.py sdist

# backup_home.yaml
- mkdir -p ~/backups
- tar -czf ~/backups/backup_$(date).tar.gz ~/
```

### Usage

#### Python API
```python
from terminalbrain.advanced import WorkflowDetector
from pathlib import Path

detector = WorkflowDetector(min_frequency=3)

# Analyze history
history = [
    "git add .", "git commit -m 'fix'", "git push",
    "git add .", "git commit -m 'fix'", "git push",
    "git add .", "git commit -m 'fix'", "git push"
]

patterns = detector.analyze_history(history)

for name, pattern in patterns.items():
    print(f"Workflow: {name}")
    print(f"  Commands: {' → '.join(pattern.commands)}")
    print(f"  Frequency: {pattern.frequency} times")
    print()

# Save workflows
detector.save_all_workflows(Path("~/.terminalbrain/workflows"))

# Get statistics
stats = detector.get_workflow_stats()
print(f"Total workflows: {stats['total_workflows']}")
print(f"Most frequent: {stats['most_frequent']}")
```

#### CLI
```bash
# Detect workflows from history
$ tb analyze

Detected workflow patterns:
1. git_sync (15 occurrences)
   git add . → git commit → git push

2. docker_deploy (8 occurrences)
   git pull → docker build → docker compose up

3. python_test_deploy (5 occurrences)
   python -m pytest → pip install → python setup

# Save detected workflows
$ tb analyze --save-workflows

Workflows saved to ~/.terminalbrain/workflows/

# Execute workflow
$ tb workflow git_sync

Executing git_sync workflow...
[1/3] git add .
[2/3] git commit -m "update"
[3/3] git push origin main

✓ Workflow completed!
```

---

## Command Explanation Engine

### Overview
Explains Linux commands and their flags in human-readable format.

### Features
- **Man Page Integration**: Pulls from system man pages
- **Flag Explanations**: Breaks down each command flag
- **Common Commands**: Built-in explanations for 20+ common tools
- **Examples**: Real-world usage examples

### Supported Commands
- File operations: `ls`, `find`, `grep`, `tar`, `cp`, `mv`, `rm`
- Version control: `git` (20+ subcommands)
- Package managers: `apt`, `pip`, `npm`
- Containers: `docker`
- Development: `gcc`, `make`, `python`

### Usage

#### Python API
```python
from terminalbrain.advanced import CommandExplainer

explainer = CommandExplainer()

# Explain a command
explanation = explainer.explain("tar")

print(f"Command: {explanation.command}")
print(f"Description: {explanation.description}")
print(f"Syntax: {explanation.syntax}")

# Explain flags
for flag in explanation.flags[:5]:
    print(f"  {flag.flag} ({flag.short_form}): {flag.description}")

# Explain specific command
parts = explainer.explain_command_parts("tar -czvf archive.tar.gz folder/")
for part, explanation in parts.items():
    print(f"{part}: {explanation}")

# Output:
# tar: archive utility
# -c: create archive
# -z: compress using gzip
# -v: verbose output
# -f: output file name
# archive.tar.gz: output filename
# folder/: input directory
```

#### CLI
```bash
# Explain a command
$ tb explain "tar -czvf backup.tar.gz folder"

Command: tar
Description: archive files

Flags:
  -c: create archive
  -z: compress using gzip
  -v: verbose output
  -f: output file name

Syntax: tar [OPTIONS] [FILES]

Examples:
  tar -czf archive.tar.gz folder
  tar -xzf archive.tar.gz
  tar -tf archive.tar.gz

# Or directly from shell
$ explain tar
$ explain "grep -r pattern file"
```

---

## Script Generation

### Overview
Generates shell scripts from natural language descriptions with safety checks.

### Features
- **Template-based Generation**: Backup, deploy, cleanup, install scripts
- **Safety Checks**: Detects dangerous patterns in generated scripts
- **Comments & Headers**: Well-documented generated code
- **Language Support**: Bash, Zsh (extensible)

### Script Templates

#### Backup Template
```bash
#!/bin/bash
set -e

BACKUP_DIR="$HOME/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="backup_$TIMESTAMP.tar.gz"

mkdir -p "$BACKUP_DIR"
tar -czf "$BACKUP_DIR/$BACKUP_NAME" /home/user

echo "Backup completed: $BACKUP_DIR/$BACKUP_NAME"
```

#### Deploy Template
```bash
#!/bin/bash
set -e

git pull origin main
docker build -t app:latest .
docker compose up -d

echo "Deployment completed!"
```

### Usage

#### Python API
```python
from terminalbrain.advanced import ScriptGenerator

generator = ScriptGenerator()

# Generate backup script
script = generator.generate("backup home folder daily")

print(f"Generated: {script.name}")
print(f"Safety Level: {script.safety_level}")
print(script.content)

# Save script
with open(f"~/scripts/{script.name}", "w") as f:
    f.write(script.content)

# Generate deployment script
deploy_script = generator.generate("deploy docker project")
print(f"Requires: {', '.join(deploy_script.requires)}")
```

#### CLI
```bash
# Generate script from description
$ tb generate "backup my home folder"

Generated script: backup_backup.sh

#!/bin/bash
# Backup script - backup my home folder
set -e

BACKUP_DIR="$HOME/backups"
...

Options:
  [r] Run script
  [s] Save script to ~/scripts/
  [e] Edit script
  [c] Cancel

# Or generate deploy script
$ tb generate "deploy docker project"

⚠️ Safety Level: MEDIUM

This script will:
- Pull from git repository
- Build Docker image
- Start containers

Continue? (y/n)
```

---

## Alias Suggestions

### Overview
Analyzes your command usage and suggests useful aliases to save typing time.

### Features
- **Usage Analysis**: Finds frequently typed long commands
- **Character Savings**: Calculates time saved per alias
- **Bash & Zsh Support**: Generates compatible alias scripts
- **Function Generation**: For complex command aliases

### Suggested Aliases
- `ls -la` → `ll` (saves 5 chars)
- `git add .` → `ga` (saves 6 chars)
- `git commit` → `gc` (saves 7 chars)
- `git push` → `gp` (saves 7 chars)
- `docker ps` → `dps` (saves 6 chars)

### Usage

#### Python API
```python
from terminalbrain.advanced import AliasSuggester

suggester = AliasSuggester()

# Analyze command history
history = [
    "ls -la", "ls -la", "ls -la",
    "git add .", "git add .",
    "git commit -m 'msg'",
    "docker ps", "docker ps"
]

suggestions = suggester.analyze_history(history)

for suggestion in suggestions[:5]:
    print(f"{suggestion.command:20} → {suggestion.alias:8} "
          f"(saves {suggestion.time_saved_per_use} chars, used {suggestion.frequency}x)")

# Generate bash alias script
bash_script = suggester.get_alias_script(suggestions)
print(bash_script)

# Output:
# alias ll='ls -la'  # saves 5 chars
# alias ga='git add .'  # saves 6 chars
```

#### CLI
```bash
# Get alias suggestions
$ tb alias-suggest

Suggested aliases (by usage):
1. ll='ls -la'  (saves 5 chars, used 47 times)
2. ga='git add .'  (saves 6 chars, used 23 times)
3. gc='git commit -m'  (saves 13 chars, used 18 times)
4. gp='git push'  (saves 7 chars, used 15 times)
5. dps='docker ps'  (saves 6 chars, used 12 times)

Save to ~/.aliases.sh? (y/n)

# Use an alias
$ ll
# Expands to: ls -la
```

---

## Workflow Recommendations

### Overview
Recommends intelligent command pipelines for common tasks.

### Available Workflows

#### Find Large Files
```bash
# Quick overview
du -ah | sort -rh | head -20

# Detailed search
find . -type f -size +100M -exec ls -lh {} \;
```

#### Monitor System
```bash
# Real-time top processes
watch -n 1 'ps aux | head -20'

# Single snapshot
top -b -n 1 | head -30
```

#### Search in Files
```bash
# Python files with line numbers
grep -r 'pattern' . --include='*.py' -n

# Find text files containing pattern
find . -name '*.txt' -exec grep -l 'pattern' {} \;
```

#### Compress Files
```bash
# Gzip tar
tar -czf archive.tar.gz folder/

# ZIP format
zip -r archive.zip folder/
```

#### Batch Rename Files
```bash
# Rename extensions
for f in *.old; do mv "$f" "${f%.old}.new"; done

# Using rename tool
rename 's/old/new/' *.txt
```

### Usage

#### Python API
```python
from terminalbrain.advanced import WorkflowRecommender

recommender = WorkflowRecommender()

# Get recommendation
result = recommender.recommend("find large files")

print(f"Task: {result.task}")
print(f"Pipeline: {result.pipeline}")
print(f"Explanation: {result.explanation}")
print(f"Tools needed: {', '.join(result.tools_required)}")

# Get alternatives
for alt in result.alternative_pipelines:
    print(f"Alternative: {alt}")

# Add custom pipeline
recommender.add_custom_pipeline(
    "my_backup",
    "tar -czf backup_$(date +%s).tar.gz ~/data",
    "Custom backup workflow"
)
```

#### CLI
```bash
# Get workflow recommendation
$ tb workflow "find large files"

Recommended pipeline:
$ du -ah | sort -rh | head -20

Explanation: Show top 20 largest files/directories

Alternative approaches:
$ find . -type f -size +100M -exec ls -lh {} \;

Tools required: du, sort, head

Estimated time: quick

# Run the pipeline
$ du -ah | sort -rh | head -20

# Or use recommender for other tasks
$ tb workflow "monitor system"
$ tb workflow "backup database"
$ tb workflow "convert images"
```

---

## Learning Feedback Loop

### Overview
Terminal Brain learns from your feedback to improve suggestions over time.

### Feedback Types
- **ACCEPTED**: You accepted the suggestion
- **REJECTED**: You rejected the suggestion
- **MODIFIED**: You accepted but modified the suggestion
- **HELPFUL**: You marked as helpful
- **NOT_HELPFUL**: You marked as unhelpful

### Features
- **Score Adjustment**: Suggestions improve/worsen based on feedback
- **Pattern Learning**: Learns which command types you prefer
- **Statistics**: Tracks acceptance rate and improvement
- **Model Insights**: Provides recommendations for improvement

### Usage

#### Python API
```python
from terminalbrain.advanced import LearningFeedback, FeedbackType

feedback = LearningFeedback()

# Record feedback
entry = feedback.record_feedback(
    suggestion="git add .",
    feedback_type=FeedbackType.ACCEPTED,
    context={"command_type": "git", "error_type": None},
    confidence_before=0.75
)

# Record rejection
feedback.record_feedback(
    "rm -rf /",
    FeedbackType.REJECTED,
    context={"safety_level": "critical"}
)

# Record modification
feedback.record_feedback(
    "git commit",
    FeedbackType.MODIFIED,
    user_modification="git commit -m 'fix: issue'",
)

# Get statistics
stats = feedback.get_statistics()
print(f"Acceptance rate: {stats['acceptance_rate']:.0%}")
print(f"Total feedback: {stats['total_feedback']}")

# Get best and worst suggestions
best = feedback.get_best_suggestions(top_k=5)
worst = feedback.get_worst_suggestions(top_k=5)

# Export insights
insights = feedback.export_insights()
print(f"Best suggestions: {insights['best_suggestions']}")

# Save feedback history
feedback.save_history(Path("~/.terminalbrain/feedback.json"))
```

#### CLI
```bash
# View learning statistics
$ tb feedback stats

Feedback Statistics:
  Total feedback entries: 247
  Acceptance rate: 78%
  Rejection rate: 12%
  Modification rate: 10%
  
  Most accepted pattern: git
  Most rejected pattern: rm operations

# View best/worst suggestions
$ tb feedback insights

Top performing suggestions:
  1. git add . (confidence: 0.92)
  2. git commit -m (confidence: 0.89)
  3. git push (confidence: 0.87)

Worst performing suggestions:
  1. old_command (confidence: 0.15)
  2. rarely_used_flag (confidence: 0.22)

# Get improvement recommendations
$ tb feedback recommendations

Model improvement suggestions:
  - Rejection rate above 30% - consider retraining
  - Many suggestions are modified - improve completeness
```

---

## Safety Checker

### Overview
Detects and confirms dangerous terminal operations before execution.

### Risk Levels

#### CRITICAL ⚠️
- `rm -rf /` - Recursive deletion of root
- `dd if=` - Direct disk writing
- `mkfs.` - Filesystem formatting
- `:/: (fork bomb)` - System crash

#### HIGH ⚠️
- `rm -rf [paths]` - Recursive deletion
- `sudo chown -R` - Recursive permission change
- `chmod 777` - Overly permissive permissions
- `DROP DATABASE` - Database deletion
- `rm /tmp/` - System directory deletion

#### MEDIUM ⚠️
- `apt remove` - System package removal
- `kill -9` - Force kill process
- Hardcoded passwords

#### LOW ⚠️
- `git push +` - Force push
- `mv * /` - Move to system directories

### Usage

#### Python API
```python
from terminalbrain.advanced import SafetyChecker

checker = SafetyChecker()

# Check command
risk = checker.check("rm -rf /important")

print(f"Risk Level: {risk.risk_level}")
print(f"Description: {risk.description}")
print(f"Requires Confirmation: {risk.confirmation_required}")

if risk.suggested_alternative:
    print(f"Alternative: {risk.suggested_alternative}")

# Get safety score (0=dangerous, 1=safe)
score = checker.get_safety_score("ls -la")
print(f"Safety Score: {score:.0%}")  # 100%

# Get confirmation message
if risk.confirmation_required:
    message = checker.get_confirmation_message(risk)
    print(message)
```

#### CLI
```bash
# Command is checked automatically
$ tb ask "delete all files"

⚠️ CRITICAL RISK DETECTED

Suggested command: rm -rf *.txt

This command will affect:
  - All .txt files in current directory
  - Multiple files

Suggested alternative: Use 'find' for more selective deletion

Type 'YES I UNDERSTAND THE RISKS' to execute, or Ctrl+C to cancel:

# Safe commands proceed normally
$ tb ask "list files"

ls -la

[Execute safely]
```

---

## Configuration

### Advanced Features Settings

Update `~/.config/terminalbrain/terminalbrain.toml`:

```toml
[advanced]
# Error Analysis
error_analysis_enabled = true
auto_fix_suggestions = true

# Command Prediction
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

# Learning Feedback
learning_enabled = true
feedback_history_file = "~/.terminalbrain/feedback.json"

# Safety
safety_level = "high"  # "low", "medium", "high"
require_command_confirmation = true
dangerous_command_patterns = [
    "rm -rf /",
    "dd if=",
    "mkfs",
    ":/:",
    "chmod 777"
]
```

### Disabling Features

```toml
# Disable error analysis
[advanced]
error_analysis_enabled = false

# Disable safety checks
safety_level = "low"
require_command_confirmation = false

# Disable learning
learning_enabled = false
```

---

## Integration Examples

### Example 1: Automated Workflow Detection and Execution

```python
from terminalbrain.advanced import WorkflowDetector
from pathlib import Path

# Load history
history = load_command_history()

# Detect workflows
detector = WorkflowDetector()
workflows = detector.analyze_history(history)

# Save detected workflows
detector.save_all_workflows(Path("~/.terminalbrain/workflows"))

# Execute frequently used workflow
workflow = detector.get_workflow("git_sync")
for cmd in workflow.commands:
    execute_command(cmd)
```

### Example 2: Smart Error Recovery

```python
from terminalbrain.advanced import ErrorAnalyzer

analyzer = ErrorAnalyzer()

try:
    result = execute_command(user_command)
except CommandError as e:
    # Analyze error
    analysis = analyzer.analyze(user_command, e.stderr, e.exit_code)
    
    # Suggest fixes
    print(f"Error: {analysis.message}")
    for fix in analysis.fixes[:3]:
        print(f"  - {fix}")
    
    # Learn from what works
    if user_accepts_fix(fix):
        analyzer.learn_from_fix(analysis.category, fix)
```

### Example 3: Intelligent Script Generation with Safety

```python
from terminalbrain.advanced import ScriptGenerator, SafetyChecker

generator = ScriptGenerator()
checker = SafetyChecker()

# Generate script from description
script = generator.generate("backup important files")

# Check safety
risk = checker.check(script.content)

# Get confirmation if needed
if risk.risk_level.value >= "high":
    message = checker.get_confirmation_message(risk)
    if get_user_confirmation(message):
        execute_script(script)
else:
    execute_script(script)
```

### Example 4: Continuous Learning System

```python
from terminalbrain.advanced import (
    LearningFeedback,
    RecommendationEngine,
    FeedbackType
)

feedback_system = LearningFeedback()
recommender = RecommendationEngine()

# Get recommendation
suggestion = recommender.recommend(user_query)

# User accepts/modifies/rejects
if user_accepts(suggestion):
    feedback_system.record_feedback(
        suggestion.command,
        FeedbackType.ACCEPTED,
        confidence_before=suggestion.confidence
    )
elif user_modifies(suggestion):
    feedback_system.record_feedback(
        suggestion.command,
        FeedbackType.MODIFIED,
        user_modification=user_command,
        confidence_before=suggestion.confidence
    )

# Get model improvement recommendations
improvements = feedback_system.recommend_model_improvements()
if improvements:
    print("Model can be improved:")
    for rec in improvements:
        print(f"  - {rec}")
```

---

## Performance Considerations

### Prediction Performance
- **Bigram lookup**: <5ms
- **Trigram lookup**: <10ms
- **Workflow detection**: <100ms (per 1000 commands)

### Error Analysis Performance
- **Pattern matching**: <1ms
- **Fix suggestion**: <5ms

### Script Generation Performance
- **Template-based generation**: <10ms
- **Safety analysis**: <20ms

### Recommendations
- Cache frequently used predictions
- Batch error analysis for multiple commands
- Periodically reload learning feedback system
- Archive old feedback histories (> 10,000 entries)

---

## Best Practices

1. **Enable Learning**: Keep feedback system enabled for continuous improvement
2. **Use Safety Checks**: Never disable safety checks for critical commands
3. **Save Workflows**: Regularly save detected workflows for reuse
4. **Monitor Stats**: Check feedback statistics monthly for improvement areas
5. **Update Patterns**: Periodically retrain models on recent command history
6. **Backup Configuration**: Keep copies of workflow configurations
7. **Review Suggestions**: Always review generated scripts before execution

---

## Troubleshooting

### Predictions are inaccurate
- **Cause**: Model needs more training data
- **Solution**: Continue using Terminal Brain for more accurate history analysis

### Safety warnings on safe commands
- **Cause**: Pattern matches false positives
- **Solution**: Adjust dangerous_command_patterns in config

### Workflows not detected
- **Cause**: Minimum frequency threshold too high
- **Solution**: Lower workflow_min_frequency in config

### Performance issues
- **Cause**: Large command history or feedback file
- **Solution**: Archive old histories, limit feedback history size

---

## API Reference

### ErrorAnalyzer
```python
class ErrorAnalyzer:
    analyze(command: str, stderr: str, exit_code: int) -> ErrorSuggestion
    learn_from_fix(error_category: str, successful_fix: str) -> None
    get_error_statistics() -> Dict[str, int]
    save_patterns(filepath: Path) -> None
    load_patterns(filepath: Path) -> None
```

### CommandPredictor
```python
class CommandPredictor:
    train(command_history: List[str]) -> None
    predict_next(recent_commands: List[str], top_k: int = 5) -> PredictionResult
    predict_workflow(workflow_start: List[str]) -> List[str]
    get_workflow_patterns(min_frequency: int = 3) -> List[CommandSequence]
    save_model(filepath: Path) -> None
    load_model(filepath: Path) -> None
```

### WorkflowDetector
```python
class WorkflowDetector:
    analyze_history(command_history: List[str]) -> Dict[str, WorkflowPattern]
    get_workflow(name: str) -> Optional[WorkflowPattern]
    list_workflows() -> List[WorkflowPattern]
    save_workflow(name: str, filepath: Path) -> None
    save_all_workflows(workflows_dir: Path) -> None
    load_workflow(filepath: Path) -> Optional[WorkflowPattern]
    execute_workflow(name: str) -> List[str]
```

### SafetyChecker
```python
class SafetyChecker:
    check(command: str) -> SafetyRisk
    get_safety_score(command: str) -> float
    get_confirmation_message(risk: SafetyRisk) -> str
    should_require_confirmation(risk: SafetyRisk) -> bool
```

### LearningFeedback
```python
class LearningFeedback:
    record_feedback(
        suggestion: str,
        feedback_type: FeedbackType,
        user_modification: Optional[str] = None,
        context: Optional[Dict[str, str]] = None,
        confidence_before: float = 0.5
    ) -> FeedbackEntry
    get_suggestion_score(suggestion: str) -> float
    get_statistics() -> Dict[str, any]
    get_best_suggestions(top_k: int = 10) -> List[tuple]
    export_insights() -> Dict[str, any]
    save_history(filepath: Path) -> None
    load_history(filepath: Path) -> None
```

---

## Contributing Advanced Features

To extend Terminal Brain with custom advanced features:

```python
# Create custom error patterns
from terminalbrain.advanced import ErrorAnalyzer, ErrorPattern

analyzer = ErrorAnalyzer()
custom_pattern = ErrorPattern(
    pattern=r"my custom error",
    category="custom_category",
    description="My custom error description",
    fixes=["Fix 1", "Fix 2"],
    confidence=0.85
)
analyzer.error_patterns.append(custom_pattern)

# Create custom workflows
from terminalbrain.advanced import WorkflowDetector

detector = WorkflowDetector()
detector.patterns["my_workflow"] = detector.WorkflowPattern(
    name="my_workflow",
    commands=["cmd1", "cmd2", "cmd3"],
    frequency=10,
    last_used=datetime.now().isoformat()
)
```

---

**Last Updated**: March 6, 2026
**Version**: 2.0.0
**License**: MIT
