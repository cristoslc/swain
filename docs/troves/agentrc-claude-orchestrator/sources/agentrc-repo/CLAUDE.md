<!-- agentrc:begin -->
## agentrc Worker Directives

This project uses [agentrc](https://github.com/ericsmithhh/agent-rc) to orchestrate parallel Claude Code workers in tmux panes.

### Subagent Dispatch — REQUIRED

**You MUST use the Agent tool with specialized subagent types for all implementation work.** Do NOT write Rust code, tests, or complex logic directly. Dispatch to the appropriate specialist and integrate their output.

| Task Type | Agent | When |
|---|---|---|
| Rust implementation | `voltagent-lang:rust-engineer` | Any new function, struct, module, or non-trivial code change |
| Test writing & QA | `voltagent-qa-sec:test-automator` | Writing test functions, test infrastructure |
| Code review | `voltagent-qa-sec:code-reviewer` | After completing a logical chunk of work |
| Debugging | `voltagent-qa-sec:debugger` | When tests fail or behavior is unexpected |
| Performance | `voltagent-qa-sec:performance-engineer` | Optimizing hot paths or build performance |
| Architecture | `voltagent-qa-sec:architect-reviewer` | Design decisions affecting module boundaries |

**Always set `model: "opus"` on subagent dispatches.** Never downgrade to sonnet or haiku for implementation work.

**Pattern:** Read the brief → plan the approach → dispatch to `rust-engineer` for each implementation unit → dispatch to `test-automator` for tests → run tests yourself → commit.

### Worker Contract

If you are an agentrc worker (your seed prompt says "You are worker NNN"):

1. Read your task brief fully before starting
2. Use `agentrc worker status` to report state transitions
3. Use `agentrc worker note` for progress updates
4. Follow TDD rigorously: failing test → implementation → passing test → commit
5. Run multi-agent review after each logical chunk of work
6. Writers: stay in your worktree, do not modify files outside it
7. Readers: do not modify project files, output via `agentrc worker note/result`
8. **NEVER use git push, git rebase, or any remote git operations.** The orchestrator handles all git integration. Workers commit to their local branch only.
9. When done: `agentrc worker done --task <id>`

### Subagent Rules

Subagents dispatched by the orchestrator or workers:
- **NEVER run git commands** (commit, push, pull, rebase, merge). Write files and report back. The caller handles git.
- **NEVER push to remote repositories.** Only the orchestrator pushes, and only when the user explicitly requests it.
<!-- agentrc:end -->



