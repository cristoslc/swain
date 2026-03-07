# Troubleshooting

Error paths and recovery procedures for spec-management operations.

## Artifact creation failures

### Parent artifact doesn't exist

**Symptom:** Creating a SPEC, STORY, or EPIC that references a parent (`parent-epic`, `parent-vision`) that can't be found in `docs/`.

**Action:** Stop creation. Report the missing parent with its expected ID and path. Ask whether to (a) create the parent first, or (b) proceed without the parent reference and fix it later. Option (b) leaves the artifact in a Draft state with a `TODO` comment in the parent field — this will be caught by the cross-reference auditor.

### Next number collision

**Symptom:** The scan of `docs/<type>/` to find the next available number produces a collision (e.g., two artifacts claim the same number).

**Action:** Report both conflicting files. Renumber the newer artifact (by filesystem creation date or git log). Update the index after resolving.

### Index file doesn't exist

**Symptom:** `list-<type>.md` is missing when the index refresh step runs.

**Action:** Create it from scratch. Scan all artifacts of that type in `docs/<type>/`, build the full index with one table per phase, and write the file. This is self-healing — a missing index is never a blocker.

## Phase transition failures

### Artifact already in target phase

**Symptom:** Attempting to transition an artifact to the phase it's already in.

**Action:** No-op. Report that the artifact is already in the target phase. Do not add a duplicate lifecycle table row.

### Backward phase transition attempted

**Symptom:** Target phase is earlier in the sequence than the current phase.

**Action:** Reject the transition. Report the current phase, the requested phase, and the valid forward phases. If the user insists, suggest Abandoning the artifact and creating a new one.

### Dependencies not resolved

**Symptom:** `specgraph.sh blocks <ID>` shows unresolved dependencies when attempting a completion/implementation transition.

**Action:** Report the blocking artifacts and their current phases. Do not transition. Suggest either (a) completing the blockers first, or (b) removing the dependency if it's no longer relevant (edit `depends-on:` in frontmatter, re-run `specgraph.sh build`).

## Script failures

### specgraph.sh: jq not installed

**Symptom:** `specgraph.sh` fails with "command not found: jq".

**Action:** Install jq (`brew install jq` on macOS, `apt install jq` on Debian/Ubuntu). The script cannot function without it — there is no fallback.

### specgraph.sh: cache corrupt or stale

**Symptom:** `specgraph.sh` returns incorrect results or errors parsing `/tmp/agents-specgraph-*.json`.

**Action:** Force rebuild with `specgraph.sh build`. This deletes and regenerates the cache from frontmatter.

### specwatch.sh: fswatch not installed

**Symptom:** `specwatch.sh watch` fails with "fswatch is not installed."

**Action:** Use `specwatch.sh scan` instead for one-time checks. The `scan` subcommand has no external dependencies beyond Python 3. Install fswatch (`brew install fswatch`) for background monitoring.

### specwatch.sh: watcher died silently

**Symptom:** `specwatch.sh status` shows "not running" but you expected it to be active.

**Action:** The watcher auto-terminates after 1 hour of inactivity (no `touch` calls). Restart with `specwatch.sh watch`. Check `.agents/specwatch.log` for any stale references caught before it stopped.

## Cross-reference issues

### Dangling addresses field

**Symptom:** An artifact's `addresses:` field references a `JOURNEY-NNN.PP-NN` that doesn't exist in any journey.

**Action:** Verify the journey and pain-point ID. If the journey was reorganized, update the `addresses` field. If the pain point was removed, drop the reference.

### Circular dependencies

**Symptom:** `specgraph.sh tree <ID>` loops or shows artifact A depending on B depending on A.

**Action:** Identify the cycle and break it by removing the less-important `depends-on` edge. Circular dependencies indicate a modeling error — two artifacts cannot block each other.
