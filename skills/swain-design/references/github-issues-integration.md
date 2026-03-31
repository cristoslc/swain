# GitHub Issues Integration

SPECs can be linked to GitHub Issues via the `source-issue` frontmatter field. This enables bidirectional sync between swain's artifact workflow and GitHub's issue tracker.

## Promoting an issue to a SPEC

When the user wants to turn a GitHub issue into a SPEC:

1. Run `scripts/issue-integration.sh check` to verify `gh` CLI availability.
2. Run `scripts/issue-integration.sh promote <issue-url-or-ref>` to fetch issue data as JSON.
3. Create a new SPEC using the standard creation workflow, populating:
   - `source-issue: github:<owner>/<repo>#<number>` in frontmatter
   - Problem Statement from the issue body
   - Title from the issue title

Accepted reference formats:
- `github:<owner>/<repo>#<number>` (canonical)
- `https://github.com/<owner>/<repo>/issues/<number>` (URL, converted automatically)

## Transition hooks

During phase transitions on SPECs with a `source-issue` field, post notifications to the linked issue:

| Transition target | Action | Script command |
|-------------------|--------|---------------|
| Needs Manual Test | Post comment | `issue-integration.sh transition-comment <source-issue> <artifact-id> Needs Manual Test` |
| Complete | Close issue | `issue-integration.sh transition-close <source-issue> <artifact-id>` |
| Abandoned | Post comment (do NOT close) | `issue-integration.sh transition-comment <source-issue> <artifact-id> Abandoned` |
| Other phases | Post comment | `issue-integration.sh transition-comment <source-issue> <artifact-id> <phase>` |

If `gh` CLI is unavailable, log a warning and continue the transition — issue sync is best-effort, not a gate.

## Backend abstraction

The `source-issue` value uses URL-prefix dispatch: `github:` routes to the GitHub backend (`gh` CLI). Future backends (Linear, Jira) would add new prefixes and implement the same operations: `promote`, `comment`, `close`. Core swain-design logic does not change when a backend is added.
