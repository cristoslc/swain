---
title: "Retro: Untethered Operator Implementation"
artifact: RETRO-2026-04-06-untethered-operator-implementation
track: standing
status: Active
created: 2026-04-06
last-updated: 2026-04-06
scope: "VISION-006 implementation session — microkernel build through live round trip"
period: "2026-04-06"
linked-artifacts:
  - VISION-006
  - ADR-038
  - SPEC-291
  - DESIGN-024
  - DESIGN-025
  - EPIC-070
  - EPIC-071
  - EPIC-072
  - EPIC-073
---

# Retro: Untethered Operator Implementation

## Summary

Second session on [VISION-006](../vision/Active/(VISION-006)-Untethered-Operator/(VISION-006)-Untethered-Operator.md) Untethered Operator. The first session (see RETRO-2026-04-06-untethered-operator-mvp) brainstormed and smoke-tested. This session built the full stack: microkernel plugin architecture, Zulip chat adapter, project bridge, tmux runtime adapter, non-interactive launcher mode, and control topic flows. The session ended with a live round trip verified end to end — Zulip message in, kernel routes to project bridge, tmux session runs the command, pipe-pane captures output, response posted back to Zulip. 64+ integration tests added, 516 total tests passing.

## Artifacts

| Artifact | Title | Outcome |
|----------|-------|---------|
| [ADR-038](../adr/Active/(ADR-038)-Microkernel-Plugin-Architecture/(ADR-038)-Microkernel-Plugin-Architecture.md) | Microkernel Plugin Architecture | Implemented. HostKernel, PluginProcess, NDJSON stdio protocol all built and tested. |
| [SPEC-291](../spec/Active/(SPEC-291)-Non-Interactive-Launcher-Mode/(SPEC-291)-Non-Interactive-Launcher-Mode.md) | Non-Interactive Launcher Mode | Implemented. `bin/swain --format ndjson` mode built. |
| [DESIGN-024](../design/Active/(DESIGN-024)-Orchestrator-Event-Schema/(DESIGN-024)-Orchestrator-Event-Schema.md) | Orchestrator Event Schema | Updated to match implementation. Pipe-pane streaming, new command types. |
| [DESIGN-025](../design/Active/(DESIGN-025)-Unified-Session-Launcher/(DESIGN-025)-Unified-Session-Launcher.md) | Unified Session Launcher | Created. Converges bin/swain and Zulip control topic launch paths. Revised for tmux model. |
| [EPIC-070](../epic/Active/(EPIC-070)-Host-Bridge-Kernel/(EPIC-070)-Host-Bridge-Kernel.md) | Host Bridge Kernel | Active. Core kernel built and tested. |
| [EPIC-071](../epic/Active/(EPIC-071)-Project-Bridge-Kernel/(EPIC-071)-Project-Bridge-Kernel.md) | Project Bridge Kernel | Active. Session lifecycle management built. |
| [EPIC-072](../epic/Active/(EPIC-072)-Chat-Plugin-System/(EPIC-072)-Chat-Plugin-System.md) | Chat Plugin System | Active. Zulip adapter with call_on_each_message built. |
| [EPIC-073](../epic/Active/(EPIC-073)-Runtime-Plugin-System/(EPIC-073)-Runtime-Plugin-System.md) | Runtime Plugin System | Active. TmuxPaneAdapter built — pipe-pane + tail -f streaming. |

## Reflection

### What went well

- **TDD was highly productive.** The red-green cycle caught bugs before they reached integration. When the session switched from live debugging to test-first, velocity jumped. Every module started with failing tests, then implementation. The 64 integration tests now serve as living documentation of the protocol and adapter contracts.
- **Microkernel boundaries held up.** The [ADR-038](../adr/Active/(ADR-038)-Microkernel-Plugin-Architecture/(ADR-038)-Microkernel-Plugin-Architecture.md) plugin architecture (HostKernel spawns PluginProcess children over NDJSON stdio) proved clean in practice. Each adapter — Zulip, project bridge, tmux — was built and tested in isolation, then wired together. The NDJSON protocol made debugging easy because every message was human-readable.
- **Operator course-corrections saved hours.** The operator caught the subprocess pipe model early and redirected to tmux. The operator also flagged that `call_on_each_message` exists in the Zulip SDK, replacing 100+ lines of manual event queue code. Both corrections happened before significant code was written the wrong way.
- **pipe-pane + tail -f solved output capture cleanly.** After considering FIFOs (which have open/close race conditions), the tmux pipe-pane approach proved robust. Output streams to a file; tail -f reads it. No blocking, no races, no lost data.

### What was surprising

- **pkill -f with broad patterns is dangerous.** A cleanup command matching "untethered" in process arguments also matched the operator's shell (because the working directory path contained "untethered"). The operator's terminal was killed mid-session. Process cleanup needs exact PID tracking, not pattern matching.
- **Zulip message timing is unintuitive.** Messages only arrive after a queue is registered. If the adapter restarts, messages sent between shutdown and queue registration are invisible. This is not a bug — it is how Zulip's event system works. But it caused "missing messages" during development that looked like bugs.
- **Mock paths can hide real wiring bugs.** The `UNTETHERED_MOCK_LLM=1` environment variable triggers a mock response path that fires before the TmuxPaneAdapter is ever called. Tests using that mock prove the control flow works, but they do not prove tmux wiring works. The mock path and the real path diverge at the adapter boundary.
- **SDK convenience methods beat raw API calls.** The Zulip SDK's `call_on_each_message` handles queue registration, heartbeat filtering, reconnection, and error recovery. The manual `register` + `get_events` loop reimplemented all of that, badly. When an SDK wraps a complex protocol, use the wrapper first and only drop down when the wrapper cannot do what you need.

### What would change

- **Write tests before live debugging.** The session spent time running the full stack to diagnose issues that would have been caught by a unit test. When the approach shifted to TDD, each module worked on the first integration attempt. Live debugging has its place, but only after the unit-level contract is proven.
- **Track PIDs, not patterns.** Process cleanup should store the PID at spawn time and kill that exact PID. Pattern-based `pkill -f` is a landmine when working directory paths or environment variables contain the search term.
- **Test the real adapter, not just the mock path.** Integration tests should include at least one path that exercises the actual TmuxPaneAdapter (or a thin fake that preserves its interface), not just the mock LLM shortcut.
- **Document SDK capabilities before writing adapters.** Reading the Zulip SDK's `call_on_each_message` source would have saved the manual event loop entirely. For any new adapter, spend 15 minutes reading the SDK before writing wrapper code.

### Patterns observed

- **Operator corrections cluster at architecture boundaries.** Both major corrections (subprocess to tmux, manual polling to SDK) happened at the boundary between "how the system talks to the outside world" and "how the system works internally." The agent is good at internal design but over-engineers external integration. Operators catch this because they know the external tools.
- **TDD velocity compounds.** Each tested module made the next module faster to build, because the contract was already proven. The project bridge tests proved the session lifecycle, so the tmux adapter only needed to prove I/O. The compound effect was visible — later modules shipped faster than earlier ones.
- **Race conditions live at process boundaries.** FIFO open/close races, Zulip queue registration timing, pkill pattern collisions — every bug in this session happened where two processes interact. The fix is always the same: make the handoff explicit (PID files, registered queues, pipe-pane files) rather than implicit (pattern matching, timing assumptions, FIFO blocking).

### README drift

The README does not mention the untethered operator, remote interaction, Zulip integration, or the microkernel architecture. This is expected — VISION-006 is still Active and the implementation is not yet shipped. No README update is needed until the feature reaches a user-facing milestone.

## Learnings captured

| Item | Type | Summary |
|------|------|---------|
| PID-based process cleanup | SPEC candidate | Replace all `pkill -f` patterns in untethered operator with PID file tracking. Broad pattern matching killed the operator's shell. |
| Integration tests for real adapters | SPEC candidate | Add integration test paths that exercise TmuxPaneAdapter (not just the mock LLM shortcut). Mock path hides tmux wiring bugs. |
| SDK-first adapter development | ADR candidate | When building adapters for external services, read the SDK source and use convenience methods before writing raw API calls. Manual Zulip event loop was 100+ lines that `call_on_each_message` replaced. |
| Zulip queue registration timing | SPEC candidate | Document and test the message gap between adapter restarts. Messages sent while no queue is registered are lost. Consider persistent queue IDs or catch-up polling. |
