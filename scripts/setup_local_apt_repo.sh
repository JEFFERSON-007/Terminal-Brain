#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOCAL_REPO_ROOT="${1:-/srv/apt/terminal-brain}"
DEB_DIR="${2:-$ROOT_DIR/dist/deb}"
LIST_FILE="/etc/apt/sources.list.d/terminalbrain-local.list"

if [[ $EUID -eq 0 ]]; then
  echo "Run as your normal user (script uses sudo where needed)." >&2
  exit 1
fi

if ! ls "$DEB_DIR"/terminal-brain_*.deb >/dev/null 2>&1; then
  "$ROOT_DIR/scripts/build_deb.sh"
fi

sudo mkdir -p "$LOCAL_REPO_ROOT"
sudo chown -R "$USER":"$USER" "$LOCAL_REPO_ROOT"

"$ROOT_DIR/scripts/generate_apt_repo.sh" "$LOCAL_REPO_ROOT" "$DEB_DIR"

sudo chmod -R a+rX "$LOCAL_REPO_ROOT"
echo "deb [trusted=yes] file:$LOCAL_REPO_ROOT stable main" | sudo tee "$LIST_FILE" >/dev/null

sudo apt update
apt policy terminal-brain | cat

echo "Local APT repo configured."
echo "Install with: sudo apt install terminal-brain"
