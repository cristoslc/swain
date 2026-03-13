---
name: swain-dispatch
description: "Dispatch swain artifacts to background agents via GitHub Issues. Creates a GitHub Issue with the artifact content and triggers the Claude Code Action workflow for autonomous implementation. Use when the user wants to offload work to a background agent."
user-invocable: true
allowed-tools: Bash, Read, Grep, Glob
metadata:
  short-description: Dispatch artifacts to background agents via GitHub
  version: 1.0.0
  author: cristos
  license: MIT
  source: swain
---
<!-- swain-model-hint: sonnet, effort: low -->

# Agent Dispatch

Dispatches swain-design artifacts to background agents via GitHub Issues. The agent runs autonomously using `anthropics/claude-code-action@v1` on a GitHub Actions runner.

## Prerequisites

Before first use, verify:

```bash
gh auth status
gh api repos/{owner}/{repo}/actions/secrets --jq '.secrets[].name' 2>/dev/null | grep -q ANTHROPIC_API_KEY
```

If `ANTHROPIC_API_KEY` is not set as a repo secret, tell the user:
> Dispatch requires `ANTHROPIC_API_KEY` as a GitHub Actions secret.
> Run: `gh secret set ANTHROPIC_API_KEY`

Also verify the workflow file exists:
```bash
test -f .github/workflows/agent-dispatch.yml && echo "workflow exists" || echo "workflow missing"
```

If missing, tell the user to run `/swain-init` or create the workflow manually.

## Dispatch workflow

### Step 1 — Resolve the artifact

Parse the user's request to identify the artifact ID (e.g., `SPEC-025`, `SPIKE-007`).

```bash
ARTIFACT_ID="SPEC-025"  # from user input
ARTIFACT_PATH="$(find docs/ -path "*${ARTIFACT_ID}*" -name "*.md" -print -quit)"
```

If not found, report the error and stop.

### Step 2 — Read the artifact

Read the full artifact content. This becomes the issue body.

### Step 3 — Read dispatch settings

Check `swain.settings.json` for dispatch configuration:

```bash
jq -r '.dispatch // {}' swain.settings.json 2>/dev/null
```

Defaults:
- `model`: `claude-sonnet-4-6`
- `maxTurns`: `15`
- `labels`: `["agent-dispatch", "swain"]`
- `autoTrigger`: `true`

### Step 4 — Create the GitHub Issue

```bash
gh issue create \
  --title "[dispatch] ${ARTIFACT_TITLE}" \
  --body "$(cat <<'EOF'
## Dispatched Artifact: ${ARTIFACT_ID}

This issue was created by `swain-dispatch` for background agent execution.

### Instructions

Implement the artifact below. Follow the acceptance criteria. Create a PR when done.

---

${ARTIFACT_CONTENT}
EOF
)" \
  --label "agent-dispatch" --label "swain"
```

Capture the issue number from the output.

### Step 5 — Trigger the workflow

If `autoTrigger` is true (default):

```bash
OWNER_REPO="$(gh repo view --json nameWithOwner -q .nameWithOwner)"
gh api "repos/${OWNER_REPO}/dispatches" \
  -f event_type="agent-dispatch" \
  -f client_payload[artifact]="${ARTIFACT_ID}" \
  -f client_payload[issue_number]="${ISSUE_NUMBER}" \
  -f client_payload[model]="${MODEL}" \
  -f client_payload[max_turns]="${MAX_TURNS}"
```

### Step 6 — Report

Tell the user:
> Dispatched ${ARTIFACT_ID} to background agent.
> Issue: ${ISSUE_URL}
> Workflow will run on the next available runner.
> Monitor progress in the issue comments.

## Manual dispatch

If the user prefers manual dispatch (or `autoTrigger` is false), skip Step 5 and tell them:
> Issue created: ${ISSUE_URL}
> To trigger the agent, comment `@claude` on the issue.

## Checking dispatch status

When the user asks about dispatch status:

```bash
gh issue list --label agent-dispatch --state open --json number,title,updatedAt
```

Show open dispatch issues with their last update time.
