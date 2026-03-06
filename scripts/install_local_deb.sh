#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEB_PATH="${1:-$ROOT_DIR/dist/deb/terminal-brain.deb}"

if [[ ! -f "$DEB_PATH" ]]; then
    echo "Package not found: $DEB_PATH" >&2
    echo "Build it first with: ./scripts/build_deb.sh" >&2
    exit 1
fi

sudo apt install -y "$DEB_PATH"

echo "terminal-brain installed. Try: terminal-brain --help"
