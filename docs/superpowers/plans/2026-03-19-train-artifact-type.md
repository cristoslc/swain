# TRAIN Artifact Type Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add TRAIN-NNN as a new standing artifact type for product documentation, with enriched `linked-artifacts` for commit-pinned staleness tracking.

**Architecture:** TRAIN is a standing-track artifact (like Persona, Design, Runbook) with Diataxis-based typing (how-to, reference, quickstart). Enriched `linked-artifacts` entries support `rel` tags and commit pinning. A new `train-check.sh` script detects dependency drift. Phase transition hooks nudge TRAIN creation/updates on SPEC and EPIC completion.

**Tech Stack:** Bash (train-check.sh, specwatch, rebuild-index), Python (specgraph parser), Markdown (definitions, templates, reference docs)

**Spec:** `docs/spec/Active/(SPEC-091)-Train-Artifact-Type/SPEC-091.md`
**Design:** `docs/superpowers/specs/2026-03-19-train-artifact-and-docs-viewer-design.md`

---

## File Structure

### Files to Create

| File | Responsibility |
|------|---------------|
| `.claude/skills/swain-design/references/train-definition.md` | Artifact type definition: lifecycle, folder structure, conventions |
| `.claude/skills/swain-design/references/train-template.md.template` | Jinja2 template: frontmatter fields, document skeleton |
| `.claude/skills/swain-design/scripts/train-check.sh` | Staleness detection: diff commit pins against HEAD |
| `.claude/skills/swain-design/scripts/specgraph/tests/__init__.py` | Test package init |
| `.claude/skills/swain-design/scripts/specgraph/tests/test_parser_enriched.py` | Tests for enriched linked-artifacts parsing |
| `.claude/skills/swain-design/scripts/specgraph/tests/test_train_check.sh` | Integration tests for train-check.sh |

### Files to Modify

| File | Change |
|------|--------|
| `.claude/skills/swain-design/scripts/specgraph/parser.py` | Handle enriched list items (dict entries) in `parse_frontmatter` and `extract_list_ids` |
| `.claude/skills/swain-design/SKILL.md` | Add TRAIN to type table (line ~35) and inference table (line ~47) |
| `.claude/skills/swain-design/references/relationship-model.md` | Add TRAIN entity to ER diagram, add `documents` rel type |
| `.claude/skills/swain-design/references/phase-transitions.md` | Add SPEC/EPIC completion hooks, extend step 4e |
| `.claude/skills/swain-design/scripts/specwatch.sh` | Add `train` to TYPE_DIRS (line ~910), add train-check pass in `scan` |
| `.claude/skills/swain-design/scripts/rebuild-index.sh` | Add `train` type mapping (line ~37) |
| `.claude/skills/swain-sync/SKILL.md` | Add `train` to rebuild-index loop (line ~283), ADR path list (line ~151) |

---

## Chunk 1: Reference Documents

### Task 1: Create train-definition.md

**Files:**
- Create: `.claude/skills/swain-design/references/train-definition.md`

- [ ] **Step 1: Create the definition file**

Follow the pattern of `runbook-definition.md` and `design-definition.md`. Key elements:

```markdown
# Training Documents (TRAIN-NNN)

**Template:** [train-template.md.template](train-template.md.template)

**Lifecycle track: Standing**

\`\`\`mermaid
stateDiagram-v2
    [*] --> Proposed
    Proposed --> Active
    Active --> Retired
    Active --> Superseded
    Retired --> [*]
    Superseded --> [*]
    Proposed --> Abandoned
    Active --> Abandoned
    Abandoned --> [*]
\`\`\`

A TRAIN artifact is structured product documentation for human operators. It teaches users how to use features specified by SPECs and delivered by EPICs. TRAINs are the furthest-downstream artifact — they translate technical specifications into learning materials.

TRAIN uses the [Diataxis framework](https://diataxis.fr/) for document typing. Each TRAIN has exactly one type; never mix types in a single document.

**Train types:**
- `how-to` — goal-oriented steps for a specific task. Assumes competence. ("How to configure credential scoping")
- `reference` — factual lookup material. Descriptive, complete, neutral. ("Artifact type reference")
- `quickstart` — compressed tutorial for time-to-first-success under 10 minutes. ("Your first swain project")

Additional Diataxis types (`tutorial`, `explanation`) are not defined at launch. Add when demand emerges.

- **Folder structure:** `docs/train/<Phase>/(TRAIN-NNN)-<Title>/` — the TRAIN folder lives inside a subdirectory matching its current lifecycle phase. Phase subdirectories: `Proposed/`, `Active/`, `Retired/`, `Superseded/`.
  - Example: `docs/train/Active/(TRAIN-001)-Getting-Started/`
  - When transitioning phases, **move the folder** to the new phase directory.
  - Primary file: `(TRAIN-NNN)-<Title>.md` — the training document.
  - Supporting docs: screenshots, diagrams, example configs, exercise files.
- **Audience:** The `audience` field references PERSONAs when available or accepts free-text (e.g., "new operators", "skill authors"). It describes who the document is for.
- **Hierarchy:** `parent-epic` OR `parent-initiative`, never both (same pattern as SPEC). TRAINs without parents are valid but flagged as unanchored.
- **Default granularity:** One TRAIN per EPIC minimum. Operator-overridable via swain config.
- **Staleness tracking:** TRAINs use enriched `linked-artifacts` entries with `rel: [documents]` and commit pinning. The `train-check.sh` script detects drift between pinned commits and current HEAD. See the design doc for the enriched format specification.
- A TRAIN is "Active" when its content has been reviewed and accurately reflects the current state of the artifacts it documents. "Superseded" when a newer TRAIN replaces it (link via `superseded-by:`). "Retired" when the features it describes no longer exist.
- TRAINs do NOT replace READMEs, CLAUDE.md, or AGENTS.md (operational configuration). TRAINs do NOT replace RUNBOOKs (executable procedures with pass/fail outcomes). TRAINs are educational content with learning objectives.
```

- [ ] **Step 2: Commit**

```bash
git add .claude/skills/swain-design/references/train-definition.md
git commit -m "docs: add TRAIN artifact type definition"
```

### Task 2: Create train-template.md.template

**Files:**
- Create: `.claude/skills/swain-design/references/train-template.md.template`

- [ ] **Step 1: Create the template file**

Follow the Jinja2 pattern of existing templates (`runbook-template.md.template`, `design-template.md.template`). Include enriched `linked-artifacts` format:

```markdown
<!-- Jinja2 structural template — uses {{ variable }} placeholders. Read as a structural reference; no rendering pipeline needed. -->
---
title: "{{ title }}"
artifact: TRAIN-{{ number }}
track: standing
status: {{ status | default("Proposed") }}
train-type: {{ train_type | default("how-to") }}
audience: {{ audience | default("") }}
author: {{ author }}
created: {{ created_date }}
last-updated: {{ last_updated_date }}
parent-epic: {{ parent_epic | default("") }}
parent-initiative: {{ parent_initiative | default("") }}
linked-artifacts:
{%- for link in linked_artifacts | default([]) %}
  - artifact: {{ link.artifact }}
    rel: {{ link.rel | default("[linked]") }}
{%- if link.commit %}
    commit: {{ link.commit }}
    verified: {{ link.verified }}
{%- endif %}
{%- endfor %}
superseded-by: {{ superseded_by | default("") }}
---

# {{ title }}

## Prerequisites

{{ prerequisites | default("What the reader needs before starting (tools, access, prior knowledge).") }}

## Learning Objectives

{{ learning_objectives | default("What the reader will be able to do after completing this document.") }}

## Body

{{ body | default("The training content itself. Format varies by train-type:\n- how-to: numbered steps with expected outcomes\n- reference: structured lookup tables, parameter descriptions\n- quickstart: minimal steps to first success") }}

## Key Takeaways

{{ key_takeaways | default("Summary of essential points the reader should remember.") }}

## Next Steps

{{ next_steps | default("Links to related TRAINs or artifacts for further learning.") }}

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| {{ status | default("Draft") }} | {{ created_date }} | {{ commit_hash }} | Initial creation |
```

- [ ] **Step 2: Commit**

```bash
git add .claude/skills/swain-design/references/train-template.md.template
git commit -m "docs: add TRAIN artifact template"
```

### Task 3: Update SKILL.md — type table and inference table

**Files:**
- Modify: `.claude/skills/swain-design/SKILL.md:23-54`

- [ ] **Step 1: Add TRAIN row to the artifact type table**

After the Design row (line ~34), add:

```markdown
| Training Document (TRAIN-NNN) | Structured product documentation — how-to guides, reference material, and quickstart tutorials for human operators. Uses the Diataxis framework. | [definition](references/train-definition.md) | [template](references/train-template.md.template) |
```

- [ ] **Step 2: Add TRAIN to the "Choosing the right artifact type" inference table**

After the ADR row in the intent table (line ~47), add:

```markdown
| Teach users how to use a feature | **TRAIN** | "document this", "write a guide", "create docs", "how-to for", "reference for", "quickstart" |
```

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/swain-design/SKILL.md
git commit -m "docs: register TRAIN in swain-design artifact type tables"
```

### Task 4: Update relationship-model.md

**Files:**
- Modify: `.claude/skills/swain-design/references/relationship-model.md:3-37`

- [ ] **Step 1: Add TRAIN entity to the ER diagram**

In the Mermaid ER diagram (lines 3-25), add the TRAIN entity and its relationships:

```mermaid
    TRAIN }o--o| EPIC : "parent-epic"
    TRAIN }o--o| INITIATIVE : "parent-initiative"
    TRAIN }o--o{ SPEC : "documents (enriched)"
    TRAIN }o--o{ RUNBOOK : "documents (enriched)"
    TRAIN }o--o{ EPIC : "documents (enriched)"
```

- [ ] **Step 2: Add `documents` rel type to the relationship vocabulary**

After the existing cross-reference notes (line ~37), add a new section:

```markdown
## Enriched `linked-artifacts` format

Entries in `linked-artifacts` can be plain strings (backward compatible) or objects with explicit relationship type and optional commit pinning:

\`\`\`yaml
linked-artifacts:
  - artifact: SPEC-067
    rel: [documents]
    commit: abc1234
    verified: 2026-03-19
  - DESIGN-003              # plain string = rel: linked (default)
\`\`\`

### Relationship vocabulary

| rel | Semantics | Commit-pinnable? | Currently modeled as |
|---|---|---|---|
| `linked` | Informational cross-reference (default) | no | `linked-artifacts` (plain string) |
| `depends-on` | Blocking. Gates readiness. | no | `depends-on-artifacts` field |
| `addresses` | Traceability. Resolves a pain point. | no | `addresses` field |
| `validates` | Operational. Verifies artifact works. | no | `validates` field |
| `documents` | Content dependency. Teaches humans about this artifact. | **yes** | new (TRAIN) |

An entry can carry multiple rels (e.g., `rel: [documents, depends-on]`).

**Design bet:** The enriched format is experimental. If it proves unwieldy, fall back to a separate `dependencies` field. The commit-pinning mechanism works either way.
```

- [ ] **Step 3: Add TRAIN to the type/track table**

Add a row to the type table:

```markdown
| TRAIN | standing | Proposed → Active → Retired/Superseded | Training document for product users |
```

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/swain-design/references/relationship-model.md
git commit -m "docs: add TRAIN and documents rel type to relationship model"
```

---

## Chunk 2: Enriched `linked-artifacts` Parser

### Task 5: Write failing tests for enriched linked-artifacts parsing

**Files:**
- Create: `.claude/skills/swain-design/scripts/specgraph/tests/__init__.py`
- Create: `.claude/skills/swain-design/scripts/specgraph/tests/test_parser_enriched.py`

- [ ] **Step 1: Create test package**

```bash
mkdir -p .claude/skills/swain-design/scripts/specgraph/tests
touch .claude/skills/swain-design/scripts/specgraph/tests/__init__.py
```

- [ ] **Step 2: Write the failing tests**

```python
"""Tests for enriched linked-artifacts parsing in specgraph parser."""
import sys
from pathlib import Path

# Add parent to path so we can import parser
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from parser import parse_frontmatter, extract_list_ids


def test_plain_string_linked_artifacts_unchanged():
    """Plain string entries continue to work as before."""
    content = """---
title: "Test"
artifact: SPEC-001
linked-artifacts:
  - SPEC-002
  - DESIGN-003
---
# Body
"""
    fields = parse_frontmatter(content)
    assert fields is not None
    ids = extract_list_ids(fields, "linked-artifacts")
    assert "SPEC-002" in ids
    assert "DESIGN-003" in ids


def test_enriched_entry_parsed_as_dict():
    """Enriched entries with artifact/rel/commit become dicts in the list."""
    content = """---
title: "Test TRAIN"
artifact: TRAIN-001
linked-artifacts:
  - artifact: SPEC-067
    rel: [documents]
    commit: abc1234
    verified: 2026-03-19
---
# Body
"""
    fields = parse_frontmatter(content)
    assert fields is not None
    la = fields["linked-artifacts"]
    assert len(la) == 1
    assert isinstance(la[0], dict)
    assert la[0]["artifact"] == "SPEC-067"
    assert la[0]["rel"] == ["documents"]
    assert la[0]["commit"] == "abc1234"
    assert la[0]["verified"] == "2026-03-19"


def test_enriched_entry_extract_list_ids():
    """extract_list_ids returns artifact IDs from enriched dict entries."""
    content = """---
title: "Test TRAIN"
artifact: TRAIN-001
linked-artifacts:
  - artifact: SPEC-067
    rel: [documents]
    commit: abc1234
    verified: 2026-03-19
  - DESIGN-003
---
# Body
"""
    fields = parse_frontmatter(content)
    ids = extract_list_ids(fields, "linked-artifacts")
    assert "SPEC-067" in ids
    assert "DESIGN-003" in ids


def test_mixed_plain_and_enriched():
    """Lists can contain both plain strings and enriched dicts."""
    content = """---
title: "Test TRAIN"
artifact: TRAIN-001
linked-artifacts:
  - artifact: SPEC-067
    rel: [documents]
    commit: abc1234
    verified: 2026-03-19
  - artifact: RUNBOOK-002
    rel: [documents, depends-on]
    commit: def5678
    verified: 2026-03-19
  - DESIGN-003
---
# Body
"""
    fields = parse_frontmatter(content)
    la = fields["linked-artifacts"]
    assert len(la) == 3
    assert isinstance(la[0], dict)
    assert isinstance(la[1], dict)
    assert isinstance(la[2], str)
    assert la[1]["rel"] == ["documents", "depends-on"]


def test_enriched_multiple_rels():
    """rel field parsed as a list even with multiple values."""
    content = """---
title: "Test"
artifact: TRAIN-001
linked-artifacts:
  - artifact: SPEC-042
    rel: [documents, depends-on]
---
# Body
"""
    fields = parse_frontmatter(content)
    la = fields["linked-artifacts"]
    assert la[0]["rel"] == ["documents", "depends-on"]


def test_enriched_no_commit_pin():
    """Enriched entry without commit pin is valid (just rel, no staleness tracking)."""
    content = """---
title: "Test"
artifact: TRAIN-001
linked-artifacts:
  - artifact: SPEC-042
    rel: [documents]
---
# Body
"""
    fields = parse_frontmatter(content)
    la = fields["linked-artifacts"]
    assert isinstance(la[0], dict)
    assert la[0]["artifact"] == "SPEC-042"
    assert "commit" not in la[0]
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
cd .claude/skills/swain-design/scripts/specgraph
uv run python3 -m pytest tests/test_parser_enriched.py -v
```

Expected: FAIL — `test_enriched_entry_parsed_as_dict` and others fail because the parser doesn't handle enriched entries yet.

- [ ] **Step 4: Commit test file**

```bash
git add .claude/skills/swain-design/scripts/specgraph/tests/
git commit -m "test: add failing tests for enriched linked-artifacts parsing"
```

### Task 6: Update `parse_frontmatter` to handle enriched entries

**Files:**
- Modify: `.claude/skills/swain-design/scripts/specgraph/parser.py:68-111`

- [ ] **Step 1: Modify parse_frontmatter**

Add tracking for enriched (dict) list items. The key change: when a list item matches `key: value` pattern (like `artifact: SPEC-067`), start accumulating a dict. Subsequent indented `key: value` lines (like `rel: [documents]`) are added to that dict.

In `parse_frontmatter`, replace the loop body (lines 82-109) with:

```python
    current_list_key: Optional[str] = None
    current_item_dict: Optional[dict] = None

    for line in fm_text.splitlines():
        # Check for list item continuation
        list_match = re.match(r"^\s+-\s+(.+)$", line)
        if list_match and current_list_key is not None:
            val = list_match.group(1).strip()
            # Strip quotes
            val = re.sub(r'^["\']|["\']$', "", val)

            # Check if this list item is a YAML mapping (e.g., "artifact: SPEC-067")
            item_kv = re.match(r"^([a-z][a-z0-9-]*):\s+(.+)$", val)
            if item_kv:
                current_item_dict = {
                    item_kv.group(1): _parse_inline_value(item_kv.group(2).strip())
                }
                fields[current_list_key].append(current_item_dict)
            else:
                current_item_dict = None
                fields[current_list_key].append(val)
            continue

        # Check for enriched item continuation (indented key: value after a mapping list item)
        if current_item_dict is not None and current_list_key is not None:
            indent_kv = re.match(r"^\s+([a-z][a-z0-9-]*):\s+(.+)$", line)
            if indent_kv:
                key = indent_kv.group(1)
                val = _parse_inline_value(indent_kv.group(2).strip())
                current_item_dict[key] = val
                continue
            else:
                current_item_dict = None

        # Check for scalar field
        scalar_match = re.match(r"^([a-z][a-z0-9-]*):\s*(.*)$", line)
        if scalar_match:
            current_item_dict = None
            key = scalar_match.group(1)
            val = scalar_match.group(2).strip()
            # Strip quotes
            val = re.sub(r'^["\']|["\']$', "", val)

            if not val or val in ("[]", "~", "null"):
                fields[key] = [] if not val or val == "[]" else val
                current_list_key = key if not val or val == "[]" else None
            else:
                fields[key] = val
                current_list_key = None
        else:
            current_item_dict = None
            current_list_key = None
```

- [ ] **Step 2: Add `_parse_inline_value` helper**

Add before `parse_frontmatter` (around line 65):

```python
def _parse_inline_value(val: str) -> Any:
    """Parse an inline YAML value: [list], quoted string, or plain string."""
    val = re.sub(r'^["\']|["\']$', "", val)
    if val.startswith("[") and val.endswith("]"):
        return [v.strip() for v in val[1:-1].split(",") if v.strip()]
    return val
```

- [ ] **Step 3: Run tests to verify enriched parsing works**

```bash
cd .claude/skills/swain-design/scripts/specgraph
uv run python3 -m pytest tests/test_parser_enriched.py -v
```

Expected: All tests PASS.

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/swain-design/scripts/specgraph/parser.py
git commit -m "feat: support enriched linked-artifacts entries in frontmatter parser"
```

### Task 7: Update `extract_list_ids` to handle dict entries

**Files:**
- Modify: `.claude/skills/swain-design/scripts/specgraph/parser.py:158-168`

- [ ] **Step 1: Update extract_list_ids**

Replace lines 158-168:

```python
def extract_list_ids(fields: dict, key: str) -> list[str]:
    """Extract artifact IDs (TYPE-NNN) from a frontmatter list field.

    Handles both plain string entries and enriched dict entries
    (where the artifact ID is in the 'artifact' key).
    """
    val = fields.get(key, [])
    if isinstance(val, str):
        return _ARTIFACT_ID_RE.findall(val)
    if isinstance(val, list):
        ids = []
        for item in val:
            if isinstance(item, dict):
                artifact_val = item.get("artifact", "")
                ids.extend(_ARTIFACT_ID_RE.findall(str(artifact_val)))
            else:
                ids.extend(_ARTIFACT_ID_RE.findall(str(item)))
        return ids
    return []
```

- [ ] **Step 2: Run all tests**

```bash
cd .claude/skills/swain-design/scripts/specgraph
uv run python3 -m pytest tests/test_parser_enriched.py -v
```

Expected: All tests PASS (including `test_enriched_entry_extract_list_ids`).

- [ ] **Step 3: Run chart.sh build to verify no regression**

```bash
bash .claude/skills/swain-design/scripts/chart.sh build
```

Expected: Graph builds successfully with same node/edge counts as before (no TRAIN artifacts exist yet, so no change).

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/swain-design/scripts/specgraph/parser.py
git commit -m "feat: extract_list_ids handles enriched dict entries"
```

---

## Chunk 3: train-check.sh

### Task 8: Create train-check.sh

**Files:**
- Create: `.claude/skills/swain-design/scripts/train-check.sh`

- [ ] **Step 1: Write the script**

```bash
#!/usr/bin/env bash
# train-check.sh — Staleness detection for TRAIN artifacts.
#
# Reads enriched linked-artifacts entries with rel: [documents] and commit pins.
# Compares pinned commit hash against the documented artifact's current HEAD commit.
#
# Usage:
#   train-check.sh [path-to-train-dir]   Check a single TRAIN
#   train-check.sh                        Check all TRAINs under docs/train/
#
# Exit codes:
#   0 — all pins current
#   1 — drift found (at least one stale dependency)
#   2 — git unavailable or not in a git repo

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)" || {
    echo "train-check: git not available or not in a git repo" >&2
    exit 2
}

DOCS_DIR="$REPO_ROOT/docs"
TRAIN_DIR="$DOCS_DIR/train"
LOG_FILE="${REPO_ROOT}/.agents/train-check.log"

stale_count=0
checked_count=0

# Find the TRAIN's primary markdown file in a TRAIN directory
find_train_md() {
    local train_dir="$1"
    find "$train_dir" -maxdepth 1 -name '*TRAIN-*.md' | head -1
}

# Resolve an artifact ID to its file path
resolve_artifact_path() {
    local artifact_id="$1"
    local prefix type_dir
    prefix=$(echo "$artifact_id" | sed 's/-[0-9]*//')
    case "$prefix" in
        SPEC)       type_dir="spec" ;;
        EPIC)       type_dir="epic" ;;
        SPIKE)      type_dir="research" ;;
        ADR)        type_dir="adr" ;;
        VISION)     type_dir="vision" ;;
        INITIATIVE) type_dir="initiative" ;;
        JOURNEY)    type_dir="journey" ;;
        PERSONA)    type_dir="persona" ;;
        RUNBOOK)    type_dir="runbook" ;;
        DESIGN)     type_dir="design" ;;
        TRAIN)      type_dir="train" ;;
        *)          return 1 ;;
    esac
    # Search across all phase subdirectories
    find "$DOCS_DIR/$type_dir" -name "*${artifact_id}*" -name "*.md" 2>/dev/null | head -1
}

# Check a single TRAIN directory for stale dependencies
check_train() {
    local train_dir="$1"
    local train_md
    train_md=$(find_train_md "$train_dir")
    if [[ -z "$train_md" ]]; then
        return 0
    fi

    local train_id
    train_id=$(grep -m1 '^artifact:' "$train_md" | sed 's/artifact:\s*//' | tr -d '[:space:]')

    # Extract enriched linked-artifacts entries using Python for reliable YAML-ish parsing
    local stale_deps
    stale_deps=$(uv run python3 -c "
import sys, re

content = open('$train_md').read()
# Extract frontmatter
fm_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
if not fm_match:
    sys.exit(0)

fm = fm_match.group(1)
lines = fm.splitlines()
in_linked = False
current_entry = None
entries = []

for line in lines:
    if re.match(r'^linked-artifacts:', line):
        in_linked = True
        continue
    if in_linked:
        list_match = re.match(r'^\s+-\s+(.+)$', line)
        if list_match:
            if current_entry and 'artifact' in current_entry:
                entries.append(current_entry)
            val = list_match.group(1).strip()
            kv = re.match(r'^([a-z][a-z0-9-]*):\s+(.+)$', val)
            if kv:
                current_entry = {kv.group(1): kv.group(2).strip()}
            else:
                current_entry = None
            continue
        indent_kv = re.match(r'^\s+([a-z][a-z0-9-]*):\s+(.+)$', line)
        if indent_kv and current_entry is not None:
            val = indent_kv.group(2).strip()
            if val.startswith('[') and val.endswith(']'):
                val = [v.strip() for v in val[1:-1].split(',') if v.strip()]
            current_entry[indent_kv.group(1)] = val
            continue
        if re.match(r'^[a-z]', line):
            in_linked = False
            if current_entry and 'artifact' in current_entry:
                entries.append(current_entry)
            current_entry = None

if current_entry and 'artifact' in current_entry:
    entries.append(current_entry)

# Filter for documents rel with commit pins
for e in entries:
    rel = e.get('rel', [])
    if isinstance(rel, str):
        rel = [rel]
    if 'documents' not in rel:
        continue
    commit = e.get('commit')
    if not commit:
        continue
    artifact_id = e['artifact']
    print(f'{artifact_id}\t{commit}')
" 2>/dev/null) || return 0

    if [[ -z "$stale_deps" ]]; then
        return 0
    fi

    local found_stale=0
    while IFS=$'\t' read -r dep_id pinned_commit; do
        local dep_path
        dep_path=$(resolve_artifact_path "$dep_id")
        if [[ -z "$dep_path" ]]; then
            echo "WARN: $train_id → $dep_id (artifact not found)" | tee -a "$LOG_FILE"
            continue
        fi

        local current_commit
        current_commit=$(git -C "$REPO_ROOT" log -1 --format=%H -- "$dep_path" 2>/dev/null) || continue

        checked_count=$((checked_count + 1))

        if [[ "$pinned_commit" != "$current_commit" ]]; then
            local behind
            behind=$(git -C "$REPO_ROOT" rev-list --count "${pinned_commit}..${current_commit}" 2>/dev/null) || behind="?"
            echo "STALE: $train_id → $dep_id (pinned: $pinned_commit, current: $current_commit, $behind commits behind)" | tee -a "$LOG_FILE"
            found_stale=1
            stale_count=$((stale_count + 1))
        fi
    done <<< "$stale_deps"

    return $found_stale
}

# Main
mkdir -p "$(dirname "$LOG_FILE")"
> "$LOG_FILE"

if [[ $# -ge 1 ]]; then
    # Check a single TRAIN
    check_train "$1" || true
else
    # Check all TRAINs
    if [[ ! -d "$TRAIN_DIR" ]]; then
        echo "train-check: no docs/train/ directory found" >&2
        exit 0
    fi
    while read -r dir; do
        check_train "$dir" || true
    done < <(find "$TRAIN_DIR" -mindepth 2 -maxdepth 3 -type d -name '*TRAIN-*' 2>/dev/null)
fi

if [[ $stale_count -gt 0 ]]; then
    echo "train-check: found $stale_count stale dependency(ies) across $checked_count checked." | tee -a "$LOG_FILE"
    exit 1
elif [[ $checked_count -gt 0 ]]; then
    echo "train-check: $checked_count dependency(ies) checked, all current."
    exit 0
else
    echo "train-check: no pinned dependencies found."
    exit 0
fi
```

- [ ] **Step 2: Make executable**

```bash
chmod +x .claude/skills/swain-design/scripts/train-check.sh
```

- [ ] **Step 3: Smoke test with no TRAIN artifacts**

```bash
bash .claude/skills/swain-design/scripts/train-check.sh
```

Expected: `train-check: no docs/train/ directory found` and exit 0.

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/swain-design/scripts/train-check.sh
git commit -m "feat: add train-check.sh for TRAIN staleness detection"
```

---

## Chunk 4: Tooling Integration

### Task 9: Update specwatch.sh — TYPE_DIRS and train-check pass

**Files:**
- Modify: `.claude/skills/swain-design/scripts/specwatch.sh:908-911` (TYPE_DIRS)
- Modify: `.claude/skills/swain-design/scripts/specwatch.sh:1073-1081` (scan subcommand)

- [ ] **Step 1: Add `train` to TYPE_DIRS**

In the Python heredoc inside `phase_fix()` (line ~910), change:

```python
TYPE_DIRS = {
    'vision', 'journey', 'epic', 'story', 'spec',
    'research', 'adr', 'persona', 'runbook', 'design'
}
```

to:

```python
TYPE_DIRS = {
    'vision', 'journey', 'epic', 'story', 'spec',
    'research', 'adr', 'persona', 'runbook', 'design', 'train'
}
```

- [ ] **Step 2: Add train-check pass to the `scan` subcommand**

In the `scan)` case (line ~1073), add a `train-check` call after `scan_arch_diagrams`:

```bash
scan)
    scan_stale_refs "full" || scan_result=$?
    scan_result="${scan_result:-0}"
    scan_tk_sync || tk_result=$?
    tk_result="${tk_result:-0}"
    scan_arch_diagrams || arch_result=$?
    arch_result="${arch_result:-0}"
    # TRAIN staleness check
    train_result=0
    train_check_script="$(dirname "${BASH_SOURCE[0]}")/train-check.sh"
    if [[ -x "$train_check_script" ]]; then
        bash "$train_check_script" || train_result=$?
        if [[ $train_result -eq 2 ]]; then
            train_result=0  # git unavailable is not a scan failure
        fi
    fi
    exit $(( scan_result > 0 || tk_result > 0 || arch_result > 0 || train_result > 0 ? 1 : 0 ))
    ;;
```

- [ ] **Step 3: Test specwatch scan still works**

```bash
bash .claude/skills/swain-design/scripts/specwatch.sh scan
```

Expected: Normal scan output plus `train-check: no docs/train/ directory found` (or similar).

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/swain-design/scripts/specwatch.sh
git commit -m "feat: add train to specwatch TYPE_DIRS and scan pipeline"
```

### Task 10: Update rebuild-index.sh

**Files:**
- Modify: `.claude/skills/swain-design/scripts/rebuild-index.sh:27-37`

- [ ] **Step 1: Add `train` type mapping**

After the `journey)` line (line ~36), before the `*)` catch-all, add:

```bash
    train)    title="Training Documents" ;;
```

- [ ] **Step 2: Commit**

```bash
git add .claude/skills/swain-design/scripts/rebuild-index.sh
git commit -m "feat: add train type mapping to rebuild-index.sh"
```

### Task 11: Verify adr-check.sh handles TRAIN artifacts

**Files:**
- Verify: `.claude/skills/swain-design/scripts/adr-check.sh`

`adr-check.sh` accepts an artifact path as its `$1` argument — it doesn't maintain its own list of artifact directories. Any artifact file can be passed to it. The gating of which directories trigger ADR checks lives in `swain-sync/SKILL.md` (the ADR compliance path list updated in Task 12). No code changes needed in `adr-check.sh` itself.

- [ ] **Step 1: Verify adr-check.sh works with a TRAIN path**

```bash
# Create a minimal test file
mkdir -p docs/train/Active/test-train
echo -e "---\ntitle: test\nartifact: TRAIN-999\n---\n# Test" > docs/train/Active/test-train/TRAIN-999.md
bash .claude/skills/swain-design/scripts/adr-check.sh docs/train/Active/test-train/TRAIN-999.md
rm -rf docs/train/Active/test-train
```

Expected: `OK TRAIN-999: no ADR compliance findings`

### Task 12: Update swain-sync SKILL.md (was Task 11)

**Files:**
- Modify: `.claude/skills/swain-sync/SKILL.md:151` (ADR compliance path list)
- Modify: `.claude/skills/swain-sync/SKILL.md:283` (rebuild-index type loop)

- [ ] **Step 1: Add `docs/train/` to ADR compliance path list**

At line ~151, add `docs/train/` to the comma-separated path list.

- [ ] **Step 2: Add `train` to rebuild-index type loop**

At line ~283, change:

```bash
for type in spec epic spike adr persona runbook design vision journey; do
```

to:

```bash
for type in spec epic spike adr persona runbook design vision journey train; do
```

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/swain-sync/SKILL.md
git commit -m "feat: add train to swain-sync index rebuild and ADR compliance paths"
```

---

## Chunk 5: Phase Transition Hooks

### Task 13: Update phase-transitions.md — SPEC/EPIC hooks and step 4e

**Files:**
- Modify: `.claude/skills/swain-design/references/phase-transitions.md`

- [ ] **Step 1: Extend step 4e to include TRAINs**

At step 4e (line ~20), in the instruction that says "scan for artifacts whose assumptions may be invalidated," add TRAINs to the scope. After point 2 ("Query `chart.sh scope <SPIKE-ID>` to identify sibling artifacts"), add:

```markdown
   2b. Additionally scan `docs/train/` for TRAINs whose `linked-artifacts` contain any artifact in the same parent-vision or parent-initiative scope with `rel: [documents]`.
```

And in point 3, change "For each sibling that is Complete or Active" to:

```markdown
   3. For each sibling (SPEC, EPIC, or TRAIN) that is Complete or Active, check whether any acceptance criteria, documented behavior, or training content contradict the spike's findings.
```

- [ ] **Step 2: Add SPEC completion hook**

After the existing completion rules section, add a new subsection:

```markdown
### TRAIN documentation hooks

**On SPEC completion** (`In Progress → Needs Manual Test` or `Needs Manual Test → Complete`):
1. Scan `docs/train/` for TRAINs whose enriched `linked-artifacts` contain this SPEC with `rel: [documents]`.
2. If found: surface advisory — "SPEC-NNN completed. TRAIN-NNN documents this spec — review for updates." Strong preference for updating existing TRAINs over creating new ones.
3. If not found: no action (documentation is optional per-SPEC).

**On EPIC completion** (`Active → Complete`):
1. Collect all SPECs under this EPIC.
2. Scan `docs/train/` for TRAINs documenting any of those SPECs.
3. If TRAINs found: surface advisory — "EPIC-NNN completed. TRAIN-NNN documents features from this epic — review for updates."
4. If no TRAINs found: surface suggestion — "EPIC-NNN completed with no linked TRAIN artifacts. Consider documenting: [epic title]."
5. The agent/subagent/MCP tool drafts the TRAIN; the operator reviews.
```

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/swain-design/references/phase-transitions.md
git commit -m "feat: add TRAIN hooks to phase transitions (SPEC/EPIC completion, step 4e)"
```

---

## Chunk 6: End-to-End Verification

### Task 14: Create a test TRAIN artifact and verify full pipeline

**Files:**
- Create: `docs/train/Active/(TRAIN-001)-Test-TRAIN/` (temporary, for verification)

- [ ] **Step 1: Create a test TRAIN artifact with enriched linked-artifacts**

Create `docs/train/Active/(TRAIN-001)-Test-TRAIN/(TRAIN-001)-Test-TRAIN.md` using the template. Link it to an existing SPEC with a stale commit pin (use an old commit hash).

- [ ] **Step 2: Verify chart.sh build includes TRAIN node**

```bash
bash .claude/skills/swain-design/scripts/chart.sh build
```

Expected: Node count increases by 1. TRAIN-001 appears in the graph.

- [ ] **Step 3: Verify train-check.sh detects staleness**

```bash
bash .claude/skills/swain-design/scripts/train-check.sh
```

Expected: `STALE: TRAIN-001 → SPEC-NNN (pinned: ..., current: ..., N commits behind)`

- [ ] **Step 4: Verify specwatch scan includes train-check**

```bash
bash .claude/skills/swain-design/scripts/specwatch.sh scan
```

Expected: Scan output includes train-check findings.

- [ ] **Step 5: Verify adr-check.sh processes the TRAIN**

```bash
bash .claude/skills/swain-design/scripts/adr-check.sh "docs/train/Active/(TRAIN-001)-Test-TRAIN/(TRAIN-001)-Test-TRAIN.md"
```

Expected: `OK TRAIN-001: no ADR compliance findings`

- [ ] **Step 6: Verify rebuild-index.sh handles train type**

```bash
bash .claude/skills/swain-design/scripts/rebuild-index.sh train
```

Expected: Creates `docs/train/list-train.md` with TRAIN-001 listed.

- [ ] **Step 7: Clean up test artifact**

```bash
rm -rf docs/train/Active/(TRAIN-001)-Test-TRAIN/
rm -f docs/train/list-train.md
```

- [ ] **Step 8: Final commit**

```bash
git add -A
git commit -m "feat(SPEC-091): TRAIN artifact type complete — definition, template, parser, staleness detection, tooling integration"
```
