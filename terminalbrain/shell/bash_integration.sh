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

# Real-time suggestion on every prompt
# Shows predicted next command before you type
if [[ -z "$TERMINALBRAIN_PROMPT_DISABLED" ]]; then
    PROMPT_COMMAND="terminalbrain predict --quiet 2>/dev/null; $PROMPT_COMMAND"
fi

# Function for quick help
tb_help() {
    echo "Terminal Brain shortcuts:"
    echo "  tb <query>        - Ask for command suggestion"
    echo "  ask <query>       - Alias for 'tb'"
    echo "  tbdash            - Show system dashboard"
    echo "  tbpred            - Predict next command"
    echo "  tban              - Analyze command history"
    echo "  tbmod             - List/manage modules"
    echo ""
    echo "Examples:"
    echo "  tb find large files"
    echo "  tb backup home directory"
    echo "  tb show disk usage"
}
