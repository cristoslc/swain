"""Config loading and 1Password credential resolution for swain-helm."""

import json
import logging
import subprocess

logger = logging.getLogger(__name__)

HELM_REQUIRED_KEYS = {"scan_paths", "chat", "opencode"}
PROJECT_REQUIRED_KEYS = {
    "name",
    "path",
    "stream",
    "runtime",
    "auto_start",
    "worktree_poll_interval_s",
}

_resolved_cache: dict[str, str] = {}


class ResolutionError(Exception):
    """Raised when an op:// reference cannot be resolved."""

    def __init__(self, reference: str, detail: str = ""):
        self.reference = reference
        self.detail = detail
        super().__init__(f"Failed to resolve {reference}: {detail}")


def resolve_op_references(config: dict) -> dict:
    """Walk config tree, resolve all op:// references, return resolved config."""
    return _walk(config)


def _walk(value):
    if isinstance(value, dict):
        return {k: _walk(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_walk(item) for item in value]
    if isinstance(value, str) and value.startswith("op://"):
        return _resolve_one(value)
    return value


def _resolve_one(reference: str) -> str:
    """Call ``op read`` for the reference. Cache and return the result."""
    if reference in _resolved_cache:
        return _resolved_cache[reference]

    result = subprocess.run(
        ["op", "read", reference],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        detail = result.stderr.strip() or f"exit code {result.returncode}"
        logger.error("Failed to resolve 1Password item: %s", reference)
        raise ResolutionError(reference, detail)

    resolved = result.stdout.rstrip("\n")
    _resolved_cache[reference] = resolved
    logger.info("Resolved 1Password item: %s (success)", reference)
    return resolved


def load_helm_config(path: str) -> dict:
    """Load helm.config.json, resolve op:// references, validate schema."""
    with open(path) as f:
        config = json.load(f)
    config = resolve_op_references(config)
    validate_helm_schema(config)
    return config


def load_project_config(path: str) -> dict:
    """Load project config, resolve op:// references, validate schema."""
    with open(path) as f:
        config = json.load(f)
    config = resolve_op_references(config)
    validate_project_schema(config)
    return config


def validate_helm_schema(config: dict) -> None:
    """Validate helm.config.json has required top-level keys."""
    missing = HELM_REQUIRED_KEYS - config.keys()
    if missing:
        raise ValueError(f"helm.config.json missing required keys: {sorted(missing)}")


def validate_project_schema(config: dict) -> None:
    """Validate project config has required fields."""
    missing = PROJECT_REQUIRED_KEYS - config.keys()
    if missing:
        raise ValueError(f"Project config missing required keys: {sorted(missing)}")
