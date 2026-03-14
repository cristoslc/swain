# Index Maintenance

Every doc-type directory keeps a single lifecycle index (`list-<type>.md`). The index is a **human-facing display artifact** — specgraph reads frontmatter directly, not the index. Index updates are **lazy**: skipped per-artifact, batched at session end.

## Lazy refresh model (SPEC-047)

**Per-artifact creation/transition**: Do NOT update `list-<type>.md`. Only write the artifact frontmatter and lifecycle table.

**Batch refresh (session end)**: Run `skills/swain-design/scripts/rebuild-index.sh <type>` for each artifact type that had activity in the session. This is called automatically by swain-sync before committing.

**Explicit refresh**: Run `rebuild-index.sh <type>` when the user requests an up-to-date index view.

## What the batch refresh produces

`rebuild-index.sh <type>` scans `docs/<type>/` across all phase subdirectories and regenerates `list-<type>.md`:
1. Groups artifacts by phase (Proposed, Ready, Active, Complete, etc.)
2. Extracts `artifact:`, `title:`, `last-updated:`, and latest lifecycle commit from each file
3. Writes the table sections in phase order
4. Atomic write via temp file → rename (idempotent — safe to run multiple times)

## Usage

```bash
# Refresh spec index
bash skills/swain-design/scripts/rebuild-index.sh spec

# Refresh multiple types after a busy session
bash skills/swain-design/scripts/rebuild-index.sh spec epic spike
```

## When to run

| Trigger | Action |
|---------|--------|
| Session end (swain-sync) | Auto-run for each type with activity |
| User requests fresh index | Run explicitly |
| After bulk migrations or audits | Run for affected types |
| Per-artifact creation/transition | Skip (lazy) |

## Legacy behavior

Prior to SPEC-047, the index was refreshed per-artifact as step 10 of the authoring workflow. That behavior is now replaced by the lazy model above. If you encounter old workflow instructions saying "refresh the index now", skip that step — `rebuild-index.sh` will handle it at session end.
