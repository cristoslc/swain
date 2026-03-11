#!/usr/bin/env -S uv run python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "textual>=1.0.0",
# ]
# ///
"""swain-motd — Textual-based MOTD status panel for swain-stage.

Reads project data from swain-status cache (status-cache.json) and agent
state from stage-status.json. Renders a live-updating dashboard in a tmux
pane with proper Unicode box drawing, colors, and responsive layout.
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.reactive import reactive
from textual.widgets import Rule, Static


# --- Path resolution ---

def get_repo_root() -> Path:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
        )
        return Path(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return Path.cwd()


def get_settings(repo_root: Path) -> dict:
    """Read merged settings (user overrides project)."""
    settings = {}
    project_file = repo_root / "swain.settings.json"
    user_file = Path(
        os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")
    ) / "swain" / "settings.json"

    for path in [project_file, user_file]:  # user loads second, overrides
        if path.is_file():
            try:
                with open(path) as f:
                    data = json.load(f)
                _deep_merge(settings, data)
            except (json.JSONDecodeError, OSError):
                pass
    return settings


def _deep_merge(base: dict, override: dict) -> None:
    for k, v in override.items():
        if k in base and isinstance(base[k], dict) and isinstance(v, dict):
            _deep_merge(base[k], v)
        else:
            base[k] = v


REPO_ROOT = get_repo_root()
PROJECT_NAME = REPO_ROOT.name
SETTINGS = get_settings(REPO_ROOT)

_PROJECT_SLUG = str(REPO_ROOT).replace("/", "-")
MEMORY_DIR = Path(
    os.environ.get(
        "SWAIN_MEMORY_DIR",
        Path.home() / ".claude" / "projects" / _PROJECT_SLUG / "memory",
    )
)
AGENT_STATUS_FILE = MEMORY_DIR / "stage-status.json"
STATUS_CACHE = MEMORY_DIR / "status-cache.json"

CACHE_STALE_SECONDS = 300  # 5 minutes


def art_link(aid: str, file: str | None = None) -> str:
    """Wrap an artifact ID in Rich link markup for clickable terminal links."""
    if file:
        url = f"file://{REPO_ROOT}/{file}"
        return f"[link={url}]{aid}[/link]"
    return aid

SPINNER_STYLES = {
    "braille": ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"],
    "dots": ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
    "bar": ["[    ]", "[=   ]", "[==  ]", "[=== ]", "[ ===]", "[  ==]", "[   =]", "[    ]"],
}

REFRESH_INTERVAL = (
    SETTINGS.get("stage", {}).get("motd", {}).get("refreshInterval", 5)
)
SPINNER_STYLE = (
    SETTINGS.get("stage", {}).get("motd", {}).get("spinnerStyle", "braille")
)
FRAMES = SPINNER_STYLES.get(SPINNER_STYLE, SPINNER_STYLES["braille"])


# --- Data readers ---

def _read_json(path: Path) -> dict | None:
    if not path.is_file():
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def cache_is_usable() -> bool:
    if not STATUS_CACHE.is_file():
        return False
    age = time.time() - STATUS_CACHE.stat().st_mtime
    return age < CACHE_STALE_SECONDS


def read_status_cache() -> dict | None:
    if cache_is_usable():
        return _read_json(STATUS_CACHE)
    return None


def read_agent_status() -> dict:
    data = _read_json(AGENT_STATUS_FILE)
    if data:
        return data
    return {"state": "idle", "context": ""}


def git_branch() -> str:
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, check=True,
        )
        return r.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "detached"


def git_dirty() -> str:
    try:
        r = subprocess.run(
            ["git", "diff", "--quiet", "HEAD"],
            capture_output=True,
        )
        if r.returncode == 0:
            # Also check staged
            r2 = subprocess.run(
                ["git", "diff", "--cached", "--quiet"],
                capture_output=True,
            )
            if r2.returncode == 0:
                return "clean"
        count_r = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            capture_output=True, text=True,
        )
        count = len([l for l in count_r.stdout.strip().split("\n") if l])
        return f"{count} changed"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "?"


def git_last_commit() -> str:
    try:
        r = subprocess.run(
            ["git", "log", "-1", "--pretty=format:%cr: %s"],
            capture_output=True, text=True, check=True,
        )
        return r.stdout.strip()[:40]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "no commits"


def get_bd_task_direct() -> str:
    try:
        r = subprocess.run(
            ["bd", "list", "--status", "in_progress", "--format", "#{id} {title}"],
            capture_output=True, text=True, timeout=5,
        )
        # Filter out noise — bd may print "No issues found." or similar on stderr/stdout
        lines = [
            l for l in r.stdout.strip().split("\n")
            if l.strip() and not l.strip().startswith("No ")
        ]
        if lines:
            return lines[0][:40]
    except (FileNotFoundError, subprocess.TimeoutExpired, subprocess.CalledProcessError):
        pass
    return "no active task"


# --- Collect all data into a flat dict ---

def collect_data() -> dict:
    """Gather all display data, preferring cache when available."""
    cache = read_status_cache()
    agent = read_agent_status()

    if cache:
        branch = cache.get("git", {}).get("branch", "detached")
        git_data = cache.get("git", {})
        if git_data.get("dirty"):
            dirty = f"{git_data.get('changedFiles', 0)} changed"
        else:
            dirty = "clean"

        lc = git_data.get("lastCommit", {})
        last = f"{lc.get('age', '?')}: {lc.get('message', '')}"[:36]

        # Epic progress
        epics = cache.get("artifacts", {}).get("epics", {})
        if epics:
            first = next(iter(epics.values()))
            p = first.get("progress", {})
            eid = art_link(first.get("id", "?"), first.get("file"))
            epic = f"{eid} {p.get('done', 0)}/{p.get('total', 0)}"
        else:
            epic = "no active epics"

        # Task
        tasks_ip = cache.get("tasks", {}).get("inProgress", [])
        if tasks_ip:
            t = tasks_ip[0]
            task = f"{t.get('id', '')} {t.get('title', '')}"[:40]
        else:
            task = "no active task"

        ready = cache.get("artifacts", {}).get("counts", {}).get("ready", 0)

        assigned = cache.get("issues", {}).get("assigned", [])
        issues = len(assigned)
    else:
        branch = git_branch()
        dirty = git_dirty()
        last = git_last_commit()[:36]
        epic = "no cache"
        task = get_bd_task_direct()
        ready = "?"
        issues = 0

    return {
        "branch": branch,
        "dirty": dirty,
        "last": last,
        "epic": epic,
        "task": task,
        "ready": ready,
        "issues": issues,
        "agent_state": agent.get("state", "idle"),
        "agent_context": agent.get("context", ""),
        "touched": len(agent.get("touchedFiles", [])),
    }


# --- Textual widgets ---

class HeaderLine(Static):
    """Project name, branch, dirty state."""


class AgentLine(Static):
    """Agent status with spinner."""


class DataLine(Static):
    """A single data row (label: value)."""


class MotdPanel(Vertical):
    """The status panel container."""


class MotdApp(App):
    """swain MOTD — live project status dashboard."""

    CSS = """
    Screen {
        background: $surface;
    }
    MotdPanel {
        border: round $primary;
        padding: 0 1;
        height: auto;
        max-height: 100%;
    }
    HeaderLine {
        color: $text;
        text-style: bold;
    }
    AgentLine {
        color: $text-muted;
    }
    DataLine {
        color: $text;
    }
    Rule {
        color: $primary-darken-2;
        margin: 0;
    }
    .working {
        color: $warning;
    }
    .idle {
        color: $success;
    }
    """

    frame_idx = reactive(0)

    def compose(self) -> ComposeResult:
        with MotdPanel():
            yield HeaderLine(id="header")
            yield AgentLine(id="agent")
            yield Rule()
            yield DataLine(id="epic")
            yield DataLine(id="task")
            yield DataLine(id="ready")
            yield DataLine(id="last")
            yield DataLine(id="issues")
            yield DataLine(id="touched")

    def on_mount(self) -> None:
        # Initial data load
        self._refresh_data()
        # Periodic refresh — data every N seconds, spinner every 0.2s
        self.set_interval(REFRESH_INTERVAL, self._refresh_data)
        self.set_interval(0.2, self._tick_spinner)

    def _refresh_data(self) -> None:
        self._data = collect_data()
        self._render_all()

    def _tick_spinner(self) -> None:
        if self._data.get("agent_state") == "working":
            self.frame_idx = (self.frame_idx + 1) % len(FRAMES)
            self._render_agent()

    def _render_all(self) -> None:
        d = self._data

        self.query_one("#header", HeaderLine).update(
            f"{PROJECT_NAME} @ {d['branch']} ({d['dirty']})"
        )
        self._render_agent()

        self.query_one("#epic", DataLine).update(f"epic: {d['epic']}")
        self.query_one("#task", DataLine).update(f"task: {d['task']}")
        self.query_one("#ready", DataLine).update(f"ready: {d['ready']} actionable")
        self.query_one("#last", DataLine).update(f"last: {d['last']}")

        issues_widget = self.query_one("#issues", DataLine)
        if d["issues"] > 0:
            issues_widget.update(f"issues: {d['issues']} assigned")
            issues_widget.display = True
        else:
            issues_widget.display = False

        touched_widget = self.query_one("#touched", DataLine)
        if d["touched"] > 0:
            touched_widget.update(f"touched: {d['touched']} file(s)")
            touched_widget.display = True
        else:
            touched_widget.display = False

    def _render_agent(self) -> None:
        d = self._data
        agent_widget = self.query_one("#agent", AgentLine)

        if d["agent_state"] == "working":
            spinner = FRAMES[self.frame_idx % len(FRAMES)]
            ctx = d["agent_context"]
            if ctx and ctx not in ("no status", ""):
                agent_widget.update(f"{spinner} working: {ctx[:34]}")
            else:
                agent_widget.update(f"{spinner} agent working...")
            agent_widget.remove_class("idle")
            agent_widget.add_class("working")
        else:
            agent_widget.update("● idle")
            agent_widget.remove_class("working")
            agent_widget.add_class("idle")


if __name__ == "__main__":
    MotdApp().run()
