# Lifecycle Table Format

## Frontmatter fields (Initiative-related)

Two scalar fields introduced with the INITIATIVE artifact type are also valid on EPIC and SPEC:

| Field | Type | Valid values | Description |
|-------|------|-------------|-------------|
| `parent-initiative` | scalar | `INITIATIVE-NNN` | The Initiative this artifact belongs to. Sits alongside `parent-vision` and `parent-epic` in the hierarchy. |
| `priority-weight` | scalar | `high`, `medium`, `low` | Relative priority within the parent Initiative or Vision. Used by `specgraph recommend` to compute ranked scores. |

Example EPIC frontmatter:

```yaml
parent-vision: VISION-001
parent-initiative: INITIATIVE-003
priority-weight: high
```

Every artifact embeds a lifecycle table tracking phase transitions:

```markdown
### Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Planned | 2026-02-24 | abc1234 | Initial creation |
| Active  | 2026-02-25 | def5678 | Dependency X satisfied |
```

## Stamping patterns

There are two patterns for recording the transition commit hash, selected based on artifact complexity tier (see SPEC-045 for tier classification).

### Two-commit stamp (default — EPICs and full-ceremony SPECs)

Commit the transition first, then stamp the resulting hash into the lifecycle table in a second commit. This keeps the stamped hash reachable in git history.

```
Commit A: lifecycle(SPEC-001): transition to Complete
  ↳ lifecycle row: | Complete | 2026-03-14 | -- | ... |

Commit B: docs(SPEC-001): stamp lifecycle hash for Complete transition
  ↳ lifecycle row: | Complete | 2026-03-14 | <commit-A-hash> | ... |
```

Use two-commit stamp for:
- All EPICs (always — they are linked by child SPECs)
- Feature SPECs with downstream dependents (`depends-on` or `linked-artifacts` from other artifacts)
- Any artifact where precision is required for audit trails

### Inline stamp (fast-path tier artifacts only)

For fast-path eligible artifacts with no downstream dependents, use `git rev-parse HEAD` *before* the transition commit to pre-fill the lifecycle row hash. Only one commit is needed.

```bash
IMPL_HASH=$(git rev-parse HEAD)
# Edit lifecycle table: | Complete | 2026-03-14 | $IMPL_HASH | ... |
git mv docs/spec/Ready/(SPEC-099)-.../ docs/spec/Complete/(SPEC-099)-.../
git add ...
git commit -m "lifecycle(SPEC-099): transition to Complete"
```

```
Commit A: lifecycle(SPEC-099): transition to Complete
  ↳ lifecycle row: | Complete | 2026-03-14 | <prev-HEAD-hash> | ... |
```

The hash points to the implementation commit (one before the transition), not the transition commit itself. This ~1-commit offset is acceptable for trivial artifacts where lifecycle auditing is rarely needed.

Use inline stamp for:
- Bug/fix SPECs with no `parent-epic` (fast-path tier)
- SPIKEs with no `parent-epic` (fast-path tier)
- Any artifact classified as fast-path that has no other artifacts depending on it
