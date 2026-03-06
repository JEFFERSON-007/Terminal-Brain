"""
ZSH integration script for Terminal Brain
Provides hooks and integration with zsh
"""

# This script should be sourced in ~/.zshrc

export TERMINALBRAIN_ENABLED=1

# Terminal Brain functions
tb_suggest() {
    local query="$*"
    python3 -m terminalbrain.cli ask "$query"
}

tb_predict() {
    python3 -m terminalbrain.cli predict
}

tb_dashboard() {
    python3 -m terminalbrain.cli dashboard
}

tb_generate() {
    local description="$*"
    python3 -m terminalbrain.cli generate "$description"
}

# ZSH completion
_tb_completion() {
    local cur=${words[CURRENT]}
    local options="ask predict dashboard generate config analyze knowledge version"
    
    if [[ $CURRENT -eq 2 ]]; then
        compadd $(echo "$options" | tr ' ' '\n')
    fi
}

compdef _tb_completion tb

# Aliases
alias ask='tb_suggest'
alias tb='tb_suggest'
alias tbdash='tb_dashboard'
