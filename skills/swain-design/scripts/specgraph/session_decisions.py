"""JSONL session decision log for SESSION-ROADMAP.md (SPEC-118).

Provides append-only logging and reading of operator decisions made during
a session. The log lives at .agents/session-decisions.jsonl and is the
durable store — SESSION-ROADMAP.md reads from it at generation time.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone


_LOG_FILENAME = os.path.join(".agents", "session-decisions.jsonl")


def append_decision_record(
    repo_root: str,
    artifact: str,
    action: str,
    commit: str,
    session_id: str | None = None,
) -> dict:
    """Append a decision record to the JSONL log.

    Returns the written entry dict.
    """
    logfile = os.path.join(repo_root, _LOG_FILENAME)
    os.makedirs(os.path.dirname(logfile), exist_ok=True)

    entry = {
        "session": session_id or "",
        "artifact": artifact,
        "action": action,
        "commit": commit,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    with open(logfile, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return entry


def read_decision_records(
    repo_root: str,
    session_id: str | None = None,
) -> list[dict]:
    """Read all decision records from the JSONL log.

    If session_id is provided, filter to only entries matching that session.
    Malformed lines are silently skipped.
    """
    logfile = os.path.join(repo_root, _LOG_FILENAME)
    if not os.path.isfile(logfile):
        return []

    records: list[dict] = []
    with open(logfile, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except (json.JSONDecodeError, ValueError):
                continue
            if session_id and entry.get("session") != session_id:
                continue
            records.append(entry)

    return records
