#!/usr/bin/env bash
# swain-preflight.sh — lightweight session-start check
#
# Exit 0 = everything looks fine, skip swain-doctor
# Exit 1 = something needs attention, invoke swain-doctor
#
# This replaces the unconditional auto-invoke of swain-doctor,
# saving tokens on clean sessions. See ADR-001 / SPEC-008.

set -euo pipefail

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

issues=()

# 1. Governance files exist
if [[ ! -f AGENTS.md ]] && [[ ! -f CLAUDE.md ]]; then
  issues+=("no governance file (AGENTS.md or CLAUDE.md)")
fi

# 2. Governance markers present
if ! grep -q "swain governance" AGENTS.md CLAUDE.md 2>/dev/null; then
  issues+=("governance markers missing")
fi

# 2b. Governance freshness — compare installed block against canonical
CANONICAL="$SKILL_DIR/references/AGENTS.content.md"
if [[ -f "$CANONICAL" ]] && grep -q "swain governance" AGENTS.md CLAUDE.md 2>/dev/null; then
  GOV_FILE=$(grep -l "swain governance" AGENTS.md CLAUDE.md 2>/dev/null | head -1 || true)
  if [[ -n "$GOV_FILE" ]]; then
    # Extract content between markers (exclusive) and hash
    extract_gov() { awk '/<!-- swain governance/{f=1;next}/<!-- end swain governance/{f=0}f' "$1"; }
    INSTALLED_HASH=$(extract_gov "$GOV_FILE" | shasum -a 256 | cut -d' ' -f1)
    CANONICAL_HASH=$(extract_gov "$CANONICAL" | shasum -a 256 | cut -d' ' -f1)
    if [[ "$INSTALLED_HASH" != "$CANONICAL_HASH" ]]; then
      issues+=("governance block is stale (differs from canonical AGENTS.content.md)")
    fi
  fi
fi

# 3. .agents directory exists (ADR-020: self-heal)
if [[ ! -d .agents ]]; then
  mkdir -p .agents
  echo "advisory: created .agents/ directory"
fi

# 4. .tickets/ directory is valid (if it exists)
if [[ -d .tickets ]]; then
  for f in .tickets/*.md; do
    [[ -f "$f" ]] || continue
    if ! head -1 "$f" | grep -q '^---$'; then
      issues+=("invalid ticket frontmatter: $f")
      break
    fi
  done
fi

# 5. No stale .beads/ directory (needs auto-migration)
if [[ -d .beads ]]; then
  issues+=("stale .beads/ directory needs migration to .tickets/")
fi

# Evidence pool migration check
if [[ -d "$REPO_ROOT/docs/evidence-pools" ]]; then
  echo "preflight: docs/evidence-pools/ detected — trove migration needed"
  issues+=("docs/evidence-pools/ detected — trove migration needed")
fi

# 6. Stale tk lock files (older than 1 hour) (ADR-020: self-heal)
if [[ -d .tickets/.locks ]]; then
  _stale_lock_count=$(find .tickets/.locks -type d -mmin +60 2>/dev/null | wc -l | tr -d ' ')
  if [[ "$_stale_lock_count" -gt 0 ]]; then
    find .tickets/.locks -type d -mmin +60 -exec rm -rf {} + 2>/dev/null
    echo "advisory: removed $_stale_lock_count stale tk lock(s)"
  fi
fi

# 7. Old lifecycle phase directories (ADR-003 migration)
OLD_PHASES="Draft Planned Review Approved Testing Implemented Adopted Deprecated Archived Sunset Validated"
for dir in docs/*/; do
  [[ -d "$dir" ]] || continue
  for phase in $OLD_PHASES; do
    phase_dir="${dir}${phase}"
    if [[ -d "$phase_dir" ]]; then
      # Only flag non-empty directories (ignore .DS_Store and hidden files)
      if find "$phase_dir" -maxdepth 1 -not -name '.*' -not -name "$phase" -print -quit 2>/dev/null | grep -q .; then
        issues+=("old lifecycle directory: $phase_dir (run migrate-lifecycle-dirs.py)")
        break 2
      fi
    fi
  done
done

# 8. Commit signing configured
if [[ "$(git config --local commit.gpgsign 2>/dev/null)" != "true" ]]; then
  issues+=("commit signing not configured (run swain-keys --provision)")
fi

# 9. Script permissions (spot check) (ADR-020: self-heal)
_bad_perms=$(find .claude/skills/*/scripts/ .agents/skills/*/scripts/ skills/*/scripts/ -type f \( -name '*.sh' -o -name '*.py' \) ! -perm -u+x 2>/dev/null || true)
if [[ -n "$_bad_perms" ]]; then
  _fix_count=$(echo "$_bad_perms" | wc -l | tr -d ' ')
  echo "$_bad_perms" | xargs chmod +x
  echo "advisory: fixed executable permissions on $_fix_count script(s)"
fi

# 9b. SSH alias readiness for repos using swain-keys host aliases
SSH_HELPER="$SCRIPT_DIR/ssh-readiness.sh"
if [[ -x "$SSH_HELPER" ]]; then
  ssh_output="$(bash "$SSH_HELPER" --check 2>/dev/null || true)"
  if [[ -n "$ssh_output" ]]; then
    while IFS= read -r line; do
      [[ -z "$line" ]] && continue
      issues+=("${line#ISSUE: }")
    done <<< "$ssh_output"
  fi
fi

# 9c. Skill folder gitignore hygiene (advisory — non-blocking)
# Only check vendored swain skill directories (swain/ and swain-*/), not all skills.
# Skip if this is the swain source repo (skill folders are tracked there).
_origin_url="$(git remote get-url origin 2>/dev/null || true)"
if [[ "$_origin_url" != *"cristoslc/swain"* ]]; then
  for _base in .claude/skills .agents/skills; do
    [ -d "$_base" ] || continue
    for _skill_path in "$_base"/swain "$_base"/swain-*/; do
      if [[ -d "$_skill_path" ]] && ! git check-ignore -q "$_skill_path" 2>/dev/null; then
        echo "swain-preflight: $REPO_ROOT/$_skill_path not gitignored (advisory)"
      fi
    done
  done
fi

# 10. Superpowers detection (advisory — warn but don't fail)
SUPERPOWERS_SKILLS="brainstorming writing-plans test-driven-development verification-before-completion subagent-driven-development executing-plans"
sp_missing=0
for skill in $SUPERPOWERS_SKILLS; do
  if ! ls .agents/skills/$skill/SKILL.md .claude/skills/$skill/SKILL.md 2>/dev/null | head -1 | grep -q .; then
    sp_missing=$((sp_missing + 1))
  fi
done
if [[ $sp_missing -gt 0 ]]; then
  echo "swain-preflight: superpowers: $sp_missing/6 skills missing (advisory)"
fi

# 11. Security scanner availability (INFO — advisory, non-blocking) (SPEC-059)
SCANNER_SCRIPT="$SKILLS_ROOT/swain-security-check/scripts/scanner_availability.py"
if [[ -x "$SCANNER_SCRIPT" ]]; then
  scanner_output=$(python3 "$SCANNER_SCRIPT" 2>/dev/null || true)
  # Extract the summary line (first line: "Scanner availability: N/4 scanners found")
  scanner_summary=$(echo "$scanner_output" | head -1)
  if [[ -n "$scanner_summary" ]] && ! echo "$scanner_summary" | grep -q "4/4"; then
    echo "swain-preflight: $scanner_summary (advisory)"
    # Print missing scanner details
    echo "$scanner_output" | grep '^\s*\[--\]' | while read -r line; do
      echo "  $line"
    done
  fi
fi

# Check mmdc availability (SPEC-110)
if ! command -v mmdc >/dev/null 2>&1; then
    echo "swain-preflight: mmdc (mermaid-cli) not found — quadrant chart will use inline Mermaid instead of PNG"
fi

# 12. Lightweight security diagnostic (advisory, non-blocking) (SPEC-061)
DOCTOR_SECURITY_SCRIPT="$SKILLS_ROOT/swain-security-check/scripts/doctor_security_check.py"
if [[ -x "$DOCTOR_SECURITY_SCRIPT" ]]; then
  security_output=$(python3 "$DOCTOR_SECURITY_SCRIPT" 2>/dev/null || true)
  if [[ -n "$security_output" ]]; then
    echo "$security_output"
  fi
fi

# 13. Skill change discipline (SPEC-148) — advisory, triggers doctor
SKILL_CHECK_SCRIPT="$SCRIPT_DIR/check-skill-changes.sh"
if [[ -x "$SKILL_CHECK_SCRIPT" ]]; then
  skill_output=$(bash "$SKILL_CHECK_SCRIPT" 2>/dev/null || true)
  skill_status=$?
  if [[ $skill_status -ne 0 && -n "$skill_output" ]]; then
    echo "$skill_output"
    issues+=("non-trivial skill changes detected on trunk (use worktree branches)")
  fi
fi

# Auto-repair .agents/bin/ symlinks (ADR-019, SPEC-186)
# Agent-facing scripts live in skills/*/scripts/ and are symlinked to .agents/bin/
AGENTS_BIN="$REPO_ROOT/.agents/bin"
OPERATOR_SCRIPTS="swain swain-box"  # operator-facing — skip for .agents/bin/
_agents_bin_repaired=0
for skill_scripts_dir in "$REPO_ROOT"/skills/*/scripts; do
  [[ -d "$skill_scripts_dir" ]] || continue
  for script in "$skill_scripts_dir"/*; do
    [[ -f "$script" && -x "$script" ]] || continue
    script_name="$(basename "$script")"
    # Skip test scripts and operator-facing scripts
    [[ "$script_name" == test-* ]] && continue
    echo " $OPERATOR_SCRIPTS " | grep -q " $script_name " && continue
    # Check .agents/bin/ symlink
    target="$AGENTS_BIN/$script_name"
    rel_path="$(python3 -c "import os,sys; print(os.path.relpath(sys.argv[1], sys.argv[2]))" "$script" "$AGENTS_BIN" 2>/dev/null || echo "")"
    if [[ -L "$target" ]] && [[ "$(readlink "$target")" == "$rel_path" ]]; then
      continue  # ok
    elif [[ -e "$target" ]] && [[ ! -L "$target" ]]; then
      issues+=(".agents/bin/$script_name is a real file, not a symlink — manual fix needed")
    else
      # missing or stale — auto-repair
      mkdir -p "$AGENTS_BIN"
      ln -sf "$rel_path" "$target"
      _agents_bin_repaired=$((_agents_bin_repaired + 1))
    fi
  done
done
if [[ $_agents_bin_repaired -gt 0 ]]; then
  echo "advisory: repaired $_agents_bin_repaired .agents/bin/ symlink(s) (ADR-019)"
fi

# Auto-repair bin/ symlinks for operator-facing scripts (ADR-019, SPEC-188)
BIN_DIR="$REPO_ROOT/bin"
_bin_repaired=0
for op_script in $OPERATOR_SCRIPTS; do
  # Find canonical location in skill tree
  canonical="$(find "$REPO_ROOT/skills" -name "$op_script" -path '*/scripts/*' ! -name 'test-*' -print -quit 2>/dev/null)"
  [[ -n "$canonical" && -x "$canonical" ]] || continue
  target="$BIN_DIR/$op_script"
  rel_path="$(python3 -c "import os,sys; print(os.path.relpath(sys.argv[1], sys.argv[2]))" "$canonical" "$BIN_DIR" 2>/dev/null || echo "")"
  if [[ -L "$target" ]] && [[ "$(readlink "$target")" == "$rel_path" ]]; then
    continue  # ok
  elif [[ -e "$target" ]] && [[ ! -L "$target" ]]; then
    issues+=("bin/$op_script is a real file, not a symlink — manual fix needed")
  else
    # missing or stale — auto-repair
    mkdir -p "$BIN_DIR"
    ln -sf "$rel_path" "$target"
    _bin_repaired=$((_bin_repaired + 1))
  fi
  # Migrate old root symlink if present
  if [[ -L "$REPO_ROOT/$op_script" ]]; then
    rm -f "$REPO_ROOT/$op_script"
    echo "advisory: migrated ./$op_script to bin/$op_script (ADR-019)"
  fi
done
if [[ $_bin_repaired -gt 0 ]]; then
  echo "advisory: repaired $_bin_repaired bin/ symlink(s) (ADR-019)"
fi

# Trunk/release branch model detection (EPIC-029, ADR-013, ADR-019)
# Check that .agents/bin/swain-trunk.sh exists and the detected trunk branch has a remote
TRUNK_SCRIPT="$REPO_ROOT/.agents/bin/swain-trunk.sh"
if [[ ! -x "$TRUNK_SCRIPT" ]]; then
  issues+=(".agents/bin/swain-trunk.sh missing or not executable — no agent-facing scripts found in skill tree")
else
  DETECTED_TRUNK=$(bash "$TRUNK_SCRIPT" 2>/dev/null || echo "")
  if [[ -z "$DETECTED_TRUNK" ]]; then
    issues+=("swain-trunk.sh returned empty — cannot detect trunk branch")
  elif ! git ls-remote --heads origin "$DETECTED_TRUNK" 2>/dev/null | grep -q "$DETECTED_TRUNK"; then
    echo "advisory: trunk branch '$DETECTED_TRUNK' has no remote counterpart on origin"
  fi
  # Check if release branch exists (ADR-013 trunk+release model)
  if ! git rev-parse --verify release 2>/dev/null >/dev/null; then
    echo "advisory: no 'release' branch found — trunk+release model (ADR-013) not configured"
    echo "  run: bash scripts/migrate-to-trunk-release.sh --dry-run"
  fi
fi

# Check for epics without parent-initiative (initiative migration advisory)
EPICS_WITHOUT_INITIATIVE=0
while IFS= read -r -d '' f; do
  if grep -q '^parent-vision:' "$f" 2>/dev/null && ! grep -q '^parent-initiative:' "$f" 2>/dev/null; then
    EPICS_WITHOUT_INITIATIVE=$((EPICS_WITHOUT_INITIATIVE + 1))
  fi
done < <(find docs/epic -name '*.md' -not -name 'README.md' -not -name 'list-*.md' -print0 2>/dev/null)
if [[ "$EPICS_WITHOUT_INITIATIVE" -gt 0 ]]; then
  echo "advisory: $EPICS_WITHOUT_INITIATIVE epic(s) without parent-initiative — run initiative migration"
fi

# Report
if [[ ${#issues[@]} -eq 0 ]]; then
  exit 0
else
  echo "swain-preflight: ${#issues[@]} issue(s) found:"
  for issue in "${issues[@]}"; do
    echo "  - $issue"
  done
  exit 1
fi
