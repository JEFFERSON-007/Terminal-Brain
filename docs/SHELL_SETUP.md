# Terminal Brain Shell Setup Guide

## Overview

Terminal Brain now integrates seamlessly with your shell to provide:
- **Short aliases** for quick access (`tb`, `ask`, `tbdash`)
- **Real-time suggestions** that appear automatically before each prompt
- **Shell completion** for all Terminal Brain commands

## For Bash

### 1. Add integration to ~/.bashrc

```bash
echo 'source ~/.terminalbrain/shell/bash_integration.sh' >> ~/.bashrc
```

### 2. Reload your shell

```bash
source ~/.bashrc
```

### 3. Start using it!

From now on, you'll see predictions appear automatically before each prompt:

```bash
$ ls
$ cd Documents
[Suggestion: next file operation might be...]
$ 
```

## For Zsh

### 1. Add integration to ~/.zshrc

```bash
echo 'source ~/.terminalbrain/shell/zsh_integration.sh' >> ~/.zshrc
```

### 2. Reload your shell

```bash
source ~/.zshrc
```

### 3. Start using it!

Same real-time suggestions as Bash.

## Available Aliases

Once shell integration is enabled:

| Alias | Command | Purpose |
|-------|---------|---------|
| `tb` | `terminalbrain` | Generic Terminal Brain command |
| `ask` | `terminalbrain ask` | Ask for command suggestion |
| `tbdash` | `terminalbrain dashboard` | Show system dashboard |
| `tbpred` | `terminalbrain predict` | Predict next command |
| `tban` | `terminalbrain analyze` | Analyze command history |
| `tbmod` | `terminalbrain modules` | List installed modules |

## Examples

### Simple usage
```bash
$ tb find large files
# Provides command suggestions for finding large files

$ ask backup home directory
# Suggests commands for backing up your home directory

$ tbpred
# Predicts your next command based on history
```

### Install optional modules
```bash
$ terminalbrain install llm
$ terminalbrain install knowledgebase
$ tbmod
# List all installed modules
```

## Real-Time Suggestions

Terminal Brain automatically runs predictions on every prompt. The predictions appear before the next prompt without blocking your shell.

### How it works:

**Bash**: Uses `PROMPT_COMMAND` to run `terminalbrain predict --quiet`  
**Zsh**: Uses `precmd_functions` to run `terminalbrain predict --quiet`

The `--quiet` flag means suggestions are shown but won't interfere with your work.

## Disabling Real-Time Suggestions

If you want to disable automatic suggestions temporarily:

```bash
export TERMINALBRAIN_PROMPT_DISABLED=1
```

Re-enable by:
```bash
unset TERMINALBRAIN_PROMPT_DISABLED
```

## Troubleshooting

### Aliases not working

Make sure you've sourced the integration file:
```bash
source ~/.bashrc  # For Bash
source ~/.zshrc   # For Zsh
```

### No suggestions appearing

1. Ensure Terminal Brain is installed: `which terminalbrain`
2. Test manually: `terminalbrain predict --quiet`
3. Check if predictions are disabled: `echo $TERMINALBRAIN_PROMPT_DISABLED`

### Shell completion not working

Terminal Brain uses Typer's built-in completion. Ensure you've sourced the shell integration file, then try:

```bash
# Bash
eval "$(terminalbrain --show-completion bash)"

# Zsh
eval "$(terminalbrain --show-completion zsh)"
```

## Performance Notes

- Predictions run with `--quiet` flag (minimal overhead)
- Runs asynchronously in background (doesn't block prompt)
- Completes within milliseconds for typical hardware
- If too slow, disable with: `export TERMINALBRAIN_PROMPT_DISABLED=1`

## Advanced

### Custom shell functions

You can define additional shortcuts in your shell config:

```bash
# Find commands similar to previous
tb_similar() {
    terminalbrain analyze --similar "$@"
}

# Quick help
tb help() {
    terminalbrain --help | less
}
```

### Customize prompt format

To show predictions in a different format, customize your shell's `PROMPT_COMMAND` (Bash) or `precmd_functions` (Zsh).

## Quick Reference

After setup, use:
```bash
tb_help  # Display all available shortcuts
```

## Next Steps

1. ✅ Source the shell integration file in your shell config
2. ✅ Reload your shell
3. ✅ Try using `tb` instead of `terminalbrain`
4. ✅ Watch for automatic predictions on each prompt
5. (Optional) Install additional modules: `terminalbrain install llm`
