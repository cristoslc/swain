## Post-operation bookmark (auto-update protocol)

Other swain skills update the session bookmark after completing operations. This gives the developer a "where I left off" marker without requiring manual bookmarking.

### When to update

A skill should update the bookmark when it completes a **state-changing operation** — artifact transitions, task updates, commits, releases, or status checks.

### How to update

Use `scripts/swain-bookmark.sh` (relative to this skill's directory):

```bash
# Find the script
BOOKMARK_SCRIPT="$(find . .claude .agents -path '*/swain-session/scripts/swain-bookmark.sh' -print -quit 2>/dev/null)"

# Basic note
bash "$BOOKMARK_SCRIPT" "Transitioned SPEC-001 to Approved"

# Note with files
bash "$BOOKMARK_SCRIPT" "Implemented auth middleware" --files src/auth.ts src/auth.test.ts

# Clear bookmark
bash "$BOOKMARK_SCRIPT" --clear
```

The script handles session.json discovery, atomic writes, and graceful degradation (no jq = silent no-op).
