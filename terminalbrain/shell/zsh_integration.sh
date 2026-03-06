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
alias tbsearch='terminalbrain search'

# Real-time suggestion on every prompt
if [[ -z "$TERMINALBRAIN_PROMPT_DISABLED" ]]; then
    precmd_functions+=(terminalbrain_prompt)
    
    terminalbrain_prompt() {
        terminalbrain predict --quiet 2>/dev/null || true
    }
fi

# Setup keybindings for terminal integration
# Alt+S opens Terminal Brain search
bindkey -e
bindkey '\es' 'terminalbrain search'

# Zsh completion for terminalbrain
if command -v terminalbrain &>/dev/null; then
    eval "$(terminalbrain --show-completion zsh 2>/dev/null || true)"
fi

# Quick help
tb_help() {
    echo ""
    echo "╔════════════════════════════════════════════════════╗"
    echo "║     Terminal Brain - Integrated Terminal Mode     ║"
    echo "╚════════════════════════════════════════════════════╝"
    echo ""
    echo "Commands:"
    echo "  tb <query>        - Ask for command suggestion"
    echo "  ask <query>       - Alias for 'tb'"
    echo "  tbsearch          - Interactive search (like Google!)"
    echo "  tbdash            - Show system dashboard"
    echo "  tbpred            - Predict next command"
    echo "  tban              - Analyze your history"
    echo "  tbmod             - Manage modules"
    echo ""
    echo "Keyboard Shortcuts:"
    echo "  Alt+S             - Open Terminal Brain search"
    echo ""
    echo "Real-Time Features:"
    echo "  → Auto-predictions before each prompt"
    echo "  → Suggestions update as your work"
    echo ""
    echo "Examples:"
    echo "  tb find large files"
    echo "  ask backup my documents"
    echo "  tbsearch          # Try interactive search!"
    echo ""
}
