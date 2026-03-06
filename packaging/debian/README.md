# Debian Packaging Assets

This directory contains Debian packaging templates used by the automated scripts.

## Files

- `terminal-brain/DEBIAN/control.template`
  - Metadata template for package control file.
- `terminal-brain/DEBIAN/postinst`
  - Initializes `/opt/terminal-brain/venv` and installs Terminal Brain.
- `terminal-brain/DEBIAN/postrm`
  - Removes `/opt/terminal-brain` when package is purged.

## Build Entry Point

Use:

```bash
./scripts/build_deb.sh
```

This script assembles package payload and metadata under `build/debian/terminal-brain/` and then runs `dpkg-deb --build`.
