#!/usr/bin/env bash
# Wrapper to run security_check.py via uv (no pip install needed).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec uv run python3 "$SCRIPT_DIR/security_check.py" "$@"
