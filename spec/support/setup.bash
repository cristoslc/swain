#!/usr/bin/env bash
# spec/support/setup.bash — shared setup for all swain BDD specs
#
# Source this in each .bats file:
#   load 'support/setup'

# Load bats helpers
SPEC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
load "${SPEC_DIR}/support/lib/bats-support/load"
load "${SPEC_DIR}/support/lib/bats-assert/load"
load "${SPEC_DIR}/support/lib/bats-file/load"

# Resolve the repo root (works from any spec/ subdirectory)
# NOTE: We do NOT export SWAIN_REPO_ROOT here — scripts under test
# must discover their own repo root via git rev-parse, so they see
# the test sandbox, not the real swain repo.
SWAIN_SPEC_REPO_ROOT="$(cd "${SPEC_DIR}/.." && pwd)"

# Scripts under test — always point to the real repo's scripts
export AGENTS_BIN="${SWAIN_SPEC_REPO_ROOT}/.agents/bin"

# Ensure scripts under test discover the sandbox, not the real repo
unset SWAIN_REPO_ROOT
unset SWAIN_SESSION_FILE

# Create a disposable git sandbox for tests that need one.
# Call this from setup_file or setup; the sandbox is cleaned up
# automatically via teardown_file / teardown.
create_test_sandbox() {
  local sandbox
  sandbox="$(mktemp -d "${TMPDIR:-/tmp}/swain-test.XXXXXX")"
  # Canonicalize path (macOS /tmp -> /private/var symlink)
  sandbox="$(cd "$sandbox" && pwd -P)"
  cd "$sandbox" || return 1
  git init --quiet
  git config user.email "test@swain.dev"
  git config user.name "swain-test"
  # Initial commit so HEAD exists
  echo "# test" > README.md
  git add README.md
  git commit --quiet -m "initial"
  echo "$sandbox"
}

# Tear down a sandbox directory
destroy_test_sandbox() {
  local sandbox="$1"
  if [[ -n "$sandbox" && -d "$sandbox" ]]; then
    rm -rf "$sandbox"
  fi
}

# Create a minimal swain project structure inside a sandbox.
# Commits all scaffolded files so the tree starts clean.
scaffold_swain_project() {
  local root="${1:-.}"
  mkdir -p "$root/.agents/bin"
  mkdir -p "$root/.agents/skills"
  mkdir -p "$root/docs/spec/Active"
  mkdir -p "$root/docs/epic/Active"
  mkdir -p "$root/docs/vision/Active"
  mkdir -p "$root/docs/initiative/Active"
  mkdir -p "$root/.tickets"
  echo '{}' > "$root/.agents/session.json"
  # Commit scaffold so tree is clean for dirty-state tests
  (cd "$root" && git add -A && git commit --quiet -m "scaffold swain project" 2>/dev/null || true)
}

# Create a minimal artifact file
create_artifact() {
  local root="${1:-.}"
  local type="$2"    # e.g., spec, epic, vision
  local id="$3"      # e.g., SPEC-001
  local title="${4:-Test Artifact}"
  local phase="${5:-Active}"

  local dir="$root/docs/$type/$phase"
  mkdir -p "$dir"
  cat > "$dir/$id.md" <<EOF
---
id: $id
title: $title
status: $phase
type: $type
---

# $title

Test artifact for BDD specs.
EOF
  echo "$dir/$id.md"
}
