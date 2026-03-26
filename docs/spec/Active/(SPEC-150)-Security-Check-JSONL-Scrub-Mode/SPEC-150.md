---
title: "swain-security-check: JSONL scrub mode"
artifact: SPEC-150
track: implementable
status: Active
author: cristos
created: 2026-03-22
last-updated: 2026-03-22
priority-weight: ""
type: enhancement
parent-epic: EPIC-042
parent-initiative: ""
linked-artifacts:
  - EPIC-042
  - SPEC-151
depends-on-artifacts: []
addresses: []
evidence-pool: "agent-alignment-monitoring@8047381"
source-issue: ""
swain-do: required
---

# swain-security-check: JSONL scrub mode

## Problem Statement

swain-security-check currently scans files and reports findings (scan → report). For retro JSONL archival, we need a mode that scans and redacts — producing a clean copy rather than a report (scan → transform). No scrubbing capability exists today, so session transcripts cannot be safely committed to git.

## Desired Outcomes

Operators can archive session transcripts knowing that secrets and PII are automatically stripped. The scrubber is a composable pipeline transform — it always produces output, making it usable as a step in any workflow that needs sanitized JSONL (not just retros).

## External Behavior

**Input:** JSONL file path or stdin
**Output:** Scrubbed JSONL to stdout; scrub report (JSON) to stderr

**Scrubbing pipeline (ordered):**
1. Strip `file-history-snapshot` entries entirely — full file backups with high secret/PII risk and no retro value
2. Secret redaction — reuse gitleaks regex patterns when gitleaks is installed; fall back to built-in patterns for common secret formats (AWS keys, GitHub tokens, base64 credentials, connection strings)
3. PII redaction — regex-based:
   - Email addresses → `[REDACTED-EMAIL]`
   - IPv4/IPv6 addresses → `[REDACTED-IP]`
   - Phone numbers (US/international formats) → `[REDACTED-PHONE]`
   - Filesystem paths containing usernames (`/Users/<name>/`, `/home/<name>/`) → replace `<name>` with `[REDACTED-USER]`

**Scrub report (stderr, JSON):**
```json
{
  "scrubber_version": "1.0.0",
  "patterns_source": "gitleaks",
  "entries_total": 233,
  "entries_stripped": 16,
  "secrets_redacted": 2,
  "pii_redacted": 7,
  "categories": [
    {"type": "secret", "count": 2, "patterns": ["aws-access-key", "github-token"]},
    {"type": "email", "count": 3},
    {"type": "ip", "count": 0},
    {"type": "phone", "count": 0},
    {"type": "filesystem-path", "count": 4}
  ]
}
```

**Exit codes:** 0 = success, 1 = scrub completed with warnings (e.g., pattern parse errors), 2 = error (invalid input, I/O failure)

**Preconditions:** Python 3.9+. gitleaks optional (graceful fallback to builtin patterns).
**Postconditions:** Output JSONL contains zero strings matching the active pattern set.

## Acceptance Criteria

- Given a JSONL file containing AWS access keys, GitHub tokens, and email addresses, when `jsonl_scrub.py` is run, then the output contains `[REDACTED-SECRET]` and `[REDACTED-EMAIL]` in place of the originals
- Given a JSONL file with `file-history-snapshot` entries, when scrubbed, then zero `file-history-snapshot` entries appear in the output
- Given a JSONL file with filesystem paths like `/Users/cristos/...`, when scrubbed, then the output contains `/Users/[REDACTED-USER]/...`
- Given a JSONL file with no secrets or PII, when scrubbed, then the output is identical to input (minus file-history-snapshots) and exit code is 0
- Given gitleaks is not installed, when scrubbed, then builtin patterns are used and `patterns_source` in the report says `"builtin"`
- Given stdin input (piped), when `jsonl_scrub.py` is run without a file argument, then it reads from stdin and writes to stdout

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Script lives at `skills/swain-security-check/scripts/jsonl_scrub.py`
- Must not import any dependencies beyond Python stdlib + the existing security check modules
- The scrubber is a transform, not a scanner — it always produces output
- Filesystem path scrubbing only targets username segments, not the full path (to preserve directory structure context in retro summaries)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-22 | — | Initial creation |
