# Session Check Preamble

State-changing skills should check for an active session before proceeding. This is a soft gate — the operator can always dismiss it.

## Integration

Add this to the top of state-changing skill SKILL.md files (after frontmatter, before the first section):

```markdown
<!-- session-check -->
Before proceeding, verify an active session exists:
\`\`\`bash
bash "$(find "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" -path '*/swain-session/scripts/swain-session-check.sh' -print -quit 2>/dev/null)" 2>/dev/null
\`\`\`
If the output JSON has `status` other than `"active"`, inform the operator: "No active session — start one with `/swain-session`?" and proceed if they dismiss.
```

## Skip list

These skills are read-only and skip the session check:
- swain-help
- swain-search (discover mode)
- swain-status
- swain-session (manages sessions itself)
- swain-doctor

## Performance

The check script reads one JSON file and does a timestamp comparison. Target: < 100ms.
