---
title: "Retro: Untethered Operator Phase B"
artifact: RETRO-2026-04-06-untethered-operator-phase-b
track: standing
status: Active
created: 2026-04-06
last-updated: 2026-04-06
scope: "VISION-006 Phase B — opencode serve discovery, tmux adapter hardening, live round trip with Gemma 4"
period: "2026-04-06"
linked-artifacts:
  - VISION-006
  - SPEC-292
  - DESIGN-025
  - EPIC-072
  - EPIC-073
---

# Retro: Untethered Operator Phase B

## Summary

Third session on [VISION-006](../vision/Active/(VISION-006)-Untethered-Operator/(VISION-006)-Untethered-Operator.md) Untethered Operator. The previous session (see RETRO-2026-04-06-untethered-operator-implementation) built the microkernel stack and achieved first round trip. This session hardened the stack for real use: replaced manual event handling with Zulip SDK `call_on_each_message`, built the TmuxPaneAdapter with pipe-pane streaming, verified a live Zulip-to-tmux-to-Zulip round trip with Gemma 4 via Ollama Cloud, added TextBatcher and TypingIndicator for UX polish, and discovered that opencode's `serve` mode exposes an HTTP API that is cleaner than tmux scraping. The session ended with a strategic pivot: opencode serve is the MVP adapter path (SPEC-292), tmux is the fallback.

## Artifacts

| Artifact | Title | Outcome |
|----------|-------|---------|
| [SPEC-292](../spec/) | Opencode Serve Adapter | New. HTTP API adapter for opencode's serve mode, replacing tmux as primary runtime path. |
| [DESIGN-025](../design/Active/(DESIGN-025)-Unified-Session-Launcher/(DESIGN-025)-Unified-Session-Launcher.md) | Unified Session Launcher | Updated with two adapter strategies and mermaid diagrams. |
| [EPIC-072](../epic/Active/(EPIC-072)-Chat-Plugin-System/(EPIC-072)-Chat-Plugin-System.md) | Chat Plugin System | Advanced. Zulip adapter now uses SDK call_on_each_message. |
| [EPIC-073](../epic/Active/(EPIC-073)-Runtime-Plugin-System/(EPIC-073)-Runtime-Plugin-System.md) | Runtime Plugin System | Advanced. TmuxPaneAdapter built and live-verified. Opencode serve path identified. |

## Reflection

### What went well

- **Live round trip proved the architecture works.** A Zulip message went from the chat adapter through the kernel to the tmux runtime, Gemma 4 processed it via Ollama Cloud, and the response came back to Zulip. This was the first real proof that the full stack works end to end with a real LLM.
- **TextBatcher and TypingIndicator improved UX fast.** Rapid `text_output` events from tmux pipe-pane were flooding Zulip with one post per line. TextBatcher coalesces them into single posts. TypingIndicator shows typing status while the session works and auto-expires after 15 seconds. Both were small additions with big user impact.
- **ANSI stripping and message dedup caught real issues.** Terminal output contains escape codes that render as garbage in chat. Dedup prevents the same output from posting twice when pipe-pane re-reads overlapping chunks. Both were bugs found in live testing that would not have shown up in unit tests alone.
- **Opencode serve discovery was high-value research.** Finding that opencode exposes an HTTP API for session management means the MVP adapter can skip terminal scraping entirely. HTTP request/response is simpler to implement, test, and debug than pipe-pane file tailing. This changes the build plan for the better.

### What was surprising

- **opencode run is single-shot with no session persistence.** The initial assumption was that `opencode run` would keep a session alive for follow-up messages. It does not. Each invocation starts fresh. Only `opencode serve` maintains a persistent session over HTTP. This distinction was not in any docs — it came from reading source code and testing.
- **Zulip typing indicator is safe by design.** The typing status auto-expires after 15 seconds without a pulse. There is no way to leave a "ghost typing" state. This made the TypingIndicator implementation simpler than expected — just pulse every 10 seconds and stop when done.
- **pipe-pane works but FIFO approach has race conditions.** Named pipes (FIFOs) seemed like the right tool for streaming terminal output. In practice, the open/close semantics create races: if the reader opens before the writer, it blocks; if the writer closes, the reader gets EOF. pipe-pane to a regular file with tail -f avoids all of this.
- **Mermaid diagrams are preferred over ASCII art.** The operator gave direct feedback that mermaid renders better in their tooling. DESIGN-025 was updated to use mermaid for all architecture diagrams. This is a project-wide preference going forward.

### What would change

- **Test before live debugging, every time.** This lesson appeared in the previous retro and repeated in this session. Time spent running the full stack to find a bug was time that a unit test would have saved. The pattern is consistent enough to make it a rule: no live testing until the unit-level contract passes.
- **Research runtime APIs before building adapters.** The opencode serve HTTP API was discovered after the TmuxPaneAdapter was built. If the research had come first, the tmux adapter might have been skipped or deprioritized. For any new runtime, spend 30 minutes looking for an API before writing terminal automation.
- **Use narrow process patterns or PID files.** The pkill -f lesson from the previous retro was reinforced when broad path matching continued to cause problems. PID files are the only safe approach for process cleanup in a development environment where paths contain project names.

### Patterns observed

- **Two-adapter strategy reduces risk.** Having both an HTTP adapter (opencode serve) and a terminal adapter (tmux) means the system can fall back if one runtime does not support the primary path. The cost is two adapter implementations, but the insurance is worth it for a system that must support multiple runtimes.
- **UX polish compounds trust.** TextBatcher and TypingIndicator are small features, but they make the system feel reliable rather than broken. Without batching, the chat floods with fragments. Without typing status, the user does not know if the system is working or stuck. These are not features — they are table stakes for a chat interface.
- **Evidence troves pay for themselves.** Building a trove of opencode server API evidence (HTTP endpoints, request/response shapes, session lifecycle) took 20 minutes but saved hours of trial-and-error during adapter design. The trove is also reusable for SPEC-292 acceptance criteria.
- **Retro lessons repeat until they become rules.** "Test before live debugging" appeared in the previous retro and repeated here. "Research APIs before building" is the same lesson in a different shape. When a lesson appears twice, it should become a project rule, not just a suggestion.

### README drift

No README update needed. VISION-006 is still Active and the untethered operator is not yet shipped.

## Learnings captured

| Item | Type | Summary |
|------|------|---------|
| Opencode serve HTTP API | SPEC-292 | opencode serve exposes persistent sessions over HTTP. Cleaner than tmux scraping. MVP adapter path. |
| opencode run is single-shot | Documentation | No session persistence in run mode. Only serve mode maintains state between requests. |
| Mermaid over ASCII | Project preference | Operator prefers mermaid diagrams. Update DESIGN artifacts to use mermaid going forward. |
| Repeated retro lessons become rules | Process | When the same lesson appears in two retros, promote it to a project rule in AGENTS.md or a relevant ADR. |
| TextBatcher pattern | Reusable component | Coalescing rapid events into batched posts is a general pattern for any chat adapter, not just Zulip. |
