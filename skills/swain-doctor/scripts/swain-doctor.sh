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

# Portable path resolution — works whether installed at skills/ or .agents/skills/
_src="${BASH_SOURCE[0]}"
while [[ -L "$_src" ]]; do
  _dir="$(cd "$(dirname "$_src")" && pwd)"
  _src="$(readlink "$_src")"
  [[ "$_src" != /* ]] && _src="$_dir/$_src"
done
SCRIPT_DIR="$(cd "$(dirname "$_src")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
SKILLS_ROOT="$(dirname "$SKILL_DIR")"

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
  local canonical="$SKILL_DIR/references/AGENTS.content.md"
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
      if [[ ! -x "$SKILLS_ROOT/swain-do/bin/tk" ]]; then
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
  local tk_bin="$SKILLS_ROOT/swain-do/bin/tk"
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
# Check 15: Operator bin/ symlinks (SPEC-214, ADR-019)
# Scans skills/*/usr/bin/ manifest directories for operator-facing
# scripts and auto-repairs bin/ symlinks.
# ============================================================
check_operator_bin_symlinks() {
  local bin_dir="$REPO_ROOT/bin"
  local repaired=0
  local conflicts=()
  local repairs=()
  local manifest_count=0

  # Scan all usr/bin/ manifest directories in the skill tree
  for manifest_dir in "$REPO_ROOT"/skills/*/usr/bin; do
    [[ -d "$manifest_dir" ]] || continue
    for entry in "$manifest_dir"/*; do
      [[ -e "$entry" || -L "$entry" ]] || continue
      local cmd_name
      cmd_name="$(basename "$entry")"
      manifest_count=$((manifest_count + 1))

      # Resolve the actual script through the manifest symlink
      local script_path
      script_path="$(cd "$manifest_dir" && readlink -f "$cmd_name" 2>/dev/null || true)"
      if [[ -z "$script_path" || ! -f "$script_path" ]]; then
        # Manifest entry points to a missing script — skip
        continue
      fi

      # Compute relative path from bin/ to the script
      local rel_path
      rel_path="$(python3 -c "import os,sys; print(os.path.relpath(sys.argv[1], sys.argv[2]))" "$script_path" "$bin_dir" 2>/dev/null || echo "")"
      [[ -z "$rel_path" ]] && continue

      if [[ -L "$bin_dir/$cmd_name" ]]; then
        # Symlink exists — check if target is correct
        local current_target
        current_target="$(readlink "$bin_dir/$cmd_name")"
        if [[ "$(cd "$bin_dir" && readlink -f "$cmd_name" 2>/dev/null)" == "$script_path" ]]; then
          continue  # resolves correctly
        fi
        # Stale — replace
        ln -sf "$rel_path" "$bin_dir/$cmd_name"
        repairs+=("$cmd_name (stale, repaired)")
        repaired=$((repaired + 1))
      elif [[ -e "$bin_dir/$cmd_name" ]]; then
        # Real file — conflict, don't overwrite
        conflicts+=("$cmd_name")
      else
        # Missing — auto-repair
        mkdir -p "$bin_dir"
        ln -sf "$rel_path" "$bin_dir/$cmd_name"
        repairs+=("$cmd_name (created)")
        repaired=$((repaired + 1))
      fi
    done
  done

  if [[ "$manifest_count" -eq 0 ]]; then
    add_check "operator_bin_symlinks" "ok" "no operator scripts in usr/bin/ manifests"
    return
  fi

  local issues=()
  [[ ${#conflicts[@]} -gt 0 ]] && issues+=("${#conflicts[@]} conflict(s): ${conflicts[*]}")
  [[ ${#repairs[@]} -gt 0 ]] && issues+=("${#repairs[@]} repaired: ${repairs[*]}")

  if [[ ${#issues[@]} -eq 0 ]]; then
    add_check "operator_bin_symlinks" "ok" "bin/ symlinks for $manifest_count operator script(s) OK"
  elif [[ ${#conflicts[@]} -gt 0 ]]; then
    local detail
    detail=$(printf '%s; ' "${issues[@]}")
    add_check "operator_bin_symlinks" "warning" "bin/ symlink issues" "${detail%;* }"
  else
    local detail
    detail=$(printf '%s; ' "${issues[@]}")
    add_check "operator_bin_symlinks" "ok" "bin/ symlinks repaired" "${detail%;* }"
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
  local ssh_helper="$SCRIPT_DIR/ssh-readiness.sh"
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
# Check 18: Crash debris detection (SPEC-182)
# ============================================================
check_crash_debris() {
  local lib="$SCRIPT_DIR/crash-debris-lib.sh"
  if [[ ! -f "$lib" ]]; then
    add_check "crash_debris" "ok" "crash-debris-lib.sh not found (skipped)"
    return
  fi

  source "$lib"
  local output
  output=$(check_all_crash_debris "$REPO_ROOT" 2>/dev/null || true)

  local found_count
  found_count=$(echo "$output" | grep -c 'found' || echo "0")

  if [[ "$found_count" -eq 0 ]]; then
    add_check "crash_debris" "ok" "no crash debris detected"
    return
  fi

  local details
  details=$(echo "$output" | grep 'found' | cut -f3 | tr '\n' '; ' | sed 's/; $//')
  add_check "crash_debris" "warning" "$found_count crash debris item(s) detected" "$details"
}

# ============================================================
# Check 19: bin/swain symlink (SPEC-180, ADR-019)
# ============================================================
check_swain_symlink() {
  local symlink="$REPO_ROOT/bin/swain"
  if [[ ! -L "$symlink" ]]; then
    if [[ -f "$SKILLS_ROOT/swain/scripts/swain" ]]; then
      add_check "swain_symlink" "warning" "bin/swain symlink missing (script exists at $SKILLS_ROOT/swain/scripts/swain)"
    else
      add_check "swain_symlink" "ok" "bin/swain not applicable (no pre-runtime script)"
    fi
    return
  fi

  if [[ ! -e "$symlink" ]]; then
    add_check "swain_symlink" "warning" "bin/swain symlink broken (target missing)"
    return
  fi

  add_check "swain_symlink" "ok" "bin/swain symlink resolves"
}

# ============================================================
# Check 20: .agents/bin/ symlink completeness (SPEC-206)
# Aligns with preflight auto-repair (ADR-019, SPEC-186):
#   - Scans all executable files in skills/*/scripts/ (not just .sh)
#   - Excludes test-* and operator-facing scripts (SPEC-214 manifest-driven)
#   - Uses os.path.relpath for portable symlink targets
#   - Auto-repairs missing/stale symlinks (detect + fix)
# ============================================================
check_agents_bin_symlinks() {
  local bin_dir="$REPO_ROOT/.agents/bin"
  if [[ ! -d "$bin_dir" ]]; then
    mkdir -p "$bin_dir"
    add_check "agents_bin_symlinks" "warning" ".agents/bin/ directory was missing (created)"
    return
  fi

  local broken=()
  local missing=()
  local stale=()
  local repaired=0

  # Check for broken symlinks in .agents/bin/
  while IFS= read -r link; do
    [[ -z "$link" ]] && continue
    if [[ ! -e "$link" ]]; then
      broken+=("$(basename "$link")")
      rm -f "$link"
    fi
  done < <(find "$bin_dir" -type l 2>/dev/null)

  # Build operator-script exclusion set from usr/bin/ manifests (SPEC-214)
  local operator_scripts=" "
  for manifest_dir in "$REPO_ROOT"/skills/*/usr/bin; do
    [[ -d "$manifest_dir" ]] || continue
    for entry in "$manifest_dir"/*; do
      [[ -e "$entry" || -L "$entry" ]] || continue
      operator_scripts+="$(basename "$entry") "
    done
  done

  # Scan all executable scripts in skills/*/scripts/ (ADR-019 convention)
  for skill_scripts_dir in "$REPO_ROOT"/skills/*/scripts; do
    [[ -d "$skill_scripts_dir" ]] || continue
    for script in "$skill_scripts_dir"/*; do
      [[ -f "$script" && -x "$script" ]] || continue
      local script_name
      script_name="$(basename "$script")"
      # Skip test scripts and operator-facing scripts
      [[ "$script_name" == test-* || "$script_name" == test_* ]] && continue
      # Skip operator-facing scripts — those belong in bin/, not .agents/bin/
      echo "$operator_scripts" | grep -q " $script_name " && continue
      # Compute portable relative path (works in worktrees and trunk)
      local target="$bin_dir/$script_name"
      local rel_path
      rel_path="$(python3 -c "import os,sys; print(os.path.relpath(sys.argv[1], sys.argv[2]))" "$script" "$bin_dir" 2>/dev/null || echo "")"
      [[ -z "$rel_path" ]] && continue
      if [[ -L "$target" ]] && [[ "$(readlink "$target")" == "$rel_path" ]]; then
        continue  # ok
      elif [[ -e "$target" ]] && [[ ! -L "$target" ]]; then
        missing+=("$script_name (conflict: real file)")
      elif [[ -L "$target" ]]; then
        # stale — wrong target
        stale+=("$script_name")
        ln -sf "$rel_path" "$target"
        repaired=$((repaired + 1))
      else
        # missing — auto-repair
        missing+=("$script_name")
        ln -sf "$rel_path" "$target"
        repaired=$((repaired + 1))
      fi
    done
  done

  local issues=()
  [[ ${#broken[@]} -gt 0 ]] && issues+=("${#broken[@]} broken (removed): ${broken[*]}")
  [[ ${#stale[@]} -gt 0 ]] && issues+=("${#stale[@]} stale (repaired): ${stale[*]}")
  [[ ${#missing[@]} -gt 0 ]] && issues+=("${#missing[@]} missing (repaired): ${missing[*]}")

  if [[ ${#issues[@]} -eq 0 ]]; then
    add_check "agents_bin_symlinks" "ok" ".agents/bin/ symlinks complete"
  elif [[ $repaired -gt 0 ]]; then
    local detail
    detail=$(printf '%s; ' "${issues[@]}")
    add_check "agents_bin_symlinks" "advisory" "repaired $repaired .agents/bin/ symlink(s)" "${detail%;* }"
  else
    local detail
    detail=$(printf '%s; ' "${issues[@]}")
    add_check "agents_bin_symlinks" "warning" ".agents/bin/ symlink issues" "${detail%;* }"
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
check_operator_bin_symlinks
check_commit_signing
check_ssh_readiness
check_crash_debris
check_agents_bin_symlinks

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
