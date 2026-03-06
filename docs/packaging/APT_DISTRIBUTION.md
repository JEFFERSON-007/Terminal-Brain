# APT Distribution Guide for Terminal Brain

This guide defines the Debian/Ubuntu packaging and APT repository workflow for Terminal Brain using standard Debian tooling.

## 1) Deliverables Included

- Debian package metadata template: [packaging/debian/terminal-brain/DEBIAN/control.template](../../packaging/debian/terminal-brain/DEBIAN/control.template)
- Build script for `.deb`: [scripts/build_deb.sh](../../scripts/build_deb.sh)
- Repository index generation script: [scripts/generate_apt_repo.sh](../../scripts/generate_apt_repo.sh)
- Local install helper: [scripts/install_local_deb.sh](../../scripts/install_local_deb.sh)
- CI/CD pipeline: [.github/workflows/debian-package.yml](../../.github/workflows/debian-package.yml)

## 2) Debian Package Structure

The build script creates this package root before running `dpkg-deb`:

```text
terminal-brain/
├── DEBIAN/
│   ├── control
│   ├── postinst
│   └── postrm
├── usr/
│   ├── bin/
│   │   ├── terminal-brain
│   │   └── tb
│   └── share/
│       ├── terminal-brain/
│       │   └── src/               # Project source copied from repository
│       └── doc/
│           └── terminal-brain/
│               ├── README.md
│               ├── changelog
│               └── copyright
└── etc/
    └── terminalbrain/
        └── terminalbrain.toml
```

## 3) Build the `.deb` Package

Prerequisites on Debian/Ubuntu:

- `dpkg-deb`
- `fakeroot`
- `python3`
- `python3-venv`
- `python3-pip`

Build:

```bash
./scripts/build_deb.sh
```

Output:

- `dist/deb/terminal-brain_<version>_<arch>.deb`
- `dist/deb/terminal-brain.deb`

Manual install:

```bash
sudo apt install ./dist/deb/terminal-brain.deb
```

The package `postinst` script initializes:

- `/opt/terminal-brain/venv`
- installs Terminal Brain into that venv from `/usr/share/terminal-brain/src`

## 4) APT Repository Layout

Generated repository layout:

```text
repo/
├── dists/
│   └── stable/
│       ├── Release
│       └── main/
│           └── binary-amd64/
│               ├── Packages
│               └── Packages.gz
└── pool/
    └── main/
        └── t/
            └── terminal-brain/
                └── terminal-brain_<version>_amd64.deb
```

Generate repository index:

```bash
./scripts/generate_apt_repo.sh ./repo ./dist/deb
```

Internally this uses standard tooling:

```bash
dpkg-scanpackages --multiversion pool /dev/null > dists/stable/main/binary-amd64/Packages
gzip -9c dists/stable/main/binary-amd64/Packages > dists/stable/main/binary-amd64/Packages.gz
```

## 5) Hosting Options

You can host the generated repository on:

- GitHub Pages
- S3-compatible static hosting
- Cloudflare R2 static website
- VPS static web server (Nginx/Apache)

Requirements:

- HTTPS endpoint
- Publicly readable `dists/` and `pool/` paths

## 6) User Setup for Global `apt` Install

After hosting under `https://your-repo-url/apt`, users run:

```bash
echo "deb [trusted=yes] https://your-repo-url/apt stable main" | sudo tee /etc/apt/sources.list.d/terminalbrain.list
sudo apt update
sudo apt install terminal-brain
```

Then:

```bash
terminal-brain --help
```

> Note: `[trusted=yes]` is suitable for early testing. For production, sign your repo metadata with GPG and distribute the key.

## 7) Updates and Upgrades

When a new package version is published to the same repository:

```bash
sudo apt update
sudo apt upgrade
```

`apt` will upgrade `terminal-brain` if the version in `Packages` is newer.

## 8) CI/CD Automation

Workflow file:

- [.github/workflows/debian-package.yml](../../.github/workflows/debian-package.yml)

By default, repository publishing is opt-in. Set repository variable `ENABLE_PAGES_PUBLISH=true` to enable the `publish-pages` job.

Pipeline stages:

1. Build `.deb` using `./scripts/build_deb.sh`
2. Generate repository with `./scripts/generate_apt_repo.sh`
3. Upload build artifacts
4. Publish repo to GitHub Pages on `main` and release tags

## 9) Recommended Production Hardening

- Add GPG signing for `Release` / `InRelease`
- Pin exact dependency versions in release process
- Add amd64 + arm64 matrix builds if needed
- Add smoke test job that installs from generated repo in a clean container
