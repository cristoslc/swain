#!/usr/bin/env bash
set -euo pipefail
# swain chart — vision-rooted hierarchy display
# Subsumes specgraph. All commands route through the Python CLI.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH:-}"

exec python3 "${SCRIPT_DIR}/chart_cli.py" "$@"
