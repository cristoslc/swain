"""NDJSON plugin protocol — the published language from DESIGN-024.

All events and commands that flow between kernel components (host bridge,
project bridge) and plugins (chat adapters, runtime adapters) over stdio.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any


# Event types — project scope
_PROJECT_EVENT_TYPES = {
    "session_spawned",
    "session_promoted",
    "session_starting",
    "session_exported",
    "text_output",
    "tool_call",
    "tool_result",
    "approval_needed",
    "session_died",
    "web_output_available",
    "worktree_added",
    "worktree_removed",
}

# Event types — host scope
_HOST_EVENT_TYPES = {
    "host_status",
    "unmanaged_session_found",
    "unmanaged_session_gone",
    "bridge_started",
    "bridge_stopped",
}

_ALL_EVENT_TYPES = _PROJECT_EVENT_TYPES | _HOST_EVENT_TYPES

# Command types — project scope
_PROJECT_COMMAND_TYPES = {
    "start_session",
    "launch_session",
    "send_prompt",
    "approve",
    "cancel",
    "bind_artifact",
    "control_message",
}

# Command types — host scope
_HOST_COMMAND_TYPES = {
    "clone_project",
    "init_project",
    "start_bridge",
    "stop_bridge",
    "adopt_session",
}

_ALL_COMMAND_TYPES = _PROJECT_COMMAND_TYPES | _HOST_COMMAND_TYPES


def _now_ms() -> int:
    return int(time.time() * 1000)


@dataclass
class Event:
    type: str
    bridge: str | None
    session_id: str | None
    timestamp: int
    payload: dict[str, Any]

    # --- Project-scope factory methods ---

    @classmethod
    def text_output(cls, *, bridge: str, session_id: str, content: str) -> Event:
        return cls(
            type="text_output",
            bridge=bridge,
            session_id=session_id,
            timestamp=_now_ms(),
            payload={"content": content},
        )

    @classmethod
    def tool_call(
        cls,
        *,
        bridge: str,
        session_id: str,
        tool_name: str,
        input: dict[str, Any],
        call_id: str,
    ) -> Event:
        return cls(
            type="tool_call",
            bridge=bridge,
            session_id=session_id,
            timestamp=_now_ms(),
            payload={"tool_name": tool_name, "input": input, "call_id": call_id},
        )

    @classmethod
    def tool_result(
        cls, *, bridge: str, session_id: str, call_id: str, output: str, success: bool
    ) -> Event:
        return cls(
            type="tool_result",
            bridge=bridge,
            session_id=session_id,
            timestamp=_now_ms(),
            payload={"call_id": call_id, "output": output, "success": success},
        )

    @classmethod
    def approval_needed(
        cls,
        *,
        bridge: str,
        session_id: str,
        tool_name: str,
        description: str,
        call_id: str,
    ) -> Event:
        return cls(
            type="approval_needed",
            bridge=bridge,
            session_id=session_id,
            timestamp=_now_ms(),
            payload={
                "tool_name": tool_name,
                "description": description,
                "call_id": call_id,
            },
        )

    @classmethod
    def session_starting(
        cls, *, bridge: str, session_id: str, runtime: str, artifact: str | None = None
    ) -> Event:
        """Emitted when session spawn begins (before server health check)."""
        payload: dict[str, Any] = {"runtime": runtime}
        if artifact:
            payload["artifact"] = artifact
        return cls(
            type="session_starting",
            bridge=bridge,
            session_id=session_id,
            timestamp=_now_ms(),
            payload=payload,
        )

    @classmethod
    def session_spawned(
        cls, *, bridge: str, session_id: str, runtime: str, artifact: str | None = None
    ) -> Event:
        payload: dict[str, Any] = {"runtime": runtime}
        if artifact:
            payload["artifact"] = artifact
        return cls(
            type="session_spawned",
            bridge=bridge,
            session_id=session_id,
            timestamp=_now_ms(),
            payload=payload,
        )

    @classmethod
    def session_promoted(
        cls, *, bridge: str, session_id: str, artifact: str, topic: str | None = None
    ) -> Event:
        payload: dict[str, Any] = {"artifact": artifact}
        if topic:
            payload["topic"] = topic
        return cls(
            type="session_promoted",
            bridge=bridge,
            session_id=session_id,
            timestamp=_now_ms(),
            payload=payload,
        )

    @classmethod
    def session_died(cls, *, bridge: str, session_id: str, reason: str) -> Event:
        return cls(
            type="session_died",
            bridge=bridge,
            session_id=session_id,
            timestamp=_now_ms(),
            payload={"reason": reason},
        )

    @classmethod
    def web_output_available(
        cls, *, bridge: str, session_id: str, path_or_port: str, label: str
    ) -> Event:
        return cls(
            type="web_output_available",
            bridge=bridge,
            session_id=session_id,
            timestamp=_now_ms(),
            payload={"path_or_port": path_or_port, "label": label},
        )

    @classmethod
    def session_exported(
        cls, *, bridge: str, session_id: str, export_path: str
    ) -> Event:
        return cls(
            type="session_exported",
            bridge=bridge,
            session_id=session_id,
            timestamp=_now_ms(),
            payload={"export_path": export_path},
        )

    @classmethod
    def worktree_added(
        cls, *, bridge: str, worktree_path: str, branch_name: str
    ) -> Event:
        return cls(
            type="worktree_added",
            bridge=bridge,
            session_id=None,
            timestamp=_now_ms(),
            payload={"worktree_path": worktree_path, "branch_name": branch_name},
        )

    @classmethod
    def worktree_removed(
        cls, *, bridge: str, worktree_path: str, branch_name: str
    ) -> Event:
        return cls(
            type="worktree_removed",
            bridge=bridge,
            session_id=None,
            timestamp=_now_ms(),
            payload={"worktree_path": worktree_path, "branch_name": branch_name},
        )

    # --- Host-scope factory methods ---

    @classmethod
    def host_status(cls, *, bridges_running: int, disk: str, load: str) -> Event:
        return cls(
            type="host_status",
            bridge="__host__",
            session_id=None,
            timestamp=_now_ms(),
            payload={"bridges_running": bridges_running, "disk": disk, "load": load},
        )

    @classmethod
    def unmanaged_session_found(
        cls,
        *,
        tmux_target: str,
        runtime_hint: str | None = None,
        project_path: str | None = None,
    ) -> Event:
        payload: dict[str, Any] = {"tmux_target": tmux_target}
        if runtime_hint:
            payload["runtime_hint"] = runtime_hint
        if project_path:
            payload["project_path"] = project_path
        return cls(
            type="unmanaged_session_found",
            bridge="__host__",
            session_id=None,
            timestamp=_now_ms(),
            payload=payload,
        )

    @classmethod
    def unmanaged_session_gone(cls, *, tmux_target: str) -> Event:
        return cls(
            type="unmanaged_session_gone",
            bridge="__host__",
            session_id=None,
            timestamp=_now_ms(),
            payload={"tmux_target": tmux_target},
        )

    @classmethod
    def bridge_started(cls, *, project: str, bridge_id: str) -> Event:
        return cls(
            type="bridge_started",
            bridge="__host__",
            session_id=None,
            timestamp=_now_ms(),
            payload={"project": project, "bridge_id": bridge_id},
        )

    @classmethod
    def bridge_stopped(cls, *, project: str, bridge_id: str, reason: str) -> Event:
        return cls(
            type="bridge_stopped",
            bridge="__host__",
            session_id=None,
            timestamp=_now_ms(),
            payload={"project": project, "bridge_id": bridge_id, "reason": reason},
        )


@dataclass
class Command:
    type: str
    bridge: str | None
    session_id: str | None
    timestamp: int
    payload: dict[str, Any]

    # --- Project-scope factory methods ---

    @classmethod
    def start_session(
        cls,
        *,
        bridge: str,
        runtime: str,
        artifact: str | None = None,
        prompt: str | None = None,
    ) -> Command:
        payload: dict[str, Any] = {"runtime": runtime}
        if artifact:
            payload["artifact"] = artifact
        if prompt:
            payload["prompt"] = prompt
        return cls(
            type="start_session",
            bridge=bridge,
            session_id=None,
            timestamp=_now_ms(),
            payload=payload,
        )

    @classmethod
    def launch_session(cls, *, bridge: str, text: str | None = None) -> Command:
        payload: dict[str, Any] = {}
        if text:
            payload["text"] = text
        return cls(
            type="launch_session",
            bridge=bridge,
            session_id=None,
            timestamp=_now_ms(),
            payload=payload,
        )

    @classmethod
    def send_prompt(cls, *, bridge: str, session_id: str, text: str) -> Command:
        return cls(
            type="send_prompt",
            bridge=bridge,
            session_id=session_id,
            timestamp=_now_ms(),
            payload={"text": text},
        )

    @classmethod
    def approve(
        cls, *, bridge: str, session_id: str, call_id: str, approved: bool
    ) -> Command:
        return cls(
            type="approve",
            bridge=bridge,
            session_id=session_id,
            timestamp=_now_ms(),
            payload={"call_id": call_id, "approved": approved},
        )

    @classmethod
    def cancel(cls, *, bridge: str, session_id: str) -> Command:
        return cls(
            type="cancel",
            bridge=bridge,
            session_id=session_id,
            timestamp=_now_ms(),
            payload={},
        )

    @classmethod
    def control_message(cls, *, bridge: str, text: str) -> Command:
        return cls(
            type="control_message",
            bridge=bridge,
            session_id=None,
            timestamp=_now_ms(),
            payload={"text": text},
        )

    @classmethod
    def bind_artifact(
        cls, *, bridge: str, session_id: str, artifact_id: str
    ) -> Command:
        return cls(
            type="bind_artifact",
            bridge=bridge,
            session_id=session_id,
            timestamp=_now_ms(),
            payload={"artifact_id": artifact_id},
        )

    # --- Host-scope factory methods ---

    @classmethod
    def clone_project(cls, *, repo_url: str, host_path: str | None = None) -> Command:
        payload: dict[str, Any] = {"repo_url": repo_url}
        if host_path:
            payload["host_path"] = host_path
        return cls(
            type="clone_project",
            bridge="__host__",
            session_id=None,
            timestamp=_now_ms(),
            payload=payload,
        )

    @classmethod
    def init_project(cls, *, project_path: str) -> Command:
        return cls(
            type="init_project",
            bridge="__host__",
            session_id=None,
            timestamp=_now_ms(),
            payload={"project_path": project_path},
        )

    @classmethod
    def start_bridge(cls, *, project_path: str) -> Command:
        return cls(
            type="start_bridge",
            bridge="__host__",
            session_id=None,
            timestamp=_now_ms(),
            payload={"project_path": project_path},
        )

    @classmethod
    def stop_bridge(cls, *, project: str) -> Command:
        return cls(
            type="stop_bridge",
            bridge="__host__",
            session_id=None,
            timestamp=_now_ms(),
            payload={"project": project},
        )

    @classmethod
    def adopt_session(
        cls,
        *,
        tmux_target: str,
        project: str,
        runtime: str | None = None,
        artifact: str | None = None,
    ) -> Command:
        payload: dict[str, Any] = {"tmux_target": tmux_target, "project": project}
        if runtime:
            payload["runtime"] = runtime
        if artifact:
            payload["artifact"] = artifact
        return cls(
            type="adopt_session",
            bridge="__host__",
            session_id=None,
            timestamp=_now_ms(),
            payload=payload,
        )


@dataclass
class ConfigMessage:
    plugin_type: str  # "chat" or "runtime"
    config: dict[str, Any]
    type: str = field(default="config", init=False)


def encode_message(msg: Event | Command | ConfigMessage) -> str:
    if isinstance(msg, ConfigMessage):
        data = {
            "type": msg.type,
            "plugin_type": msg.plugin_type,
            "config": msg.config,
        }
    else:
        data = {
            "type": msg.type,
            "bridge": msg.bridge,
            "session_id": msg.session_id,
            "timestamp": msg.timestamp,
            "payload": msg.payload,
        }
    return json.dumps(data, separators=(",", ":")) + "\n"


def decode_message(line: str) -> Event | Command | ConfigMessage | None:
    line = line.strip()
    try:
        data = json.loads(line)
    except (json.JSONDecodeError, ValueError):
        return None

    msg_type = data.get("type")
    if not msg_type:
        return None

    if msg_type == "config":
        return ConfigMessage(
            plugin_type=data.get("plugin_type", ""),
            config=data.get("config", {}),
        )

    if msg_type in _ALL_COMMAND_TYPES:
        return Command(
            type=msg_type,
            bridge=data.get("bridge"),
            session_id=data.get("session_id"),
            timestamp=data.get("timestamp", 0),
            payload=data.get("payload", {}),
        )

    # Default to Event for known types AND unknown types (forward compat).
    return Event(
        type=msg_type,
        bridge=data.get("bridge"),
        session_id=data.get("session_id"),
        timestamp=data.get("timestamp", 0),
        payload=data.get("payload", {}),
    )


def parse_ndjson_line(line: str) -> Event | Command | ConfigMessage | None:
    """Parse a single NDJSON line. Returns None for malformed input."""
    return decode_message(line)
