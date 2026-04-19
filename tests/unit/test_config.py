"""Tests for config loading and 1Password credential resolution."""

import json
import logging

import pytest

from swain_helm.config import (
    ResolutionError,
    _resolved_cache,
    load_helm_config,
    load_project_config,
    resolve_op_references,
    validate_helm_schema,
    validate_project_schema,
)


@pytest.fixture(autouse=True)
def clear_cache():
    _resolved_cache.clear()
    yield
    _resolved_cache.clear()


@pytest.fixture
def mock_op_read(monkeypatch):
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        ref = cmd[2] if len(cmd) >= 3 else ""
        if ref == "op://vault/bad-item/field":
            return type(
                "R", (), {"returncode": 1, "stderr": "item not found", "stdout": ""}
            )()
        value = f"secret-for-{ref.split('/')[-1]}"
        return type("R", (), {"returncode": 0, "stderr": "", "stdout": value + "\n"})()

    monkeypatch.setattr("swain_helm.config.subprocess.run", fake_run)
    return calls


class TestResolveOpReferences:
    def test_resolves_op_reference_via_op_read(self, mock_op_read):
        config = {"api_key": "op://vault/item/field"}
        result = resolve_op_references(config)
        assert result["api_key"] == "secret-for-field"
        assert mock_op_read

    def test_nested_dict_resolution(self, mock_op_read):
        config = {"chat": {"token": "op://vault/zulip-token/password"}}
        result = resolve_op_references(config)
        assert result["chat"]["token"] == "secret-for-password"

    def test_list_values_resolved(self, mock_op_read):
        config = {"keys": ["op://vault/key-a/value", "plain-text"]}
        result = resolve_op_references(config)
        assert result["keys"][0] == "secret-for-value"
        assert result["keys"][1] == "plain-text"

    def test_non_op_strings_untouched(self, mock_op_read):
        config = {"name": "swain", "count": 42}
        result = resolve_op_references(config)
        assert result == {"name": "swain", "count": 42}
        assert not mock_op_read


class TestCaching:
    def test_second_resolution_uses_cache(self, mock_op_read):
        config = {"a": "op://vault/item/x", "b": "op://vault/item/x"}
        resolve_op_references(config)
        op_calls = [c for c in mock_op_read if c[0] == "op"]
        assert len(op_calls) == 1

    def test_cache_populated(self, mock_op_read):
        resolve_op_references({"k": "op://vault/item/y"})
        assert "op://vault/item/y" in _resolved_cache


class TestResolutionError:
    def test_failed_op_read_raises_with_reference(self, mock_op_read):
        with pytest.raises(ResolutionError) as exc_info:
            resolve_op_references({"key": "op://vault/bad-item/field"})
        assert "op://vault/bad-item/field" in str(exc_info.value)
        assert exc_info.value.reference == "op://vault/bad-item/field"


class TestNoDiskWrites:
    def test_resolved_values_not_written_to_disk(self, tmp_path, mock_op_read):
        config = {"secret": "op://vault/item/field"}
        resolved = resolve_op_references(config)
        files_written = list(tmp_path.iterdir())
        assert files_written == []
        assert resolved["secret"] == "secret-for-field"


class TestLogging:
    def test_log_shows_reference_not_contents(self, mock_op_read, caplog):
        with caplog.at_level(logging.INFO, logger="swain_helm.config"):
            resolve_op_references({"k": "op://vault/item/field"})
        logged = caplog.text
        assert "op://vault/item/field" in logged
        assert "secret-for-field" not in logged

    def test_log_failure_shows_reference_not_contents(self, mock_op_read, caplog):
        with caplog.at_level(logging.ERROR, logger="swain_helm.config"):
            with pytest.raises(ResolutionError):
                resolve_op_references({"k": "op://vault/bad-item/field"})
        logged = caplog.text
        assert "op://vault/bad-item/field" in logged


class TestProjectSchemaValidation:
    def test_valid_project_config(self):
        config = {
            "name": "swain",
            "path": "/home/user/swain",
            "stream": "zulip",
            "runtime": "claude",
            "auto_start": True,
            "worktree_poll_interval_s": 30,
        }
        validate_project_schema(config)

    def test_missing_field_raises_value_error(self):
        config = {"name": "swain", "path": "/home/user/swain"}
        with pytest.raises(ValueError, match="missing required keys"):
            validate_project_schema(config)

    def test_extra_fields_allowed(self):
        config = {
            "name": "swain",
            "path": "/home/user/swain",
            "stream": "zulip",
            "runtime": "claude",
            "auto_start": True,
            "worktree_poll_interval_s": 30,
            "extra": "ok",
        }
        validate_project_schema(config)


class TestHelmSchemaValidation:
    def test_valid_helm_config(self):
        config = {
            "scan_paths": ["/home"],
            "chat": {"type": "zulip"},
            "opencode": {"bin": "opencode"},
        }
        validate_helm_schema(config)

    def test_missing_field_raises_value_error(self):
        config = {"scan_paths": ["/home"], "chat": {"type": "zulip"}}
        with pytest.raises(ValueError, match="missing required keys"):
            validate_helm_schema(config)

    def test_extra_fields_allowed(self):
        config = {
            "scan_paths": ["/home"],
            "chat": {"type": "zulip"},
            "opencode": {"bin": "opencode"},
            "debug": True,
        }
        validate_helm_schema(config)


class TestLoadHelmConfig:
    def test_loads_resolves_validates(self, tmp_path, mock_op_read):
        raw = {
            "scan_paths": ["/home/user/code"],
            "chat": {"api_key": "op://vault/item/field"},
            "opencode": {"bin": "opencode"},
        }
        p = tmp_path / "helm.config.json"
        p.write_text(json.dumps(raw))
        loaded = load_helm_config(str(p))
        assert loaded["chat"]["api_key"] == "secret-for-field"

    def test_invalid_schema_raises(self, tmp_path, mock_op_read):
        raw = {"scan_paths": ["/home"], "chat": {}}
        p = tmp_path / "helm.config.json"
        p.write_text(json.dumps(raw))
        with pytest.raises(ValueError, match="missing required keys"):
            load_helm_config(str(p))


class TestLoadProjectConfig:
    def test_loads_resolves_validates(self, tmp_path, mock_op_read):
        raw = {
            "name": "swain",
            "path": "/home/user/swain",
            "stream": {"api_key": "op://vault/item/field"},
            "runtime": "claude",
            "auto_start": True,
            "worktree_poll_interval_s": 30,
        }
        p = tmp_path / "project.json"
        p.write_text(json.dumps(raw))
        loaded = load_project_config(str(p))
        assert loaded["stream"]["api_key"] == "secret-for-field"

    def test_invalid_schema_raises(self, tmp_path, mock_op_read):
        raw = {"name": "swain"}
        p = tmp_path / "project.json"
        p.write_text(json.dumps(raw))
        with pytest.raises(ValueError, match="missing required keys"):
            load_project_config(str(p))
