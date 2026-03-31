#!/usr/bin/env bash
# swain-startup-timing.sh — SPIKE-001: Instrument session startup time
#
# Measures wall time for each phase of the session startup chain.
# Does NOT modify any existing scripts — wraps them with timing.
#
# Usage:
#   swain-startup-timing.sh [--include-status] [--runs N] [--json]
#
# Output: timing breakdown by phase (human-readable or JSON)

set +e

# Portable path resolution — resolves through symlinks
_src="${BASH_SOURCE[0]}"
while [[ -L "$_src" ]]; do
  _dir="$(cd "$(dirname "$_src")" && pwd)"
  _src="$(readlink "$_src")"
  [[ "$_src" != /* ]] && _src="$_dir/$_src"
done
SCRIPT_DIR="$(cd "$(dirname "$_src")" && pwd)"
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

INCLUDE_STATUS=0
RUNS=1
JSON_OUTPUT=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --include-status) INCLUDE_STATUS=1; shift ;;
    --runs) RUNS="$2"; shift 2 ;;
    --json) JSON_OUTPUT=1; shift ;;
    *) shift ;;
  esac
done

# Portable millisecond timer (macOS date doesn't support %N)
if command -v gdate &>/dev/null; then
  _ts() { gdate +%s%3N; }
elif date +%s%N &>/dev/null 2>&1; then
  _ts() { echo $(( $(date +%s%N) / 1000000 )); }
else
  # Fallback: second-level precision (macOS without coreutils)
  _ts() { python3 -c "import time; print(int(time.time()*1000))"; }
fi

declare -a PHASE_NAMES
declare -a PHASE_DURATIONS

time_phase() {
  local name="$1"
  shift
  local start=$(_ts)
  "$@" >/dev/null 2>&1
  local end=$(_ts)
  local dur=$((end - start))
  PHASE_NAMES+=("$name")
  PHASE_DURATIONS+=("$dur")
}

run_single() {
  PHASE_NAMES=()
  PHASE_DURATIONS=()

  local total_start=$(_ts)

  # Phase 1: .swain-init marker check (what the shell launcher would do)
  time_phase "init_marker_check" test -f "$REPO_ROOT/.swain-init"

  # Phase 2: Preflight
  time_phase "preflight" bash "$(dirname "$(dirname "$SCRIPT_DIR")")/swain-doctor/scripts/swain-preflight.sh"

  # Phase 3: Bootstrap (tab naming + worktree detect + session.json)
  time_phase "bootstrap_full" bash "$SCRIPT_DIR/swain-session-bootstrap.sh" --auto

  # Phase 3a: Bootstrap sub-phases (individual measurement)
  # Tab naming only
  if [[ -n "${TMUX:-}" ]] && [[ -f "$SCRIPT_DIR/swain-tab-name.sh" ]]; then
    time_phase "tab_naming" bash "$SCRIPT_DIR/swain-tab-name.sh" --auto
  else
    PHASE_NAMES+=("tab_naming")
    PHASE_DURATIONS+=("0")
  fi

  # Worktree detection only
  time_phase "worktree_detect" git rev-parse --git-common-dir

  # Session.json read only
  time_phase "session_json_read" jq -r '.focus_lane // empty' "$REPO_ROOT/.agents/session.json"

  # Phase 4: Status dashboard (optional — this is the expensive one)
  if [[ "$INCLUDE_STATUS" -eq 1 ]] && [[ -f "$SCRIPT_DIR/swain-status.sh" ]]; then
    time_phase "status_dashboard" bash "$SCRIPT_DIR/swain-status.sh" --json --refresh
  fi

  local total_end=$(_ts)
  local total=$((total_end - total_start))
  PHASE_NAMES+=("total_measured")
  PHASE_DURATIONS+=("$total")
}

# ─── Execution ───

ALL_RESULTS=()

for ((i=1; i<=RUNS; i++)); do
  run_single

  if [[ "$JSON_OUTPUT" -eq 1 ]]; then
    # Build JSON for this run
    run_json="{"
    for ((j=0; j<${#PHASE_NAMES[@]}; j++)); do
      [[ $j -gt 0 ]] && run_json+=","
      run_json+="\"${PHASE_NAMES[$j]}\":${PHASE_DURATIONS[$j]}"
    done
    run_json+="}"
    ALL_RESULTS+=("$run_json")
  else
    echo "=== Run $i/$RUNS ==="
    for ((j=0; j<${#PHASE_NAMES[@]}; j++)); do
      printf "  %-25s %6d ms\n" "${PHASE_NAMES[$j]}" "${PHASE_DURATIONS[$j]}"
    done
    echo ""
  fi
done

if [[ "$JSON_OUTPUT" -eq 1 ]]; then
  echo -n '{"runs":['
  for ((i=0; i<${#ALL_RESULTS[@]}; i++)); do
    [[ $i -gt 0 ]] && echo -n ","
    echo -n "${ALL_RESULTS[$i]}"
  done
  echo -n '],"note":"Times are script execution only. LLM inference and tool-call overhead are not measured here — they dominate total wall time but cannot be measured from within scripts."}'
fi
