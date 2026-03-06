#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PACKAGE_NAME="terminal-brain"
ARCH="${ARCH:-$(dpkg --print-architecture)}"

if [[ $# -gt 0 ]]; then
    VERSION="$1"
else
    VERSION="$(python3 - <<'PY'
from pathlib import Path
import re
text = Path('pyproject.toml').read_text(encoding='utf-8')
match = re.search(r'^version\s*=\s*"([^"]+)"', text, flags=re.MULTILINE)
if not match:
    raise SystemExit('Could not read version from pyproject.toml')
print(match.group(1))
PY
)"
fi

BUILD_ROOT="$ROOT_DIR/build/debian"
PKG_ROOT="$BUILD_ROOT/$PACKAGE_NAME"
DEBIAN_DIR="$PKG_ROOT/DEBIAN"
DIST_DIR="$ROOT_DIR/dist/deb"
OUTPUT_FILE="$DIST_DIR/${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"

rm -rf "$PKG_ROOT"
mkdir -p "$DEBIAN_DIR" "$PKG_ROOT/usr/bin" "$PKG_ROOT/usr/share/$PACKAGE_NAME/src" "$PKG_ROOT/etc/terminalbrain" "$PKG_ROOT/usr/share/doc/$PACKAGE_NAME"

# Copy project source into the package payload.
tar -C "$ROOT_DIR" \
  --exclude='./.git' \
  --exclude='./build' \
  --exclude='./dist' \
  --exclude='./.venv' \
  --exclude='./venv' \
  --exclude='./__pycache__' \
  --exclude='./.pytest_cache' \
  -cf - . | tar -C "$PKG_ROOT/usr/share/$PACKAGE_NAME/src" -xf -

# Global default configuration.
install -m 644 "$ROOT_DIR/config/terminalbrain.toml" "$PKG_ROOT/etc/terminalbrain/terminalbrain.toml"

# Debian metadata.
sed \
  -e "s/@VERSION@/$VERSION/g" \
  -e "s/@ARCH@/$ARCH/g" \
  "$ROOT_DIR/packaging/debian/terminal-brain/DEBIAN/control.template" > "$DEBIAN_DIR/control"

install -m 755 "$ROOT_DIR/packaging/debian/terminal-brain/DEBIAN/postinst" "$DEBIAN_DIR/postinst"
install -m 755 "$ROOT_DIR/packaging/debian/terminal-brain/DEBIAN/postrm" "$DEBIAN_DIR/postrm"

cat > "$PKG_ROOT/usr/bin/terminal-brain" <<'EOF'
#!/bin/sh
set -e

VENV_BIN="/opt/terminal-brain/venv/bin/terminalbrain"

if [ ! -x "$VENV_BIN" ]; then
    echo "terminal-brain is not fully initialized. Reconfigure with: sudo dpkg --configure terminal-brain" >&2
    exit 1
fi

exec "$VENV_BIN" "$@"
EOF

cat > "$PKG_ROOT/usr/bin/tb" <<'EOF'
#!/bin/sh
set -e
exec /usr/bin/terminal-brain "$@"
EOF

chmod 755 "$PKG_ROOT/usr/bin/terminal-brain" "$PKG_ROOT/usr/bin/tb"

install -m 644 "$ROOT_DIR/README.md" "$PKG_ROOT/usr/share/doc/$PACKAGE_NAME/README.md"
install -m 644 "$ROOT_DIR/CHANGELOG.md" "$PKG_ROOT/usr/share/doc/$PACKAGE_NAME/changelog"
install -m 644 "$ROOT_DIR/LICENSE" "$PKG_ROOT/usr/share/doc/$PACKAGE_NAME/copyright"

mkdir -p "$DIST_DIR"
fakeroot dpkg-deb --build "$PKG_ROOT" "$OUTPUT_FILE"
cp "$OUTPUT_FILE" "$DIST_DIR/${PACKAGE_NAME}.deb"

echo "Built package: $OUTPUT_FILE"
echo "Convenience path: $DIST_DIR/${PACKAGE_NAME}.deb"
