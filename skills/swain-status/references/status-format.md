# Status Format Reference

## OSC 8 Hyperlinks

Terminal hyperlinks use the OSC 8 escape sequence, supported by iTerm2, Kitty, WezTerm, and other modern terminals.

Format:
```
\e]8;;URL\e\\DISPLAY_TEXT\e]8;;\e\\
```

### Link types used

| Type | URL scheme | Example |
|------|-----------|---------|
| File path | `file:///absolute/path` | Opens in system default app |
| GitHub issue | `https://github.com/owner/repo/issues/N` | Opens in browser |
| GitHub PR | `https://github.com/owner/repo/pull/N` | Opens in browser |

### Fallback

If the terminal doesn't support OSC 8, the display text is shown as plain text — links degrade gracefully.

## Full output layout

```
# project — Status

**Resuming:** bookmark note here
  Files: file1.md, file2.md

## Pipeline

Branch: **trunk** (clean)
Last commit: `abc123` feat(auth): add token rotation (2 hours ago)

## Active Epics

### EPIC-003: Architecture Discovery and Scaling [Active]

Progress: **4/7** specs resolved

  - [x] SPEC-015: Discovery Service [Implemented]
  - [x] SPEC-016: Load Balancer [Implemented]
  - [x] SPEC-017: Health Checks [Implemented]
  - [x] SPEC-018: Metrics Pipeline [Implemented]
  - [ ] SPEC-019: Auto-scaling Rules [Draft]
  - [ ] SPEC-020: Capacity Planning [Draft]
  - [ ] SPEC-021: Failover Strategy [Draft]

## Actionable Now

- SPEC-019: Auto-scaling Rules [Draft]  docs/specs/SPEC-019.md
- SPEC-020: Capacity Planning [Draft]  docs/specs/SPEC-020.md

## Blocked

- SPEC-021: Failover Strategy [Draft]  <- waiting on: SPEC-019

## Tasks

**In progress:**
- #42 Implement auto-scaling threshold config

**Recently completed:**
- #40 Add health check endpoints
- #39 Configure load balancer rules

12 total tracked issues.

## GitHub Issues

**Assigned to you:**
- #15 Investigate memory leak in discovery service
- #12 Update deployment docs

---
Artifacts: 30 total, 23 resolved, 4 ready, 1 blocked
Updated: 2026-03-10T22:30:00Z
```

## Compact output layout (for MOTD)

```
trunk (clean)
epic: EPIC-003 4/7
task: #42 Implement auto-scaling threshold
ready: 4 actionable
issues: 2 assigned
```

The compact format is designed for a 40-character-wide MOTD box. Each line maps to one data source. The MOTD script reads these lines positionally.

## Cache JSON schema

```json
{
  "timestamp": "ISO-8601",
  "repo": "/absolute/path",
  "project": "project-name",
  "git": {
    "branch": "trunk",
    "dirty": false,
    "changedFiles": 0,
    "lastCommit": { "hash": "abc123", "message": "...", "age": "2 hours ago" },
    "recentCommits": [...]
  },
  "artifacts": {
    "ready": [{ "id": "SPEC-019", "status": "Draft", "title": "...", "type": "SPEC", "file": "docs/..." }],
    "blocked": [{ "id": "SPEC-021", "status": "Draft", "title": "...", "waiting": ["SPEC-019"] }],
    "epics": {
      "EPIC-003": {
        "id": "EPIC-003",
        "title": "...",
        "status": "Active",
        "progress": { "done": 4, "total": 7 },
        "children": [...]
      }
    },
    "counts": { "total": 30, "resolved": 23, "ready": 4, "blocked": 1 }
  },
  "tasks": {
    "inProgress": [{ "id": "#42", "title": "..." }],
    "recentlyCompleted": [{ "id": "#40", "title": "..." }],
    "total": 12,
    "available": true
  },
  "issues": {
    "open": [{ "number": 15, "title": "...", "labels": [...], "assignees": [...] }],
    "assigned": [{ "number": 15, "title": "..." }],
    "available": true
  },
  "session": {
    "bookmark": { "note": "...", "files": [...] },
    "lastBranch": "main",
    "lastContext": "..."
  }
}
```
