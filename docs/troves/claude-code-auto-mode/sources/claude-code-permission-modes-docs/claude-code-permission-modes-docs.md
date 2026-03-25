---
source-id: "claude-code-permission-modes-docs"
title: "Choose a permission mode — Claude Code Docs"
type: web
url: "https://code.claude.com/docs/en/permission-modes"
fetched: 2026-03-24T00:00:00Z
hash: "59ea1edb696832f32f859dbd65a25957569562ed3ab14bc057ae5708db206394"
---

# Choose a permission mode

Switch between supervised editing, read-only planning, and auto mode where a background classifier replaces manual permission prompts. Cycle modes with Shift+Tab in the CLI or use the mode selector in VS Code, Desktop, and claude.ai.

Permission modes control whether Claude asks before acting. Different tasks call for different levels of autonomy: you might want full oversight for sensitive work, minimal interruptions for a long refactor, or read-only access while exploring a codebase.

## Switch permission modes

You can switch modes at any time during a session, at startup, or as a persistent default.

**CLI:**

- **During a session**: press `Shift+Tab` to cycle through `default` → `acceptEdits` → `plan` → `auto`. `auto` does not appear in the cycle until you pass `--enable-auto-mode` at startup. Auto also requires a Team (or Enterprise/API once available) plan and Claude Sonnet 4.6 or Opus 4.6.
- **At startup**: `claude --permission-mode plan`
- **As a default**: set `defaultMode` in settings:

```json
{
  "permissions": {
    "defaultMode": "acceptEdits"
  }
}
```

- **Non-interactively**: `claude -p "refactor auth" --permission-mode acceptEdits`

`dontAsk` is never in the `Shift+Tab` cycle. `bypassPermissions` appears only if you started with `--permission-mode bypassPermissions`, `--dangerously-skip-permissions`, or `--allow-dangerously-skip-permissions`.

**VS Code** uses friendly labels: Ask permissions (`default`), Auto accept edits (`acceptEdits`), Plan mode (`plan`), Auto (`auto`), Bypass permissions (`bypassPermissions`). Auto and Bypass appear only after enabling "Allow dangerously skip permissions" in extension settings.

**Desktop**: use the mode selector next to the send button.

**Web and mobile**: mode dropdown next to the prompt box. For cloud VMs, the dropdown offers Auto accept edits and Plan mode only. For Remote Control sessions, Ask permissions, Auto accept edits, and Plan mode are available.

## Available modes

| Mode | What Claude can do without asking | Best for |
| --- | --- | --- |
| `default` | Read files | Getting started, sensitive work |
| `acceptEdits` | Read and edit files | Iterating on code you're reviewing |
| `plan` | Read files | Exploring a codebase, planning a refactor |
| `auto` | All actions, with background safety checks | Long-running tasks, reducing prompt fatigue |
| `bypassPermissions` | All actions, no checks | Isolated containers and VMs only |
| `dontAsk` | Only pre-approved tools | Locked-down environments |

## Analyze before you edit with plan mode

Plan mode tells Claude to research and propose changes without making them. Claude reads files, runs shell commands to explore, asks clarifying questions, and writes a plan file, but does not edit your source code. Permission prompts work the same as default mode.

**Use cases:**
- Multi-step implementation (edits across many files)
- Code exploration before changing anything
- Interactive development (iterate on direction with Claude)

Enter plan mode for a single request by prefixing with `/plan`, or switch the whole session with `Shift+Tab`, or start with `claude --permission-mode plan`.

When the plan is ready, Claude presents it and asks how to proceed:
- Approve and start in auto mode
- Approve and accept edits
- Approve and manually review each edit
- Keep planning (sends feedback back for another round)

Each approve option also offers to clear the planning context first.

## Eliminate prompts with auto mode

Auto mode is available on Team plans, with Enterprise and API support rolling out shortly. On Team and Enterprise, an admin must enable it in Claude Code admin settings before users can turn it on. It requires Claude Sonnet 4.6 or Claude Opus 4.6, and is not available on Haiku, claude-3 models, or third-party providers (Bedrock, Vertex, Foundry).

Before each action runs, a separate classifier model reviews the conversation and decides whether the action matches what you asked for: it blocks actions that escalate beyond the task scope, target infrastructure the classifier doesn't recognize as trusted, or appear to be driven by hostile content encountered in a file or web page.

**Auto mode is a research preview.** It reduces prompts but does not guarantee safety. It provides more protection than `bypassPermissions` but is not as thorough as manually reviewing each action.

**Model**: the classifier runs on Claude Sonnet 4.6, even if your main session uses a different model.

**Cost**: classifier calls count toward your token usage the same as main-session calls. Each checked action sends a portion of the conversation transcript plus the pending action to the classifier. The extra cost comes mainly from shell commands and network operations, since read-only actions and file edits in your working directory don't trigger a classifier call.

**Latency**: each classifier check adds a round-trip before the action executes.

### How actions are evaluated

Each action goes through a fixed decision order. The first matching step wins:

1. Actions matching your allow or deny rules resolve immediately
2. Read-only actions and file edits in your working directory are auto-approved
3. Everything else goes to the classifier
4. If the classifier blocks, Claude receives the reason and attempts an alternative approach

On entering auto mode, Claude Code drops any allow rule that is known to grant arbitrary code execution: blanket shell access like `Bash(*)`, wildcarded script interpreters like `Bash(python*)` or `Bash(node*)`, package-manager run commands, and any `Agent` allow rule. These rules would auto-approve commands and subagent delegations most capable of causing damage before the classifier ever sees them. Narrow rules like `Bash(npm test)` carry over. Dropped rules are restored when you leave auto mode.

The classifier receives user messages and tool calls as input, with Claude's own text and tool results stripped out. It also receives your CLAUDE.md content, so actions described in your project instructions are factored into allow and block decisions. Because tool results never reach the classifier, hostile content in a file or web page cannot manipulate it directly. The classifier evaluates the pending action against a customizable set of block and allow rules, checking whether the action is an overeager escalation beyond what you asked for, a mistake about what's safe to touch, or a sudden departure from your stated intent that suggests Claude may have been steered by something it read.

Unlike your permission rules, which match tool names and argument patterns, the classifier reads prose descriptions of what to block and allow: it reasons about the action in context rather than matching syntax.

### How auto mode handles subagents

When Claude spawns a subagent, the classifier evaluates the delegated task before the subagent starts. A task description that looks dangerous on its own, like "delete all remote branches matching this pattern", is blocked at spawn time.

Inside the subagent, auto mode runs with the same block and allow rules as the parent session. Any `permissionMode` the subagent defines in its own frontmatter is ignored. The subagent's own tool calls go through the classifier independently.

When the subagent finishes, the classifier reviews its full action history. A subagent that was benign at spawn could have been compromised mid-run by content it read. If the return check flags a concern, a security warning is prepended to the subagent's results so the main agent can decide how to proceed.

### What the classifier blocks by default

Out of the box, the classifier trusts your working directory and, if you're in a git repo, that repo's configured remotes. Everything else is treated as external.

**Blocked by default**:
- Downloading and executing code, like `curl | bash` or scripts from cloned repos
- Sending sensitive data to external endpoints
- Production deploys and migrations
- Mass deletion on cloud storage
- Granting IAM or repo permissions
- Modifying shared infrastructure
- Irreversibly destroying files that existed before the session started
- Destructive source control operations like force push or pushing directly to `main`

**Allowed by default**:
- Local file operations in your working directory
- Installing dependencies already declared in your lock files or manifests
- Reading `.env` and sending credentials to their matching API
- Read-only HTTP requests
- Pushing to the branch you started on or one Claude created

To see the full default rule lists as the classifier receives them, run `claude auto-mode defaults`.

If auto mode blocks something routine for your team, like pushing to your own org's repo or writing to a company bucket, it's because the classifier doesn't know those are trusted. Administrators can add trusted repos, buckets, and internal services via the `autoMode.environment` setting: see Configure the auto mode classifier in the permissions docs.

### When auto mode falls back

If the classifier blocks an action 3 times in a row or 20 times total in one session, auto mode pauses and Claude Code resumes prompting for each action. These thresholds are not configurable.

- **CLI**: you see a notification in the status area. Approving the prompted action resets the denial counters, so you can continue in auto mode.
- **Non-interactive mode** with `-p` flag: aborts the session, since there is no user to prompt.

Repeated blocks usually mean the task genuinely requires actions the classifier is built to stop, or the classifier is missing context about your trusted infrastructure.

## Allow only pre-approved tools with dontAsk mode

`dontAsk` mode auto-denies every tool that is not explicitly allowed. Only actions matching your allow rules or `permissions.allow` settings can execute. If a tool has an explicit `ask` rule, the action is also denied rather than prompting. This makes the mode fully non-interactive, suitable for CI pipelines or restricted environments.

## Skip all checks with bypassPermissions mode

`bypassPermissions` mode disables all permission prompts and safety checks. Every tool call executes immediately without any verification. Only use in isolated environments (containers, VMs, devcontainers without internet access).

The `--dangerously-skip-permissions` flag is equivalent to `--permission-mode bypassPermissions`.

Administrators can block this mode by setting `permissions.disableBypassPermissionsMode` to `"disable"` in managed settings.

## Compare permission approaches

| | `default` | `acceptEdits` | `auto` | `dontAsk` | `bypassPermissions` |
| --- | --- | --- | --- | --- | --- |
| Permission prompts | File edits and commands | Commands only | None unless fallback triggers | None, blocked unless pre-allowed | None |
| Safety checks | You review each action | You review commands | Classifier reviews commands | Your pre-approved rules only | None |
| Token usage | Standard | Standard | Higher, from classifier calls | Standard | Standard |

## Customize permissions further

Permission modes set the baseline approval behavior. For control over individual tools or commands, layer additional configuration on top:

- **Permission rules**: Add `allow`, `ask`, or `deny` entries to pre-approve safe commands, force prompts for risky ones, or block specific tools. Rules apply in every mode except `bypassPermissions`.
- **Hooks**: A `PreToolUse` hook runs before every tool call and can allow, deny, or escalate based on command content, file paths, time of day, or a response from an external policy service. A `PermissionRequest` hook intercepts the permission dialog itself and answers on your behalf.
