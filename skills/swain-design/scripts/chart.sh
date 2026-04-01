#!/usr/bin/env bash
set -euo pipefail
# swain chart — vision-rooted hierarchy display
# Subsumes specgraph. All commands route through the Python CLI.

SCRIPT_PATH="$(python3 -c 'import os, sys; print(os.path.realpath(sys.argv[1]))' "$0")"
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH:-}"

exec python3 "${SCRIPT_DIR}/chart_cli.py" "$@"
