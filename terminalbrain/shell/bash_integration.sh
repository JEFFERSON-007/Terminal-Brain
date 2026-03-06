#!/bin/bash
# Bash integration for Terminal Brain
# Add real-time suggestions and shortcuts
# Source this in ~/.bashrc or ~/.bash_profile

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
# Shows predicted next command before you type
if [[ -z "$TERMINALBRAIN_PROMPT_DISABLED" ]]; then
    PROMPT_COMMAND="terminalbrain predict --quiet 2>/dev/null; $PROMPT_COMMAND"
fi

# Setup keybindings for terminal integration
if [[ -n "$BASH_VERSION" ]]; then
    # Alt+S opens Terminal Brain search
    bind '"\es": "terminalbrain search\n"' 2>/dev/null
    
    # Ctrl+T shows terminal brain help
    bind '"\C-t": "tb_help\n"' 2>/dev/null
fi

# Function for quick help
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
    echo "  Ctrl+T            - Show this help"
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
