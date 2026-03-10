#!/bin/bash
# adr-check.sh — Check an artifact against Adopted ADRs for compliance gaps.
# Deterministic frontmatter checks: linkage relevance, retired/superseded deps,
# date-based staleness. Content-level review is left to the calling agent.
#
# Output goes to stdout in a structured format. Exit 0 = clean or advisory only,
# exit 1 = findings that need attention, exit 2 = usage error.

set -euo pipefail

# --- Resolve repo root ---
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "Error: not inside a git repository" >&2
  exit 2
}
DOCS_DIR="$REPO_ROOT/docs"
ADR_ADOPTED_DIR="$DOCS_DIR/adr/Adopted"
ADR_RETIRED_DIR="$DOCS_DIR/adr/Retired"
ADR_SUPERSEDED_DIR="$DOCS_DIR/adr/Superseded"

usage() {
  cat <<'USAGE'
Usage: adr-check.sh <artifact-path>

Checks an artifact against all Adopted ADRs for:
  1. Linkage relevance — Adopted ADRs whose scope overlaps the artifact
  2. Retired/Superseded deps — artifact references a dead ADR
  3. Staleness — ADR adopted after artifact was last updated

Output format:
  RELEVANT <adr-id> <artifact-id>
    reason: <why this ADR is relevant>
    decision: <first sentence of the Decision section>
    action: review

  DEAD_REF <artifact-id> -> <adr-id>
    phase: <Retired|Superseded>
    superseded-by: <replacement-adr-id|NONE>
    action: review against replacement | reassess without backing decision

  STALE <artifact-id> last-updated:<date> < <adr-id> adopted:<date>
    decision: <first sentence of the Decision section>
    action: review artifact against decision adopted since last edit

Exit codes:
  0  No findings (or advisory only)
  1  Findings that need attention
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

# --- Python does all the heavy lifting ---
uv run python3 - "$ARTIFACT_PATH" "$DOCS_DIR" "$ADR_ADOPTED_DIR" "$ADR_RETIRED_DIR" "$ADR_SUPERSEDED_DIR" <<'PYEOF'
import os, re, sys, glob
from datetime import datetime

artifact_path = sys.argv[1]
docs_dir = sys.argv[2]
adr_adopted_dir = sys.argv[3]
adr_retired_dir = sys.argv[4]
adr_superseded_dir = sys.argv[5]

findings = []

# --- Frontmatter parser ---

def parse_frontmatter(filepath):
    """Return dict of frontmatter fields and raw body text."""
    try:
        with open(filepath) as f:
            lines = f.readlines()
    except (OSError, UnicodeDecodeError):
        return {}, ""

    if not lines or lines[0].strip() != '---':
        return {}, "".join(lines)

    fm = {}
    current_key = None
    current_list = []
    body_start = len(lines)

    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            body_start = i + 1
            break
        # List continuation
        if line.startswith('  - ') and current_key:
            current_list.append(line.strip().lstrip('- ').strip())
            fm[current_key] = current_list
            continue
        # New key
        m = re.match(r'^(\S[^:]*?):\s*(.*)', line)
        if m:
            current_key = m.group(1).strip()
            val = m.group(2).strip()
            if val:
                fm[current_key] = val
                current_list = []
            else:
                current_list = []
                fm[current_key] = current_list
        else:
            current_key = None
            current_list = []

    body = "".join(lines[body_start:])
    return fm, body


def extract_artifact_id(fm):
    """Get artifact ID from frontmatter."""
    return fm.get('artifact', '')


def extract_list(fm, key):
    """Get a list field from frontmatter, normalizing to list."""
    val = fm.get(key, [])
    if isinstance(val, str):
        return [v.strip() for v in val.split(',') if v.strip()] if val else []
    return val


def get_decision_summary(body):
    """Extract first sentence of the Decision section."""
    m = re.search(r'##\s*Decision\s*\n+(.*?)(?:\n\n|\n##|\Z)', body, re.DOTALL)
    if not m:
        return "(no Decision section found)"
    text = m.group(1).strip()
    # First sentence
    sent = re.split(r'(?<=[.!?])\s', text, maxsplit=1)
    return sent[0] if sent else text[:200]


def get_adopted_date(body):
    """Extract the date when the ADR entered Adopted phase from lifecycle table."""
    for line in body.split('\n'):
        if re.search(r'\|\s*Adopted\s*\|', line):
            m = re.search(r'\|\s*(\d{4}-\d{2}-\d{2})\s*\|', line)
            if m:
                return m.group(1)
    return None


def parse_date(date_str):
    """Parse YYYY-MM-DD date string."""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except (ValueError, TypeError):
        return None


def find_adr_files(directory):
    """Find all .md files in a directory (non-recursive, skip list-*)."""
    if not os.path.isdir(directory):
        return []
    return [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.endswith('.md') and not f.startswith('list-')
    ]


def extract_adr_refs_from_body(body):
    """Find all ADR-NNN references in body text."""
    return set(re.findall(r'ADR-\d+', body))


# --- Parse the target artifact ---

art_fm, art_body = parse_frontmatter(artifact_path)
art_id = extract_artifact_id(art_fm)
art_last_updated = art_fm.get('last-updated', art_fm.get('created', ''))
art_parent_epic = art_fm.get('parent-epic', '')
art_linked_adrs = set(extract_list(art_fm, 'linked-adrs'))
art_linked_epics = set(extract_list(art_fm, 'linked-epics'))
art_linked_specs = set(extract_list(art_fm, 'linked-specs'))
art_depends_on = set(extract_list(art_fm, 'depends-on'))
art_linked_research = set(extract_list(art_fm, 'linked-research'))
art_type = art_id.split('-')[0] if '-' in art_id else ''

# All ADR refs the artifact mentions (frontmatter + body)
art_all_adr_refs = set()
art_all_adr_refs.update(art_linked_adrs)
art_all_adr_refs.update(r for r in art_depends_on if r.startswith('ADR-'))
art_all_adr_refs.update(r for r in art_linked_research if r.startswith('ADR-'))
art_all_adr_refs.update(extract_adr_refs_from_body(art_body))

# --- Sibling resolution (for non-ADR artifacts under an epic) ---
# Find sibling specs under the same parent epic for broader ADR matching.

sibling_specs = set()
if art_parent_epic:
    for root, dirs, files in os.walk(docs_dir):
        for fname in files:
            if not fname.endswith('.md') or fname.startswith('list-'):
                continue
            fpath = os.path.join(root, fname)
            try:
                with open(fpath) as f:
                    head = f.read(2000)
            except (OSError, UnicodeDecodeError):
                continue
            if f'parent-epic: {art_parent_epic}' in head:
                m = re.search(r'artifact:\s*(SPEC-\d+)', head)
                if m and m.group(1) != art_id:
                    sibling_specs.add(m.group(1))

# --- Check 1: Adopted ADR relevance ---

adopted_files = find_adr_files(adr_adopted_dir)

for adr_path in adopted_files:
    adr_fm, adr_body = parse_frontmatter(adr_path)
    adr_id = extract_artifact_id(adr_fm)
    if not adr_id:
        continue

    # Skip self-check (when checking an ADR against itself)
    if adr_id == art_id:
        continue

    adr_linked_epics = set(extract_list(adr_fm, 'linked-epics'))
    adr_linked_specs = set(extract_list(adr_fm, 'linked-specs'))
    adr_depends_on = set(extract_list(adr_fm, 'depends-on'))
    decision_summary = get_decision_summary(adr_body)

    reasons = []

    if art_type == 'ADR':
        # ADR-on-ADR checks
        # Overlapping epics
        overlap_epics = art_linked_epics & adr_linked_epics
        if overlap_epics:
            reasons.append(f"shared linked-epics: {', '.join(sorted(overlap_epics))}")
        # Overlapping specs
        overlap_specs = art_linked_specs & adr_linked_specs
        if overlap_specs:
            reasons.append(f"shared linked-specs: {', '.join(sorted(overlap_specs))}")
        # Direct dependency
        if adr_id in art_depends_on:
            reasons.append(f"artifact depends-on {adr_id}")
        if art_id in adr_depends_on:
            reasons.append(f"{adr_id} depends-on artifact")
    else:
        # Non-ADR artifact checks
        # Direct linkage to this artifact
        if art_id in adr_linked_epics or art_id in adr_linked_specs:
            reasons.append(f"directly linked via frontmatter")
        # Parent epic linkage
        if art_parent_epic and art_parent_epic in adr_linked_epics:
            reasons.append(f"linked to parent epic {art_parent_epic}")
        # Sibling spec linkage
        overlap_siblings = sibling_specs & adr_linked_specs
        if overlap_siblings:
            reasons.append(f"linked to sibling specs: {', '.join(sorted(overlap_siblings))}")

    if reasons:
        # Check staleness: was ADR adopted after artifact was last updated?
        adopted_date = get_adopted_date(adr_body)
        art_date = parse_date(art_last_updated)
        adr_date = parse_date(adopted_date) if adopted_date else None
        stale = False
        if art_date and adr_date and adr_date > art_date:
            stale = True

        findings.append({
            'type': 'RELEVANT',
            'adr_id': adr_id,
            'art_id': art_id,
            'reasons': reasons,
            'decision': decision_summary,
            'stale': stale,
            'adopted_date': adopted_date,
            'art_last_updated': art_last_updated,
        })

# --- Check 2: References to Retired/Superseded ADRs ---

dead_dirs = [
    (adr_retired_dir, 'Retired'),
    (adr_superseded_dir, 'Superseded'),
]

for dead_dir, phase in dead_dirs:
    for adr_path in find_adr_files(dead_dir):
        adr_fm, adr_body = parse_frontmatter(adr_path)
        adr_id = extract_artifact_id(adr_fm)
        if not adr_id:
            continue

        if adr_id in art_all_adr_refs:
            superseded_by = adr_fm.get('superseded-by', 'NONE')
            if isinstance(superseded_by, list):
                superseded_by = ', '.join(superseded_by) if superseded_by else 'NONE'
            findings.append({
                'type': 'DEAD_REF',
                'adr_id': adr_id,
                'art_id': art_id,
                'phase': phase,
                'superseded_by': superseded_by if superseded_by else 'NONE',
            })

# --- Check 3: Pure staleness (relevant ADRs adopted after last update) ---
# Already captured in Check 1's stale flag, emitted as separate STALE entries.

# --- Output ---

if not findings:
    print(f"OK {art_id}: no ADR compliance findings")
    sys.exit(0)

has_actionable = False

for f in findings:
    if f['type'] == 'RELEVANT':
        print(f"RELEVANT {f['adr_id']} {f['art_id']}")
        print(f"  reason: {'; '.join(f['reasons'])}")
        print(f"  decision: {f['decision']}")
        if f['stale']:
            has_actionable = True
            print(f"  stale: artifact last-updated {f['art_last_updated']} < ADR adopted {f['adopted_date']}")
            print(f"  action: review artifact against decision adopted since last edit")
        else:
            print(f"  action: review content for compliance")
        print()

    elif f['type'] == 'DEAD_REF':
        has_actionable = True
        print(f"DEAD_REF {f['art_id']} -> {f['adr_id']}")
        print(f"  phase: {f['phase']}")
        print(f"  superseded-by: {f['superseded_by']}")
        if f['superseded_by'] != 'NONE':
            print(f"  action: review against replacement {f['superseded_by']}")
        else:
            print(f"  action: reassess without backing decision")
        print()

sys.exit(1 if has_actionable else 0)
PYEOF
