#!/usr/bin/env bash
set -euo pipefail

DEST="$HOME/.openclaw/workspace/skills"
if [[ "${1:-}" == "--dest" && -n "${2:-}" ]]; then
  DEST="$2"
fi

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

ARCHIVE_URL="https://codeload.github.com/sdyzjx/paper-zotero-skills-installer/tar.gz/refs/heads/main"
curl -fsSL "$ARCHIVE_URL" -o "$TMP_DIR/repo.tar.gz"

tar -xzf "$TMP_DIR/repo.tar.gz" -C "$TMP_DIR"
SRC_DIR="$TMP_DIR/paper-zotero-skills-installer-main/skills"

mkdir -p "$DEST"
cp -R "$SRC_DIR"/* "$DEST/"

echo "Installed skills to: $DEST"
echo "Installed: ieee-zotero-save, literature-research-orchestrator, literature-summary-agent, pdf, zotero-library"
