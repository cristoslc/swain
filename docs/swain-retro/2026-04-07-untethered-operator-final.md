---
title: "Retro: Untethered Operator Final Phase"
artifact: RETRO-2026-04-07-untethered-operator-final
track: standing
status: Active
created: 2026-04-07
last-updated: 2026-04-07
scope: "VISION-006 Final Phase — HTTP adapter, synthetic UAT, runbooks, typing indicator fix"
period: "2026-04-06 to 2026-04-07"
linked-artifacts:
  - VISION-006
  - SPEC-292
  - RUNBOOK-003
  - EPIC-073
---

# Retro: Untethered Operator Final Phase

## Summary

Final session on [VISION-006](../vision/Active/(VISION-006)-Untethered-Operator/(VISION-006)-Untethered-Operator.md) Untethered Operator. The previous session (see RETRO-2026-04-06-untethered-operator-phase-b) discovered the opencode serve HTTP API and planned a pivot away from tmux scraping. This session completed that pivot: replaced TmuxPaneAdapter with OpenCodeServerAdapter backed by HTTP, verified session persistence with opencode serve and opencode attach, fixed the typing indicator lifecycle, ran synthetic UAT through computer-use MCP against the Zulip desktop app, wrote RUNBOOK-003 and bin/swain-bridge, and achieved 80 integration tests passing. A subagent verified full architectural alignment across the stack.

## Artifacts

| Artifact | Title | Outcome |
|----------|-------|---------|
| [SPEC-292](../spec/) | Opencode Serve Adapter | Implemented. OpenCodeServerAdapter replaces TmuxPaneAdapter as the primary runtime path. |
| RUNBOOK-003 | Untethered Operator Guide | New. Operator guide for running the untethered bridge. |
| bin/swain-bridge | Bridge Launcher | New. Shell script to start the full untethered bridge stack. |
| [EPIC-073](../epic/Active/(EPIC-073)-Runtime-Plugin-System/(EPIC-073)-Runtime-Plugin-System.md) | Runtime Plugin System | Advanced. HTTP adapter built, tested, and live-verified. |

## Reflection

### What went well

- **HTTP adapter is far simpler than tmux scraping.** The OpenCodeServerAdapter sends a POST request and reads a JSON response. No pipe-pane file tailing, no ANSI stripping, no output dedup, no tail -f race conditions. The adapter code is roughly one-third the size of the tmux adapter it replaced. Simpler code means fewer bugs and easier testing.
- **Typing indicator fix was clean.** The indicator was tied to session death, which never fires for long-lived opencode serve sessions. Moving the stop trigger to the TextBatcher on_flush callback means the indicator stops when the response finishes, not when the session ends. This is the correct lifecycle — typing matches response, not session.
- **Synthetic UAT via computer-use MCP proved the system works from the user's perspective.** Sending messages through the Zulip desktop app (not the API) and verifying responses exercises the full path: desktop client to Zulip server to chat adapter to kernel to runtime adapter to opencode to Zulip. No shortcuts, no mocks.
- **80 integration tests provide real coverage.** Up from 64 in the previous session. The new tests cover the HTTP adapter, the typing indicator lifecycle, and the TextBatcher flush behavior. Each test documents a contract that future changes must honor.

### What was surprising

- **opencode serve vs opencode run is a critical distinction.** `opencode run` is single-shot — it starts a session, sends one message, and exits. `opencode serve` starts a persistent HTTP server that accepts messages over time and keeps chat history. The operator attaches with `opencode attach` to see the conversation. This distinction was not obvious from docs and required source reading to confirm.
- **Computer-use MCP needs careful app focus management.** The Evenlight screen overlay can intercept clicks meant for Zulip. Screenshots must confirm the correct window is focused before typing. Synthetic UAT works, but it is slower and more fragile than API-level testing. It is best used as a final validation, not a primary test loop.
- **Subagent architectural verification is high-value.** A dispatched subagent reviewed the full stack for alignment between the kernel, adapters, bridge script, and runbook. It caught no misalignment, which is the point — confidence that the pieces fit together after rapid iteration.

### What would change

- **Start with HTTP adapters when available.** The tmux adapter was built first because it was the known path. The HTTP adapter was simpler in every way: easier to implement, easier to test, easier to debug. When a runtime offers an API, use the API. Fall back to terminal automation only when no API exists.
- **Fix indicator lifecycle at design time.** The typing indicator bug was caused by assuming the session would be short-lived. When the session became persistent, the indicator never stopped. This is a design-level concern — lifecycle coupling should be reviewed whenever the session model changes.
- **Run synthetic UAT earlier in the cycle.** The computer-use UAT found no bugs, but it could have. Running it after all tests pass is safe but late. A quick smoke test through the real UI midway through the session would catch UX issues sooner.

### Patterns observed

- **API adapters beat terminal adapters.** This is now confirmed across three sessions. The Zulip SDK beat manual event polling (session 1). Opencode serve beat tmux pipe-pane (this session). The pattern is consistent: when an API exists, it is faster to build, test, and maintain than terminal automation. Terminal automation is a fallback, not a first choice.
- **Lifecycle coupling is a recurring bug source.** Typing indicator coupled to session death. TextBatcher coupled to message arrival rate. Both needed recoupling to the correct lifecycle event. When adding any stateful behavior, ask: "What event should start this? What event should stop it?" If the answer involves a different entity's lifecycle, the coupling is wrong.
- **Runbooks close the gap between working code and usable systems.** The bridge worked before RUNBOOK-003 existed, but only the developer could run it. The runbook makes the system operable by anyone with access. Writing the runbook also forced a review of the launcher script, which caught two missing environment variable checks.
- **Subagent verification scales trust.** Manually reviewing every file for alignment after rapid iteration is slow and error-prone. Dispatching a subagent with a clear checklist produces a structured confidence report. This is worth the cost for any session that touches multiple architectural layers.

### README drift

No README update needed. VISION-006 is still Active and the untethered operator is not yet shipped. RUNBOOK-003 covers operator-facing documentation for now.

## Learnings captured

| Item | Type | Summary |
|------|------|---------|
| API adapters over terminal adapters | Project rule | When a runtime offers an HTTP API, use it. Terminal automation (tmux, pipe-pane) is a fallback only. Confirmed across three sessions. |
| Typing indicator lifecycle coupling | Bug pattern | Stateful UX behaviors must couple to the correct lifecycle event. Session death is wrong for long-lived sessions; response completion is right. |
| Computer-use MCP for synthetic UAT | Technique | Sending messages through the real UI via computer-use MCP exercises the full path. Useful as final validation, but fragile due to focus management. |
| Runbooks force operability review | Process | Writing an operator guide surfaces missing checks in launcher scripts. Write the runbook before declaring the feature done. |
| Subagent architectural verification | Technique | Dispatch a subagent with a checklist to verify alignment across layers after rapid iteration. Cheaper than manual review, more structured than hoping. |
