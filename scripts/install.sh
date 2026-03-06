#!/bin/bash

# Terminal Brain Installation Script
# This script installs Terminal Brain and sets up shell integration

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${GREEN}======================================${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${GREEN}======================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check Python version
print_header "Checking system requirements"

if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
print_success "Python $PYTHON_VERSION found"

# Check pip
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is not installed"
    exit 1
fi

print_success "pip3 found"

# Create virtual environment
print_header "Setting up virtual environment"

if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

source venv/bin/activate
print_success "Virtual environment activated"

# Install dependencies
print_header "Installing dependencies"

pip install --upgrade pip setuptools wheel
pip install -e .

print_success "Dependencies installed"

# Optional: Install GPU support
if command -v nvidia-smi &> /dev/null; then
    print_warning "NVIDIA GPU detected. Install GPU-accelerated FAISS? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        pip install faiss-gpu torch
        print_success "GPU packages installed"
    fi
fi

# Optional: Install Ollama for local LLM
print_header "Local LLM Setup (Optional)"
print_warning "Terminal Brain works best with local LLMs via Ollama"
echo "Install Ollama from: https://ollama.ai"
echo "Then run: ollama pull mistral"

# Setup shell integration
print_header "Setting up shell integration"

SHELL_NAME=${SHELL##*/}

if [ "$SHELL_NAME" = "bash" ]; then
    BASHRC="$HOME/.bashrc"
    if ! grep -q "terminalbrain" "$BASHRC"; then
        echo "" >> "$BASHRC"
        echo "# Terminal Brain Integration" >> "$BASHRC"
        echo "source $(pwd)/terminalbrain/shell/bash_integration.sh" >> "$BASHRC"
        print_success "Added Terminal Brain to $BASHRC"
    else
        print_warning "Terminal Brain already in $BASHRC"
    fi

elif [ "$SHELL_NAME" = "zsh" ]; then
    ZSHRC="$HOME/.zshrc"
    if ! grep -q "terminalbrain" "$ZSHRC"; then
        echo "" >> "$ZSHRC"
        echo "# Terminal Brain Integration" >> "$ZSHRC"
        echo "source $(pwd)/terminalbrain/shell/zsh_integration.sh" >> "$ZSHRC"
        print_success "Added Terminal Brain to $ZSHRC"
    else
        print_warning "Terminal Brain already in $ZSHRC"
    fi
fi

# Create config directory
print_header "Creating configuration"

CONFIG_DIR="$HOME/.config/terminalbrain"
mkdir -p "$CONFIG_DIR"

if [ ! -f "$CONFIG_DIR/terminalbrain.toml" ]; then
    cat > "$CONFIG_DIR/terminalbrain.toml" << 'EOF'
[general]
theme = "dark"
startup_message = true
suggestion_frequency = 3

[ai]
backend = "ollama"
model = "mistral"
temperature = 0.7
max_suggestions = 5

[ui]
show_dashboard = true
show_battery = true
show_network_speed = true
show_processes = true
refresh_interval = 2000

[security]
dangerous_commands = ["rm -rf", "mkfs", "dd", ":|", "> /dev"]
require_confirmation = true

[knowledge]
enable_rag = true
knowledge_source = "tldr"
cache_embeddings = true
EOF
    print_success "Created configuration at $CONFIG_DIR/terminalbrain.toml"
else
    print_warning "Configuration already exists at $CONFIG_DIR/terminalbrain.toml"
fi

print_header "Installation complete!"

echo ""
echo "✓ Terminal Brain has been installed successfully"
echo ""
echo "Next steps:"
echo "  1. Reload your shell: source ${SHELL} or restart terminal"
echo "  2. Try: tb ask 'list files'"
echo "  3. View dashboard: tb dashboard"
echo "  4. Analyze history: tb analyze"
echo ""
echo "For local LLM support, install Ollama:"
echo "  https://ollama.ai"
echo ""
echo "Documentation: docs/README.md"
echo ""
