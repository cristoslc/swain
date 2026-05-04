---
source-id: agentrc-claude-md
type: repository
url: "https://github.com/ericsmithhh/agent.rc/blob/master/CLAUDE.md"
fetched: 2026-04-13
title: "agentrc CLAUDE.md — Worker directives and subagent dispatch rules"
author: ericsmithhh
---

# agentrc Worker Directives

## Mandatory subagent dispatch

Implementation work must be delegated to specialized agents rather than handled
directly. All implementation goes through subagents typed by domain:

| Role | Subagent type |
|------|--------------|
| Rust code | `voltagent-lang:rust-engineer` |
| Testing | `voltagent-qa-sec:test-automator` |
| Code review | `voltagent-qa-sec:code-reviewer` |
| Debugging | `voltagent-qa-sec:debugger` |
| Performance | `voltagent-qa-sec:performance-engineer` |
| Architecture | `voltagent-qa-sec:architect-reviewer` |

All subagent work requires the `opus` model setting.

## Worker obligations

Workers must:

- Complete task briefs before starting.
- Report status via `agentrc worker *` commands.
- Practice test-driven development.
- Avoid git operations beyond local commits.
- Never modify files outside their assigned worktree.
- Complete work via `agentrc worker done`.

Subagents cannot execute remote git operations or push to repositories. The
orchestrator handles all integration.
