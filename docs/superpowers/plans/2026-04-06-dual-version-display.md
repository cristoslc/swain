# Dual Version Display Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Show both release version (git tag) and skill version (SKILL.md frontmatter) wherever swain reports version info.

**Architecture:** Add a `check_release_version` function to the preflight script that reads the latest semver git tag. Pipe the result through the existing JSON emitter as two new fields (`marker.release_version`, `marker.last_release_version`). Update swain-init SKILL.md Phase 0 messages and Step 6.4 marker format to use both. Update swain-update Step 7 report to show a release header.

**Tech Stack:** Bash (preflight script), Markdown (SKILL.md skill files), Python 3 (JSON emitter in preflight).

---

## File Map

| File | Action | Responsibility |
|------|--------|---------------|
| `skills/swain-init/scripts/swain-init-preflight.sh` | Modify | Add `check_release_version` function, wire into JSON emitter. |
| `skills/swain-init/scripts/test-swain-init-preflight.sh` | Modify | Add tests for release version field (with tags, without tags, old marker with release). |
| `skills/swain-init/SKILL.md` | Modify | Update Phase 0 messages and Step 6.4 marker format. |
| `skills/swain-update/SKILL.md` | Modify | Update Step 7 report to include release version header. |

---

## Chunk 1: Preflight script + tests

### Task 1: Add release version detection to preflight script

**Files:**
- Modify: `skills/swain-init/scripts/swain-init-preflight.sh:78-113` (check_marker function)
- Modify: `skills/swain-init/scripts/swain-init-preflight.sh:385-456` (JSON emitter)

- [ ] **Step 1: Write the failing test — release version from git tag**

Add to `skills/swain-init/scripts/test-swain-init-preflight.sh` before the "Run all tests" section (before line 290):

```bash
# --- Test 10: Release version from git tag ---

test_release_version_from_tag() {
  local dir
  dir=$(setup_temp)

  # Create a semver tag
  git -C "$dir" commit --allow-empty -m "init" -q
  git -C "$dir" tag "v0.29.0-alpha"

  local output
  output=$(bash "$PREFLIGHT" --repo-root "$dir" 2>/dev/null)

  assert_json_valid "$output" "release-tag: valid JSON"
  assert_json_key "$output" "marker.release_version" "v0.29.0-alpha" "release-tag: marker.release_version"

  cleanup_temp "$dir"
}
```

Add `test_release_version_from_tag` to the test runner list (after `test_governance_present`).

- [ ] **Step 2: Write the failing test — no git tags fallback**

Add to `skills/swain-init/scripts/test-swain-init-preflight.sh` after the previous test:

```bash
# --- Test 11: No git tags — release version fallback ---

test_release_version_no_tags() {
  local dir
  dir=$(setup_temp)

  local output
  output=$(bash "$PREFLIGHT" --repo-root "$dir" 2>/dev/null)

  assert_json_valid "$output" "release-notag: valid JSON"
  assert_json_key "$output" "marker.release_version" "(unreleased)" "release-notag: marker.release_version"

  cleanup_temp "$dir"
}
```

Add `test_release_version_no_tags` to the test runner list.

- [ ] **Step 3: Write the failing test — last release version from marker**

Add to `skills/swain-init/scripts/test-swain-init-preflight.sh` after the previous test:

```bash
# --- Test 12: Last release version from marker ---

test_last_release_version_from_marker() {
  local dir
  dir=$(setup_temp)

  # Create marker with release field
  cat > "$dir/.swain-init" << 'MARKER'
{
  "history": [
    {
      "version": "4.0.0",
      "release": "v0.28.0-alpha",
      "timestamp": "2026-04-01T00:00:00Z",
      "action": "init"
    }
  ]
}
MARKER

  mkdir -p "$dir/.claude/skills/swain-init"
  cat > "$dir/.claude/skills/swain-init/SKILL.md" << 'SKILL'
---
name: swain-init
metadata:
  version: 4.0.0
---
SKILL

  # Create a newer tag
  git -C "$dir" commit --allow-empty -m "init" -q
  git -C "$dir" tag "v0.29.0-alpha"

  local output
  output=$(bash "$PREFLIGHT" --repo-root "$dir" 2>/dev/null)

  assert_json_valid "$output" "release-marker: valid JSON"
  assert_json_key "$output" "marker.last_release_version" "v0.28.0-alpha" "release-marker: marker.last_release_version"
  assert_json_key "$output" "marker.release_version" "v0.29.0-alpha" "release-marker: marker.release_version"

  cleanup_temp "$dir"
}
```

Add `test_last_release_version_from_marker` to the test runner list.

- [ ] **Step 4: Write the failing test — old marker without release field**

Add to `skills/swain-init/scripts/test-swain-init-preflight.sh` after the previous test:

```bash
# --- Test 13: Old marker without release field ---

test_old_marker_no_release_field() {
  local dir
  dir=$(setup_temp)

  # Create marker WITHOUT release field (old format)
  cat > "$dir/.swain-init" << 'MARKER'
{
  "history": [
    {
      "version": "3.0.0",
      "timestamp": "2026-01-01T00:00:00Z",
      "action": "init"
    }
  ]
}
MARKER

  mkdir -p "$dir/.claude/skills/swain-init"
  cat > "$dir/.claude/skills/swain-init/SKILL.md" << 'SKILL'
---
name: swain-init
metadata:
  version: 4.0.0
---
SKILL

  git -C "$dir" commit --allow-empty -m "init" -q
  git -C "$dir" tag "v0.29.0-alpha"

  local output
  output=$(bash "$PREFLIGHT" --repo-root "$dir" 2>/dev/null)

  assert_json_valid "$output" "release-oldmarker: valid JSON"
  assert_json_key "$output" "marker.last_release_version" "(unknown)" "release-oldmarker: marker.last_release_version"
  assert_json_key "$output" "marker.release_version" "v0.29.0-alpha" "release-oldmarker: marker.release_version"

  cleanup_temp "$dir"
}
```

Add `test_old_marker_no_release_field` to the test runner list.

- [ ] **Step 5: Run the tests to confirm they fail**

Run: `bash skills/swain-init/scripts/test-swain-init-preflight.sh`
Expected: 4 new failures — `marker.release_version` and `marker.last_release_version` keys not found in JSON output.

- [ ] **Step 6: Implement `check_release_version` in the preflight script**

In `skills/swain-init/scripts/swain-init-preflight.sh`, add a new function after `check_marker` (after line 113):

```bash
# --- Release version check ---
check_release_version() {
  RELEASE_VERSION="(unreleased)"
  LAST_RELEASE_VERSION=""

  # Current release version from latest semver git tag
  local latest_tag
  latest_tag=$(git tag --sort=-v:refname 2>/dev/null | head -1)
  if [ -n "$latest_tag" ]; then
    RELEASE_VERSION="$latest_tag"
  fi

  # Last release version from marker (if marker exists and has release field)
  if [ "$MARKER_EXISTS" = true ] && [ -f ".swain-init" ]; then
    LAST_RELEASE_VERSION=$(python3 -c "
import json, sys
try:
    d = json.load(open('.swain-init'))
    r = d['history'][-1].get('release', '')
    print(r)
except Exception:
    sys.exit(1)
" 2>/dev/null || echo "")
    # Old markers without release field → "(unknown)"
    if [ -z "$LAST_RELEASE_VERSION" ]; then
      LAST_RELEASE_VERSION="(unknown)"
    fi
  fi
}
```

Add `check_release_version || true` to the "Run all checks" section, immediately after `check_marker || true` (after line 345).

- [ ] **Step 7: Wire the new variables into the JSON emitter**

In the JSON emitter section of the preflight script, update the `marker` dict (around line 386-391) to include the two new fields. The new `marker` block becomes:

```python
    'marker': {
        'exists': to_bool(sys.argv[1]),
        'last_version': to_str_or_null(sys.argv[2]),
        'current_version': to_str_or_null(sys.argv[3]),
        'action': sys.argv[4],
        'release_version': sys.argv[5],
        'last_release_version': to_str_or_null(sys.argv[6]),
    },
```

This shifts all subsequent `sys.argv` indices by 2. Update the full argument list at the bottom of the python3 call to insert the two new vars after `$MARKER_ACTION`:

```
  "$MARKER_EXISTS" "$MARKER_LAST_VERSION" "$MARKER_CURRENT_VERSION" "$MARKER_ACTION" \
  "$RELEASE_VERSION" "$LAST_RELEASE_VERSION" \
  "$MIGRATION_STATE" ...
```

And update all `sys.argv[N]` references after index 4:
- `migration.state` was `sys.argv[5]` → now `sys.argv[7]`
- `migration.claude_md` was `sys.argv[6]` → now `sys.argv[8]`
- `migration.agents_md` was `sys.argv[7]` → now `sys.argv[9]`
- `uv.available` was `sys.argv[8]` → now `sys.argv[10]`
- `uv.path` was `sys.argv[9]` → now `sys.argv[11]`
- `tk.path` was `sys.argv[10]` → now `sys.argv[12]`
- `tk.healthy` was `sys.argv[11]` → now `sys.argv[13]`
- `beads.exists` was `sys.argv[12]` → now `sys.argv[14]`
- `beads.has_backup` was `sys.argv[13]` → now `sys.argv[15]`
- `bin_manifests` was `sys.argv[14]` → now `sys.argv[16]`
- `precommit.config_exists` was `sys.argv[15]` → now `sys.argv[17]`
- `precommit.framework` was `sys.argv[16]` → now `sys.argv[18]`
- `superpowers.installed` was `sys.argv[17]` → now `sys.argv[19]`
- `tmux.installed` was `sys.argv[18]` → now `sys.argv[20]`
- `launcher.shell` was `sys.argv[19]` → now `sys.argv[21]`
- `launcher.rc_file` was `sys.argv[20]` → now `sys.argv[22]`
- `launcher.already_installed` was `sys.argv[21]` → now `sys.argv[23]`
- `launcher.runtimes` was `sys.argv[22]` → now `sys.argv[24]`
- `launcher.template_dir` was `sys.argv[23]` → now `sys.argv[25]`
- `governance.installed` was `sys.argv[24]` → now `sys.argv[26]`
- `readme.exists` was `sys.argv[25]` → now `sys.argv[27]`
- `readme.has_code` was `sys.argv[26]` → now `sys.argv[28]`
- `readme.has_artifacts` was `sys.argv[27]` → now `sys.argv[29]`
- `readme.active_count` was `sys.argv[28]` → now `sys.argv[30]`
- `agents_dir.exists` was `sys.argv[29]` → now `sys.argv[31]`

Also update the JSON schema comment at the top of the file (around lines 12-14) to add:
```
#   marker.release_version      string  — current release version from latest git tag ("(unreleased)" if none)
#   marker.last_release_version string  — release version from last marker entry (null if no marker, "(unknown)" if old marker)
```

- [ ] **Step 8: Run tests to verify they pass**

Run: `bash skills/swain-init/scripts/test-swain-init-preflight.sh`
Expected: All 13 tests pass (9 existing + 4 new).

- [ ] **Step 9: Commit**

```bash
git add skills/swain-init/scripts/swain-init-preflight.sh skills/swain-init/scripts/test-swain-init-preflight.sh
git commit -m "feat(SPEC-287): add release version detection to preflight script

Add check_release_version function that reads latest semver git tag.
Emit marker.release_version and marker.last_release_version in JSON.
Fall back to '(unreleased)' when no tags, '(unknown)' for old markers."
```

---

## Chunk 2: Skill file updates

### Task 2: Update swain-init Phase 0 messages

**Files:**
- Modify: `skills/swain-init/SKILL.md:36-45` (Phase 0 messages)

- [ ] **Step 1: Update delegate message (line 37)**

Change:
```markdown
> Project already initialized (swain `marker.last_version`). Delegating to swain-session.
```
To:
```markdown
> Project already initialized (swain `marker.release_version`, init v`marker.last_version`). Delegating to swain-session.
```

- [ ] **Step 2: Update upgrade message (lines 41-43)**

Change:
```markdown
> Project was initialized with swain `marker.last_version` (current: `marker.current_version`). Consider running `/swain update` to pick up new features.
> Starting session.
```
To:
```markdown
> Project was initialized with swain `marker.last_release_version` (init v`marker.last_version`). Current: `marker.release_version` (init v`marker.current_version`). Consider running `/swain update` to pick up new features.
> Starting session.
```

- [ ] **Step 3: Commit**

```bash
git add skills/swain-init/SKILL.md
git commit -m "feat(SPEC-287): update swain-init Phase 0 to show dual versions

Delegate and upgrade messages now show both release version (git tag)
and skill version (init vX.Y.Z) side by side."
```

### Task 3: Update swain-init Step 6.4 marker format

**Files:**
- Modify: `skills/swain-init/SKILL.md:511-527` (Step 6.4 marker write)

- [ ] **Step 1: Update the marker JSON example**

Change the JSON example at lines 517-526 to:
```json
{
  "history": [
    {
      "version": "4.0.0",
      "release": "v0.29.0-alpha",
      "timestamp": "2026-03-26T18:30:00Z",
      "action": "init"
    }
  ]
}
```

- [ ] **Step 2: Update the instruction text**

Change line 513:
```markdown
After all onboarding phases complete, write the `.swain-init` marker file. Read `marker.current_version` from the preflight JSON for the version.
```
To:
```markdown
After all onboarding phases complete, write the `.swain-init` marker file. Read `marker.current_version` from the preflight JSON for the skill version and `marker.release_version` for the release version.
```

- [ ] **Step 3: Commit**

```bash
git add skills/swain-init/SKILL.md
git commit -m "feat(SPEC-287): include release version in .swain-init marker format

Step 6.4 now writes a 'release' field alongside 'version' in each
history entry, sourced from marker.release_version in preflight JSON."
```

### Task 4: Update swain-update Step 7 report

**Files:**
- Modify: `skills/swain-update/SKILL.md:163-177` (Step 7 report)

- [ ] **Step 1: Add release version header before skill list**

Change the Step 7 section (lines 163-175) to:

```markdown
## Step 7 — Report

Display the current release version (from the latest git tag):

```bash
release_tag=$(git tag --sort=-v:refname | head -1)
echo "swain ${release_tag:-(unreleased)}"
```

Then list the installed swain skill directories and extract each skill's version from its `SKILL.md` frontmatter:

```bash
for skill in .claude/skills/swain-*/SKILL.md; do
  name=$(grep '^name:' "$skill" | head -1 | sed 's/name: *//')
  version=$(grep 'version:' "$skill" | head -1 | sed 's/.*version: *//')
  echo "  $name  v$version"
done
```

Show the user the list and confirm the update is complete.
```

- [ ] **Step 2: Commit**

```bash
git add skills/swain-update/SKILL.md
git commit -m "feat(SPEC-287): show release version in swain-update report

Step 7 now displays the git tag release version as a header line
before the per-skill version list."
```

### Task 5: Final verification

- [ ] **Step 1: Run preflight tests one more time**

Run: `bash skills/swain-init/scripts/test-swain-init-preflight.sh`
Expected: All 13 pass.

- [ ] **Step 2: Run the preflight script on the real repo to sanity-check output**

Run: `bash skills/swain-init/scripts/swain-init-preflight.sh | python3 -c "import json,sys; d=json.load(sys.stdin); print('release_version:', d['marker']['release_version']); print('last_release_version:', d['marker'].get('last_release_version'))"`
Expected output (on the swain repo with tag v0.29.0-alpha and an existing .swain-init marker):
```
release_version: v0.29.0-alpha
last_release_version: (unknown)
```
The `last_release_version` is `(unknown)` because the current `.swain-init` marker predates this feature and has no `release` field. If the marker doesn't exist, it shows `None`.

**Note on Chunk 2 skill file changes:** SKILL.md files are prose instructions to an LLM agent, not executable code. The agent reads `PREFLIGHT_JSON`, extracts fields like `marker.release_version`, and constructs user-facing messages at runtime. There are no templates or substitution engines — the agent interprets the instructions and formats output. Chunk 2 changes are documentation updates that the agent follows.
