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
LEGACY_SKILLS_LIB="$SKILL_DIR/references/legacy-skills-lib.sh"

if [[ -f "$LEGACY_SKILLS_LIB" ]]; then
  # shellcheck disable=SC1090
  source "$LEGACY_SKILLS_LIB"
fi

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
# CLI flags
# ============================================================
FIX_FLAT=false
for arg in "$@"; do
  case "$arg" in
    --fix-flat-artifacts) FIX_FLAT=true ;;
  esac
done

# ============================================================
# Check 1: Governance (SPEC-222: auto-repair stale block when markers present)
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
    return
  fi

  # Stale — attempt auto-repair if both markers are present
  if grep -q '<!-- swain governance' "$gov_file" && grep -q '<!-- end swain governance' "$gov_file"; then
    # Write canonical block content to temp file (avoids awk -v newline limitation)
    local tmp_canonical
    tmp_canonical=$(mktemp)
    extract_gov "$canonical" > "$tmp_canonical"
    awk -v tmpfile="$tmp_canonical" '
      BEGIN{ while ((getline line < tmpfile) > 0) { buf = buf line "\n" } }
      /<!-- swain governance/{print; p=1; printf "%s", buf; next}
      /<!-- end swain governance/{p=0}
      !p{print}
    ' "$gov_file" > "${gov_file}.tmp" && mv -f "${gov_file}.tmp" "$gov_file"
    rm -f "$tmp_canonical"
    add_check "governance" "advisory" "governance block updated to match canonical"
  else
    add_check "governance" "warning" "governance block is stale — markers missing, cannot auto-repair" "installed=$installed_hash canonical=$canonical_hash"
  fi
}

# ============================================================
# Check 2: Legacy skill cleanup
# ============================================================
check_legacy_skills() {
  local legacy_json="$SKILL_DIR/references/legacy-skills.json"
  if [[ ! -f "$legacy_json" ]] || ! declare -F legacy_skill_entries >/dev/null 2>&1; then
    add_check "legacy_skills" "warning" "legacy skill map unavailable — cannot check stale skill directories"
    return
  fi

  local removed=()
  local skipped=()
  local kind old_name replacement base_dir skill_dir replacement_dir

  while IFS=$'\t' read -r kind old_name replacement; do
    [[ -n "$old_name" ]] || continue
    for base_dir in "$REPO_ROOT/.agents/skills" "$REPO_ROOT/.claude/skills"; do
      skill_dir="$base_dir/$old_name"
      [[ -d "$skill_dir" ]] || continue

      if [[ "$kind" == "renamed" ]]; then
        replacement_dir="$base_dir/$replacement"
        if [[ ! -d "$replacement_dir" ]]; then
          skipped+=("$skill_dir (replacement missing: $replacement)")
          continue
        fi
      fi

      if ! legacy_skill_matches_fingerprint "$skill_dir" "$legacy_json"; then
        skipped+=("$skill_dir (no swain fingerprint)")
        continue
      fi

      rm -rf "$skill_dir"
      if [[ "$kind" == "renamed" ]]; then
        removed+=("$skill_dir -> $replacement")
      else
        removed+=("$skill_dir (absorbed by $replacement)")
      fi
    done
  done < <(legacy_skill_entries "$legacy_json")

  if [[ ${#removed[@]} -eq 0 && ${#skipped[@]} -eq 0 ]]; then
    add_check "legacy_skills" "ok" "no legacy skill directories found"
    return
  fi

  local detail=""
  if [[ ${#removed[@]} -gt 0 ]]; then
    detail="removed: ${removed[*]}"
  fi
  if [[ ${#skipped[@]} -gt 0 ]]; then
    detail="${detail:+$detail; }manual review: ${skipped[*]}"
  fi

  if [[ ${#skipped[@]} -gt 0 ]]; then
    add_check "legacy_skills" "warning" "legacy skill cleanup requires manual review" "$detail"
  else
    add_check "legacy_skills" "advisory" "removed ${#removed[@]} legacy skill director$( [[ ${#removed[@]} -eq 1 ]] && echo "y" || echo "ies" )" "$detail"
  fi
}

# ============================================================
# Check 3: .agents directory
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
# Check 7: Script permissions (SPEC-222: auto-repair)
# ============================================================
check_script_permissions() {
  local bad_scripts_list
  bad_scripts_list=$(find "$SKILLS_ROOT" -type f \( -path '*/scripts/*.sh' -o -path '*/scripts/*.py' \) ! -perm -u+x 2>/dev/null || true)
  local bad_count=0
  [[ -n "$bad_scripts_list" ]] && bad_count=$(echo "$bad_scripts_list" | grep -c .)

  if [[ "$bad_count" -gt 0 ]]; then
    local repaired=0
    while IFS= read -r script; do
      [[ -z "$script" ]] && continue
      chmod +x "$script" 2>/dev/null && repaired=$((repaired + 1))
    done <<< "$bad_scripts_list"
    add_check "script_permissions" "advisory" "fixed execute permission on $repaired script(s)"
  else
    add_check "script_permissions" "ok" "all scripts executable"
  fi
}

# ============================================================
# Check 8: Memory directory (SPEC-222: auto-repair)
# ============================================================
check_memory_directory() {
  local project_slug
  project_slug=$(echo "$REPO_ROOT" | tr '/' '-')
  local memory_dir="$HOME/.claude/projects/${project_slug}/memory"

  if [[ -d "$memory_dir" ]]; then
    add_check "memory_directory" "ok" "memory directory exists"
  else
    mkdir -p "$memory_dir" 2>/dev/null
    if [[ -d "$memory_dir" ]]; then
      add_check "memory_directory" "advisory" "memory directory created at $memory_dir"
    else
      add_check "memory_directory" "warning" "memory directory missing and could not be created at $memory_dir"
    fi
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
  worktree_count=$(git worktree list --porcelain 2>/dev/null | grep -c '^worktree ') || worktree_count=0

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

  # SPEC-246: Cross-reference lockfiles with worktrees
  local lockfile_orphans=0
  local unclaimed=0
  local stale_locks=0
  local lockfile_dir="$REPO_ROOT/.agents/worktrees"
  local lockfile_script="$REPO_ROOT/.agents/bin/swain-lockfile.sh"

  if [[ -d "$lockfile_dir" ]] && [[ -f "$lockfile_script" ]]; then
    # Check lockfiles without corresponding worktrees
    for lockfile in "$lockfile_dir"/*.lock; do
      [[ -f "$lockfile" ]] || continue
      local lock_wt_path=""
      lock_wt_path=$(grep '^worktree_path=' "$lockfile" | head -1 | cut -d= -f2-)
      if [[ -n "$lock_wt_path" ]] && [[ ! -d "$lock_wt_path" ]]; then
        lockfile_orphans=$((lockfile_orphans + 1))
      fi
      # Check for stale lockfiles
      local lock_branch
      lock_branch="$(basename "$lockfile" .lock)"
      if bash "$lockfile_script" is-stale "$lock_branch" >/dev/null 2>&1; then
        stale_locks=$((stale_locks + 1))
      fi
    done

    # Check worktrees without lockfiles (non-trunk)
    local wt_in_first=1
    local wt_path=""
    while IFS= read -r line; do
      if [[ "$line" == worktree\ * ]]; then
        wt_path="${line#worktree }"
      elif [[ -z "$line" ]]; then
        if [[ $wt_in_first -eq 1 ]]; then
          wt_in_first=0
          wt_path=""
          continue
        fi
        if [[ -n "$wt_path" ]]; then
          # Check if any lockfile references this path
          local has_lock=false
          for lf in "$lockfile_dir"/*.lock; do
            [[ -f "$lf" ]] || continue
            if grep -q "worktree_path=$wt_path" "$lf" 2>/dev/null; then
              has_lock=true
              break
            fi
          done
          if [[ "$has_lock" = false ]]; then
            unclaimed=$((unclaimed + 1))
          fi
        fi
        wt_path=""
      fi
    done < <(git worktree list --porcelain 2>/dev/null; echo "")
  fi

  local total_issues=$((orphaned + stale + lockfile_orphans + unclaimed + stale_locks))
  if [[ $total_issues -gt 0 ]]; then
    local details=""
    [[ $orphaned -gt 0 ]] && details="$orphaned orphaned"
    [[ $stale -gt 0 ]] && details="${details:+$details, }$stale stale (merged)"
    [[ $lockfile_orphans -gt 0 ]] && details="${details:+$details, }$lockfile_orphans lockfile(s) without worktree"
    [[ $unclaimed -gt 0 ]] && details="${details:+$details, }$unclaimed unclaimed worktree(s)"
    [[ $stale_locks -gt 0 ]] && details="${details:+$details, }$stale_locks stale lockfile(s)"
    add_check "worktrees" "warning" "$details"
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
# Scans installed skill `usr/bin/` manifest directories for operator-facing
# scripts and auto-repairs bin/ symlinks.
# ============================================================
check_operator_bin_symlinks() {
  local bin_dir="$REPO_ROOT/bin"
  local repaired=0
  local conflicts=()
  local repairs=()
  local manifest_count=0

  # Scan all usr/bin/ manifest directories in the skill tree
  for manifest_dir in "$SKILLS_ROOT"/*/usr/bin; do
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
# Check 16: Commit signing (SPEC-222: auto-repair if signing key detectable)
# ============================================================
check_commit_signing() {
  if [[ "$(git config --local commit.gpgsign 2>/dev/null)" == "true" ]]; then
    add_check "commit_signing" "ok" "commit signing configured"
    return
  fi

  # Detect a usable signing key
  local key_found=false
  local conventional_key="$HOME/.ssh/swain_signing"
  local allowed_signers
  allowed_signers=$(git config --global gpg.ssh.allowedSignersFile 2>/dev/null || echo "")

  [[ -f "$conventional_key" ]] && key_found=true
  [[ -n "$allowed_signers" && -f "$allowed_signers" ]] && key_found=true

  if [[ "$key_found" == "true" ]]; then
    git config --local commit.gpgsign true
    git config --local gpg.format ssh
    add_check "commit_signing" "advisory" "commit signing enabled (gpgsign=true, gpg.format=ssh)"
  else
    add_check "commit_signing" "warning" "commit signing not configured (no signing key detected)"
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
    issue_count=$(echo "$ssh_output" | grep -c "ISSUE:") || issue_count=0
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
# Check 12: Artifact index staleness (SPEC-227)
# Regenerates supported list-*.md files and reports deterministic repairs.
# ============================================================
check_artifact_indexes() {
  local rebuild_script="$REPO_ROOT/.agents/bin/rebuild-index.sh"
  if [[ ! -x "$rebuild_script" ]]; then
    rebuild_script="$SKILLS_ROOT/swain-design/scripts/rebuild-index.sh"
  fi

  if [[ ! -x "$rebuild_script" ]]; then
    add_check "artifact_indexes" "warning" "rebuild-index.sh not found or not executable"
    return
  fi

  local repaired=()
  local failures=()
  local type dir_name docs_dir index_file before_exists before_hash after_hash

  for type in spec epic initiative spike adr persona runbook design vision journey train; do
    dir_name="$type"
    case "$type" in
      spike) dir_name="research" ;;
    esac

    docs_dir="$REPO_ROOT/docs/$dir_name"
    index_file="$docs_dir/list-${type}.md"
    [[ -d "$docs_dir" ]] || continue

    before_exists=false
    before_hash=""
    if [[ -f "$index_file" ]]; then
      before_exists=true
      before_hash=$(shasum -a 256 "$index_file" | awk '{print $1}')
    fi

    if ! bash "$rebuild_script" "$type" >/dev/null 2>&1; then
      failures+=("$type")
      continue
    fi

    if [[ ! -f "$index_file" ]]; then
      failures+=("$type")
      continue
    fi

    after_hash=$(shasum -a 256 "$index_file" | awk '{print $1}')
    if [[ "$before_exists" == "false" ]]; then
      repaired+=("${type} (created)")
    elif [[ "$before_hash" != "$after_hash" ]]; then
      repaired+=("${type} (updated)")
    fi
  done

  if [[ ${#failures[@]} -gt 0 ]]; then
    local detail
    detail=$(printf '%s, ' "${failures[@]}")
    if [[ ${#repaired[@]} -gt 0 ]]; then
      add_check "artifact_indexes" "warning" "artifact indexes partially repaired" "repaired: ${repaired[*]}; failed: ${detail%, }"
    else
      add_check "artifact_indexes" "warning" "artifact index rebuild failed" "${detail%, }"
    fi
    return
  fi

  if [[ ${#repaired[@]} -gt 0 ]]; then
    add_check "artifact_indexes" "advisory" "repaired ${#repaired[@]} artifact index file(s)" "${repaired[*]}"
  else
    add_check "artifact_indexes" "ok" "artifact indexes current"
  fi
}

# ============================================================
# Check 18: Crash debris detection (SPEC-182, SPEC-222: auto-repair git lock only)
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
  found_count=$(echo "$output" | grep -c 'found' 2>/dev/null) || found_count=0

  if [[ "$found_count" -eq 0 ]]; then
    add_check "crash_debris" "ok" "no crash debris detected"
    return
  fi

  # Auto-repair: remove stale .git/index.lock if found (safe regardless of other debris)
  local lock_lines other_lines lock_removed=false
  lock_lines=$(echo "$output" | grep 'found' | grep '^git_index_lock' || true)
  other_lines=$(echo "$output" | grep 'found' | grep -v '^git_index_lock' || true)

  if [[ -n "$lock_lines" ]]; then
    local git_dir="$REPO_ROOT/.git"
    if [[ -f "$git_dir" ]]; then
      git_dir=$(sed 's/^gitdir: //' "$git_dir")
      [[ "$git_dir" != /* ]] && git_dir="$REPO_ROOT/$git_dir"
    fi
    local lock_file="$git_dir/index.lock"
    if [[ -f "$lock_file" ]]; then
      rm -f "$lock_file"
      lock_removed=true
    fi
  fi

  if [[ "$lock_removed" == "true" && -z "$other_lines" ]]; then
    add_check "crash_debris" "advisory" "removed stale .git/index.lock"
    return
  fi

  if [[ "$lock_removed" == "true" ]]; then
    # Lock removed but other debris remains — warn about remaining items
    local remaining_count
    remaining_count=$(echo "$other_lines" | grep -c . 2>/dev/null) || remaining_count=0
    local details
    details=$(echo "$other_lines" | cut -f3 | tr '\n' '; ' | sed 's/; $//')
    add_check "crash_debris" "warning" "removed .git/index.lock; $remaining_count other debris item(s) remain" "$details"
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
#   - Scans all executable files in the installed skill tree (not just .sh)
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
  for manifest_dir in "$SKILLS_ROOT"/*/usr/bin; do
    [[ -d "$manifest_dir" ]] || continue
    for entry in "$manifest_dir"/*; do
      [[ -e "$entry" || -L "$entry" ]] || continue
      operator_scripts+="$(basename "$entry") "
    done
  done

  # Scan all executable scripts in the installed skill tree (ADR-019 convention)
  for skill_scripts_dir in "$SKILLS_ROOT"/*/scripts; do
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

# Check: Flat-file artifact detection (ADR-027, SPEC-225)
check_flat_artifacts() {
  local fix_mode=false
  [[ "${1:-}" == "--fix" ]] && fix_mode=true

  # Artifact directories to scan (type -> docs subdir)
  # Retros excluded — SPEC-252 handles retro renumbering + foldering separately
  local -a dirs=()
  for d in docs/spec docs/epic docs/adr docs/initiative docs/research \
           docs/vision docs/design docs/persona docs/runbook docs/journey \
           docs/train; do
    [[ -d "$d" ]] && dirs+=("$d")
  done

  if [[ ${#dirs[@]} -eq 0 ]]; then
    add_check "flat_artifacts" "ok" "no artifact directories found (skipped)"
    return
  fi

  # Find .md files in phase directories that are NOT inside a (TYPE-NNN) folder.
  # Flat files sit at: docs/<type>/<Phase>/filename.md
  # Foldered files sit at: docs/<type>/<Phase>/(TYPE-NNN)-Title/filename.md
  # Also catch flat retros: docs/swain-retro/filename.md (no phase subdir)
  local -a flat_files=()
  for d in "${dirs[@]}"; do
    while IFS= read -r f; do
      [[ -z "$f" ]] && continue
      local parent_name
      parent_name="$(basename "$(dirname "$f")")"
      # Skip index files and READMEs
      local fname
      fname="$(basename "$f")"
      [[ "$fname" == list-* ]] && continue
      [[ "$fname" == README.md ]] && continue
      # If parent dir name starts with ( it's inside a folder — skip
      [[ "$parent_name" == \(* ]] && continue
      flat_files+=("$f")
    done < <(find "$d" -maxdepth 3 -name "*.md" -not -path "*/_unparented/*" -not -path "*/_Related/*" -not -path "*/_Depends-On/*" 2>/dev/null)
  done

  if [[ ${#flat_files[@]} -eq 0 ]]; then
    add_check "flat_artifacts" "ok" "all artifacts are foldered"
    return
  fi

  if $fix_mode; then
    local migrated=0
    local failed=0
    for f in "${flat_files[@]}"; do
      # Parse artifact ID from frontmatter
      local artifact_id
      artifact_id=$(sed -n 's/^artifact: *//p' "$f" | head -1 | tr -d '[:space:]')
      if [[ -z "$artifact_id" ]]; then
        failed=$((failed + 1))
        continue
      fi

      # Derive folder name from filename convention
      local fname parent_dir folder_name target_dir target_file
      fname="$(basename "$f" .md)"
      parent_dir="$(dirname "$f")"

      # Build canonical folder name from frontmatter title
      local raw_title
      raw_title=$(sed -n 's/^title: *"\{0,1\}\(.*\)"\{0,1\}$/\1/p' "$f" | head -1 | sed 's/^ *//;s/ *$//')
      if [[ -n "$raw_title" ]]; then
        # Title-Case with hyphens: lowercase → capitalize first letter of each word → spaces to hyphens
        local title_slug
        title_slug=$(echo "$raw_title" | sed 's/[^a-zA-Z0-9 -]//g; s/  */ /g; s/ /-/g')
        folder_name="(${artifact_id})-${title_slug}"
      elif [[ "$fname" == \(* ]]; then
        # Filename already has parens — use as-is
        folder_name="$fname"
      elif [[ "$fname" == "${artifact_id}"* ]]; then
        # Filename starts with artifact ID — wrap in parens
        local title_part="${fname#"${artifact_id}"}"
        title_part="${title_part#-}"
        folder_name="(${artifact_id})-${title_part}"
      else
        # Fallback: wrap artifact ID + filename
        folder_name="(${artifact_id})-${fname}"
      fi

      target_dir="${parent_dir}/${folder_name}"
      target_file="${target_dir}/${folder_name}.md"

      if [[ -d "$target_dir" ]]; then
        failed=$((failed + 1))
        continue
      fi

      mkdir -p "$target_dir"
      git mv "$f" "$target_file" 2>/dev/null
      if [[ $? -eq 0 ]]; then
        migrated=$((migrated + 1))
      else
        # Fallback: plain move if not tracked
        mv "$f" "$target_file" 2>/dev/null && migrated=$((migrated + 1)) || failed=$((failed + 1))
      fi
    done

    if [[ $failed -gt 0 ]]; then
      add_check "flat_artifacts" "warning" "migrated $migrated, failed $failed flat-file artifact(s)"
    else
      add_check "flat_artifacts" "advisory" "migrated $migrated flat-file artifact(s) to folders"
    fi
  else
    # Report only
    local detail
    detail=$(printf '%s;' "${flat_files[@]:0:10}")
    [[ ${#flat_files[@]} -gt 10 ]] && detail="${detail}... and $((${#flat_files[@]} - 10)) more"
    add_check "flat_artifacts" "warning" "${#flat_files[@]} flat-file artifact(s) — run swain-doctor --fix-flat-artifacts to migrate" "$detail"
  fi
}

# ============================================================
# Check: Branch model (ADR-013)
# ============================================================
check_branch_model() {
  local has_trunk has_release
  has_trunk=$(git rev-parse --verify trunk >/dev/null 2>&1 && echo "yes" || echo "no")
  has_release=$(git rev-parse --verify release >/dev/null 2>&1 && echo "yes" || echo "no")

  if [[ "$has_trunk" == "yes" && "$has_release" == "yes" ]]; then
    add_check "branch_model" "ok" "trunk+release branches present"
  else
    local missing=""
    [[ "$has_trunk" == "no" ]] && missing="trunk"
    [[ "$has_release" == "no" ]] && missing="${missing:+$missing, }release"
    add_check "branch_model" "advisory" "missing branch(es): $missing — see ADR-013"
  fi
}

# ============================================================
# Check: Platform dotfolder cleanup
# ============================================================
check_platform_dotfolders() {
  if ! command -v jq >/dev/null 2>&1; then
    add_check "platform_dotfolders" "skipped" "jq not available"
    return
  fi

  local json_file="$SKILL_DIR/references/platform-dotfolders.json"
  if [[ ! -f "$json_file" ]]; then
    add_check "platform_dotfolders" "skipped" "platform-dotfolders.json not found"
    return
  fi

  local stubs=()
  while IFS= read -r entry; do
    local dotfolder cmd det found=false
    dotfolder=$(echo "$entry" | jq -r '.project_dotfolder')
    cmd=$(echo "$entry" | jq -r '.command // empty')
    det=$(echo "$entry" | jq -r '.detection // empty')

    if [[ -n "$cmd" ]] && command -v "$cmd" &>/dev/null; then
      found=true
    fi
    if [[ "$found" == "false" && -n "$det" ]]; then
      local det_expanded
      det_expanded=$(echo "$det" | sed "s|~|$HOME|g")
      det_expanded=$(eval echo "$det_expanded" 2>/dev/null || echo "")
      [[ -n "$det_expanded" && -d "$det_expanded" ]] && found=true
    fi

    # If platform not installed but dotfolder exists in project, it's a stub
    if [[ "$found" == "false" && -d "$REPO_ROOT/$dotfolder" ]]; then
      # Verify it's an installer stub (only contains skills/ or is empty)
      local entries
      entries=$(ls -A "$REPO_ROOT/$dotfolder" 2>/dev/null | wc -l | tr -d ' ')
      if [[ "$entries" -le 1 ]] && { [[ -d "$REPO_ROOT/$dotfolder/skills" ]] || [[ "$entries" -eq 0 ]]; }; then
        stubs+=("$dotfolder")
      fi
    fi
  done < <(jq -c '.platforms[]' "$json_file")

  if [[ ${#stubs[@]} -eq 0 ]]; then
    add_check "platform_dotfolders" "ok" "no orphaned platform dotfolders"
  else
    add_check "platform_dotfolders" "warning" "${#stubs[@]} orphaned platform dotfolder(s): ${stubs[*]}"
  fi
}

# ============================================================
# Check: Skill folder gitignore hygiene
# ============================================================
check_skill_gitignore() {
  # Skip if this is the swain source repo
  local remote_url
  remote_url="$(git remote get-url origin 2>/dev/null || true)"
  if [[ "$remote_url" == *"cristoslc/swain"* ]]; then
    add_check "skill_gitignore" "ok" "swain source repo — skill folders are tracked"
    return
  fi

  local missing=()
  for base in .claude/skills .agents/skills; do
    [[ -d "$base" ]] || continue
    for dir in "$base"/swain "$base"/swain-*/; do
      [[ -d "$dir" ]] || continue
      if ! git check-ignore -q "$dir" 2>/dev/null; then
        missing+=("$dir")
      fi
    done
  done

  if [[ ${#missing[@]} -eq 0 ]]; then
    add_check "skill_gitignore" "ok" "vendored swain skill folders gitignored (or none exist)"
  else
    add_check "skill_gitignore" "warning" "${#missing[@]} vendored swain skill folder(s) not gitignored: ${missing[*]}"
  fi
}

# ============================================================
# Run all checks (set +e so failures don't cascade)
# ============================================================
set +e

check_governance
check_legacy_skills
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
check_artifact_indexes
check_evidence_pools
check_worktrees
check_lifecycle_dirs
check_tk_health
check_operator_bin_symlinks
check_commit_signing
check_ssh_readiness
check_crash_debris
check_agents_bin_symlinks
check_branch_model
check_platform_dotfolders
check_skill_gitignore
if $FIX_FLAT; then
  check_flat_artifacts --fix
else
  check_flat_artifacts
fi

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
