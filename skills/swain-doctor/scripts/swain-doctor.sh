#!/usr/bin/env bash
# swain-doctor.sh — consolidated health check script (SPEC-192)
#
# Runs all swain-doctor checks in a single process with set +e,
# eliminating the parallel tool-call cascade failure where one
# erroring check cancels all sibling checks.
#
# Output: JSON object with { checks: [...], summary: {...} }
# Exit: always 0 — findings are reported in the JSON, not the exit code.

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$REPO_ROOT"

# Collect results
declare -a CHECKS=()

add_check() {
  local name="$1"
  local status="$2"
  local message="${3:-}"
  local detail="${4:-}"
  local entry="{\"name\":\"$name\",\"status\":\"$status\""
  if [[ -n "$message" ]]; then
    # Escape quotes and newlines in message
    message=$(echo "$message" | sed 's/"/\\"/g' | tr '\n' ' ')
    entry="$entry,\"message\":\"$message\""
  fi
  if [[ -n "$detail" ]]; then
    detail=$(echo "$detail" | sed 's/"/\\"/g' | tr '\n' ' ')
    entry="$entry,\"detail\":\"$detail\""
  fi
  entry="$entry}"
  CHECKS+=("$entry")
}

# ============================================================
# Check 1: Governance
# ============================================================
check_governance() {
  local gov_files
  gov_files=$(grep -l "swain governance" CLAUDE.md AGENTS.md .cursor/rules/swain-governance.mdc 2>/dev/null || true)

  if [[ -z "$gov_files" ]]; then
    add_check "governance" "warning" "governance markers not found in any context file"
    return
  fi

  # Freshness check
  local canonical="skills/swain-doctor/references/AGENTS.content.md"
  if [[ ! -f "$canonical" ]]; then
    add_check "governance" "ok" "governance markers present (canonical source not found for freshness check)"
    return
  fi

  local gov_file
  gov_file=$(echo "$gov_files" | head -1)
  extract_gov() { awk '/<!-- swain governance/{f=1;next}/<!-- end swain governance/{f=0}f' "$1"; }
  local installed_hash canonical_hash
  installed_hash=$(extract_gov "$gov_file" | shasum -a 256 | cut -d' ' -f1)
  canonical_hash=$(extract_gov "$canonical" | shasum -a 256 | cut -d' ' -f1)

  if [[ "$installed_hash" == "$canonical_hash" ]]; then
    add_check "governance" "ok" "governance current"
  else
    add_check "governance" "warning" "governance block is stale (differs from canonical)" "installed=$installed_hash canonical=$canonical_hash"
  fi
}

# ============================================================
# Check 2: .agents directory
# ============================================================
check_agents_directory() {
  if [[ -d .agents ]]; then
    add_check "agents_directory" "ok" ".agents directory exists"
  else
    add_check "agents_directory" "warning" ".agents directory missing"
  fi
}

# ============================================================
# Check 3: Tickets validation
# ============================================================
check_tickets() {
  if [[ ! -d .tickets ]]; then
    add_check "tickets" "ok" "no .tickets directory (skipped)"
    return
  fi

  local invalid=0
  for f in .tickets/*.md; do
    [[ -f "$f" ]] || continue
    if ! head -1 "$f" | grep -q '^---$'; then
      invalid=$((invalid + 1))
    fi
  done

  # Check stale locks
  local stale_locks=""
  if [[ -d .tickets/.locks ]]; then
    stale_locks=$(find .tickets/.locks -type f -mmin +60 2>/dev/null | head -5 || true)
  fi

  if [[ $invalid -gt 0 && -n "$stale_locks" ]]; then
    add_check "tickets" "warning" "$invalid invalid ticket(s), stale lock files found"
  elif [[ $invalid -gt 0 ]]; then
    add_check "tickets" "warning" "$invalid ticket(s) with invalid YAML frontmatter"
  elif [[ -n "$stale_locks" ]]; then
    add_check "tickets" "warning" "stale lock files in .tickets/.locks/"
  else
    add_check "tickets" "ok" ".tickets valid"
  fi
}

# ============================================================
# Check 4: Stale .beads/ migration
# ============================================================
check_beads() {
  if [[ -d .beads ]]; then
    add_check "beads_migration" "warning" "stale .beads/ directory needs migration to .tickets/"
  else
    add_check "beads_migration" "ok" "no stale .beads/ (skipped)"
  fi
}

# ============================================================
# Check 5: Tool availability
# ============================================================
check_tools() {
  local missing_required=""
  local missing_optional=""

  # Required
  for cmd in git jq; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
      missing_required="${missing_required:+$missing_required, }$cmd"
    fi
  done

  # Optional
  for cmd in tk uv gh tmux fswatch; do
    if [[ "$cmd" == "tk" ]]; then
      if [[ ! -x "skills/swain-do/bin/tk" ]]; then
        missing_optional="${missing_optional:+$missing_optional, }tk"
      fi
    else
      if ! command -v "$cmd" >/dev/null 2>&1; then
        missing_optional="${missing_optional:+$missing_optional, }$cmd"
      fi
    fi
  done

  if [[ -n "$missing_required" ]]; then
    add_check "tools" "warning" "required tools missing: $missing_required" "optional missing: ${missing_optional:-none}"
  elif [[ -n "$missing_optional" ]]; then
    add_check "tools" "ok" "all required tools present" "optional missing: $missing_optional"
  else
    add_check "tools" "ok" "all tools present"
  fi
}

# ============================================================
# Check 6: Settings validation
# ============================================================
check_settings() {
  local issues=""

  if [[ ! -f swain.settings.json ]]; then
    issues="swain.settings.json missing"
  elif command -v jq >/dev/null 2>&1 && ! jq empty swain.settings.json 2>/dev/null; then
    issues="swain.settings.json contains invalid JSON"
  fi

  local user_settings="${XDG_CONFIG_HOME:-$HOME/.config}/swain/settings.json"
  if [[ -f "$user_settings" ]] && command -v jq >/dev/null 2>&1 && ! jq empty "$user_settings" 2>/dev/null; then
    issues="${issues:+$issues; }user settings.json contains invalid JSON"
  fi

  if [[ -n "$issues" ]]; then
    add_check "settings" "warning" "$issues"
  else
    add_check "settings" "ok" "settings valid"
  fi
}

# ============================================================
# Check 7: Script permissions
# ============================================================
check_script_permissions() {
  local bad_scripts
  bad_scripts=$(find skills/*/scripts/ -type f \( -name '*.sh' -o -name '*.py' \) ! -perm -u+x 2>/dev/null | wc -l | tr -d ' ')

  if [[ "$bad_scripts" -gt 0 ]]; then
    add_check "script_permissions" "warning" "$bad_scripts script(s) missing executable permission"
  else
    add_check "script_permissions" "ok" "all scripts executable"
  fi
}

# ============================================================
# Check 8: Memory directory
# ============================================================
check_memory_directory() {
  local project_slug
  project_slug=$(echo "$REPO_ROOT" | tr '/' '-')
  local memory_dir="$HOME/.claude/projects/${project_slug}/memory"

  if [[ -d "$memory_dir" ]]; then
    add_check "memory_directory" "ok" "memory directory exists"
  else
    add_check "memory_directory" "warning" "memory directory missing at $memory_dir"
  fi
}

# ============================================================
# Check 9: Superpowers detection
# ============================================================
check_superpowers() {
  local found=0
  local missing=0
  local missing_names=""
  for skill in brainstorming writing-plans test-driven-development verification-before-completion subagent-driven-development executing-plans; do
    if [[ -f ".agents/skills/$skill/SKILL.md" ]] || [[ -f ".claude/skills/$skill/SKILL.md" ]]; then
      found=$((found + 1))
    else
      missing=$((missing + 1))
      missing_names="${missing_names:+$missing_names, }$skill"
    fi
  done

  if [[ $missing -eq 0 ]]; then
    add_check "superpowers" "ok" "$found/6 skills detected"
  elif [[ $found -eq 0 ]]; then
    add_check "superpowers" "warning" "superpowers not installed (0/6)" "$missing_names"
  else
    add_check "superpowers" "warning" "partial install ($found/6)" "missing: $missing_names"
  fi
}

# ============================================================
# Check 10: Epics without parent-initiative
# ============================================================
check_epics_initiative() {
  local count=0
  while IFS= read -r -d '' f; do
    if grep -q '^parent-vision:' "$f" 2>/dev/null && ! grep -q '^parent-initiative:' "$f" 2>/dev/null; then
      count=$((count + 1))
    fi
  done < <(find docs/epic -name '*.md' -not -name 'README.md' -not -name 'list-*.md' -print0 2>/dev/null)

  if [[ $count -gt 0 ]]; then
    add_check "epics_initiative" "advisory" "$count epic(s) without parent-initiative"
  else
    add_check "epics_initiative" "ok" "all epics have parent-initiative or no epics exist"
  fi
}

# ============================================================
# Check 11: Evidence pool / trove migration
# ============================================================
check_evidence_pools() {
  if [[ -d docs/evidence-pools ]]; then
    add_check "evidence_pools" "warning" "docs/evidence-pools/ exists — trove migration needed"
  elif [[ -d docs/troves ]]; then
    add_check "evidence_pools" "ok" "troves found"
  else
    add_check "evidence_pools" "ok" "no evidence pools or troves (skipped)"
  fi
}

# ============================================================
# Check 12: Stale worktree detection
# ============================================================
check_worktrees() {
  local worktree_count
  worktree_count=$(git worktree list --porcelain 2>/dev/null | grep -c '^worktree ' || echo "0")

  if [[ "$worktree_count" -le 1 ]]; then
    add_check "worktrees" "ok" "no linked worktrees"
    return
  fi

  local stale=0
  local orphaned=0
  # Parse linked worktrees (skip main — first entry)
  local in_first=1
  local path="" branch=""
  while IFS= read -r line; do
    if [[ "$line" == worktree\ * ]]; then
      path="${line#worktree }"
    elif [[ "$line" == branch\ * ]]; then
      branch="${line#branch }"
    elif [[ -z "$line" ]]; then
      if [[ $in_first -eq 1 ]]; then
        in_first=0
        path=""
        branch=""
        continue
      fi
      if [[ -n "$path" ]]; then
        if [[ ! -d "$path" ]]; then
          orphaned=$((orphaned + 1))
        elif [[ -n "$branch" ]] && git merge-base --is-ancestor "$branch" HEAD 2>/dev/null; then
          stale=$((stale + 1))
        fi
      fi
      path=""
      branch=""
    fi
  done < <(git worktree list --porcelain 2>/dev/null; echo "")

  if [[ $orphaned -gt 0 || $stale -gt 0 ]]; then
    add_check "worktrees" "warning" "$orphaned orphaned, $stale stale (merged) worktree(s)"
  else
    add_check "worktrees" "ok" "$((worktree_count - 1)) linked worktree(s), all active"
  fi
}

# ============================================================
# Check 13: Lifecycle directory migration
# ============================================================
check_lifecycle_dirs() {
  local old_phases="Draft Planned Review Approved Testing Implemented Adopted Deprecated Archived Sunset Validated"
  local found=0

  for dir in docs/*/; do
    [[ -d "$dir" ]] || continue
    for phase in $old_phases; do
      local phase_dir="${dir}${phase}"
      if [[ -d "$phase_dir" ]]; then
        if find "$phase_dir" -maxdepth 1 -not -name '.*' -not -name "$(basename "$phase_dir")" -print -quit 2>/dev/null | grep -q .; then
          found=$((found + 1))
        fi
      fi
    done
  done

  if [[ $found -gt 0 ]]; then
    add_check "lifecycle_dirs" "warning" "$found old lifecycle directory(ies) found — run migrate-lifecycle-dirs.py"
  else
    add_check "lifecycle_dirs" "ok" "no old lifecycle directories"
  fi
}

# ============================================================
# Check 14: tk health
# ============================================================
check_tk_health() {
  local tk_bin="skills/swain-do/bin/tk"
  if [[ ! -x "$tk_bin" ]]; then
    add_check "tk_health" "warning" "vendored tk not found or not executable"
    return
  fi

  if [[ ! -d .tickets ]]; then
    add_check "tk_health" "ok" "tk available, no .tickets/ (skipped)"
    return
  fi

  add_check "tk_health" "ok" "tk available and .tickets/ present"
}

# ============================================================
# Check 15: swain-box symlink (ADR-019)
# ============================================================
check_swain_box() {
  local swain_box_src
  swain_box_src=$(find skills -name "swain-box" -path '*/scripts/*' ! -name 'test-*' -print -quit 2>/dev/null)

  if [[ -z "$swain_box_src" ]]; then
    add_check "swain_box" "ok" "swain-box script not found (skipped)"
    return
  fi

  if [[ -L "bin/swain-box" ]]; then
    add_check "swain_box" "ok" "bin/swain-box symlink present"
  elif [[ -e "bin/swain-box" ]]; then
    add_check "swain_box" "warning" "bin/swain-box is a real file, not a symlink"
  else
    add_check "swain_box" "warning" "bin/swain-box symlink missing"
  fi
}

# ============================================================
# Check 16: Commit signing
# ============================================================
check_commit_signing() {
  if [[ "$(git config --local commit.gpgsign 2>/dev/null)" == "true" ]]; then
    add_check "commit_signing" "ok" "commit signing configured"
  else
    add_check "commit_signing" "warning" "commit signing not configured"
  fi
}

# ============================================================
# Check 17: SSH alias readiness
# ============================================================
check_ssh_readiness() {
  local ssh_helper="skills/swain-doctor/scripts/ssh-readiness.sh"
  if [[ ! -x "$ssh_helper" ]]; then
    add_check "ssh_readiness" "ok" "ssh-readiness helper not found (skipped)"
    return
  fi

  local ssh_output
  ssh_output=$(bash "$ssh_helper" --check 2>/dev/null || true)
  if [[ -n "$ssh_output" ]]; then
    local issue_count
    issue_count=$(echo "$ssh_output" | grep -c "ISSUE:" || echo "0")
    add_check "ssh_readiness" "warning" "$issue_count SSH readiness issue(s)" "$ssh_output"
  else
    add_check "ssh_readiness" "ok" "SSH alias readiness OK"
  fi
}

# ============================================================
# Check: README existence (SPEC-208)
# ============================================================
check_readme() {
  if [[ -f "README.md" ]]; then
    add_check "readme" "ok" "README.md exists"
  else
    add_check "readme" "warning" "README.md missing — swain alignment loop has no public intent anchor"
  fi
}

# ============================================================
# Run all checks (set +e so failures don't cascade)
# ============================================================
set +e

check_governance
check_agents_directory
check_tickets
check_beads
check_tools
check_settings
check_script_permissions
check_memory_directory
check_superpowers
check_epics_initiative
check_readme
check_evidence_pools
check_worktrees
check_lifecycle_dirs
check_tk_health
check_swain_box
check_commit_signing
check_ssh_readiness

set -e

# ============================================================
# Build JSON output
# ============================================================
total=${#CHECKS[@]}
ok_count=0
warning_count=0
advisory_count=0

for check in "${CHECKS[@]}"; do
  status=$(echo "$check" | sed -n 's/.*"status":"\([^"]*\)".*/\1/p')
  case "$status" in
    ok) ok_count=$((ok_count + 1)) ;;
    warning) warning_count=$((warning_count + 1)) ;;
    advisory) advisory_count=$((advisory_count + 1)) ;;
  esac
done

# Assemble JSON
checks_json=""
for i in "${!CHECKS[@]}"; do
  if [[ $i -gt 0 ]]; then
    checks_json="$checks_json,"
  fi
  checks_json="$checks_json${CHECKS[$i]}"
done

cat <<ENDJSON
{"checks":[$checks_json],"summary":{"total":$total,"ok":$ok_count,"warning":$warning_count,"advisory":$advisory_count}}
ENDJSON

exit 0
