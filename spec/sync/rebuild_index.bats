#!/usr/bin/env bats
# Index rebuild behavioral specs (SPEC-047)
#
# After staging changes, swain-sync rebuilds the list-<type>.md index
# for each artifact type that has staged changes. The index is the
# single source of truth for browsing artifacts by phase.

load '../support/setup'

setup() {
  export TEST_SANDBOX
  TEST_SANDBOX="$(create_test_sandbox)"
  cd "$TEST_SANDBOX" || fail "cannot cd to sandbox"
}

teardown() {
  destroy_test_sandbox "$TEST_SANDBOX"
}

# ─── Basic contract ───

@test "creates list-spec.md in docs/spec/" {
  mkdir -p docs/spec/Active
  cat > docs/spec/Active/SPEC-001.md <<'EOF'
---
artifact: SPEC-001
title: Test Spec
last-updated: 2026-01-01
---
# Test Spec
EOF
  run bash "$AGENTS_BIN/rebuild-index.sh" spec
  assert_success
  assert_file_exists docs/spec/list-spec.md
}

@test "index contains artifact entry" {
  mkdir -p docs/spec/Active
  cat > docs/spec/Active/SPEC-001.md <<'EOF'
---
artifact: SPEC-001
title: My First Spec
last-updated: 2026-01-01
---
# My First Spec
EOF
  bash "$AGENTS_BIN/rebuild-index.sh" spec
  run cat docs/spec/list-spec.md
  assert_output --partial "SPEC-001"
  assert_output --partial "My First Spec"
}

@test "index groups by phase" {
  mkdir -p docs/spec/Active docs/spec/Complete
  cat > docs/spec/Active/SPEC-001.md <<'EOF'
---
artifact: SPEC-001
title: Active Spec
last-updated: 2026-01-01
---
EOF
  cat > docs/spec/Complete/SPEC-002.md <<'EOF'
---
artifact: SPEC-002
title: Done Spec
last-updated: 2026-01-01
---
EOF
  bash "$AGENTS_BIN/rebuild-index.sh" spec
  run cat docs/spec/list-spec.md
  assert_output --partial "## Active"
  assert_output --partial "## Complete"
}

# ─── Multiple types ───

@test "rebuilds multiple types in one call" {
  mkdir -p docs/spec/Active docs/epic/Active
  cat > docs/spec/Active/SPEC-001.md <<'EOF'
---
artifact: SPEC-001
title: Spec
last-updated: 2026-01-01
---
EOF
  cat > docs/epic/Active/EPIC-001.md <<'EOF'
---
artifact: EPIC-001
title: Epic
last-updated: 2026-01-01
---
EOF
  run bash "$AGENTS_BIN/rebuild-index.sh" spec epic
  assert_success
  assert_file_exists docs/spec/list-spec.md
  assert_file_exists docs/epic/list-epic.md
}

# ─── Edge cases ───

@test "skips nonexistent type directory gracefully" {
  run bash "$AGENTS_BIN/rebuild-index.sh" persona
  assert_success
  assert_output --partial "not found, skipping"
}

@test "fails with usage when no type given" {
  run bash "$AGENTS_BIN/rebuild-index.sh"
  assert_failure
  assert_output --partial "Usage"
}

@test "index file is written atomically (no partial writes)" {
  mkdir -p docs/spec/Active
  cat > docs/spec/Active/SPEC-001.md <<'EOF'
---
artifact: SPEC-001
title: Atomic Test
last-updated: 2026-01-01
---
EOF
  # Run rebuild — if atomic, the file should appear complete
  bash "$AGENTS_BIN/rebuild-index.sh" spec

  # Verify it's valid markdown with header
  head -1 docs/spec/list-spec.md | grep -q "^# "
}

@test "index excludes list-*.md files from entries" {
  mkdir -p docs/spec/Active
  cat > docs/spec/Active/SPEC-001.md <<'EOF'
---
artifact: SPEC-001
title: Real Spec
last-updated: 2026-01-01
---
EOF
  # Create a stale index that should not appear as an artifact
  echo "# Old Index" > docs/spec/Active/list-spec.md

  bash "$AGENTS_BIN/rebuild-index.sh" spec
  # The index should only contain SPEC-001, not itself
  count=$(grep -c "SPEC-001" docs/spec/list-spec.md || echo 0)
  [ "$count" -eq 1 ]

  # Should not reference "Old Index"
  run grep "Old Index" docs/spec/list-spec.md
  assert_failure
}

# ─── Spike type mapping ───

@test "spike type maps to research directory" {
  mkdir -p docs/research/Active
  cat > docs/research/Active/SPIKE-001.md <<'EOF'
---
artifact: SPIKE-001
title: Research Spike
last-updated: 2026-01-01
---
EOF
  run bash "$AGENTS_BIN/rebuild-index.sh" spike
  assert_success
  assert_file_exists docs/research/list-spike.md
}
