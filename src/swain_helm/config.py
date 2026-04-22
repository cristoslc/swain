"""Config loading and 1Password credential resolution for swain-helm.

Resolution order for op:// references:
  1. Try ``op read`` (works on host with 1Password CLI)
  2. Fall back to environment variable: ``SWAIN_HELM_<dotted_path>``
     e.g. ``chat.bot_api_key`` → ``SWAIN_HELM_CHAT_BOT_API_KEY``
This two-step approach lets the same config work on the developer machine
(with ``op`` available) and inside Docker containers (where ``op`` is absent
but the host injects secrets via environment variables).
"""

import json
import logging
import os
import subprocess

logger = logging.getLogger(__name__)

DEFAULT_OPENCODE_PORT = 4096
DEFAULT_WORKTREE_POLL_INTERVAL_S = 15.0
DEFAULT_OPENCODE_BASE_URL = f"http://127.0.0.1:{DEFAULT_OPENCODE_PORT}"

HELM_REQUIRED_KEYS = {"scan_paths", "chat", "opencode"}
PROJECT_REQUIRED_KEYS = {
    "name",
    "path",
    "stream",
    "runtime",
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
    return _walk(config, path="")


def _walk(value, path=""):
    if isinstance(value, dict):
        return {
            k: _walk(v, path=f"{path}.{k}" if path else k) for k, v in value.items()
        }
    if isinstance(value, list):
        return [_walk(item, path=path) for item in value]
    if isinstance(value, str) and value.startswith("op://"):
        return _resolve_one(value, config_path=path)
    return value


def _env_key(config_path: str) -> str:
    """Convert a dotted config path to an environment variable name.

    ``chat.bot_api_key`` → ``SWAIN_HELM_CHAT_BOT_API_KEY``
    """
    return "SWAIN_HELM_" + config_path.upper().replace(".", "_")


def _resolve_one(reference: str, config_path: str = "") -> str:
    """Resolve an op:// reference.

    Tries ``op read`` first (works on host). Falls back to an environment
    variable derived from the config path (works inside Docker).
    """
    if reference in _resolved_cache:
        return _resolved_cache[reference]

    # Try 1Password CLI
    try:
        result = subprocess.run(
            ["op", "read", reference],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            resolved = result.stdout.rstrip("\n")
            _resolved_cache[reference] = resolved
            logger.info("Resolved 1Password item: %s (success)", reference)
            return resolved
        detail = result.stderr.strip() or f"exit code {result.returncode}"
        logger.warning("op read failed for %s: %s", reference, detail)
    except FileNotFoundError:
        logger.info("op CLI not found, trying env var fallback")
    except subprocess.TimeoutExpired:
        logger.warning("op read timed out for %s", reference)

    # Fall back to environment variable
    if config_path:
        env_var = _env_key(config_path)
        env_val = os.environ.get(env_var)
        if env_val:
            _resolved_cache[reference] = env_val
            logger.info("Resolved op://%s via env %s", config_path, env_var)
            return env_val

    logger.error("Cannot resolve op:// reference: %s", reference)
    raise ResolutionError(reference, "op CLI unavailable and no env var fallback")


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
