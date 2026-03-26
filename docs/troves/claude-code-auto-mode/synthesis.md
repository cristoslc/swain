# Synthesis: Claude Code Auto Mode

## Key findings

- **Auto mode is a new permission tier** in Claude Code, sitting between the conservative default (every tool call prompts) and the risky `--dangerously-skip-permissions`. Announced March 24, 2026 as a research preview on Team plans, with Enterprise and API rollout following.

- **Mechanism: Sonnet 4.6 classifier-gated execution.** Before each tool call runs, a separate Sonnet 4.6 classifier model reviews the conversation context and decides whether the action matches what the user asked for. The classifier receives user messages and tool calls but **not** Claude's own text or tool results — this means hostile content in files or web pages cannot directly manipulate the classifier. It also receives CLAUDE.md content, so project instructions factor into decisions.

- **The classifier uses prose-based rules, not pattern matching.** Unlike permission rules that match tool names and argument patterns, the classifier reasons about natural-language descriptions of what to block and allow. The full rule set is viewable via `claude auto-mode defaults`. There are 7 allow rules and 28 soft-deny rules out of the box.

- **Subagent handling is multi-layered.** The classifier evaluates the delegated task description before a subagent starts (blocking dangerous-sounding delegations), runs auto mode with the same rules inside the subagent (ignoring the subagent's own `permissionMode` frontmatter), and reviews the subagent's full action history when it finishes (catching mid-run compromises from hostile content). Security warnings are prepended to flagged subagent results.

- **Fallback thresholds: 3 consecutive blocks or 20 total per session** cause auto mode to pause and resume prompting. These are not configurable. Approving a prompted action resets the counters. In non-interactive mode (`-p`), the session aborts instead.

- **Cost and latency are real.** Classifier calls count toward token usage the same as main-session calls. Each checked action sends conversation transcript + pending action to the classifier. Read-only actions and file edits in the working directory skip the classifier. The extra cost comes mainly from shell commands and network operations.

- **On entering auto mode, dangerous allow rules are automatically dropped.** Blanket shell access (`Bash(*)`), wildcarded interpreters (`Bash(python*)`), package-manager run commands, and any `Agent` allow rule are removed. Narrow rules like `Bash(npm test)` carry over. Dropped rules are restored when leaving auto mode.

- **Hooks compose with auto mode.** `PreToolUse` hooks run before every tool call and can allow, deny, or escalate based on arbitrary logic. `PermissionRequest` hooks intercept the permission dialog. This provides deterministic control layered on top of the probabilistic classifier.

## Points of agreement

- **Anthropic and critics agree this isn't a safety guarantee.** The blog post says "reduces risk... but doesn't eliminate it entirely" and recommends isolated environments. Simon Willison echoes this, arguing for deterministic sandboxes over AI-based protections.
- **The classifier defaults are well-thought-out.** Both Anthropic's docs and Willison's analysis highlight the sophistication of the rules — distinguishing "local on disk" from "trusted," blocking scope escalation to `~/Library/` or `/etc`, and recognizing that cloned-from-external repos aren't trusted even though they're local.

## Points of disagreement

- **Non-determinism as a fundamental concern.** Willison is "unconvinced by prompt injection protections that rely on AI, since they're non-deterministic by nature." Anthropic acknowledges the classifier may miss things but positions it as strictly better than `--dangerously-skip-permissions`. The community (Reddit, via search snippets) is split — some see it as a step forward, others question using a "dumber model" (Sonnet) as classifier for a "smarter model" (Opus).
- **Supply chain attack surface.** Willison notes the allow list includes `pip install -r requirements.txt`, which wouldn't protect against supply chain attacks with unpinned dependencies — demonstrated same-day with the LiteLLM incident. The classifier defaults do block agent-chosen package names but trust declared manifests.
- **Hooks vs classifier.** Reddit community members report using `PreToolUse` hooks to deterministically block `rm -rf` and similar destructive commands, arguing this is more reliable than a probabilistic classifier. The docs suggest hooks and auto mode are complementary, not competing.

## Gaps

- **No red-team or adversarial evaluation results.** How does the classifier perform against prompt injection in files? Against multi-step attacks that individually pass but are dangerous in combination? No published evaluation.
- **Cost quantification missing.** "Small impact on token consumption" — no actual numbers. For long sessions with many tool calls, the cumulative classifier cost could be significant.
- **No comparison with plan-then-execute pattern.** Plan mode + approve-and-start-in-auto-mode is mentioned but not analyzed for safety properties vs raw auto mode.
- **Enterprise/API rollout timing vague.** "Coming days" — no specific date.
- **Reddit community reception** (r/ClaudeAI, r/ClaudeCode) was not fully fetchable — search snippets indicate skepticism about cost, trust in classifier accuracy, and preference for hooks-based alternatives. A full community thread would strengthen the reception analysis.
- **Interaction with `autoMode.environment` configuration.** The docs mention admins can configure trusted repos, buckets, and internal services, but the configuration schema isn't detailed in the sources collected.
