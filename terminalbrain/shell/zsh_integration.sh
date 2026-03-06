#!/bin/zsh
# Zsh integration for Terminal Brain
# Add real-time suggestions and shortcuts
# Source this in ~/.zshrc

export TERMINALBRAIN_ENABLED=1

# Shorter commands
alias tb='terminalbrain'
alias ask='terminalbrain ask'
alias tbdash='terminalbrain dashboard'
alias tbpred='terminalbrain predict'
alias tban='terminalbrain analyze'
alias tbmod='terminalbrain modules'

# Real-time suggestion on every prompt
if [[ -z "$TERMINALBRAIN_PROMPT_DISABLED" ]]; then
    precmd_functions+=(terminalbrain_prompt)
    
    terminalbrain_prompt() {
        terminalbrain predict --quiet 2>/dev/null || true
    }
fi

# Zsh completion for terminalbrain
if command -v terminalbrain &>/dev/null; then
    eval "$(terminalbrain --show-completion zsh 2>/dev/null || true)"
fi

# Quick help
tb_help() {
    echo "Terminal Brain shortcuts:"
    echo "  tb <query>        - Ask for command suggestion"
    echo "  ask <query>       - Alias for 'tb'"
    echo "  tbdash            - Show system dashboard"
    echo "  tbpred            - Predict next command"
    echo "  tban              - Analyze command history"
    echo "  tbmod             - List modules"
    echo ""
    echo "Examples:"
    echo "  tb find large files"
    echo "  tb backup home directory"
}
