"""Tests for SessionRegistry — SPEC-324 persistent session tracking."""

import json
import time

import pytest

from swain_helm.session_registry import SessionRegistry


@pytest.fixture
def registry(tmp_path):
    return SessionRegistry(str(tmp_path))


class TestRead:
    def test_read_missing_file_returns_empty(self, registry):
        data = registry.read()
        assert data == {}

    def test_read_existing_file(self, registry):
        registry.path.parent.mkdir(parents=True, exist_ok=True)
        registry.path.write_text(json.dumps({"trunk": {"opencode_session_id": "s1"}}))
        data = registry.read()
        assert "trunk" in data
        assert data["trunk"]["opencode_session_id"] == "s1"

    def test_read_corrupt_json(self, registry):
        registry.path.parent.mkdir(parents=True, exist_ok=True)
        registry.path.write_text("{bad json")
        data = registry.read()
        assert data == {}

    def test_read_empty_file(self, registry):
        registry.path.parent.mkdir(parents=True, exist_ok=True)
        registry.path.write_text("")
        data = registry.read()
        assert data == {}


class TestWrite:
    def test_write_creates_directories(self, registry):
        registry._data = {"trunk": {"opencode_session_id": "s1"}}
        registry.write()
        assert registry.path.exists()

    def test_write_atomic(self, registry):
        registry._data = {"trunk": {"opencode_session_id": "s1"}}
        registry.write()
        raw = registry.path.read_text()
        parsed = json.loads(raw)
        assert parsed["trunk"]["opencode_session_id"] == "s1"


class TestUpdateEntry:
    def test_update_creates_new_entry(self, registry):
        registry.read()
        registry.update_entry(
            "trunk",
            opencode_session_id="s1",
            state="active",
            topic="trunk",
            worktree_path="/tmp/swain",
            started_at=time.time(),
        )
        entry = registry.get_entry("trunk")
        assert entry is not None
        assert entry["opencode_session_id"] == "s1"
        assert entry["state"] == "active"
        assert "last_activity" in entry

    def test_update_merges_fields(self, registry):
        registry.read()
        registry.update_entry("trunk", opencode_session_id="s1", state="spawning")
        registry.update_entry("trunk", state="active")
        entry = registry.get_entry("trunk")
        assert entry["opencode_session_id"] == "s1"
        assert entry["state"] == "active"

    def test_update_persists_to_disk(self, registry):
        registry.read()
        registry.update_entry("trunk", opencode_session_id="s1", state="active")
        fresh = SessionRegistry(registry.project_dir)
        fresh.read()
        assert fresh.get_entry("trunk") is not None


class TestDeleteEntry:
    def test_delete_removes_entry(self, registry):
        registry.read()
        registry.update_entry("trunk", opencode_session_id="s1")
        registry.delete_entry("trunk")
        assert registry.get_entry("trunk") is None

    def test_delete_nonexistent_is_noop(self, registry):
        registry.read()
        registry.delete_entry("nonexistent")


class TestReconcile:
    def test_orphaned_entries_marked_dead(self, registry):
        registry.read()
        registry.update_entry("trunk", opencode_session_id="s1", state="active")
        registry.update_entry("feat", opencode_session_id="s2", state="active")
        removed = registry.reconcile(live_session_ids={"s1"})
        assert "feat" in removed
        assert registry.get_entry("feat")["state"] == "dead"
        assert registry.get_entry("trunk")["state"] == "active"

    def test_all_live_no_removals(self, registry):
        registry.read()
        registry.update_entry("trunk", opencode_session_id="s1", state="active")
        removed = registry.reconcile(live_session_ids={"s1"})
        assert removed == []

    def test_dead_entries_not_reconciled(self, registry):
        registry.read()
        registry.update_entry("trunk", opencode_session_id="s1", state="dead")
        removed = registry.reconcile(live_session_ids=set())
        assert removed == []


class TestCleanupDead:
    def test_dead_entries_removed(self, registry):
        registry.read()
        registry.update_entry("trunk", opencode_session_id="s1", state="dead")
        registry.update_entry("feat", opencode_session_id="s2", state="active")
        removed = registry.cleanup_dead()
        assert "trunk" in removed
        assert registry.get_entry("trunk") is None
        assert registry.get_entry("feat") is not None

    def test_missing_worktree_path_removed(self, registry):
        registry.read()
        registry.update_entry(
            "trunk",
            opencode_session_id="s1",
            state="active",
            worktree_path="/nonexistent",
        )
        removed = registry.cleanup_dead(existing_paths={"/tmp/swain"})
        assert "trunk" in removed

    def test_existing_worktree_path_kept(self, registry):
        registry.read()
        registry.update_entry(
            "trunk",
            opencode_session_id="s1",
            state="active",
            worktree_path="/tmp/swain",
        )
        removed = registry.cleanup_dead(existing_paths={"/tmp/swain"})
        assert removed == []


class TestEntries:
    def test_entries_property(self, registry):
        registry.read()
        registry.update_entry("trunk", opencode_session_id="s1")
        assert "trunk" in registry.entries


class TestPathTraversal:
    def test_accepts_normal_path(self, tmp_path):
        reg = SessionRegistry(str(tmp_path))
        assert reg.path.is_relative_to(tmp_path.resolve())

    def test_registry_under_project_root(self, tmp_path):
        reg = SessionRegistry(str(tmp_path))
        expected = (
            tmp_path.resolve() / ".swain" / "swain-helm" / "session-registry.json"
        )
        assert reg.path == expected
