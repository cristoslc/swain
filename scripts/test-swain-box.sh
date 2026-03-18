#!/bin/sh
# test-swain-box.sh — Shell test suite for swain-box (SPEC-067, all 12 ACs)
# Usage: bash scripts/test-swain-box.sh
set -eu

PASS=0
FAIL=0

check() {
    if [ "$1" = "$2" ]; then
        echo "PASS: $3"
        PASS=$((PASS + 1))
    else
        echo "FAIL: $3 (got: '$1', want: '$2')"
        FAIL=$((FAIL + 1))
    fi
}

# Resolve the worktree root (directory containing this script's parent)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKTREE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SWAIN_BOX="$WORKTREE_ROOT/skills/swain/scripts/swain-box"
CLAUDE_SANDBOX="$WORKTREE_ROOT/scripts/claude-sandbox"

# Temp dir for fake binaries and test logs
FAKE_BIN="$(mktemp -d)"
DOCKER_LOG="$FAKE_BIN/docker-calls.log"

cleanup() {
    rm -rf "$FAKE_BIN"
}
trap cleanup EXIT

# ---------------------------------------------------------------------------
# Helper: write a fake docker binary to FAKE_BIN
# ---------------------------------------------------------------------------

write_docker_full() {
    # A fully functional fake docker: logs all calls, passes sandbox --help check
    cat > "$FAKE_BIN/docker" <<'DOCKER_SCRIPT'
#!/bin/sh
echo "$@" >> "$DOCKER_LOG"
if [ "${1:-}" = "sandbox" ] && [ "${2:-}" = "--help" ]; then
    exit 0
fi
exit 0
DOCKER_SCRIPT
    # Substitute $DOCKER_LOG at write time (the heredoc uses single quotes so we patch it)
    sed -i.bak "s|\\\$DOCKER_LOG|$DOCKER_LOG|g" "$FAKE_BIN/docker"
    rm -f "$FAKE_BIN/docker.bak"
    chmod +x "$FAKE_BIN/docker"
}

write_docker_no_sandbox() {
    # docker exists but sandbox --help fails (simulates Docker Desktop < 4.58)
    cat > "$FAKE_BIN/docker" <<'DOCKER_SCRIPT'
#!/bin/sh
echo "$@" >> "$DOCKER_LOG"
if [ "${1:-}" = "sandbox" ] && [ "${2:-}" = "--help" ]; then
    exit 1
fi
exit 0
DOCKER_SCRIPT
    sed -i.bak "s|\\\$DOCKER_LOG|$DOCKER_LOG|g" "$FAKE_BIN/docker"
    rm -f "$FAKE_BIN/docker.bak"
    chmod +x "$FAKE_BIN/docker"
}

reset_log() {
    rm -f "$DOCKER_LOG"
}

# ---------------------------------------------------------------------------
# AC-1: docker missing — exit non-zero when docker is not on PATH
# ---------------------------------------------------------------------------
echo ""
echo "--- AC-1: docker missing ---"
reset_log
# Run with an empty PATH (only /dev/null equivalents; no docker)
OUTPUT=$(PATH="/usr/bin:/bin" sh "$SWAIN_BOX" 2>&1) || EXIT_CODE=$?
EXIT_CODE=${EXIT_CODE:-0}
check "$EXIT_CODE" "1" "AC-1: exits with code 1 when docker not found"
echo "$OUTPUT" | grep -q "docker" && FOUND=yes || FOUND=no
check "$FOUND" "yes" "AC-1: error message mentions docker"

# ---------------------------------------------------------------------------
# AC-2: docker sandbox subcommand unavailable — non-zero exit + mentions 4.58
# ---------------------------------------------------------------------------
echo ""
echo "--- AC-2: docker sandbox subcommand unavailable ---"
reset_log
write_docker_no_sandbox
OUTPUT=$(PATH="$FAKE_BIN:$PATH" sh "$SWAIN_BOX" 2>&1) || EXIT_CODE=$?
EXIT_CODE=${EXIT_CODE:-0}
check "$EXIT_CODE" "1" "AC-2: exits with code 1 when docker sandbox missing"
echo "$OUTPUT" | grep -q "4.58" && FOUND=yes || FOUND=no
check "$FOUND" "yes" "AC-2: output mentions version 4.58"

# ---------------------------------------------------------------------------
# AC-3: \$PWD default — absolute path of cwd passed to docker sandbox run
# ---------------------------------------------------------------------------
echo ""
echo "--- AC-3: \$PWD default ---"
reset_log
write_docker_full
KNOWN_DIR="$(mktemp -d)"
(
    cd "$KNOWN_DIR"
    PATH="$FAKE_BIN:$PATH" sh "$SWAIN_BOX" 2>&1 || true
)
# Check docker log for the known dir
if [ -f "$DOCKER_LOG" ]; then
    grep -q "$KNOWN_DIR" "$DOCKER_LOG" && FOUND=yes || FOUND=no
else
    FOUND=no
fi
check "$FOUND" "yes" "AC-3: \$PWD (resolved absolute) passed to docker sandbox run"
rmdir "$KNOWN_DIR"

# ---------------------------------------------------------------------------
# AC-4: Explicit path argument — resolves and passes that path
# ---------------------------------------------------------------------------
echo ""
echo "--- AC-4: explicit path argument ---"
reset_log
write_docker_full
# /tmp is a real, accessible directory
TARGET_DIR="/tmp"
# On macOS /tmp is a symlink to /private/tmp — resolve it the same way swain-box does
RESOLVED_TARGET="$(cd "$TARGET_DIR" && pwd)"
PATH="$FAKE_BIN:$PATH" sh "$SWAIN_BOX" "$TARGET_DIR" 2>&1 || true
if [ -f "$DOCKER_LOG" ]; then
    grep -q "$RESOLVED_TARGET" "$DOCKER_LOG" && FOUND=yes || FOUND=no
else
    FOUND=no
fi
check "$FOUND" "yes" "AC-4: explicit path argument (resolved absolute) passed to docker sandbox run"

# ---------------------------------------------------------------------------
# AC-5: Non-existent path rejected before docker is called
# ---------------------------------------------------------------------------
echo ""
echo "--- AC-5: non-existent path rejected ---"
reset_log
write_docker_full
NONEXISTENT="/tmp/swain-box-nonexistent-$$"
OUTPUT=$(PATH="$FAKE_BIN:$PATH" sh "$SWAIN_BOX" "$NONEXISTENT" 2>&1) || EXIT_CODE=$?
EXIT_CODE=${EXIT_CODE:-0}
check "$EXIT_CODE" "1" "AC-5: exits with code 1 for non-existent path"
# docker sandbox run must NOT have been called
if [ -f "$DOCKER_LOG" ]; then
    grep -q "sandbox run" "$DOCKER_LOG" && RUN_CALLED=yes || RUN_CALLED=no
else
    RUN_CALLED=no
fi
check "$RUN_CALLED" "no" "AC-5: docker sandbox run is NOT called for non-existent path"

# ---------------------------------------------------------------------------
# AC-6: Sandbox idempotency — no --rm or lifecycle flags in our docker call
# ---------------------------------------------------------------------------
echo ""
echo "--- AC-6: sandbox idempotency (no --rm flag) ---"
reset_log
write_docker_full
PATH="$FAKE_BIN:$PATH" sh "$SWAIN_BOX" /tmp 2>&1 || true
if [ -f "$DOCKER_LOG" ]; then
    grep -q -- "--rm" "$DOCKER_LOG" && HAS_RM=yes || HAS_RM=no
else
    HAS_RM=no
fi
check "$HAS_RM" "no" "AC-6: --rm flag is NOT passed to docker sandbox run (supports reconnection)"
# Verify the baseline call shape: sandbox run claude <path>
grep -q "sandbox run claude" "$DOCKER_LOG" && HAS_SHAPE=yes || HAS_SHAPE=no
check "$HAS_SHAPE" "yes" "AC-6: call shape is 'docker sandbox run claude <path>'"

# ---------------------------------------------------------------------------
# AC-7: API key forwarding — swain-box delegates to Docker Sandboxes, no -e flags
#
# swain-box delegates credential forwarding entirely to Docker Sandboxes;
# no --e flags are passed. The sandbox credential proxy injects ANTHROPIC_API_KEY
# into the container automatically — our script must not duplicate that.
# ---------------------------------------------------------------------------
echo ""
echo "--- AC-7: no -e ANTHROPIC_API_KEY in docker call ---"
reset_log
write_docker_full
PATH="$FAKE_BIN:$PATH" sh "$SWAIN_BOX" /tmp 2>&1 || true
if [ -f "$DOCKER_LOG" ]; then
    grep -q "ANTHROPIC_API_KEY" "$DOCKER_LOG" && HAS_KEY=yes || HAS_KEY=no
else
    HAS_KEY=no
fi
check "$HAS_KEY" "no" "AC-7: -e ANTHROPIC_API_KEY is NOT passed (credentials flow via sandbox proxy)"

# ---------------------------------------------------------------------------
# AC-8: Max sub path / CLAUDE_CODE_OAUTH_TOKEN
#
# CLAUDE_CODE_OAUTH_TOKEN must be exported in ~/.zshrc (or equivalent login
# shell config) BEFORE Docker Desktop starts; Docker Sandboxes picks it up
# from the host environment automatically. swain-box must not forward it
# manually via -e flags.
# ---------------------------------------------------------------------------
echo ""
echo "--- AC-8: no -e CLAUDE_CODE_OAUTH_TOKEN in docker call ---"
reset_log
write_docker_full
CLAUDE_CODE_OAUTH_TOKEN="test-token-should-not-appear" \
    PATH="$FAKE_BIN:$PATH" sh "$SWAIN_BOX" /tmp 2>&1 || true
if [ -f "$DOCKER_LOG" ]; then
    grep -q "CLAUDE_CODE_OAUTH_TOKEN" "$DOCKER_LOG" && HAS_OAUTH=yes || HAS_OAUTH=no
else
    HAS_OAUTH=no
fi
check "$HAS_OAUTH" "no" "AC-8: -e CLAUDE_CODE_OAUTH_TOKEN is NOT passed (host env picked up by sandbox)"

# ---------------------------------------------------------------------------
# AC-9: --docker removed from claude-sandbox
# Check no USE_DOCKER variable and no if.*USE_DOCKER condition
# ---------------------------------------------------------------------------
echo ""
echo "--- AC-9: --docker flag removed from claude-sandbox ---"
USE_DOCKER_VAR=$(grep -c "USE_DOCKER" "$CLAUDE_SANDBOX" || true)
check "$USE_DOCKER_VAR" "0" "AC-9: no USE_DOCKER variable in claude-sandbox"
# Also verify no --docker in case statement logic (functional occurrences, not comments)
DOCKER_CASE=$(grep -v '^\s*#' "$CLAUDE_SANDBOX" | grep -c -- '--docker' || true)
check "$DOCKER_CASE" "0" "AC-9: no functional --docker case/condition in claude-sandbox (non-comment lines)"

# ---------------------------------------------------------------------------
# AC-10: Dockerfile removed
# ---------------------------------------------------------------------------
echo ""
echo "--- AC-10: claude-sandbox.dockerfile does not exist ---"
DOCKERFILE_PATH="$WORKTREE_ROOT/scripts/claude-sandbox.dockerfile"
if [ -f "$DOCKERFILE_PATH" ]; then
    EXISTS=yes
else
    EXISTS=no
fi
check "$EXISTS" "no" "AC-10: scripts/claude-sandbox.dockerfile does not exist"

# ---------------------------------------------------------------------------
# AC-11: Tier 1 unaffected — claude-sandbox still has --sandbox, --here, --project=
# ---------------------------------------------------------------------------
echo ""
echo "--- AC-11: claude-sandbox Tier 1 features intact ---"
SANDBOX_FLAG=$(grep -c -- '--sandbox' "$CLAUDE_SANDBOX" || true)
[ "$SANDBOX_FLAG" -ge 1 ] && HAS_SANDBOX=yes || HAS_SANDBOX=no
check "$HAS_SANDBOX" "yes" "AC-11: claude-sandbox still contains --sandbox (Tier 1 exec line)"

HERE_FLAG=$(grep -c -- '--here' "$CLAUDE_SANDBOX" || true)
[ "$HERE_FLAG" -ge 1 ] && HAS_HERE=yes || HAS_HERE=no
check "$HAS_HERE" "yes" "AC-11: --here flag still handled in claude-sandbox"

PROJECT_FLAG=$(grep -c -- '--project=' "$CLAUDE_SANDBOX" || true)
[ "$PROJECT_FLAG" -ge 1 ] && HAS_PROJECT=yes || HAS_PROJECT=no
check "$HAS_PROJECT" "yes" "AC-11: --project= flag still handled in claude-sandbox"

# ---------------------------------------------------------------------------
# AC-12: Shell function documented in README
# ---------------------------------------------------------------------------
echo ""
echo "--- AC-12: swain-box shell function documented in README ---"
README="$WORKTREE_ROOT/README.md"
if [ -f "$README" ]; then
    grep -q "swain-box" "$README" && HAS_SWAIN_BOX=yes || HAS_SWAIN_BOX=no
    grep -q "docker sandbox" "$README" && HAS_DSR=yes || HAS_DSR=no
else
    HAS_SWAIN_BOX=no
    HAS_DSR=no
fi
check "$HAS_SWAIN_BOX" "yes" "AC-12: README.md contains 'swain-box'"
check "$HAS_DSR" "yes" "AC-12: README.md contains 'docker sandbox'"

# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------
echo ""
echo "Results: $PASS passed, $FAIL failed"

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
exit 0
