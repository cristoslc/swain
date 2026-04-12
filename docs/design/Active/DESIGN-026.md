---
title: "Project Bridge Session Routing Architecture"
artifact: DESIGN-026
track: standing
status: Active
domain: system
author: "gemma4:31b-cloud"
created: 2026-04-07
last-updated: 2026-04-07
priority-weight: high
linked-artifacts:
  - "[SPEC-298](../../spec/Active/(SPEC-298)-Control-Thread-Worktree-and-Session-Spawning/(SPEC-298)-Control-Thread-Worktree-and-Session-Spawning.md)"
  - "[EPIC-071](../../epic/Active/(EPIC-071)-Project-Bridge-Kernel/(EPIC-071)-Project-Bridge-Kernel.md)"
  - "[EPIC-072](../../epic/Active/(EPIC-072)-Chat-Plugin-System/(EPIC-072)-Chat-Plugin-System.md)"
artifact-refs:
  - rel: [aligned]
    id: EPIC-071
sourcecode-refs: []
swain-do: required
---

# Project Bridge Session Routing Architecture

## Design Intent

**Context:** The project bridge manages multiple concurrent opencode sessions across multiple worktrees, routing each session's output to the correct Zulip topic.

**Goals:**
- Sessions are isolated — output from one worktree never leaks to another topic.
- The bridge owns routing logic; opencode servers know nothing about Zulip.
- Session lifecycle (spawn, active, idle, dead) is tracked and recoverable.
- Topic IDs are stable and persisted across bridge restarts.

**Constraints:**
- Opencode speaks JSON over stdio — no Zulip awareness.
- Chat adapter is a separate plugin — bridge routes to it, not directly to Zulip.
- Multiple sessions can run concurrently under one project bridge.

**Non-goals:**
- Direct opencode-to-Zulip communication (violates layering).
- Session migration between bridges (future enhancement).

## Session Registry

The project bridge maintains an in-memory registry of active sessions:

```python
class SessionRegistry:
    sessions: dict[SessionId, SessionState]
    
class SessionState:
    session_id: str           # e.g., "session-20260407-001"
    artifact_id: str          # e.g., "SPEC-123"
    worktree_path: str        # absolute path to worktree
    zulip_topic_id: int       # Zulip topic/message ID for this session
    lifecycle_state: str      # spawning | active | idle | dead
    opencode_pid: int         # PID of opencode subprocess
    created_at: datetime
    last_activity: datetime
```

**Persistence:** The registry is written to disk (`<project>/.agents/session-registry.json`) on every state change. On restart, the bridge reconciles:
- Sessions with dead PIDs → mark as `dead`, post to control thread.
- Sessions with live PIDs → resume routing.

## Session-to-Topic Binding

When a session is spawned:

1. Bridge creates Zulip topic via chat adapter: `create_topic(room_id, artifact_id)` → returns `topic_id`.
2. Bridge stores `topic_id` in session registry.
3. All events from this session are forwarded with `topic_id` metadata.
4. Chat adapter posts to the topic.

**Topic naming convention:**
```
<artifact-id> — <short-title>
e.g., "SPEC-123 — Control Thread Worktree Spawning"
```

## C4 Container Diagram

```mermaid
C4Container
    title Project Bridge Session Routing — Container View
    
    Person(operator, "Operator", "Uses Zulip mobile/desktop app")
    
    Container_Boundary(project_bridge, "Project Bridge (per project)") {
        Container(control_handler, "Control Thread Handler", "Python", "Parses /swain-do commands from control thread")
        Container(session_registry, "Session Registry", "Python + JSON file", "Tracks active sessions, topic bindings, lifecycle state")
        Container(session_router, "Session Router", "Python", "Forwards opencode events to chat adapter with topic_id")
        Container(opencode_spawner, "Opencode Spawner", "Python", "Spawns opencode subprocess in worktree, captures stdio")
    }
    
    Container(chat_adapter, "Chat Adapter Plugin", "Go/Python", "Translates bridge events to Zulip API calls")
    Container(opencode, "Opencode Server", "Rust/Node", "Runs in worktree, emits JSON events over stdio")
    
    System(zulip, "Zulip Cloud", "Chat platform", "Hosts project rooms, control threads, session threads")
    
    Rel(operator, zulip, "reads/posts messages")
    Rel(chat_adapter, zulip, "posts events, reads commands")
    Rel(control_handler, chat_adapter, "receives /swain-do commands")
    Rel(control_handler, session_registry, "checks artifact collision")
    Rel(control_handler, opencode_spawner, "triggers session spawn")
    Rel(opencode_spawner, opencode, "spawns subprocess, captures stdio")
    Rel(opencode, session_router, "emits JSON events over stdio")
    Rel(session_router, session_registry, "looks up topic_id by session_id")
    Rel(session_router, chat_adapter, "forwards events with topic_id")
```

## Sequence Diagram: Session Spawn

```mermaid
sequenceDiagram
    autonumber
    participant O as Operator
    participant Z as Zulip
    participant CA as Chat Adapter
    participant CH as Control Handler
    participant SR as Session Registry
    participant OS as Opencode Spawner
    participant OC as Opencode (worktree)
    participant Router as Session Router
    
    O->>Z: "/swain-do dispatch SPEC-123" in control thread
    Z->>CA: message event
    CA->>CH: parse command → dispatch SPEC-123
    CH->>SR: check collision for SPEC-123
    SR-->>CH: no existing session
    CH->>OS: spawn_session(SPEC-123)
    OS->>OS: create worktree via swain-do
    OS->>CA: create_topic(room, "SPEC-123 — Title")
    CA->>Z: create topic
    Z-->>CA: topic_id: 42
    OS->>OC: spawn opencode --format json in worktree
    OS->>SR: register session(session_id, SPEC-123, worktree_path, topic_id=42)
    OS-->>CH: session spawned
    CH->>CA: post "Session started: SPEC-123" to topic 42
    CA->>Z: post message
    OC->>Router: JSON event {type: "output", content: "..."}
    Router->>SR: lookup topic_id for session_id
    SR-->>Router: topic_id=42
    Router->>CA: forward event {topic_id: 42, ...}
    CA->>Z: post to topic 42
```

## Session Lifecycle States

| State | Transition In | Transition Out | Trigger |
|-------|---------------|----------------|---------|
| `spawning` | — | `active` | Worktree created, opencode starting |
| `active` | `spawning` | `idle`, `dead` | Opencode ready, processing prompts |
| `idle` | `active` | `active`, `dead` | No activity for N minutes |
| `dead` | any | — | Opencode exited, session ended |

**State machine:**
```mermaid
stateDiagram-v2
    [*] --> spawning: /swain-do dispatch
    spawning --> active: opencode ready
    active --> idle: timeout (N min)
    idle --> active: new prompt
    active --> dead: opencode exit
    idle --> dead: opencode exit
    dead --> [*]
```

## Event Schema (Opencode → Bridge)

Opencode emits JSON over stdout. The bridge wraps events with session metadata:

**Opencode native event:**
```json
{
  "type": "output",
  "content": "Working on SPEC-123...",
  "timestamp": "2026-04-07T10:30:00Z"
}
```

**Bridge-wrapped event (to chat adapter):**
```json
{
  "bridge": "project-<project-id>",
  "session_id": "session-20260407-001",
  "topic_id": 42,
  "event": {
    "type": "output",
    "content": "Working on SPEC-123...",
    "timestamp": "2026-04-07T10:30:00Z"
  }
}
```

The chat adapter uses `topic_id` to route to the correct Zulip topic.

## Error Handling

| Error | Detection | Recovery |
|-------|-----------|----------|
| Opencode crashes | PID exits, stdio closes | Mark session `dead`, post to control thread |
| Zulip topic creation fails | Chat adapter returns error | Abort spawn, report to control thread |
| swain-do worktree creation fails | Non-zero exit code | Abort spawn, report error |
| Bridge restarts mid-session | PID dead on reconcile | Mark `dead`, offer respawn |
| Topic ID lost (corrupt registry) | Topic lookup returns None | Create new topic, update registry |

## Deployment Notes

- **Session registry location:** `<project>/.agents/session-registry.json`
- **Worktree location:** `<repo-root>/../<repo-name>-<branch>-<session-id>/`
- **Chat adapter:** Single instance per project bridge, spawned as subprocess
- **Zulip topic lifecycle:** Topics persist after session ends (Zulip behavior). Bridge does not delete topics.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-07 | | Created for SPEC-298 session routing |
