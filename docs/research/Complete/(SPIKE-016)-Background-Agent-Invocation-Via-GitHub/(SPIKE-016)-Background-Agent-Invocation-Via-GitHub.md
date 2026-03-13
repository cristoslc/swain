---
title: "Background Agent Invocation Via GitHub"
artifact: SPIKE-016
status: Complete
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
question: "How can swain invoke Claude Code (or other agents) to work on tasks in the background via GitHub Issues, and what are the mechanics of @claude mentions, webhooks, or API triggers?"
gate: Pre-EPIC-010-specs
risks-addressed:
  - Building a dispatch system without understanding the invocation mechanics
  - Assuming @claude works a certain way without testing
linked-artifacts:
  - EPIC-010
evidence-pool: |
  - https://github.com/anthropics/claude-code-action (Claude Code Action repo)
  - https://code.claude.com/docs/en/github-actions (Claude Code GitHub Actions docs)
  - https://code.claude.com/docs/en/headless (Claude Code headless/Agent SDK CLI docs)
  - https://platform.claude.com/docs/en/agent-sdk/overview (Claude Agent SDK)
  - https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent (Copilot Coding Agent)
  - https://developers.openai.com/codex/github-action/ (Codex GitHub Action)
  - https://developers.openai.com/codex/integrations/github/ (Codex GitHub integration)
  - https://github.blog/changelog/2026-02-13-github-agentic-workflows-are-now-in-technical-preview/ (GitHub Agentic Workflows)
  - https://coder.com/blog/launch-dec-2025-coder-tasks (Coder Tasks)
---

# Background Agent Invocation Via GitHub

## Question

How can swain invoke Claude Code (or other agents) to work on tasks in the background via GitHub Issues, and what are the mechanics of `@claude` mentions, webhooks, or API triggers?

## Go / No-Go Criteria

- **GO:** A reliable mechanism exists to trigger agent work via GitHub Issues with predictable behavior (agent picks up the issue, works on it, posts results)
- **NO-GO:** No reliable invocation mechanism exists or the latency/reliability is too poor for practical use

## Pivot Recommendation

If GitHub-native invocation is unreliable, explore alternative dispatch surfaces:
- GitHub Actions with Claude API calls
- Direct Claude Code CLI invocation via SSH to a dev machine
- Queue-based dispatch (e.g., a watched directory or webhook endpoint)

## Findings

### 1. Claude Code GitHub Action (`anthropics/claude-code-action@v1`)

**The primary mechanism for swain-dispatch.** Anthropic ships an official GitHub Action that runs Claude Code on GitHub-hosted runners.

**How it's triggered:**
- `@claude` mention in issue or PR comments (interactive mode)
- Issue assignment (assignment mode)
- Explicit `prompt` parameter in workflow YAML (automation mode)
- Any GitHub event: `issues.opened`, `issue_comment.created`, `pull_request`, `schedule`, `repository_dispatch`

**Latency:** Runner startup ~30-60s, then agent execution time varies by task complexity (typically 1-10 minutes for implementation tasks).

**Reliability:** GA (v1.0). Shipped September 2025. Actively maintained by Anthropic. Used in production at Spotify (650+ AI-generated code changes/month reported).

**Cost model:**
- GitHub Actions minutes (runner time on your plan)
- Anthropic API tokens per interaction (varies by task complexity and codebase size)
- Control costs via `--max-turns` in `claude_args`

**Structured input:** Yes. The action reads the full issue body, comments, linked context, and your `CLAUDE.md` file. You can pass a `prompt` parameter with structured instructions. Supports `--append-system-prompt` for custom system instructions. Supports `--json-schema` for structured output.

**Posts results back:** Yes. Comments on issues/PRs, creates PRs with branches, posts review comments with line-specific feedback, updates checkboxes for progress tracking.

**Key workflow for swain-dispatch (issue-triggered implementation):**
```yaml
name: Claude Agent Dispatch
on:
  issues:
    types: [opened, assigned]
  issue_comment:
    types: [created]
jobs:
  claude:
    if: |
      (github.event_name == 'issue_comment' && contains(github.event.comment.body, '@claude')) ||
      (github.event_name == 'issues' && contains(github.event.issue.body, '@claude'))
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          claude_args: "--model claude-sonnet-4-6 --max-turns 10"
```

**Authentication options:** Anthropic API key (direct), AWS Bedrock (OIDC), Google Vertex AI (Workload Identity Federation), Microsoft Foundry. Enterprise-friendly.

**Limitations and gotchas:**
- Cannot run arbitrary shell commands on the runner (file operations only)
- PRs created with `GITHUB_TOKEN` do NOT trigger downstream workflows (use a custom GitHub App token via `actions/create-github-app-token` instead)
- Respects model context window limits — large codebases may need scoped checkout
- No real-time streaming to the issue; results posted after completion
- Requires repo admin to install the Claude GitHub App (permissions: Contents, Issues, Pull requests read/write)

**Setup:** Run `/install-github-app` in Claude Code terminal, or manually install https://github.com/apps/claude and add `ANTHROPIC_API_KEY` as a repo secret.

---

### 2. Claude Code Headless Mode (CLI `-p` flag)

**For self-hosted or custom dispatch pipelines.** The `-p` / `--print` flag runs Claude Code non-interactively.

**How it's triggered:** Shell invocation: `claude -p "prompt" --allowedTools "Bash,Read,Edit"`

**Latency:** Immediate (no runner startup if running locally or on a persistent server).

**Reliability:** GA. Part of the core Claude Code CLI. Now rebranded as the "Agent SDK CLI" — same `-p` flag, same behavior.

**Cost model:** Anthropic API tokens only (no GitHub Actions minutes if self-hosted).

**Structured input:** Yes. Accepts `--json-schema` for structured output, `--output-format json` for metadata, `--append-system-prompt` for custom instructions. Can pipe input via stdin.

**Posts results back:** Not natively — you'd script the GitHub API calls (`gh issue comment`, `gh pr create`) around the CLI output.

**Key capabilities:**
- `--output-format json` returns `{result, session_id, usage}` for programmatic parsing
- `--output-format stream-json` with `--verbose` for real-time token streaming
- `--allowedTools "Bash,Read,Edit"` for auto-approving tool use
- `--continue` / `--resume <session_id>` for multi-step conversations
- `--json-schema` for structured output conforming to a schema
- Exit code 0 on success, non-zero on error

**Example (self-hosted dispatch):**
```bash
claude -p "Implement the feature described in this spec: $(cat spec.md)" \
  --allowedTools "Bash,Read,Edit" \
  --output-format json \
  --max-turns 15 | jq -r '.result'
```

**Limitations:**
- Requires `ANTHROPIC_API_KEY` environment variable (or Bedrock/Vertex config)
- No built-in GitHub integration — you must script the issue/PR lifecycle yourself
- Authentication in CI may require the Agent SDK API key path (not `claude.ai` login)

---

### 3. Claude Agent SDK (Python / TypeScript)

**For maximum programmatic control.** The Agent SDK (`@anthropic-ai/claude-agent-sdk` for TS, `claude-agent-sdk-python` for Python) provides the same agent loop as Claude Code in a library.

**How it's triggered:** Programmatic — call from any Python/TypeScript application, webhook handler, or GitHub Action step.

**Reliability:** GA. Same engine as Claude Code.

**Cost model:** Anthropic API tokens.

**Structured input/output:** Full control over messages, tool approval callbacks, streaming, structured outputs.

**Relevance to swain-dispatch:** Could be used to build a custom dispatch server that listens for GitHub webhooks and runs agent tasks, but this is significantly more engineering than using `claude-code-action`. Reserve for cases where the GitHub Action doesn't meet needs.

---

### 4. GitHub Copilot Coding Agent

**GitHub's native issue-to-PR agent.** Replaced Copilot Workspace (sunset May 2025).

**How it's triggered:**
- Assign a GitHub issue to "Copilot" from the issue sidebar
- Use the Agents panel on any GitHub page
- Click "Delegate to coding agent" from VS Code Copilot Chat
- Mention `@copilot` in PR comments for modifications

**Latency:** Minutes (runs in ephemeral GitHub Actions environment).

**Reliability:** GA since September 2025 for all paid Copilot plans (Pro, Pro+, Business, Enterprise).

**Cost model:** Included in existing GitHub Copilot subscription. Uses your GitHub Actions minutes allocation and premium request quota. No additional per-token charges.

**Structured input:** Reads issue description, comments, linked context. Respects `AGENTS.md` files for custom instructions. No schema-based structured input.

**Posts results back:** Yes. Creates branches, writes commits, opens PRs, requests human review, writes PR descriptions.

**Limitations:**
- Single PR per task assignment
- Repository-specific only (no cross-repo)
- Cannot approve or merge its own PRs
- Incompatible with "Require signed commits" rules (unless bypassed)
- Ignores configured content exclusions
- No model selection — uses whatever model GitHub provides
- Tied to GitHub's Copilot infrastructure (not self-hostable)

**Relevance to swain-dispatch:** A viable alternative agent backend if the operator has Copilot. Cannot control model routing (Opus vs Sonnet). Less configurable than Claude Code Action but zero API cost.

---

### 5. OpenAI Codex GitHub Integration

**How it's triggered:**
- `@codex review` comment on PRs (manual review)
- Automatic reviews (enable in Codex settings — reviews every new PR)
- `openai/codex-action@v1` GitHub Action for CI/CD workflows
- Cloud delegation from the Codex IDE for implementation tasks

**Latency:** Minutes for reviews. Implementation tasks vary.

**Reliability:** Active development (monthly changelog updates through March 2026). The GitHub Action has had reported stability issues (e.g., `codex-action@v1` failures in issue #9269).

**Cost model:** OpenAI API key required. Token-based pricing. No bundled free tier for the action.

**Structured input:** Reads `AGENTS.md` for review guidelines. Supports `prompt-file` parameter pointing to markdown instructions. No schema-based structured input for the action.

**Posts results back:** Yes for reviews (comments on PRs). Cloud delegation can create PRs. The GitHub Action itself posts results as PR comments via `actions/github-script`.

**Limitations:**
- PR review is the primary documented use case — issue-to-PR workflow is less mature
- GitHub Action requires Linux/macOS runners (Windows needs `safety-strategy: unsafe`)
- Cannot use both `prompt` and `prompt-file` simultaneously
- Severity filtering: defaults to P0/P1 issues only in reviews

**Relevance to swain-dispatch:** A possible alternative agent backend, but the issue-to-PR workflow is less developed than Claude Code Action or Copilot Coding Agent. Better suited as a review layer than a dispatch target.

---

### 6. GitHub Agentic Workflows

**How it's triggered:** Natural language workflow definitions in `.github/workflows/` converted via `gh aw` CLI extension. Supports issue events, PR events, schedule, manual dispatch, comment commands.

**Reliability:** Technical Preview (launched February 13, 2026). Not production-ready.

**Cost model:** GitHub Actions minutes. Agent costs depend on which agent is configured (Copilot CLI is the default).

**Key feature:** Write automation goals in plain Markdown instead of YAML. The `gh aw` CLI converts to standard GitHub Actions.

**Relevance to swain-dispatch:** Interesting future option. Too early (tech preview) for production use. Monitor for GA.

---

### 7. Alternative Dispatch Patterns

#### a. Repository Dispatch Events
Any system with a GitHub token can POST to `/repos/{owner}/{repo}/dispatches` to trigger a `repository_dispatch` workflow. swain could use this to programmatically trigger the Claude Code Action:

```bash
gh api repos/cristoslc/swain/dispatches \
  -f event_type="agent-dispatch" \
  -f client_payload[spec]="SPEC-012" \
  -f client_payload[prompt]="Implement this spec"
```

Combined with a workflow listening on `repository_dispatch`, this gives full programmatic control without requiring `@claude` mentions.

#### b. Webhook-Triggered Agent Execution
A lightweight webhook server (e.g., on a VPS or Coder workspace) listens for GitHub issue events and runs `claude -p` with the issue body as input. Results are posted back via `gh issue comment`. This is the most flexible pattern but requires hosting infrastructure.

#### c. Coder Tasks
Coder (coder.com) offers "Coder Tasks" — label a GitHub issue with a tag, a GitHub Action launches a Coder workspace running Claude Code as a background agent, which reads the issue and opens a PR. GA since Coder v2.29 (December 2025). Requires self-hosted Coder infrastructure.

#### d. Custom GitHub App
Build a GitHub App that subscribes to `issues.opened` / `issues.labeled` events, receives webhooks, and dispatches to Claude Code CLI or Agent SDK. Maximum flexibility but maximum engineering effort.

---

### Summary Comparison

| Mechanism | Trigger | Latency | Maturity | Cost | Structured Input | Posts Back | Best For |
|-----------|---------|---------|----------|------|-----------------|------------|----------|
| **Claude Code Action** | @claude, issue events, prompt | 1-10 min | GA (Sep 2025) | API tokens + GHA minutes | Yes (prompt, CLAUDE.md, schema) | Yes (comments, PRs) | **Primary dispatch target** |
| **Claude CLI `-p`** | Shell invocation | Seconds | GA | API tokens only | Yes (flags, stdin, schema) | No (script it) | Self-hosted dispatch |
| **Claude Agent SDK** | Programmatic | Seconds | GA | API tokens | Full control | No (build it) | Custom dispatch server |
| **Copilot Coding Agent** | Issue assignment | Minutes | GA (Sep 2025) | Copilot subscription | Issue body, AGENTS.md | Yes (PRs) | Zero-cost alternative |
| **Codex Action** | @codex, PR events | Minutes | Active dev | OpenAI API tokens | prompt-file, AGENTS.md | Yes (PR comments) | Review layer |
| **GitHub Agentic Workflows** | Markdown definitions | Minutes | Tech Preview (Feb 2026) | GHA minutes + agent | Natural language | Yes | Future option |
| **Repository Dispatch** | API POST | Seconds + workflow | GA (GitHub) | GHA minutes | JSON payload | Via workflow | Programmatic trigger |
| **Coder Tasks** | Issue label | Minutes | GA (Dec 2025) | Coder + API tokens | Issue body | Yes (PRs) | Self-hosted infra |

### Recommendation for EPIC-010

**GO.** Multiple reliable mechanisms exist. The recommended architecture:

1. **Primary:** `anthropics/claude-code-action@v1` triggered by `repository_dispatch` events. swain-dispatch creates a GitHub issue with the artifact content as the body, then triggers the workflow via `gh api dispatches`. This gives full programmatic control.

2. **Fallback:** `@claude` mention in issue comments as a manual dispatch mechanism for the operator.

3. **Model routing:** Use `claude_args: "--model claude-opus-4-6"` vs `"--model claude-sonnet-4-6"` based on swain's complexity assessment. The action supports model selection natively.

4. **Results feedback:** The action posts PR links and comments back to the originating issue automatically.

5. **Cost control:** Set `--max-turns` per complexity tier. Use Sonnet for well-scoped implementation tasks, Opus for ambiguous or architectural work.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Planned | 2026-03-13 | 6a5e1ac | Initial creation |
| Active | 2026-03-13 | — | Web research: 6 mechanisms evaluated, GO recommendation |
| Complete | 2026-03-13 | 3e54fe2 | GO: claude-code-action@v1 recommended |
