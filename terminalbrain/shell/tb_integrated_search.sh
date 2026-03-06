#!/bin/bash
# Terminal Brain - Integrated Terminal Search
# Auto-suggests commands as you type, with quick selection

# Enable Terminal Brain integrated search
export TB_INTEGRATED_SEARCH=1

# Create a smart command wrapper
tb_smart_search() {
    local query="$1"
    
    # Only show suggestions if query is meaningful
    if [[ -z "$query" || ${#query} -lt 2 ]]; then
        return
    fi
    
    # Get suggestions silently and format nicely
    local suggestions=$(terminalbrain ask "$query" 2>/dev/null | grep -E "^\│" | head -3)
    
    if [[ -n "$suggestions" ]]; then
        echo ""
        echo -e "\033[2;36m💡 Suggestions:\033[0m"
        echo "$suggestions" | while read -r line; do
            # Extract command from table format
            cmd=$(echo "$line" | awk -F'│' '{print $3}' | xargs)
            if [[ -n "$cmd" ]]; then
                echo -e "  \033[2;36m→\033[0m \033[1;32m$cmd\033[0m"
            fi
        done
        echo ""
    fi
}

# Function to intercept and suggest commands
tb_intercept_command() {
    local cmd="$1"
    shift
    local args="$@"
    
    # Show suggestions for complex commands
    if [[ $# -gt 0 ]]; then
        tb_smart_search "$cmd $args" &
    fi
    
    # Execute the command
    command "$cmd" "$@"
}

# Override common commands to show suggestions
# Commented out by default - uncomment to enable
# This could slow down your terminal, so use sparingly
# alias find='tb_intercept_command find'
# alias grep='tb_intercept_command grep'

# Function to enable interactive terminal search mode
tb_interactive_terminal() {
    echo ""
    echo -e "\033[1;36m╔═══════════════════════════════════════════════════╗\033[0m"
    echo -e "\033[1;36m║   Terminal Brain - Integrated Terminal Mode      ║\033[0m"
    echo -e "\033[1;36m╚═══════════════════════════════════════════════════╝\033[0m"
    echo ""
    echo "Type commands naturally - get AI suggestions as you work!"
    echo ""
    echo "Examples:"
    echo "  find large files      → Get find command suggestions"
    echo "  backup documents      → Get backup command suggestions"
    echo "  show memory usage      → Get system info commands"
    echo ""
    
    # Create a temporary readline inputrc
    local temp_inputrc="/tmp/tb_inputrc_$$"
    cat > "$temp_inputrc" << 'EOF'
# Terminal Brain Enhanced Readline
set editing-mode emacs
set show-all-if-ambiguous on

# F1 for Terminal Brain search
"\e[11~": "terminalbrain search\n"

# Alt+S for quick search
"\es": "terminalbrain search\n"
EOF
    
    echo "📍 Press Alt+S to open Terminal Brain search anytime"
    echo "📍 Or type: tbsearch"
    echo ""
}

# Quick keybinding helper for bash
tb_setup_keybindings() {
    # Bind Alt+S to open search
    bind '"\es": "terminalbrain search\n"'
}

# Initialize on shell load
if [[ "$BASH" ]]; then
    tb_setup_keybindings
fi

# Export for use in scripts
export -f tb_smart_search
export -f tb_intercept_command
export -f tb_interactive_terminal
export -f tb_setup_keybindings
