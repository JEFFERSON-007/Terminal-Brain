#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="${1:-$ROOT_DIR/build/apt-repo}"
DEB_DIR="${2:-$ROOT_DIR/dist/deb}"
DIST="${DIST:-stable}"
COMPONENT="${COMPONENT:-main}"
ARCH="${ARCH:-amd64}"

if ! command -v dpkg-scanpackages >/dev/null 2>&1; then
    echo "dpkg-scanpackages is required (install dpkg-dev)." >&2
    exit 1
fi

mkdir -p "$REPO_ROOT/pool/$COMPONENT/t/terminal-brain"
mkdir -p "$REPO_ROOT/dists/$DIST/$COMPONENT/binary-$ARCH"

# Copy packages into the pool.
find "$DEB_DIR" -maxdepth 1 -type f -name 'terminal-brain_*.deb' -exec cp -f {} "$REPO_ROOT/pool/$COMPONENT/t/terminal-brain/" \;

pushd "$REPO_ROOT" >/dev/null

dpkg-scanpackages --multiversion pool /dev/null > "dists/$DIST/$COMPONENT/binary-$ARCH/Packages"
gzip -9c "dists/$DIST/$COMPONENT/binary-$ARCH/Packages" > "dists/$DIST/$COMPONENT/binary-$ARCH/Packages.gz"

if command -v apt-ftparchive >/dev/null 2>&1; then
    apt-ftparchive release "dists/$DIST" > "dists/$DIST/Release"
else
    echo "Warning: apt-ftparchive not found (install apt-utils) - Release file not generated." >&2
fi

# GitHub Pages compatibility
: > .nojekyll

popd >/dev/null

echo "APT repository generated at: $REPO_ROOT"
echo "Repository root contains: dists/, pool/, and package indexes."
