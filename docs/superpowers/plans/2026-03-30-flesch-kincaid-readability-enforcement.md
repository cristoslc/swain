# Flesch-Kincaid Readability Enforcement Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a deterministic readability scoring script and governance rule so all swain artifacts meet Flesch-Kincaid grade <= 9.

**Architecture:** A bash script (`readability-check.sh`) strips markdown non-prose content and delegates FK scoring to Python via `uv run --with textstat`. A governance paragraph in AGENTS.content.md makes the check mandatory. A shared protocol doc gives skills the exact integration contract.

**Tech Stack:** Bash, Python (textstat via uv), Markdown

---

## Chunk 1: readability-check.sh Script

### Task 1: Create test fixtures

**Files:**
- Create: `skills/swain-design/tests/fixtures/readability-pass.md`
- Create: `skills/swain-design/tests/fixtures/readability-fail.md`
- Create: `skills/swain-design/tests/fixtures/readability-skip.md`
- Create: `skills/swain-design/tests/fixtures/readability-mixed-content.md`

- [ ] **Step 1: Create a passing fixture (grade <= 9)**

```markdown
---
title: "Simple Spec"
artifact: SPEC-999
status: Active
---

# Simple Spec

## Problem

The cat sat on the mat. The dog ran in the park. Birds fly in the sky.
We need a tool that checks how hard text is to read. The tool scores each
file. If the score is too high, the writer makes the text simpler.
Short words help. Short sentences help more. Active voice is best.
The reader should not need a dictionary. Clear writing saves time for
everyone who reads it. We want all docs to be easy to read.
```

- [ ] **Step 2: Create a failing fixture (grade > 9)**

```markdown
---
title: "Complex Spec"
artifact: SPEC-998
status: Active
---

# Complex Spec

## Problem

The implementation necessitates a comprehensive understanding of the
multifaceted architectural considerations that fundamentally underpin
the sophisticated infrastructure requirements. Furthermore, the
systematization of the organizational methodology requires an
extraordinarily meticulous examination of the interdependent
subsystem configurations and their corresponding operational
characteristics within the broader ecosystem of enterprise-grade
distributed computational frameworks and paradigms.
```

- [ ] **Step 3: Create a skip fixture (< 50 words after stripping)**

```markdown
---
title: "Tiny ADR"
artifact: ADR-999
status: Adopted
---

# Tiny ADR

## Decision

Use PostgreSQL.
```

- [ ] **Step 4: Create a mixed-content fixture (frontmatter, code, tables, prose)**

This file tests that stripping works correctly — the prose itself is simple but the file contains complex non-prose content.

```markdown
---
title: "Mixed Content Spec"
artifact: SPEC-997
status: Active
parent-initiative: INITIATIVE-019
linked-artifacts:
  - EPIC-042
  - ADR-015
---

# Mixed Content Spec

## Problem

The tool must strip code and tables before scoring. Only prose should count.

## External Behavior

```python
def extraordinarily_complex_implementation_methodology():
    systematization = "multifaceted_architectural_considerations"
    return comprehensively_evaluate_interdependent_subsystems(systematization)
```

| Column With Extraordinarily Long Multisyllabic Header | Another Disproportionately Verbose Column |
|-------------------------------------------------------|------------------------------------------|
| extraordinarily_complex_value | systematization_methodology |

## Scope

The tool reads files and scores the prose. It strips out code blocks,
tables, frontmatter, and inline code like `extraordinarily_complex_method()`.
It also strips URLs like https://extraordinarily-complex-url.example.com/path
and images like ![extraordinarily complex](./image.png).

Simple prose is what remains. The tool scores only that.
```

- [ ] **Step 5: Commit fixtures**

```bash
git add skills/swain-design/tests/fixtures/readability-*.md
git commit -m "test(SPEC-194): add readability check fixtures"
```

### Task 2: Write the test script

**Files:**
- Create: `skills/swain-design/tests/test-readability-check.sh`

- [ ] **Step 1: Write the test script**

Follow the pattern from `test-next-artifact-id.sh` — pure bash with assert helper, PASS/FAIL counters.

```bash
#!/usr/bin/env bash
# test-readability-check.sh — tests for readability-check.sh (SPEC-194)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
SCRIPT="$REPO_ROOT/.agents/bin/readability-check.sh"
FIXTURES="$(cd "$(dirname "$0")" && pwd)/fixtures"

PASS=0
FAIL=0
TOTAL=0

assert() {
  local desc="$1"
  local result="$2"
  TOTAL=$((TOTAL + 1))
  if [[ "$result" == "0" ]]; then
    PASS=$((PASS + 1))
    echo "  PASS: $desc"
  else
    FAIL=$((FAIL + 1))
    echo "  FAIL: $desc"
  fi
}

# --- Test 1: Script exists and is executable ---
echo "Test 1: readability-check.sh exists and is executable"
assert "script exists" "$([ -f "$SCRIPT" ] && echo 0 || echo 1)"
assert "script is executable" "$([ -x "$SCRIPT" ] && echo 0 || echo 1)"

# --- Test 2: PASS on simple prose ---
echo "Test 2: PASS on simple prose (grade <= 9)"
output=$(bash "$SCRIPT" "$FIXTURES/readability-pass.md" 2>/dev/null || true)
assert "outputs PASS" "$(echo "$output" | grep -q '^PASS' && echo 0 || echo 1)"
exit_code=0
bash "$SCRIPT" "$FIXTURES/readability-pass.md" >/dev/null 2>&1 || exit_code=$?
assert "exits 0" "$([ "$exit_code" -eq 0 ] && echo 0 || echo 1)"

# --- Test 3: FAIL on complex prose ---
echo "Test 3: FAIL on complex prose (grade > 9)"
output=$(bash "$SCRIPT" "$FIXTURES/readability-fail.md" 2>/dev/null || true)
assert "outputs FAIL" "$(echo "$output" | grep -q '^FAIL' && echo 0 || echo 1)"
exit_code=0
bash "$SCRIPT" "$FIXTURES/readability-fail.md" >/dev/null 2>&1 || exit_code=$?
assert "exits 1" "$([ "$exit_code" -eq 1 ] && echo 0 || echo 1)"

# --- Test 4: SKIP on tiny file ---
echo "Test 4: SKIP on file with < 50 words of prose"
output=$(bash "$SCRIPT" "$FIXTURES/readability-skip.md" 2>/dev/null || true)
assert "outputs SKIP" "$(echo "$output" | grep -q '^SKIP' && echo 0 || echo 1)"
exit_code=0
bash "$SCRIPT" "$FIXTURES/readability-skip.md" >/dev/null 2>&1 || exit_code=$?
assert "exits 0 for SKIP" "$([ "$exit_code" -eq 0 ] && echo 0 || echo 1)"

# --- Test 5: Stripping removes non-prose content ---
echo "Test 5: mixed-content file strips code/tables/frontmatter"
output=$(bash "$SCRIPT" "$FIXTURES/readability-mixed-content.md" 2>/dev/null || true)
assert "outputs PASS (prose is simple after stripping)" "$(echo "$output" | grep -q '^PASS' && echo 0 || echo 1)"

# --- Test 6: --threshold flag ---
echo "Test 6: --threshold override"
exit_code=0
bash "$SCRIPT" --threshold 12 "$FIXTURES/readability-fail.md" >/dev/null 2>&1 || exit_code=$?
# The fail fixture is ~grade 15+, so threshold 12 should still fail
# Use the pass fixture with threshold 1 to test that threshold lowers the bar
exit_code_low=0
bash "$SCRIPT" --threshold 1 "$FIXTURES/readability-pass.md" >/dev/null 2>&1 || exit_code_low=$?
assert "threshold 1 fails even simple prose" "$([ "$exit_code_low" -eq 1 ] && echo 0 || echo 1)"

# --- Test 7: --json flag ---
echo "Test 7: --json outputs valid JSON"
json_output=$(bash "$SCRIPT" --json "$FIXTURES/readability-pass.md" 2>/dev/null || true)
assert "output is valid JSON" "$(echo "$json_output" | python3 -m json.tool >/dev/null 2>&1 && echo 0 || echo 1)"
assert "JSON has result field" "$(echo "$json_output" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d[0]['result']=='PASS'" 2>/dev/null && echo 0 || echo 1)"

# --- Test 8: Multiple files, one fail ---
echo "Test 8: multiple files with mixed results"
exit_code=0
output=$(bash "$SCRIPT" "$FIXTURES/readability-pass.md" "$FIXTURES/readability-fail.md" 2>/dev/null) || exit_code=$?
assert "exits 1 when any file fails" "$([ "$exit_code" -eq 1 ] && echo 0 || echo 1)"
line_count=$(echo "$output" | wc -l | tr -d ' ')
assert "reports both files" "$([ "$line_count" -ge 2 ] && echo 0 || echo 1)"

# --- Summary ---
echo ""
echo "Results: $PASS/$TOTAL passed, $FAIL failed"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
```

- [ ] **Step 2: Make it executable**

```bash
chmod +x skills/swain-design/tests/test-readability-check.sh
```

- [ ] **Step 3: Run the test to verify it fails (script doesn't exist yet)**

```bash
bash skills/swain-design/tests/test-readability-check.sh
```

Expected: FAIL on "script exists" and all subsequent tests.

- [ ] **Step 4: Commit test script**

```bash
git add skills/swain-design/tests/test-readability-check.sh
git commit -m "test(SPEC-194): add readability-check.sh test script"
```

### Task 3: Implement readability-check.sh

**Files:**
- Create: `skills/swain-design/scripts/readability-check.sh`
- Create: `.agents/bin/readability-check.sh` (symlink)

- [ ] **Step 1: Write the script**

```bash
#!/usr/bin/env bash
# readability-check.sh — Score markdown artifacts for Flesch-Kincaid readability (SPEC-194)
#
# Strips non-prose content (frontmatter, code blocks, tables, URLs, images,
# HTML tags, inline code) then scores remaining prose via textstat.
#
# Usage: readability-check.sh [--threshold N] [--json] <file> [file ...]
# Output: PASS/FAIL/SKIP per file with grade level
# Exit codes:
#   0  All files PASS or SKIP
#   1  One or more files FAIL
#   3  Usage error

set -euo pipefail

THRESHOLD=9
JSON_MODE=false
FILES=()

usage() {
  cat <<'USAGE'
Usage: readability-check.sh [--threshold N] [--json] <file> [file ...]

Scores markdown files for Flesch-Kincaid grade level on prose content only.
Non-prose content (frontmatter, code blocks, tables, etc.) is stripped first.

Options:
  --threshold N   Grade-level ceiling (default: 9)
  --json          Output JSON array instead of text lines

Output (text mode):
  PASS  <file>  grade=<N>
  FAIL  <file>  grade=<N>
  SKIP  <file>  words=<N>

Exit codes:
  0  All files PASS or SKIP
  1  One or more files FAIL
  3  Usage error
USAGE
}

# --- Arg parsing ---
while [[ $# -gt 0 ]]; do
  case "$1" in
    --threshold)
      THRESHOLD="$2"
      shift 2
      ;;
    --json)
      JSON_MODE=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    -*)
      echo "Error: unknown flag $1" >&2
      usage >&2
      exit 3
      ;;
    *)
      FILES+=("$1")
      shift
      ;;
  esac
done

if [[ ${#FILES[@]} -eq 0 ]]; then
  echo "Error: no files provided" >&2
  usage >&2
  exit 3
fi

# --- Score files via Python ---
HAS_FAILURE=false

# Build file list as newline-separated for the Python script
FILE_LIST=""
for f in "${FILES[@]}"; do
  if [[ ! -f "$f" ]]; then
    echo "Error: file not found: $f" >&2
    exit 3
  fi
  FILE_LIST+="$f"$'\n'
done

RESULTS=$(echo "$FILE_LIST" | uv run --with textstat python3 -c "
import sys, re, json
import textstat

def strip_markdown(text):
    # Strip YAML frontmatter
    text = re.sub(r'^---\n.*?\n---\n', '', text, count=1, flags=re.DOTALL)
    # Strip fenced code blocks (backtick and tilde)
    text = re.sub(r'^\`\`\`.*?\`\`\`', '', text, flags=re.DOTALL | re.MULTILINE)
    text = re.sub(r'^~~~.*?~~~', '', text, flags=re.DOTALL | re.MULTILINE)
    # Strip HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Strip markdown tables (lines starting with |)
    text = re.sub(r'^\|.*\|$', '', text, flags=re.MULTILINE)
    # Strip images
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    # Strip URLs (standalone and in links)
    text = re.sub(r'\[([^\]]*)\]\([^\)]*\)', r'\1', text)
    text = re.sub(r'https?://\S+', '', text)
    # Strip inline code
    text = re.sub(r'\`[^\`]+\`', '', text)
    # Strip markdown headings markers (keep the text)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Strip bold/italic markers
    text = re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', text)
    text = re.sub(r'_{1,3}([^_]+)_{1,3}', r'\1', text)
    # Strip list markers
    text = re.sub(r'^[\s]*[-*+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^[\s]*\d+\.\s+', '', text, flags=re.MULTILINE)
    return text.strip()

files = [f.strip() for f in sys.stdin.read().strip().split('\n') if f.strip()]
threshold = float(sys.argv[1])
json_mode = sys.argv[2] == 'true'

results = []
for filepath in files:
    with open(filepath, 'r') as f:
        raw = f.read()
    prose = strip_markdown(raw)
    words = len(prose.split())
    if words < 50:
        results.append({'file': filepath, 'result': 'SKIP', 'grade': None, 'words': words})
    else:
        grade = round(textstat.flesch_kincaid_grade(prose), 1)
        result = 'PASS' if grade <= threshold else 'FAIL'
        results.append({'file': filepath, 'result': result, 'grade': grade, 'words': words})

if json_mode:
    print(json.dumps(results))
else:
    for r in results:
        if r['result'] == 'SKIP':
            print(f\"{r['result']}  {r['file']}  words={r['words']}\")
        else:
            print(f\"{r['result']}  {r['file']}  grade={r['grade']}\")
" "$THRESHOLD" "$JSON_MODE")

echo "$RESULTS"

# Check for any FAIL in results
if echo "$RESULTS" | grep -q '^FAIL\|"result": "FAIL"'; then
  HAS_FAILURE=true
fi

if $HAS_FAILURE; then
  exit 1
fi
exit 0
```

- [ ] **Step 2: Make executable and create symlink**

```bash
chmod +x skills/swain-design/scripts/readability-check.sh
ln -sf ../../skills/swain-design/scripts/readability-check.sh .agents/bin/readability-check.sh
```

- [ ] **Step 3: Run the tests**

```bash
bash skills/swain-design/tests/test-readability-check.sh
```

Expected: All tests PASS.

- [ ] **Step 4: Fix any failures and re-run until green**

Iterate on the script if any tests fail. Common issues:
- Stripping regex may need tuning for edge cases
- Grade boundaries in fixtures may need adjustment
- The `--threshold` test relies on the pass fixture scoring between 1 and 9

- [ ] **Step 5: Commit**

```bash
git add skills/swain-design/scripts/readability-check.sh .agents/bin/readability-check.sh
git commit -m "feat(SPEC-194): add readability-check.sh script"
```

## Chunk 2: Governance Rule and Protocol Doc

### Task 4: Add governance rule to AGENTS.content.md

**Files:**
- Modify: `skills/swain-doctor/references/AGENTS.content.md` — add section after "Skill change discipline"

- [ ] **Step 1: Add the readability section**

Insert after the "Skill change discipline" section (after the closing paragraph about trivial fixes), before the "Session startup" section:

```markdown
### Readability

All artifacts produced by swain skills must meet a Flesch-Kincaid grade level of 9 or below on prose content. After writing or editing an artifact, run `readability-check.sh` on it. If the score exceeds the threshold, revise the prose — use shorter sentences, simpler words, and active voice — then re-check. Do not rewrite content that already passes. If three revision attempts still fail, note the score in the commit message and proceed. See `references/readability-protocol.md` for the integration contract.
```

- [ ] **Step 2: Verify the edit renders correctly**

Read the file back and confirm the new section sits cleanly between "Skill change discipline" and "Session startup".

- [ ] **Step 3: Commit**

```bash
git add skills/swain-doctor/references/AGENTS.content.md
git commit -m "docs(SPEC-194): add readability governance rule to AGENTS.content.md"
```

### Task 5: Create readability-protocol.md

**Files:**
- Create: `skills/swain-design/references/readability-protocol.md`

The protocol doc lives alongside `bookmark-protocol.md` in swain-design references since swain-design is the primary artifact-producing skill.

- [ ] **Step 1: Write the protocol doc**

```markdown
## Readability protocol

Artifact-producing skills run a Flesch-Kincaid readability check after finalizing artifact body text, before committing. This ensures all swain artifacts stay at or below a 9th-grade reading level.

### When to run

Run the check after the artifact body is complete and all structural validation (ADR compliance, alignment check, specwatch) has passed. The readability check is the last quality gate before commit.

### Invocation

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
bash "$REPO_ROOT/.agents/bin/readability-check.sh" <artifact-path>
```

### Handling results

**PASS** — No action needed. Proceed to commit.

**SKIP** — The file has fewer than 50 words of prose after stripping non-prose content. No action needed.

**FAIL** — The prose exceeds the grade-level threshold. Revise the failing sections:
1. Break long sentences into shorter ones (aim for 15-20 words per sentence)
2. Replace complex words with simpler alternatives
3. Use active voice instead of passive
4. Remove unnecessary qualifiers and jargon
5. Re-run the check

**Maximum 3 rewrite attempts.** If the score still exceeds the threshold after three revisions, note the score in the commit message (e.g., `readability: grade 10.2 after 3 attempts`) and proceed. Do not block the operation indefinitely.

### Integration points

| Skill | Hook point |
|-------|-----------|
| swain-design | After step 8b (unanchored check), before step 9 (specwatch scan) |
| swain-retro | After retro content generation, before embedding in EPIC or committing |
| Any artifact-producing skill | After body text is finalized, before commit |

Skills do not need code changes to adopt this protocol. The governance rule in AGENTS.md directs all artifact-producing agents to run the check. This protocol doc provides the details.
```

- [ ] **Step 2: Commit**

```bash
git add skills/swain-design/references/readability-protocol.md
git commit -m "docs(SPEC-194): add readability protocol reference doc"
```

### Task 6: Propagate governance to AGENTS.md

**Files:**
- Modify: `AGENTS.md` — the reconciled governance file

- [ ] **Step 1: Add the readability section to AGENTS.md**

The same text added to AGENTS.content.md needs to appear in the live AGENTS.md between "Skill change discipline" and "Session startup". Copy the exact same paragraph.

- [ ] **Step 2: Verify both files match**

Confirm the governance block in AGENTS.md matches AGENTS.content.md (the reconciliation source of truth).

- [ ] **Step 3: Commit**

```bash
git add AGENTS.md
git commit -m "docs(SPEC-194): propagate readability rule to AGENTS.md"
```

### Task 7: Final integration test

- [ ] **Step 1: Run readability-check.sh against the SPEC itself**

```bash
bash .agents/bin/readability-check.sh "docs/spec/Active/(SPEC-194)-Flesch-Kincaid-Readability-Enforcement/(SPEC-194)-Flesch-Kincaid-Readability-Enforcement.md"
```

This is a real-world test — if the SPEC itself fails readability, fix it.

- [ ] **Step 2: Run readability-check.sh against a few existing artifacts**

```bash
bash .agents/bin/readability-check.sh docs/spec/Active/*/SPEC-*.md 2>/dev/null | head -20
```

This is informational only — we are not retroactively fixing existing artifacts. But it gives a sense of the baseline.

- [ ] **Step 3: Run the full test suite**

```bash
bash skills/swain-design/tests/test-readability-check.sh
```

Expected: All PASS.

- [ ] **Step 4: Final commit if any fixes were needed**

```bash
git add -A
git commit -m "fix(SPEC-194): readability fixes from integration test"
```

Only if changes were made in steps 1-2.
