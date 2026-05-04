---
title: "Retro: VISION-006 Untethered Operator — Full Session"
artifact: RETRO-2026-04-07-vision-006-full
track: standing
status: Active
created: 2026-04-07
last-updated: 2026-04-07
scope: "Complete VISION-006 implementation session — from ADR confirmation through live UAT"
period: "2026-04-06 to 2026-04-07"
linked-artifacts:
  - VISION-006
  - INITIATIVE-018
  - ADR-037
  - ADR-038
  - ADR-039
  - DESIGN-024
  - DESIGN-025
  - SPEC-180
  - SPEC-291
  - SPEC-292
  - RUNBOOK-003
  - EPIC-072
  - EPIC-073
---

# Retro: VISION-006 Untethered Operator — Full Session

## Summary

This was the longest and most productive single session in the swain project to date. It took VISION-006 from a set of ADRs and a dead-letter monolith to a working system where the operator types in Zulip and gets LLM-powered responses backed by a persistent opencode session. The session ran through three major architectural phases, two pivots driven by operator correction, and ended with a synthetic UAT via the Zulip desktop app.

**By the numbers:**
- 34 commits merged to trunk.
- 4,939 lines inserted across 32 files.
- 80 integration tests.
- 6 new artifacts (2 DESIGNs, 2 SPECs, 1 RUNBOOK, 1 evidence trove).
- 3 retros written during the session (this is the consolidated view).
- 2 major architectural pivots.
- 1 synthetic UAT via computer-use MCP.

---

## Timeline

### Phase 1: ADR confirmation and monolith rebuild (early session)

Started by confirming ADR-037 (Zulip Cloud as chat platform). Then attempted to wire the existing monolith code into the ADR-038 plugin architecture. The first attempt built everything in-process — Python classes calling each other directly. The operator caught this immediately: "you built a POC not an MVP." The code violated ADR-038's subprocess plugin model.

**Pivot 1: From in-process classes to subprocess plugins.**

Rebuilt the entire stack: `HostKernel` spawns `PluginProcess` subprocesses speaking NDJSON over stdio. Chat adapter and project bridge are separate executables. This was the right call — it matches the ADR and allows future plugins in any language.

Key deliverables:
- `HostKernel` and `PluginProcess` (kernel.py).
- `zulip_chat.py` plugin with Zulip polling.
- `project_bridge.py` plugin with session lifecycle.
- `protocol.py` with full event/command schema (DESIGN-024).
- NDJSON encode/decode, ConfigMessage on stdin line 0.

### Phase 2: Zulip polling, tmux adapter, live round trip (mid session)

Built the Zulip chat adapter. Initially used manual `register()` + `get_events()` in a `run_in_executor` loop. This worked in tests but failed live — the blocking long-poll never returned operator messages. Spent significant time debugging (adding INFO logs, testing with direct API calls, checking narrow filters, verifying bot subscriptions).

**Root cause:** The manual poll loop's `run_in_executor` lambda closures were not the issue. The Zulip SDK's `call_on_each_message` handles all the complexity (registration, heartbeats, re-registration, backoff). Switching to it fixed message delivery instantly.

**Lesson: Read the SDK before reimplementing its internals.**

Then built the `TmuxPaneAdapter` — runtime runs in a tmux session, output via `pipe-pane` + `tail -f`, input via `tmux send-keys`. This worked and proved the "untethered" concept (operator can `tmux attach`). But the output was noisy:
- Raw ANSI escape codes in Zulip posts.
- Each line was a separate Zulip message (spam).
- The `opencode run` command was single-shot — no session persistence.
- Shell glob characters (`?`) in operator messages caused zsh errors.

Fixed with: ANSI stripping, `TextBatcher` (2s debounce), `shlex.quote`, message ID dedup.

Key deliverables:
- `TmuxPaneAdapter` with pipe-pane streaming.
- `TextBatcher` for coalescing output.
- `TypingIndicator` for Zulip typing status.
- `SessionTopicRegistry` for artifact-named threads.
- `session_promoted` event for delayed thread creation.
- `control_message` and `launch_session` command types.
- `bin/swain --format ndjson` non-interactive launcher mode (SPEC-291).
- 64 integration tests.

### Phase 3: opencode serve HTTP adapter (late session)

The operator asked why sessions weren't visible in `tmux ls`. Answer: `opencode run` is single-shot — sessions die after each message. The operator suggested `opencode serve` (headless HTTP server). This was the second major pivot.

**Pivot 2: From tmux terminal scraping to HTTP API.**

Explored the opencode serve API by starting a server, probing endpoints, reading the OpenAPI spec. Found undocumented session endpoints (`POST /session`, `POST /session/{id}/message`). Built an evidence trove documenting the full API.

The `OpenCodeServerAdapter` is dramatically simpler than `TmuxPaneAdapter`:
- No tmux, no pipe-pane, no tail -f, no ANSI codes, no file I/O.
- Just HTTP POST for messages, JSON parsing for responses.
- Session persists server-side — full chat history across messages.
- Operator attaches via `opencode attach http://...`.

Key deliverables:
- `OpenCodeServerAdapter` (opencode_server.py).
- Evidence trove for the API (opencode-server-api-trove.md).
- SPEC-292 with 8 acceptance criteria.
- DESIGN-025 updated with two adapter strategies (HTTP + tmux fallback).
- `bin/swain-bridge` launcher script.
- RUNBOOK-003 operator guide.
- 80 integration tests.
- Synthetic UAT via computer-use MCP through Zulip desktop app.

---

## Architectural decisions made during the session

| Decision | Rationale | Artifact |
|----------|-----------|----------|
| Subprocess plugins over in-process classes | ADR-038 compliance; language-agnostic plugins | ADR-038 |
| `call_on_each_message` over manual poll loop | SDK handles complexity; manual loop was fragile | — |
| `pipe-pane` + `tail -f` over `capture-pane` polling | Real-time streaming without polling interval | DESIGN-025 |
| `opencode serve` HTTP API over tmux scraping | Cleaner, simpler, persistent sessions, operator attach | DESIGN-025, SPEC-292 |
| `--format ndjson` flag on `bin/swain` | Keeps terminal and non-terminal control surfaces in sync | SPEC-291 |
| `session_promoted` delays thread creation | Thread gets a meaningful name from the artifact, not a session ID | DESIGN-025 |
| `TextBatcher` with 2s debounce | Coalesces rapid output into single Zulip posts | — |
| Typing indicator stops on flush, not session death | Persistent sessions never die; indicator must match response lifecycle | — |
| `opencode` for control queries, `claude` for /work sessions | Different runtimes for different use cases; adapter per runtime | DESIGN-025 |
| Security domain config in `~/.config/swain/domains/` | Per-domain credentials; file permissions for secrets | — |

---

## Bugs found and fixed

| Bug | Root cause | Fix |
|-----|-----------|-----|
| Messages not delivered to chat plugin | Manual `register`/`get_events` loop hung | Switched to SDK `call_on_each_message` |
| Operator's tmux session detaches on bridge restart | `pkill -f 'untethered'` matched shell CWD path | Use specific patterns: `pkill -f 'untethered-host'` |
| ANSI escape codes in Zulip posts | `pipe-pane` captures raw terminal output | `strip_ansi()` regex before posting |
| Each output line is a separate Zulip message | No batching; each `text_output` event posted immediately | `TextBatcher` with 2s quiet-period debounce |
| Zulip message delivered twice | No dedup; SDK may redeliver on reconnect | Message ID set with 1000-entry cap |
| `zsh: no matches found: open?` | `?` glob expansion in tmux shell command | `shlex.quote()` for all arguments |
| Typing indicator persists forever | Stopped on `session_died` but persistent sessions never die | Stopped on `TextBatcher.flush` via `on_flush` callback |
| `bin/swain` crashes on missing `focus_lane` | `set -euo pipefail` + grep returning exit 1 | Added `|| true` to grep pipeline |
| No session persistence | `opencode run` is single-shot | Switched to `opencode serve` with persistent sessions |
| FIFO race condition in tmux adapter | `pipe-pane` opens/closes FIFO per write batch | Switched to regular file + `tail -f` |

---

## Tests written

| Test file | Count | Coverage |
|-----------|-------|----------|
| `test_untethered_bdd.py` | 14 | Zulip polling, adapter wiring, smoke |
| `test_control_flows.py` | 27 | Control message parsing, relay events, session promotion, launcher, mock LLM round trip, Zulip Cloud format |
| `test_subprocess_plumbing.py` | 6 | Real pipe I/O, project bridge subprocess, chat plugin poll-to-emit |
| `test_tmux_adapter.py` | 9 | Tmux session lifecycle, pipe-pane output, send-keys input, ANSI stripping, attachability |
| `test_opencode_server_adapter.py` | 6 | Mock HTTP server, health check, session creation, message sending, session persistence |
| `test_bridge_launcher.py` | 6 | Script executable, help flag, runbook existence and content |
| `test_zulip_adapter.py` | 12 | Event formatting, message parsing, slash commands |
| **Total** | **80** | |

---

## What went well

1. **TDD rescued the session.** The first half was spent debugging live (adding log lines, restarting the bridge, sending test messages). The operator said "stop. reset. TDD from architectural plan." After that, tests drove every change. Every pivot was validated before going live. The live debugging wasted 60+ minutes; the TDD approach wasted zero.

2. **Operator corrections prevented architecture debt.** Two major pivots — from in-process to subprocess, from tmux to HTTP — were both prompted by operator feedback, not by test failures. The operator saw the design diverging from intent and corrected immediately. Without those corrections, the system would have worked but been architecturally wrong.

3. **The subagent verification pattern works at scale.** Dispatching a subagent to read all artifacts and check alignment found no contradictions across 6 artifacts and 12 source files. This is cheaper than manual review and more thorough. Worth doing after every multi-artifact session.

4. **Synthetic UAT via computer-use MCP exercises the real path.** Typing a message in the Zulip desktop app and seeing a response proves the system works from the operator's perspective. No mocks, no shortcuts. The "4" response to "what is 2+2?" is the definitive proof.

5. **The evidence trove for opencode API was high-value.** Spending 20 minutes probing endpoints, reading the OpenAPI spec, and documenting findings saved hours of implementation guesswork. The trove documented undocumented endpoints that the official docs don't cover.

6. **Mermaid diagrams in design docs.** The operator explicitly requested mermaid over ASCII art. The flowchart diagrams in DESIGN-025 are clearer and render in any markdown viewer. This is now a project rule.

## What went poorly

1. **Live debugging without tests.** The Zulip polling bug consumed the most time of any single issue. Adding log lines, restarting the bridge, sending test messages, checking log output — this is slow-loop debugging. The fix (switch to `call_on_each_message`) was obvious once the SDK source was read.

2. **The in-process class architecture was built and then thrown away.** The first implementation violated ADR-038. It worked, had tests, but was architecturally wrong. The operator caught it; the tests didn't. This is a reminder that tests prove behavior, not architecture. Architecture conformance needs review, not just green tests.

3. **Multiple bridge restarts lost operator messages.** Every `pkill -f untethered` killed the bridge, which killed the Zulip event queue. Messages sent between restarts were lost. The operator sent the same message 4-5 times before one landed. This is a terrible UX and needs a startup-replay mechanism.

4. **The tmux adapter was built, tested, and then mostly replaced.** It still exists as a fallback, but the HTTP adapter is the primary path. The pipe-pane + tail -f approach works but is fragile (FIFO race conditions, ANSI codes, output batching). Building it was educational but the HTTP adapter made most of it unnecessary.

5. **`pkill -f 'untethered'` killing operator shells** is a process management anti-pattern. The path `vision-006-untethered-operator` contains "untethered", so any process with that CWD matched the pattern. PID file tracking or more specific patterns are needed.

## What was surprising

1. **opencode serve's session endpoints aren't in the OpenAPI spec.** The `POST /session` and `POST /session/{id}/message` endpoints work but aren't documented in the `/doc` OpenAPI schema. They were found by probing common REST patterns. The JS SDK wraps them but the Python adapter uses raw HTTP.

2. **Zulip typing indicators auto-expire after 15 seconds.** This is a safety feature — if the bridge crashes, the indicator clears itself. No explicit cleanup needed. The SDK's design assumed transient clients, which is exactly our model.

3. **`opencode run` vs `opencode serve` is the same binary but completely different architectures.** `run` is a CLI tool that processes one message and exits. `serve` is a long-running HTTP server. The session model, persistence, and client interaction are entirely different. This distinction is not prominently documented.

4. **The operator's Zulip message "what gh issues are open?" triggered a full `gh issue list` execution.** The Gemma 4 model, running through opencode with swain tools, autonomously decided to run a shell command, parsed the output, and formatted a summary. This was not explicitly programmed — the model chose the right tool. This is the "untethered" vision working as intended.

---

## Patterns confirmed

| Pattern | Evidence | Sessions confirming |
|---------|----------|-------------------|
| API adapters beat terminal adapters | Manual poll → SDK; tmux → HTTP API | 3 |
| TDD after architecture, not before live debugging | Live debugging wasted 60 min; TDD wasted 0 | 2 |
| Operator corrections prevent architecture debt | In-process → subprocess; tmux → HTTP | 2 |
| Evidence troves pay for themselves | opencode API trove saved hours of guesswork | 1 |
| Subagent verification scales trust | Alignment check across 6 artifacts + 12 files | 1 |
| Lifecycle coupling is a recurring bug source | Typing indicator; TextBatcher; session state | 3 |

---

## Learnings captured

| Item | Type | Summary |
|------|------|---------|
| API adapters over terminal adapters | Project rule | When a runtime has an HTTP/API mode, use it. Terminal automation (tmux, pipe-pane, send-keys) is a fallback. Confirmed across manual polling → SDK, tmux → HTTP, FIFO → tail -f. |
| Read SDK source before wrapping APIs | Process rule | The Zulip SDK's `call_on_each_message` handles registration, heartbeats, backoff, and re-registration. Reimplementing it manually wasted 60+ minutes and introduced a bug. |
| PID-based process cleanup | SPEC candidate | `pkill -f` with broad patterns matches unrelated processes via CWD paths. Use PID files or specific executable name patterns. |
| TDD after architecture, not before live debugging | Process rule | Write integration tests that prove the pipeline works with mocks. Only go live after tests pass. Live debugging is the slow loop. |
| Lifecycle coupling review on model changes | Design rule | When the session model changes (short-lived → persistent), review all stateful behaviors (typing indicator, batcher, dedup) for lifecycle coupling. |
| Evidence troves for external APIs | Process rule | Before building an adapter for an external API, probe the endpoints, read the spec, and write a trove. 20 minutes of research saves hours of guesswork. |
| Mermaid diagrams, not ASCII art | Style rule | Use mermaid flowchart syntax for all diagrams in design docs. Meaningful node names, all labels quoted. |
| Subagent architectural verification | Technique | After multi-artifact sessions, dispatch a subagent to verify alignment across all changed artifacts and code. Structured checklist, concise report. |
| `opencode serve` for persistent sessions | Technical note | `opencode run` is single-shot. `opencode serve` is a persistent HTTP server with session management, chat history, and operator attachment via `opencode attach`. |
| Zulip typing indicator auto-expires | Technical note | Zulip clears the typing indicator 15 seconds after the last pulse. Safe by design — no cleanup needed on crash. |
| TextBatcher on_flush is the response boundary | Design pattern | For long-lived sessions, "response complete" is signaled by the batcher flushing, not by session death. The on_flush callback is the integration point for any "response arrived" behavior. |

---

## Open items for future sessions

1. **Crash recovery for opencode serve** (SPEC-292 AC7). If the server dies, the adapter should restart it and reconnect.
2. **SSE streaming** (SPEC-292 AC4). Currently using synchronous POST/response. SSE would give real-time streaming for long responses.
3. **Approval mechanism** (DESIGN-025 open question). How to send approvals to runtimes that need them. opencode may have a permission endpoint.
4. **Session adoption** (DESIGN-025 Phase C). Bridge discovers existing tmux sessions from `bin/swain` terminal launches.
5. **Query triage** (DESIGN-025 Phase C). Detect questions vs work requests without needing `/work`.
6. **PID file tracking** for bridge and server processes. Replace `pkill -f` patterns.
7. **Zulip message replay on startup.** Fetch recent messages from the stream to catch anything sent while the bridge was down.
8. **Output filtering.** Strip opencode banner lines, tool call noise, and other non-content output before posting to Zulip.
