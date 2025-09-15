#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:-$(date +%Y%m%d%H%M)}"
NAME="rag-assistant-${VERSION}"
OUTDIR="dist"

mkdir -p "$OUTDIR"

echo "==> Creating $OUTDIR/${NAME}.zip"
zip -r "$OUTDIR/${NAME}.zip" . \
  -x "${OUTDIR}/*" \
  -x "venv/*" \
  -x "**/__pycache__/*" \
  -x "**/*.pyc" \
  -x "web/node_modules/*" \
  -x "web/.next/*" \
  -x ".git/*" \
  -x "logs/*" \
  -x "conversations.db" \
  -x ".DS_Store" \
  -x "**/.DS_Store"

echo "==> Release created: $OUTDIR/${NAME}.zip"

