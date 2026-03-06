#!/bin/bash

# Setup shell integration for Terminal Brain

SHELL_NAME=${SHELL##*/}
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TERMINALBRAIN_DIR="$(dirname "$SCRIPT_DIR")/terminalbrain"

setup_bash() {
    local bashrc="$HOME/.bashrc"
    local integration_source="source $TERMINALBRAIN_DIR/shell/bash_integration.sh"
    
    if grep -q "terminalbrain" "$bashrc" 2>/dev/null; then
        echo "✓ Terminal Brain already integrated in $bashrc"
        return
    fi
    
    if [ ! -f "$bashrc" ]; then
        touch "$bashrc"
    fi
    
    echo "" >> "$bashrc"
    echo "# Terminal Brain Integration" >> "$bashrc"
    echo "$integration_source" >> "$bashrc"
    
    echo "✓ Terminal Brain integrated into $bashrc"
}

setup_zsh() {
    local zshrc="$HOME/.zshrc"
    local integration_source="source $TERMINALBRAIN_DIR/shell/zsh_integration.sh"
    
    if grep -q "terminalbrain" "$zshrc" 2>/dev/null; then
        echo "✓ Terminal Brain already integrated in $zshrc"
        return
    fi
    
    if [ ! -f "$zshrc" ]; then
        touch "$zshrc"
    fi
    
    echo "" >> "$zshrc"
    echo "# Terminal Brain Integration" >> "$zshrc"
    echo "$integration_source" >> "$zshrc"
    
    echo "✓ Terminal Brain integrated into $zshrc"
}

main() {
    echo "Setting up Terminal Brain shell integration..."
    
    case "$SHELL_NAME" in
        bash)
            setup_bash
            ;;
        zsh)
            setup_zsh
            ;;
        *)
            echo "⚠ Unsupported shell: $SHELL_NAME"
            echo "Please manually source the integration scripts"
            exit 1
            ;;
    esac
    
    echo ""
    echo "✓ Setup complete! Reload your shell to enable Terminal Brain"
}

main
