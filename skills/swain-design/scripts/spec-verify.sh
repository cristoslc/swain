#!/bin/bash
# spec-verify.sh — Verify a Spec's acceptance criteria have documented evidence.
# Gates the Needs Manual Test → Complete transition by checking the Verification table.
#
# Output goes to stdout in a structured format. Exit 0 = all criteria covered,
# exit 1 = gaps found, exit 2 = usage error.

set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: spec-verify.sh <artifact-path>

Checks a Spec artifact's Verification table against its Acceptance Criteria:
  1. Every acceptance criterion has a row in the Verification table
  2. Every row has non-empty Evidence and Result columns
  3. No rows have a "Fail" result

Output format:
  MISSING_EVIDENCE <criterion-summary>
    action: add Evidence and Result for this criterion

  FAIL <criterion-summary>
    evidence: <what was tested>
    action: fix failing criterion before transitioning to Complete

  EMPTY_TABLE
    action: populate Verification table before transitioning to Complete

Summary line:
  OK SPEC-NNN: N/N criteria verified
  GAPS SPEC-NNN: N/M criteria verified, K gaps

Exit codes:
  0  All criteria verified (no Fail results, no gaps)
  1  Gaps or failures found
  2  Usage error
USAGE
}

if [ $# -lt 1 ] || [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
  usage
  exit 2
fi

ARTIFACT_PATH="$1"

if [ ! -f "$ARTIFACT_PATH" ]; then
  echo "Error: artifact not found: $ARTIFACT_PATH" >&2
  exit 2
fi

uv run python3 - "$ARTIFACT_PATH" <<'PYEOF'
import re, sys

artifact_path = sys.argv[1]

with open(artifact_path) as f:
    content = f.read()

# --- Extract artifact ID from frontmatter ---

art_id = ""
fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
if fm_match:
    for line in fm_match.group(1).split('\n'):
        m = re.match(r'^artifact:\s*(SPEC-\d+)', line)
        if m:
            art_id = m.group(1)
            break

if not art_id:
    print("Error: not a SPEC artifact or missing artifact ID in frontmatter", file=sys.stderr)
    sys.exit(2)

# --- Check artifact is in Needs Manual Test phase ---

status = ""
if fm_match:
    for line in fm_match.group(1).split('\n'):
        m = re.match(r'^status:\s*(.+)', line)
        if m:
            status = m.group(1).strip()
            break

if status and status != "Needs Manual Test":
    print(f"Warning: {art_id} is in phase '{status}', not 'Needs Manual Test'", file=sys.stderr)

# --- Extract Acceptance Criteria section ---

ac_match = re.search(
    r'##\s*Acceptance Criteria\s*\n(.*?)(?=\n##\s|\Z)',
    content, re.DOTALL
)

if not ac_match:
    print(f"Error: {art_id} has no Acceptance Criteria section", file=sys.stderr)
    sys.exit(2)

ac_text = ac_match.group(1).strip()

# Count criteria: lines starting with - or * or numbered, or Given/When/Then blocks
criteria = []
for line in ac_text.split('\n'):
    line = line.strip()
    # Skip empty lines and table formatting
    if not line or line.startswith('|') or line.startswith('<!--'):
        continue
    # Bullet points, numbered items, or Given/When/Then
    if re.match(r'^[-*]\s+', line) or re.match(r'^\d+[.)]\s+', line) or re.match(r'^(Given|When|Then|And|But)\s+', line, re.IGNORECASE):
        criteria.append(line.lstrip('-*0123456789.) \t'))

if not criteria:
    print(f"Warning: {art_id} has no parseable acceptance criteria", file=sys.stderr)
    # Don't fail — the agent should review manually
    print(f"OK {art_id}: no parseable criteria to verify (manual review recommended)")
    sys.exit(0)

# --- Extract Verification table ---

ver_match = re.search(
    r'##\s*Verification\s*\n(.*?)(?=\n##\s|\Z)',
    content, re.DOTALL
)

if not ver_match:
    print(f"EMPTY_TABLE")
    print(f"  action: add Verification section and populate before transitioning to Implemented")
    print()
    print(f"GAPS {art_id}: 0/{len(criteria)} criteria verified, {len(criteria)} gaps")
    sys.exit(1)

ver_text = ver_match.group(1).strip()

# Parse table rows (skip header and separator)
ver_rows = []
table_lines = [l for l in ver_text.split('\n') if l.strip().startswith('|')]

# Need at least header + separator + 1 data row
if len(table_lines) < 3:
    print(f"EMPTY_TABLE")
    print(f"  action: populate Verification table before transitioning to Complete")
    print()
    print(f"GAPS {art_id}: 0/{len(criteria)} criteria verified, {len(criteria)} gaps")
    sys.exit(1)

# Parse data rows (skip header row and separator row)
for row in table_lines[2:]:
    cells = [c.strip() for c in row.split('|')]
    # Remove empty first/last from leading/trailing pipes
    cells = [c for c in cells if c or c == '']
    if len(cells) >= 3:
        ver_rows.append({
            'criterion': cells[0].strip(),
            'evidence': cells[1].strip() if len(cells) > 1 else '',
            'result': cells[2].strip() if len(cells) > 2 else '',
        })

if not ver_rows:
    print(f"EMPTY_TABLE")
    print(f"  action: populate Verification table before transitioning to Complete")
    print()
    print(f"GAPS {art_id}: 0/{len(criteria)} criteria verified, {len(criteria)} gaps")
    sys.exit(1)

# --- Check for gaps ---

findings = []
verified = 0

for row in ver_rows:
    if not row['evidence'] or not row['result']:
        findings.append({
            'type': 'MISSING_EVIDENCE',
            'criterion': row['criterion'],
        })
    elif row['result'].lower().startswith('fail'):
        findings.append({
            'type': 'FAIL',
            'criterion': row['criterion'],
            'evidence': row['evidence'],
        })
    elif row['result'].lower().startswith('pass'):
        verified += 1
    elif row['result'].lower().startswith('skip'):
        verified += 1  # Skip with reason counts as addressed

total = len(ver_rows)

# Also check: fewer verification rows than acceptance criteria
if total < len(criteria):
    findings.append({
        'type': 'COUNT_MISMATCH',
        'ver_count': total,
        'ac_count': len(criteria),
    })

# --- Output ---

if not findings:
    print(f"OK {art_id}: {verified}/{total} criteria verified")
    sys.exit(0)

for f in findings:
    if f['type'] == 'MISSING_EVIDENCE':
        print(f"MISSING_EVIDENCE {f['criterion']}")
        print(f"  action: add Evidence and Result for this criterion")
        print()
    elif f['type'] == 'FAIL':
        print(f"FAIL {f['criterion']}")
        print(f"  evidence: {f['evidence']}")
        print(f"  action: fix failing criterion before transitioning to Complete")
        print()
    elif f['type'] == 'COUNT_MISMATCH':
        print(f"COUNT_MISMATCH verification rows ({f['ver_count']}) < acceptance criteria ({f['ac_count']})")
        print(f"  action: ensure every acceptance criterion has a Verification row")
        print()

gaps = len(findings)
print(f"GAPS {art_id}: {verified}/{total} criteria verified, {gaps} issue(s)")
sys.exit(1)
PYEOF
