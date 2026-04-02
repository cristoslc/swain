#!/usr/bin/env bash
# swain-preflight-timing.sh — SPIKE-001: Detailed preflight timing breakdown
set +e

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$REPO_ROOT"

# Portable path resolution — works whether installed at skills/ or .agents/skills/
_src="${BASH_SOURCE[0]}"
while [[ -L "$_src" ]]; do
  _dir="$(cd "$(dirname "$_src")" && pwd)"
  _src="$(readlink "$_src")"
  [[ "$_src" != /* ]] && _src="$_dir/$_src"
done
_TIMING_SCRIPT_DIR="$(cd "$(dirname "$_src")" && pwd)"
_TIMING_SKILLS_ROOT="$(dirname "$(dirname "$_TIMING_SCRIPT_DIR")")"

if command -v gdate &>/dev/null; then
  _ts() { gdate +%s%3N; }
else
  _ts() { python3 -c "import time; print(int(time.time()*1000))"; }
fi

time_check() {
  local name="$1"
  shift
  local start=$(_ts)
  eval "$@" >/dev/null 2>&1
  local end=$(_ts)
  printf "  %-45s %6d ms\n" "$name" "$((end - start))"
}

echo "=== Preflight Timing Breakdown ==="

time_check "governance_files_exist" '[[ -f AGENTS.md ]] || [[ -f CLAUDE.md ]]'
time_check "governance_markers" 'grep -q "swain governance" AGENTS.md CLAUDE.md 2>/dev/null'

time_check "governance_freshness_hash" '
  GOV_FILE=$(grep -l "swain governance" AGENTS.md CLAUDE.md 2>/dev/null | head -1)
  awk "/<!-- swain governance/{f=1;next}/<!-- end swain governance/{f=0}f" "$GOV_FILE" | shasum -a 256
  awk "/<!-- swain governance/{f=1;next}/<!-- end swain governance/{f=0}f" "'"$_TIMING_SKILLS_ROOT"'/swain-doctor/references/AGENTS.content.md" | shasum -a 256
'

time_check "agents_dir_check" '[[ -d .agents ]]'
time_check "tickets_dir_check" 'for f in .tickets/*.md; do [[ -f "$f" ]] && head -1 "$f" | grep -q "^---$"; break; done'
time_check "beads_dir_check" '[[ -d .beads ]]'
time_check "evidence_pool_check" '[[ -d docs/evidence-pools ]]'
time_check "stale_locks" 'find .tickets/.locks -type d -mmin +60 2>/dev/null | wc -l'
time_check "old_phase_dirs" 'find docs/*/Draft docs/*/Planned docs/*/Review 2>/dev/null | head -1'
time_check "commit_signing_check" 'git config --local commit.gpgsign'

time_check "script_permissions" "find '$_TIMING_SKILLS_ROOT' -type f \( -path '*/scripts/*.sh' -o -path '*/scripts/*.py' \) ! -perm -u+x 2>/dev/null"

time_check "ssh_readiness" "bash '$_TIMING_SKILLS_ROOT/swain-doctor/scripts/ssh-readiness.sh' --check 2>/dev/null"
time_check "skill_gitignore_hygiene" '
  _origin_url="$(git remote get-url origin 2>/dev/null || true)"
  for _base in .claude/skills .agents/skills; do
    [ -d "$_base" ] || continue
    for _skill_path in "$_base"/swain "$_base"/swain-*/; do
      [[ -d "$_skill_path" ]] && git check-ignore -q "$_skill_path" 2>/dev/null
    done
  done
'

time_check "superpowers_detection" '
  for skill in brainstorming writing-plans test-driven-development verification-before-completion subagent-driven-development executing-plans; do
    ls .agents/skills/$skill/SKILL.md .claude/skills/$skill/SKILL.md 2>/dev/null | head -1
  done
'

time_check "scanner_availability" "python3 '$_TIMING_SKILLS_ROOT/swain-security-check/scripts/scanner_availability.py' 2>/dev/null"
time_check "mmdc_check" 'command -v mmdc'
time_check "doctor_security_check" "python3 '$_TIMING_SKILLS_ROOT/swain-security-check/scripts/doctor_security_check.py' 2>/dev/null"
time_check "skill_change_discipline" "bash '$_TIMING_SKILLS_ROOT/swain-doctor/scripts/check-skill-changes.sh' 2>/dev/null"

time_check "agents_bin_symlink_repair" "
  for skill_scripts_dir in '$_TIMING_SKILLS_ROOT'/*/scripts; do
    [[ -d \"\$skill_scripts_dir\" ]] || continue
    for script in \"\$skill_scripts_dir\"/*; do
      [[ -f \"\$script\" && -x \"\$script\" ]] || continue
    done
  done
"

time_check "trunk_release_detection" 'bash .agents/bin/swain-trunk.sh 2>/dev/null && git ls-remote --heads origin trunk 2>/dev/null'

time_check "initiative_migration_check" 'find docs/epic -name "*.md" -not -name "README.md" -not -name "list-*.md" 2>/dev/null | while read f; do grep -q "parent-initiative:" "$f" 2>/dev/null; done'
