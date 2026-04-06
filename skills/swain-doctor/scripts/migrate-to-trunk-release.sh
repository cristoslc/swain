#!/usr/bin/env bash
set -euo pipefail

# migrate-to-trunk-release.sh
# One-time migration from single-branch (main) to trunk+release model (SPEC-114, ADR-013).
# Idempotent — safe to run multiple times. Use --dry-run to preview.

DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

info()  { echo "==> $*"; }
warn()  { echo "WARN: $*" >&2; }
die()   { echo "ERROR: $*" >&2; exit 1; }

run() {
  if $DRY_RUN; then
    echo "[dry-run] $*"
  else
    info "Running: $*"
    "$@"
  fi
}

# ---------------------------------------------------------------------------
# Prerequisite checks
# ---------------------------------------------------------------------------

info "Checking prerequisites..."

command -v git >/dev/null 2>&1 || die "git is not installed"
command -v gh  >/dev/null 2>&1 || die "gh CLI is not installed"

# Verify gh is authenticated
gh auth status >/dev/null 2>&1 || die "gh CLI is not authenticated — run 'gh auth login' first"

# Detect remote URL and extract owner/repo
REMOTE_URL="$(git remote get-url origin 2>/dev/null)" || die "No 'origin' remote found"
info "Remote URL: $REMOTE_URL"

# Extract owner/repo from SSH or HTTPS URLs
if [[ "$REMOTE_URL" =~ .*:(.+/.+)\.git$ ]]; then
  OWNER_REPO="${BASH_REMATCH[1]}"
elif [[ "$REMOTE_URL" =~ .*:(.+/.+)$ ]]; then
  OWNER_REPO="${BASH_REMATCH[1]}"
elif [[ "$REMOTE_URL" =~ github\.com/(.+/.+)\.git$ ]]; then
  OWNER_REPO="${BASH_REMATCH[1]}"
elif [[ "$REMOTE_URL" =~ github\.com/(.+/.+)$ ]]; then
  OWNER_REPO="${BASH_REMATCH[1]}"
else
  die "Could not extract owner/repo from remote URL: $REMOTE_URL"
fi
info "GitHub repo: $OWNER_REPO"

# Must be on main branch (or trunk if re-running)
CURRENT_BRANCH="$(git symbolic-ref --short HEAD 2>/dev/null)" || die "Detached HEAD — check out a branch first"
if [[ "$CURRENT_BRANCH" != "main" && "$CURRENT_BRANCH" != "trunk" ]]; then
  die "Must be on 'main' (or 'trunk' if re-running). Currently on '$CURRENT_BRANCH'."
fi

# Clean working tree
if ! git diff --quiet || ! git diff --cached --quiet; then
  die "Working tree is dirty — commit or stash changes first"
fi

# Fetch latest remote state
info "Fetching latest remote state..."
git fetch origin

# ---------------------------------------------------------------------------
# Step 1: Rename main → trunk (locally and on remote)
# ---------------------------------------------------------------------------

info ""
info "--- Step 1: Rename main → trunk ---"

if git show-ref --verify --quiet refs/heads/trunk; then
  info "Local branch 'trunk' already exists — skipping local rename."
else
  if git show-ref --verify --quiet refs/heads/main; then
    run git branch -m main trunk
  else
    info "No local 'main' branch found (already renamed?) — skipping."
  fi
fi

# Push trunk to remote
if git ls-remote --heads origin trunk | grep -q trunk; then
  info "Remote branch 'trunk' already exists — skipping push."
else
  run git push origin trunk
fi

# ---------------------------------------------------------------------------
# Step 2: Create release branch from trunk HEAD
# ---------------------------------------------------------------------------

info ""
info "--- Step 2: Create release branch from trunk HEAD ---"

if git show-ref --verify --quiet refs/heads/release; then
  info "Local branch 'release' already exists — skipping creation."
else
  run git branch release trunk
fi

# Push release to remote
if git ls-remote --heads origin release | grep -q release; then
  info "Remote branch 'release' already exists — skipping push."
else
  run git push origin release
fi

# ---------------------------------------------------------------------------
# Step 3: Set release as the default branch on GitHub
# ---------------------------------------------------------------------------

info ""
info "--- Step 3: Set 'release' as the default branch on GitHub ---"

CURRENT_DEFAULT="$(gh api "repos/$OWNER_REPO" --jq '.default_branch' 2>/dev/null)" || true

if [[ "$CURRENT_DEFAULT" == "release" ]]; then
  info "Default branch is already 'release' — skipping."
else
  info "Current default branch: ${CURRENT_DEFAULT:-unknown}"
  run gh api -X PATCH "repos/$OWNER_REPO" -f default_branch=release
fi

# ---------------------------------------------------------------------------
# Step 4: Push both branches (ensure up-to-date)
# ---------------------------------------------------------------------------

info ""
info "--- Step 4: Ensure both branches are pushed ---"

run git push origin trunk
run git push origin release

# ---------------------------------------------------------------------------
# Step 5: Delete old main branch on the remote
# ---------------------------------------------------------------------------

info ""
info "--- Step 5: Delete old 'main' branch on remote ---"

if git ls-remote --heads origin main | grep -q main; then
  run git push origin --delete main
else
  info "Remote branch 'main' does not exist — skipping deletion."
fi

# ---------------------------------------------------------------------------
# Step 6: Set upstream tracking
# ---------------------------------------------------------------------------

info ""
info "--- Step 6: Set upstream tracking for trunk ---"

if [[ "$(git symbolic-ref --short HEAD 2>/dev/null)" == "trunk" ]]; then
  run git branch --set-upstream-to=origin/trunk trunk
fi

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------

info ""
info "Migration complete!"
info "  trunk   → origin/trunk   (development)"
info "  release → origin/release (default branch, stable)"
if $DRY_RUN; then
  info ""
  info "(This was a dry run — no changes were made.)"
fi
