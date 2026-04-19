"""Continuous worktree discovery — polls git worktree list and emits diffs.

Per SPEC-323, the WorktreeScanner runs `git worktree list --porcelain`
on a configurable interval (default 15s), compares against cached state,
and returns added/removed worktree tuples for ProjectBridge to act on.
"""

from __future__ import annotations

import asyncio
import logging
import subprocess
from dataclasses import dataclass, field
from typing import Any

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class WorktreeInfo:
    path: str
    branch: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, WorktreeInfo):
            return NotImplemented
        return self.path == other.path and self.branch == other.branch

    def __hash__(self) -> int:
        return hash((self.path, self.branch))


@dataclass
class WorktreeDiff:
    added: list[WorktreeInfo] = field(default_factory=list)
    removed: list[WorktreeInfo] = field(default_factory=list)

    def __bool__(self) -> bool:
        return bool(self.added or self.removed)


class WorktreeScanner:
    """Polls `git worktree list --porcelain` and computes diffs."""

    def __init__(
        self,
        project_dir: str,
        *,
        poll_interval_s: float = 15.0,
        run_git: Any = None,
    ):
        self.project_dir = project_dir
        self.poll_interval_s = poll_interval_s
        self._run_git = run_git or self._default_run_git
        self._last_known: set[WorktreeInfo] | None = None
        self._task: asyncio.Task | None = None

    def scan(self) -> set[WorktreeInfo]:
        """Run `git worktree list --porcelain` and parse the output.

        Returns a set of WorktreeInfo tuples. Trunk worktrees get branch "trunk".
        """
        try:
            result = self._run_git(self.project_dir)
        except Exception:
            log.exception("git worktree list failed for %s", self.project_dir)
            return set()

        worktrees: set[WorktreeInfo] = set()
        lines = result.strip().split("\n")
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.startswith("worktree "):
                wt_path = line[len("worktree ") :]
                branch = None
                i += 1
                while i < len(lines) and lines[i]:
                    if lines[i].startswith("branch "):
                        raw_branch = lines[i][len("branch ") :]
                        branch = _branch_to_topic(raw_branch)
                    i += 1
                if branch is None:
                    branch = "trunk"
                worktrees.add(WorktreeInfo(path=wt_path, branch=branch))
            else:
                i += 1
        return worktrees

    def diff(self) -> WorktreeDiff:
        """Scan and return the diff against the last known state.

        On the first call, all discovered worktrees appear as 'added'.
        """
        current = self.scan()
        if self._last_known is None:
            self._last_known = current
            return WorktreeDiff(added=list(current))

        added = current - self._last_known
        removed = self._last_known - current
        self._last_known = current
        return WorktreeDiff(added=list(added), removed=list(removed))

    async def start_polling(
        self,
        on_diff: Any,
    ) -> None:
        """Poll on a timer, calling on_diff(diff) for each non-empty diff."""
        self._last_known = self.scan() or set()
        on_diff(WorktreeDiff(added=list(self._last_known)))
        while True:
            await asyncio.sleep(self.poll_interval_s)
            d = self.diff()
            if d:
                on_diff(d)

    def start_background(self, on_diff: Any) -> asyncio.Task:
        """Start the polling loop as a background task."""
        self._task = asyncio.create_task(
            self.start_polling(on_diff), name="worktree-scanner"
        )
        return self._task

    def stop_background(self) -> None:
        """Cancel the background polling task."""
        if self._task and not self._task.done():
            self._task.cancel()

    @staticmethod
    def _default_run_git(project_dir: str) -> str:
        result = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=10,
        )
        result.check_returncode()
        return result.stdout


def _branch_to_topic(raw_branch: str) -> str:
    """Map a git branch name to a Zulip topic.

    Trunk (refs/heads/main or refs/heads/master) maps to 'trunk'.
    Everything else maps to the short branch name.
    """
    if raw_branch in ("refs/heads/main", "refs/heads/master"):
        return "trunk"
    if raw_branch.startswith("refs/heads/"):
        return raw_branch[len("refs/heads/") :]
    return raw_branch
