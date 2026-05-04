---
title: "Worktree Session Isolation with Dedicated opencode serve Processes"
artifact: SPEC-296
status: Active
author: cristos
created: 2026-04-07
last-updated: 2026-04-18
parent-epic: EPIC-071
linked-artifacts:
  - DESIGN-025
  - SPEC-292
  - ADR-038
depends-on-artifacts:
  - DESIGN-025
  - SPEC-292
sourcecode-refs:
  - src/untethered/adapters/opencode_server.py
  - src/untethered/bridges/project.py
  - src/untethered/plugins/zulip_chat.py
---

# Worktree Session Isolation with Dedicated opencode serve Processes

## Summary

Each Zulip topic (worktree session) spawns its own dedicated `opencode serve` process. The topic name matches the worktree basename. This provides complete isolation between sessions and allows the operator to attach to any session via `opencode attach`.

## Motivation

NOTE (2026-04-18): In the swain-helm architecture, each worktree shares a single opencode serve instance (not a dedicated one per session). Sessions use `POST /session` on the shared server. Topic naming comes from the branch name, not the worktree basename. One session per worktree is enforced by the session registry. See SPEC-322 and SPEC-323 for updated implementation.

Currently, all control-topic sessions share a single `opencode serve` process on port 4097. This creates several problems:

1. **No worktree isolation**: Sessions can't have independent working directories
2. **Port conflicts**: Multiple bridges on the same machine can't coexist
3. **Topic naming**: Topics use artifact purpose, not worktree names
4. **Bridge duplication**: Worktree bridges accidentally process trunk messages

The fix: each worktree session gets its own `opencode serve` process with a dynamic port, running in that worktree's directory.

## Acceptance Criteria

1. `OpenCodeServerAdapter.spawn_server(worktree_path)` spawns `opencode serve --port <dynamic>` in the specified worktree directory.
2. The adapter finds an available port by binding to port 0 (OS assigns).
3. Server logs go to both a file (`.opencode-serve.log` in worktree) and stderr (bridge logs).
4. Health check timeout is extended to 60 seconds for cold-start worktree servers.
5. On success, the adapter emits `text_output` with the attach URL: `opencode attach http://127.0.0.1:<port>`.
6. The adapter's `stop()` method terminates the spawned server process.
7. `project.py` uses worktree basename (not artifact purpose) as the Zulip topic name.
8. `zulip_chat.py` uses the explicit `topic` field from `session_promoted` payload for topic assignment.
9. Stream filtering prevents worktree bridges from processing messages on streams not in their config.

## Implementation Notes

### OpenCodeServerAdapter changes

```python
async def spawn_server(self, worktree_path: str) -> bool:
    port = self._find_available_port()
    self.base_url = f"http://127.0.0.1:{port}"
    log_file = os.path.join(worktree_path, ".opencode-serve.log")
    
    # Spawn with stdout/err piped
    self._server_proc = await asyncio.create_subprocess_exec(
        "opencode", "serve", "--port", str(port), "--print-logs",
        cwd=worktree_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    
    # Pipe stdout to log file
    async def _pipe_stdout():
        if self._server_proc and self._server_proc.stdout:
            with open(log_file, "w") as f:
                while True:
                    line = await self._server_proc.stdout.readline()
                    if not line: break
                    f.write(line.decode())
                    f.flush()
    
    asyncio.create_task(_pipe_stdout())
    
    # Wait for health (60s timeout for cold start)
    healthy = await self.wait_for_health(timeout=60.0)
    if not healthy:
        await self.stop()
        return False
    
    # Emit attach URL
    if self.on_event:
        self.on_event(Event.text_output(
            bridge=self.bridge, session_id=self.session_id,
            content=f"Operator can attach: `opencode attach {self.base_url}`"
        ))
    return True
```

### project.py changes

Line 263-267: Extract worktree basename for topic:
```python
worktree = data.get("worktree", self.project_dir)
worktree_basename = os.path.basename(worktree) if worktree else None

self.on_event(Event.session_promoted(
    bridge=self.project, session_id=session_id,
    artifact=purpose or session_id,
    topic=worktree_basename or purpose,  # Use worktree name as topic
))
```

Line 269-283: Replace TmuxPaneAdapter with OpenCodeServerAdapter:
```python
adapter = OpenCodeServerAdapter(
    bridge=self.project,
    session_id=session_id,
    on_event=self.handle_runtime_event,
)
self._adapters[session_id] = adapter

# Spawn server in worktree
spawned = await adapter.spawn_server(worktree or self.project_dir)
if not spawned:
    # Handle spawn failure
    return

# Send initial prompt
if prompt:
    await adapter.send_command(Command.send_prompt(
        bridge=self.project, session_id=session_id, text=prompt,
    ))
```

### zulip_chat.py changes

Line 365-370: Use explicit topic from payload:
```python
if msg.type == "session_promoted":
    artifact = msg.payload.get("artifact", "")
    explicit_topic = msg.payload.get("topic")  # Use if provided
    topic = registry.assign(session_id, explicit_topic or artifact)
    # ... rest of handler
```

## Out of Scope

- Changing tmux-based runtimes for non-opencode agents (Claude, Gemini, etc.)
- Port persistence across bridge restarts (ports are dynamic per session)
- Server crash recovery within a session (adapter dies, session dies)

## Testing

1. Start a session via Zulip control topic
2. Verify topic name matches worktree basename (e.g., `vision-006-untethered-20260407`)
3. Verify `opencode attach` URL is printed and works
4. Verify two concurrent sessions have different ports
5. Verify worktree bridge doesn't process trunk messages

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-07 | | Created from VISION-006 decomposition. |
| Active | 2026-04-18 | -- | Architecture note: shared opencode serve per worktree, branch-name topics (ADR-046). See SPEC-322, SPEC-323. |
