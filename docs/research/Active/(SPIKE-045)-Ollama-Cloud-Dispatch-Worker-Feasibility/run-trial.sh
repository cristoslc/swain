#!/usr/bin/env bash
# SPIKE-045 Trial Runner
# Usage: ./run-trial.sh <model> <trial-number>
# Example: ./run-trial.sh qwen3-coder:480b 1
#
# Creates a worktree at the pre-implementation baseline (232369c),
# runs OpenCode with the specified Ollama Cloud model, and
# pushes a branch + creates a PR for evaluation.

set -euo pipefail

MODEL="${1:?Usage: $0 <model> <trial-number>}"
TRIAL="${2:?Usage: $0 <model> <trial-number>}"
REPO_ROOT="$(git rev-parse --show-toplevel)"
BASELINE="232369c"  # After SPEC-018 was written, before implementation

# Sanitize model name for branch/dir naming
MODEL_SLUG="${MODEL//[:\/]/-}"
BRANCH="spike045/${MODEL_SLUG}/trial-${TRIAL}"
WORKTREE_DIR="/tmp/spike045-${MODEL_SLUG}-trial-${TRIAL}"

echo "=== SPIKE-045 Trial ==="
echo "Model:    ollama-cloud/${MODEL}"
echo "Trial:    ${TRIAL}"
echo "Branch:   ${BRANCH}"
echo "Worktree: ${WORKTREE_DIR}"
echo "Baseline: ${BASELINE}"
echo ""

# Clean up any previous worktree at this path
if [ -d "${WORKTREE_DIR}" ]; then
  echo "Cleaning up previous worktree at ${WORKTREE_DIR}..."
  git worktree remove --force "${WORKTREE_DIR}" 2>/dev/null || rm -rf "${WORKTREE_DIR}"
fi

# Delete the branch if it exists (from a previous run)
git branch -D "${BRANCH}" 2>/dev/null || true

# Create worktree from baseline
echo "Creating worktree from baseline ${BASELINE}..."
git worktree add -b "${BRANCH}" "${WORKTREE_DIR}" "${BASELINE}"

# Copy the opencode project config if it exists
if [ -f "${REPO_ROOT}/.opencode/opencode.json" ]; then
  mkdir -p "${WORKTREE_DIR}/.opencode"
  cp "${REPO_ROOT}/.opencode/opencode.json" "${WORKTREE_DIR}/.opencode/"
fi

echo ""
echo "Worktree ready. Starting OpenCode..."
echo "---"

PROMPT="You are being evaluated on your ability to implement a swain SPEC by following project conventions.

Your task: implement SPEC-018 (Update Artifact Definitions and Templates).

Steps:
1. Read AGENTS.md to understand swain governance and conventions
2. Read the SPEC at docs/spec/Complete/(SPEC-018)-Update-Artifact-Definitions-And-Templates/(SPEC-018)-Update-Artifact-Definitions-And-Templates.md
3. Read ADR-003 (linked in the SPEC) for the three-track lifecycle model
4. Implement all changes described in the SPEC's External Behavior section
5. Stay within scope — do NOT migrate existing artifacts, update scripts, or remove STORY files
6. After implementation, commit your changes with a descriptive message
7. Push the branch to origin
8. Create a PR targeting the 'trunk' branch using: gh pr create --title 'SPIKE-045 trial: ${MODEL} #${TRIAL} — SPEC-018 implementation' --body 'Automated trial run for SPIKE-045. Model: ollama-cloud/${MODEL}, Trial: ${TRIAL}. Implementing SPEC-018: Update Artifact Definitions and Templates.'

Do not ask questions. Do your best with the information available."

# Record start time
START_TIME=$(date +%s)

# Run OpenCode with the target model
opencode run \
  --model "ollama-cloud/${MODEL}" \
  --dir "${WORKTREE_DIR}" \
  --title "SPIKE-045: ${MODEL} trial ${TRIAL}" \
  "${PROMPT}" \
  2>&1 | tee "${WORKTREE_DIR}/trial-output.log"

END_TIME=$(date +%s)
DURATION=$(( END_TIME - START_TIME ))

echo ""
echo "=== Trial Complete ==="
echo "Duration: ${DURATION}s ($(( DURATION / 60 ))m $(( DURATION % 60 ))s)"
echo "Output log: ${WORKTREE_DIR}/trial-output.log"
echo ""

# Capture stats
STATS_FILE="${REPO_ROOT}/docs/research/Active/(SPIKE-045)-Ollama-Cloud-Dispatch-Worker-Feasibility/trial-${MODEL_SLUG}-${TRIAL}.md"
cat > "${STATS_FILE}" << EOF
---
model: ollama-cloud/${MODEL}
trial: ${TRIAL}
branch: ${BRANCH}
baseline: ${BASELINE}
duration-seconds: ${DURATION}
date: $(date +%Y-%m-%d)
---

# Trial: ${MODEL} #${TRIAL}

## Timing
- Start: $(date -r ${START_TIME} +%H:%M:%S)
- End: $(date -r ${END_TIME} +%H:%M:%S)
- Duration: $(( DURATION / 60 ))m $(( DURATION % 60 ))s

## Diff Stats
\`\`\`
$(cd "${WORKTREE_DIR}" && git diff --stat "${BASELINE}..HEAD" 2>/dev/null || echo "no changes")
\`\`\`

## Scoring

| Check | Result | Notes |
|-------|--------|-------|
| Read AGENTS.md | | |
| Found and read SPEC-018 | | |
| Read ADR-003 | | |
| Definition phases match ADR-003 | /9 correct | |
| Template status defaults to Proposed | /9 correct | |
| SKILL.md updated (9 types, 3 tracks) | | |
| relationship-model.md updated | | |
| Stayed in scope | | |
| Ran specwatch | | |
| Created commit | | |
| Pushed branch | | |
| Created PR | | |

**Overall: __ / pass / partial / fail**

## PR Link

<!-- paste PR URL here, or note if agent created it -->

## Error Types

<!-- hallucination, convention violation, tool misuse, scope creep, etc. -->

## Raw Output

See \`${WORKTREE_DIR}/trial-output.log\`
EOF

echo "Scoring template: ${STATS_FILE}"
echo ""
echo "To review the diff against known-good implementation:"
echo "  cd ${WORKTREE_DIR} && git diff ${BASELINE}..HEAD"
echo ""
echo "To compare against the real implementation:"
echo "  git diff ${BRANCH}..00f11b2 -- skills/ docs/"
