#!/usr/bin/env bash
# swain-init-preflight.sh — read-only environment scanner for swain-init
#
# Runs all pre-onboarding checks and emits a single JSON object to stdout.
# This script NEVER mutates state (no file writes, installs, or symlinks).
# The skill file reads this JSON and makes decisions based on the results.
#
# Usage: bash swain-init-preflight.sh [--repo-root /path/to/repo]
#
# JSON schema (all keys present, some may be null on error):
#
#   marker.exists          bool    — .swain-init file found
#   marker.last_version    string  — version from last history entry (null if no marker)
#   marker.current_version string  — version from installed swain-init SKILL.md
#   marker.action          string  — "delegate" | "upgrade" | "onboard"
#
#   migration.state        string  — "fresh" | "migrated" | "standard" | "split"
#   migration.claude_md    string  — "missing" | "empty" | "include_only" | "has_content"
#   migration.agents_md    string  — "missing" | "empty" | "has_content"
#
#   uv.available           bool    — uv binary found in PATH
#   uv.path                string  — path to uv (null if not found)
#
#   tk.path                string  — path to vendored tk (null if not found)
#   tk.healthy             bool    — tk help runs successfully
#
#   beads.exists           bool    — .beads/ directory found
#   beads.has_backup       bool    — .beads/backup/issues.jsonl exists
#
#   bin_manifests          array   — list of {skill, commands[]} for usr/bin/ dirs
#
#   precommit.config_exists bool   — .pre-commit-config.yaml found
#   precommit.framework     bool   — pre-commit binary found in PATH
#
#   superpowers.installed  bool    — brainstorming SKILL.md found
#
#   tmux.installed         bool    — tmux binary found
#
#   launcher.shell         string  — detected shell name (zsh/bash/fish/unknown)
#   launcher.rc_file       string  — path to rc file
#   launcher.already_installed bool — swain function already in rc file
#   launcher.runtimes      array   — list of detected agentic runtimes
#   launcher.template_dir  string  — path to launcher templates (null if not found)
#
#   governance.installed   bool    — swain governance block found in AGENTS.md or CLAUDE.md
#
#   readme.exists          bool    — README.md found
#   readme.has_code        bool    — source code files found in repo
#   readme.has_artifacts   bool    — Active artifacts found in docs/
#   readme.active_count    int     — count of Active VISION/DESIGN/JOURNEY/PERSONA artifacts
#
#   agents_dir.exists      bool    — .agents/ directory exists
#
# Exit: always 0 (partial results on individual check failures)

set -euo pipefail

REPO_ROOT=""

while [ $# -gt 0 ]; do
  case "$1" in
    --repo-root) REPO_ROOT="$2"; shift 2 ;;
    *) shift ;;
  esac
done

if [ -z "$REPO_ROOT" ]; then
  REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
fi

cd "$REPO_ROOT"

# --- Collector variables ---
# Each check function sets variables prefixed with its category.
# We collect everything at the end via python3 JSON serialization.

# --- Marker check ---
check_marker() {
  MARKER_EXISTS=false
  MARKER_LAST_VERSION=""
  MARKER_CURRENT_VERSION=""
  MARKER_ACTION="onboard"

  if [ -f ".swain-init" ]; then
    MARKER_EXISTS=true
    # Extract last version — try jq first, fall back to python3, then grep
    MARKER_LAST_VERSION=$(python3 -c "
import json, sys
try:
    d = json.load(open('.swain-init'))
    print(d['history'][-1]['version'])
except Exception:
    sys.exit(1)
" 2>/dev/null || echo "")
  fi

  # Find current installed version
  SKILL_FILE=$(find . .claude .agents -path '*/swain-init/SKILL.md' -print -quit 2>/dev/null || true)
  if [ -n "$SKILL_FILE" ] && [ -f "$SKILL_FILE" ]; then
    MARKER_CURRENT_VERSION=$(head -20 "$SKILL_FILE" 2>/dev/null | grep 'version:' | awk '{print $2}' || true)
  fi

  # Determine action
  if [ "$MARKER_EXISTS" = true ] && [ -n "$MARKER_LAST_VERSION" ] && [ -n "$MARKER_CURRENT_VERSION" ]; then
    LAST_MAJOR="${MARKER_LAST_VERSION%%.*}"
    CURRENT_MAJOR="${MARKER_CURRENT_VERSION%%.*}"
    if [ "$LAST_MAJOR" = "$CURRENT_MAJOR" ]; then
      MARKER_ACTION="delegate"
    else
      MARKER_ACTION="upgrade"
    fi
  fi
}

# --- Migration state check ---
check_migration() {
  MIGRATION_STATE="fresh"
  MIGRATION_CLAUDE_MD="missing"
  MIGRATION_AGENTS_MD="missing"

  # Classify CLAUDE.md
  if [ -f "CLAUDE.md" ]; then
    if [ ! -s "CLAUDE.md" ]; then
      MIGRATION_CLAUDE_MD="empty"
    else
      CONTENT=$(cat "CLAUDE.md" 2>/dev/null)
      TRIMMED=$(echo "$CONTENT" | sed '/^[[:space:]]*$/d')
      if [ "$TRIMMED" = "@AGENTS.md" ]; then
        MIGRATION_CLAUDE_MD="include_only"
      else
        MIGRATION_CLAUDE_MD="has_content"
      fi
    fi
  fi

  # Classify AGENTS.md
  if [ -f "AGENTS.md" ]; then
    if [ ! -s "AGENTS.md" ]; then
      MIGRATION_AGENTS_MD="empty"
    else
      MIGRATION_AGENTS_MD="has_content"
    fi
  fi

  # Determine migration state
  if [ "$MIGRATION_CLAUDE_MD" = "include_only" ]; then
    MIGRATION_STATE="migrated"
  elif [ "$MIGRATION_CLAUDE_MD" = "missing" ] || [ "$MIGRATION_CLAUDE_MD" = "empty" ]; then
    if [ "$MIGRATION_AGENTS_MD" = "missing" ] || [ "$MIGRATION_AGENTS_MD" = "empty" ]; then
      MIGRATION_STATE="fresh"
    else
      MIGRATION_STATE="fresh"
    fi
  elif [ "$MIGRATION_CLAUDE_MD" = "has_content" ]; then
    if [ "$MIGRATION_AGENTS_MD" = "has_content" ]; then
      MIGRATION_STATE="split"
    else
      MIGRATION_STATE="standard"
    fi
  fi
}

# --- uv check ---
check_uv() {
  UV_AVAILABLE=false
  UV_PATH=""

  UV_PATH=$(command -v uv 2>/dev/null || true)
  if [ -n "$UV_PATH" ]; then
    UV_AVAILABLE=true
  fi
}

# --- tk check ---
check_tk() {
  TK_PATH=""
  TK_HEALTHY=false

  TK_PATH=$(find . .claude .agents -path '*/swain-do/bin/tk' -print -quit 2>/dev/null || true)
  if [ -n "$TK_PATH" ] && [ -x "$TK_PATH" ]; then
    if "$TK_PATH" help >/dev/null 2>&1; then
      TK_HEALTHY=true
    fi
  fi
}

# --- beads check ---
check_beads() {
  BEADS_EXISTS=false
  BEADS_HAS_BACKUP=false

  if [ -d ".beads" ]; then
    BEADS_EXISTS=true
    if [ -f ".beads/backup/issues.jsonl" ]; then
      BEADS_HAS_BACKUP=true
    fi
  fi
}

# --- bin manifests check ---
check_bin_manifests() {
  # Collect as newline-delimited "skill|command" pairs; python3 will parse
  BIN_MANIFESTS_RAW=""
  SKILLS_ROOT=".agents/skills"
  if [ -d "$SKILLS_ROOT" ]; then
    for manifest_dir in "$SKILLS_ROOT"/*/usr/bin; do
      [ -d "$manifest_dir" ] || continue
      skill_name=$(basename "$(dirname "$(dirname "$manifest_dir")")")
      for entry in "$manifest_dir"/*; do
        [ -e "$entry" ] || [ -L "$entry" ] || continue
        cmd_name=$(basename "$entry")
        BIN_MANIFESTS_RAW="${BIN_MANIFESTS_RAW}${skill_name}|${cmd_name}
"
      done
    done
  fi
}

# --- pre-commit check ---
check_precommit() {
  PRECOMMIT_CONFIG_EXISTS=false
  PRECOMMIT_FRAMEWORK=false

  if [ -f ".pre-commit-config.yaml" ]; then
    PRECOMMIT_CONFIG_EXISTS=true
  fi

  if command -v pre-commit >/dev/null 2>&1; then
    PRECOMMIT_FRAMEWORK=true
  fi
}

# --- superpowers check ---
check_superpowers() {
  SUPERPOWERS_INSTALLED=false

  if ls .agents/skills/brainstorming/SKILL.md .claude/skills/brainstorming/SKILL.md 2>/dev/null | head -1 | grep -q .; then
    SUPERPOWERS_INSTALLED=true
  fi
}

# --- tmux check ---
check_tmux() {
  TMUX_INSTALLED=false

  if command -v tmux >/dev/null 2>&1; then
    TMUX_INSTALLED=true
  fi
}

# --- shell launcher check ---
check_launcher() {
  LAUNCHER_SHELL="unknown"
  LAUNCHER_RC_FILE=""
  LAUNCHER_ALREADY_INSTALLED=false
  LAUNCHER_RUNTIMES_RAW=""
  LAUNCHER_TEMPLATE_DIR=""

  # Detect shell
  LAUNCHER_SHELL=$(basename "${SHELL:-unknown}")

  # Map to rc file
  case "$LAUNCHER_SHELL" in
    zsh)  LAUNCHER_RC_FILE="$HOME/.zshrc" ;;
    bash) LAUNCHER_RC_FILE="$HOME/.bashrc" ;;
    fish) LAUNCHER_RC_FILE="$HOME/.config/fish/config.fish" ;;
    *)    LAUNCHER_RC_FILE="" ;;
  esac

  # Check for existing launcher
  if [ -n "$LAUNCHER_RC_FILE" ] && [ -f "$LAUNCHER_RC_FILE" ]; then
    case "$LAUNCHER_SHELL" in
      zsh|bash)
        if grep -q 'swain\s*()' "$LAUNCHER_RC_FILE" 2>/dev/null; then
          LAUNCHER_ALREADY_INSTALLED=true
        fi
        ;;
      fish)
        if grep -q 'function swain' "$LAUNCHER_RC_FILE" 2>/dev/null; then
          LAUNCHER_ALREADY_INSTALLED=true
        fi
        ;;
    esac
  fi

  # Detect runtimes
  for rt in claude gemini codex copilot crush; do
    if command -v "$rt" >/dev/null 2>&1; then
      LAUNCHER_RUNTIMES_RAW="${LAUNCHER_RUNTIMES_RAW}${rt}
"
    fi
  done

  # Find template directory
  LAUNCHER_TEMPLATE_DIR=$(find . .claude .agents -path '*/swain-init/templates/launchers' -type d -print -quit 2>/dev/null || true)
}

# --- governance check ---
check_governance() {
  GOVERNANCE_INSTALLED=false

  if grep -q "swain governance" AGENTS.md CLAUDE.md 2>/dev/null; then
    GOVERNANCE_INSTALLED=true
  fi
}

# --- readme and artifacts check ---
check_readme() {
  README_EXISTS=false
  README_HAS_CODE=false
  README_HAS_ARTIFACTS=false
  README_ACTIVE_COUNT=0

  if [ -f "README.md" ]; then
    README_EXISTS=true
  fi

  # Check for source code
  if find . -maxdepth 3 \( -name '*.py' -o -name '*.js' -o -name '*.ts' -o -name '*.go' -o -name '*.rs' -o -name '*.sh' \) \
     -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/.agents/*' -not -path '*/.claude/*' \
     -print -quit 2>/dev/null | grep -q .; then
    README_HAS_CODE=true
  fi

  # Check for Active artifacts
  if find docs -name '*.md' -path '*/Active/*' -print -quit 2>/dev/null | grep -q .; then
    README_HAS_ARTIFACTS=true
  fi

  # Count Active VISION/DESIGN/JOURNEY/PERSONA artifacts
  README_ACTIVE_COUNT=$(find docs -path "*/Active/*" -name "*.md" 2>/dev/null | grep -cE "(VISION|DESIGN|JOURNEY|PERSONA)") || README_ACTIVE_COUNT=0
}

# --- .agents/ dir check ---
check_agents_dir() {
  AGENTS_DIR_EXISTS=false

  if [ -d ".agents" ]; then
    AGENTS_DIR_EXISTS=true
  fi
}

# --- Run all checks ---
# Each check is wrapped in a subshell-safe pattern; failures don't abort the script.
check_marker || true
check_migration || true
check_uv || true
check_tk || true
check_beads || true
check_bin_manifests || true
check_precommit || true
check_superpowers || true
check_tmux || true
check_launcher || true
check_governance || true
check_readme || true
check_agents_dir || true

# --- Emit JSON via python3 ---
python3 -c "
import json, sys

def to_bool(v):
    return v.lower() == 'true'

def to_int(v):
    try: return int(v)
    except: return 0

def to_str_or_null(v):
    return v if v else None

def to_list(raw):
    return [x for x in raw.strip().split('\n') if x] if raw.strip() else []

def parse_bin_manifests(raw):
    result = {}
    for line in raw.strip().split('\n'):
        if not line or '|' not in line:
            continue
        skill, cmd = line.split('|', 1)
        result.setdefault(skill, []).append(cmd)
    return [{'skill': k, 'commands': v} for k, v in result.items()]

data = {
    'marker': {
        'exists': to_bool(sys.argv[1]),
        'last_version': to_str_or_null(sys.argv[2]),
        'current_version': to_str_or_null(sys.argv[3]),
        'action': sys.argv[4],
    },
    'migration': {
        'state': sys.argv[5],
        'claude_md': sys.argv[6],
        'agents_md': sys.argv[7],
    },
    'uv': {
        'available': to_bool(sys.argv[8]),
        'path': to_str_or_null(sys.argv[9]),
    },
    'tk': {
        'path': to_str_or_null(sys.argv[10]),
        'healthy': to_bool(sys.argv[11]),
    },
    'beads': {
        'exists': to_bool(sys.argv[12]),
        'has_backup': to_bool(sys.argv[13]),
    },
    'bin_manifests': parse_bin_manifests(sys.argv[14]),
    'precommit': {
        'config_exists': to_bool(sys.argv[15]),
        'framework': to_bool(sys.argv[16]),
    },
    'superpowers': {
        'installed': to_bool(sys.argv[17]),
    },
    'tmux': {
        'installed': to_bool(sys.argv[18]),
    },
    'launcher': {
        'shell': sys.argv[19],
        'rc_file': to_str_or_null(sys.argv[20]),
        'already_installed': to_bool(sys.argv[21]),
        'runtimes': to_list(sys.argv[22]),
        'template_dir': to_str_or_null(sys.argv[23]),
    },
    'governance': {
        'installed': to_bool(sys.argv[24]),
    },
    'readme': {
        'exists': to_bool(sys.argv[25]),
        'has_code': to_bool(sys.argv[26]),
        'has_artifacts': to_bool(sys.argv[27]),
        'active_count': to_int(sys.argv[28]),
    },
    'agents_dir': {
        'exists': to_bool(sys.argv[29]),
    },
}

json.dump(data, sys.stdout, indent=2)
print()
" \
  "$MARKER_EXISTS" "$MARKER_LAST_VERSION" "$MARKER_CURRENT_VERSION" "$MARKER_ACTION" \
  "$MIGRATION_STATE" "$MIGRATION_CLAUDE_MD" "$MIGRATION_AGENTS_MD" \
  "$UV_AVAILABLE" "$UV_PATH" \
  "$TK_PATH" "$TK_HEALTHY" \
  "$BEADS_EXISTS" "$BEADS_HAS_BACKUP" \
  "$BIN_MANIFESTS_RAW" \
  "$PRECOMMIT_CONFIG_EXISTS" "$PRECOMMIT_FRAMEWORK" \
  "$SUPERPOWERS_INSTALLED" \
  "$TMUX_INSTALLED" \
  "$LAUNCHER_SHELL" "$LAUNCHER_RC_FILE" "$LAUNCHER_ALREADY_INSTALLED" "$LAUNCHER_RUNTIMES_RAW" "$LAUNCHER_TEMPLATE_DIR" \
  "$GOVERNANCE_INSTALLED" \
  "$README_EXISTS" "$README_HAS_CODE" "$README_HAS_ARTIFACTS" "$README_ACTIVE_COUNT" \
  "$AGENTS_DIR_EXISTS"
