#!/usr/bin/env bash
# BDD tests for ADR-023: Deprecate swain-session — Split Lifecycle into Init and Teardown
# Validates the structural changes: routing, skill content, cross-references
set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
PASS=0
FAIL=0

assert() {
  local desc="$1" result="$2"
  if [ "$result" = "true" ]; then
    echo "  PASS: $desc"
    PASS=$((PASS + 1))
  else
    echo "  FAIL: $desc"
    FAIL=$((FAIL + 1))
  fi
}

assert_file_exists() {
  local desc="$1" path="$2"
  if [ -f "$path" ]; then
    echo "  PASS: $desc"
    PASS=$((PASS + 1))
  else
    echo "  FAIL: $desc (not found: $path)"
    FAIL=$((FAIL + 1))
  fi
}

assert_contains() {
  local desc="$1" file="$2" pattern="$3"
  if grep -q "$pattern" "$file" 2>/dev/null; then
    echo "  PASS: $desc"
    PASS=$((PASS + 1))
  else
    echo "  FAIL: $desc (pattern not found in $file)"
    FAIL=$((FAIL + 1))
  fi
}

assert_not_contains() {
  local desc="$1" file="$2" pattern="$3"
  if grep -q "$pattern" "$file" 2>/dev/null; then
    echo "  FAIL: $desc (pattern found in $file)"
    FAIL=$((FAIL + 1))
  else
    echo "  PASS: $desc"
    PASS=$((PASS + 1))
  fi
}

# ============================================================
echo "=== ADR-023 AC1: ADR Artifact Exists and is Active ==="
# ============================================================

ADR_FILE="$REPO_ROOT/docs/adr/Active/(ADR-030)-Deprecate-Swain-Session/(ADR-030)-Deprecate-Swain-Session.md"
assert_file_exists "ADR-023 artifact exists" "$ADR_FILE"
assert_contains "ADR-023 status is Active" "$ADR_FILE" "status: Active"
assert_contains "ADR-023 references ADR-018" "$ADR_FILE" "ADR-018"
assert_contains "ADR-023 documents feature distribution" "$ADR_FILE" "swain-roadmap"
assert_contains "ADR-023 documents migration plan" "$ADR_FILE" "## Migration"

# ============================================================
echo ""
echo "=== ADR-023 AC2: Meta-Router Removes swain-session ==="
# ============================================================

ROUTER="$REPO_ROOT/skills/swain/SKILL.md"
assert_not_contains "meta-router has no swain-session row" "$ROUTER" "| swain-session |"
assert_contains "meta-router routes status to swain-roadmap" "$ROUTER" "swain-roadmap.*status"
assert_contains "meta-router routes teardown to swain-teardown" "$ROUTER" "swain-teardown.*teardown"
assert_contains "meta-router routes session to swain-init" "$ROUTER" "swain-init.*session"
assert_contains "meta-router routes bookmark to swain-do" "$ROUTER" "swain-do.*bookmark"
assert_contains "meta-router routes done to swain-teardown" "$ROUTER" "swain-teardown.*done"

# ============================================================
echo ""
echo "=== ADR-023 AC3: swain-teardown Owns Full Shutdown ==="
# ============================================================

TEARDOWN="$REPO_ROOT/skills/swain-teardown/SKILL.md"
assert_contains "teardown version >= 3.0.0" "$TEARDOWN" "version: 3.0.0"
assert_contains "teardown Step 1 — digest" "$TEARDOWN" "## Step 1 — Session digest"
assert_contains "teardown Step 2 — retro" "$TEARDOWN" "## Step 2 — Retro"
assert_contains "teardown Step 3 — merge" "$TEARDOWN" "## Step 3 — Merge worktree branches"
assert_contains "teardown Step 4 — cleanup" "$TEARDOWN" "## Step 4 — Worktree cleanup"
assert_contains "teardown Step 5 — close session" "$TEARDOWN" "## Step 5 — Close session state"
assert_contains "teardown Step 6 — commit" "$TEARDOWN" "## Step 6 — Commit handoff"

# AC3.1: Retro fires before session close
RETRO_LINE=$(grep -n "Step 2 — Retro" "$TEARDOWN" | head -1 | cut -d: -f1)
CLOSE_LINE=$(grep -n "Step 5 — Close session" "$TEARDOWN" | head -1 | cut -d: -f1)
assert "retro (step 2) comes before close (step 5)" "$([ "$RETRO_LINE" -lt "$CLOSE_LINE" ] && echo true || echo false)"

# AC3.2: Merge step exists (was missing in old teardown)
assert_contains "teardown has merge/PR/skip options" "$TEARDOWN" "Merge.*merge branch"
assert_contains "teardown has PR option" "$TEARDOWN" "gh pr create"

# AC3.3: Worktree cleanup runs after merge
MERGE_LINE=$(grep -n "Step 3 — Merge" "$TEARDOWN" | head -1 | cut -d: -f1)
CLEANUP_LINE=$(grep -n "Step 4 — Worktree cleanup" "$TEARDOWN" | head -1 | cut -d: -f1)
assert "merge (step 3) comes before cleanup (step 4)" "$([ "$MERGE_LINE" -lt "$CLEANUP_LINE" ] && echo true || echo false)"

# AC3.4: Teardown has link-safety integration
assert_contains "teardown runs link-safety before merge" "$TEARDOWN" "detect-worktree-links"

# AC3.5: Teardown invokes swain-retro skill
assert_contains "teardown invokes swain-retro" "$TEARDOWN" 'Skill("swain-retro"'

# AC3.6: Teardown has summary report
assert_contains "teardown has summary report" "$TEARDOWN" "Session Teardown Complete"

# AC3.7: Teardown handles no-session gracefully
assert_contains "teardown offers cleanup-only mode" "$TEARDOWN" "cleanup-only"

# ============================================================
echo ""
echo "=== ADR-023 AC4: swain-init Absorbs Session Startup ==="
# ============================================================

INIT="$REPO_ROOT/skills/swain-init/SKILL.md"

# AC4.1: Phase 0 no longer delegates to swain-session
assert_not_contains "init phase 0 does not delegate to swain-session" "$INIT" "Invoke the \*\*swain-session\*\* skill"

# AC4.2: Phase 7 exists with session start features
assert_contains "init has Phase 7" "$INIT" "## Phase 7: Session Start"
assert_contains "init Phase 7 has greeting" "$INIT" "Step 7.1 — Fast greeting"
assert_contains "init Phase 7 has session state" "$INIT" "Step 7.2 — Session state init"
assert_contains "init Phase 7 has focus lane" "$INIT" "Step 7.3 — Focus lane"
assert_contains "init Phase 7 has session purpose" "$INIT" "Step 7.4 — Session purpose text"

# AC4.3: Phase 0 fast path goes to Phase 7
assert_contains "same major version skips to Phase 7" "$INIT" "Skip to \*\*Phase 7"

# AC4.4: Init description mentions session triggers
assert_contains "init description includes session trigger" "$INIT" "session"
assert_contains "init description includes focus trigger" "$INIT" "focus on"

# AC4.5: Greeting script invocation present
assert_contains "init calls greeting script" "$INIT" "swain-session-greeting.sh"

# AC4.6: Focus lane script invocation present
assert_contains "init calls focus script" "$INIT" "swain-focus.sh"

# ============================================================
echo ""
echo "=== ADR-023 AC5: swain-roadmap Absorbs Status Dashboard ==="
# ============================================================

ROADMAP="$REPO_ROOT/skills/swain-roadmap/SKILL.md"
assert_contains "roadmap version >= 2.0.0" "$ROADMAP" "version: 2.0.0"
assert_contains "roadmap description mentions status" "$ROADMAP" "status dashboard"
assert_contains "roadmap has status dashboard section" "$ROADMAP" "## Status Dashboard"
assert_contains "roadmap has mode inference" "$ROADMAP" "Mode Inference"
assert_contains "roadmap has decisions needed" "$ROADMAP" "Decisions Needed"
assert_contains "roadmap has cache section" "$ROADMAP" "### Cache"
assert_contains "roadmap mentions status triggers" "$ROADMAP" "what's next"

# ============================================================
echo ""
echo "=== ADR-023 AC6: swain-do Absorbs Bookmarks and Decisions ==="
# ============================================================

DO="$REPO_ROOT/skills/swain-do/SKILL.md"
assert_contains "swain-do version >= 4.0.0" "$DO" "version: 4.0.0"
assert_contains "swain-do has bookmark section" "$DO" "## Bookmark management"
assert_contains "swain-do has decision recording" "$DO" "## Decision recording"
assert_contains "swain-do has progress log" "$DO" "## Progress log"
assert_contains "swain-do calls bookmark script" "$DO" "swain-bookmark.sh"
assert_contains "swain-do calls session-state record-decision" "$DO" "record-decision"
assert_contains "swain-do calls progress-log script" "$DO" "swain-progress-log.sh"
assert_contains "swain-do description mentions bookmark" "$DO" "bookmark"

# ============================================================
echo ""
echo "=== ADR-023 AC7: Cross-Skill References Updated ==="
# ============================================================

# No skill should direct operators to /swain-session anymore
# (except swain-session itself and historical docs)
SKILLS_WITH_STALE_REF=0
for skill_file in "$REPO_ROOT"/skills/*/SKILL.md; do
  skill_name=$(basename "$(dirname "$skill_file")")
  # Skip swain-session itself
  [ "$skill_name" = "swain-session" ] && continue
  if grep -q 'start one with .*/swain-session' "$skill_file" 2>/dev/null; then
    echo "  FAIL: $skill_name still directs to /swain-session"
    SKILLS_WITH_STALE_REF=$((SKILLS_WITH_STALE_REF + 1))
  fi
done
assert "no skill preambles direct to /swain-session" "$([ "$SKILLS_WITH_STALE_REF" -eq 0 ] && echo true || echo false)"

# AGENTS.md updated
AGENTS="$REPO_ROOT/AGENTS.md"
assert_not_contains "AGENTS.md routing table has no swain-session" "$AGENTS" "| Project status.*swain-session"
assert_contains "AGENTS.md has swain-roadmap in routing" "$AGENTS" "swain-roadmap"
assert_contains "AGENTS.md has swain-init in routing" "$AGENTS" "swain-init"
assert_contains "AGENTS.md has swain-teardown in routing" "$AGENTS" "swain-teardown"
assert_contains "AGENTS.md session startup references /swain-init" "$AGENTS" "manually run \`/swain-init\`"

# AGENTS.content.md (canonical governance) updated
AGENTS_CONTENT="$REPO_ROOT/skills/swain-doctor/references/AGENTS.content.md"
assert_not_contains "AGENTS.content.md has no swain-session in routing" "$AGENTS_CONTENT" "| Project status.*swain-session"
assert_contains "AGENTS.content.md has swain-roadmap" "$AGENTS_CONTENT" "swain-roadmap"
assert_contains "AGENTS.content.md session startup references /swain-init" "$AGENTS_CONTENT" "manually run \`/swain-init\`"

# ============================================================
echo ""
echo "=== ADR-023 AC8: README Reconciliation Distributed ==="
# ============================================================

RETRO="$REPO_ROOT/skills/swain-retro/SKILL.md"
SYNC="$REPO_ROOT/skills/swain-sync/SKILL.md"
RELEASE="$REPO_ROOT/skills/swain-release/SKILL.md"

assert_contains "swain-retro has README drift check" "$RETRO" "README drift"
assert_contains "swain-sync has README reconciliation" "$SYNC" "README reconciliation"
assert_contains "swain-release has README gate" "$RELEASE" "README gate"

# ============================================================
echo ""
echo "=== ADR-023 AC9: Teardown Allowed Tools ==="
# ============================================================

# Teardown needs Skill tool to invoke retro, ExitWorktree for cleanup
assert_contains "teardown has Skill in allowed-tools" "$TEARDOWN" "Skill"
assert_contains "teardown has ExitWorktree in allowed-tools" "$TEARDOWN" "ExitWorktree"

# ============================================================
echo ""
echo "=== Results ==="
echo "$PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
