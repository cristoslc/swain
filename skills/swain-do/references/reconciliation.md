# Artifact/tk Reconciliation

When specwatch detects mismatches between artifact status and tk item state (via `specwatch.sh tk-sync` or `specwatch.sh scan`), this skill is responsible for cleanup. The specwatch log (`.agents/specwatch.log`) contains `TK_SYNC` and `TK_ORPHAN` entries identifying the mismatches.

## Mismatch types and resolution

| Log entry | Meaning | Resolution |
|-----------|---------|------------|
| `TK_SYNC` artifact Implemented, tk open | Spec is done but tasks linger | Close open tk items: `tk add-note <id> "Reconciled: artifact already Implemented"` then `tk close <id>` |
| `TK_SYNC` artifact Abandoned, tk open | Spec was killed but tasks linger | Abandon open tk items: `tk add-note <id> "Abandoned: parent artifact Abandoned"` then `tk close <id>` |
| `TK_SYNC` all tk closed, artifact active | All work done but spec not transitioned | Invoke swain-design to transition the artifact forward (e.g., Approved → Implemented) |
| `TK_ORPHAN` tk refs non-existent artifact | tk items reference an artifact ID not found in docs/ | Investigate: artifact may have been renamed/deleted. Close or re-tag the tk items |

## Reconciliation workflow

1. **Read the log:** `grep '^TK_SYNC\|^TK_ORPHAN' .agents/specwatch.log`
2. **For each mismatch**, apply the resolution from the table above.
3. **Re-run sync check:** `specwatch.sh tk-sync` to confirm all mismatches resolved.

## Automated invocation

Specwatch runs `tk-sync` as part of `specwatch.sh scan` and during watch-mode event processing (when tk is available). When mismatches are found, the output directs the user to invoke swain-do for reconciliation.
