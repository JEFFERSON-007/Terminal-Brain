"""
Bash integration script for Terminal Brain
Provides hooks and integration with bash
"""

# This script should be sourced in ~/.bashrc

# Terminal Brain functions
export TERMINALBRAIN_ENABLED=1

# Function to get terminal brain suggestions
tb_suggest() {
    local query="$*"
    python3 -m terminalbrain.cli ask "$query"
}

# Function to predict next command
tb_predict() {
    python3 -m terminalbrain.cli predict
}

# Function to show dashboard
tb_dashboard() {
    python3 -m terminalbrain.cli dashboard
}

# Function to generate scripts
tb_generate() {
    local description="$*"
    python3 -m terminalbrain.cli generate "$description"
}

# Alias shortcuts
alias ask='tb_suggest'
alias tb='tb_suggest'
alias tbdash='tb_dashboard'
