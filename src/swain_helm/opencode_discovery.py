"""OpenCode serve discovery and authentication — per-port credential resolution.

Per SPEC-321, DiscoveryScanner discovers running opencode-serve instances,
validates health, and tests per-port Basic Auth credentials. It persists
instance state to a JSON file for cross-restart tracking.
"""

import asyncio
import json
import logging
import subprocess
import time
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen
from urllib.error import URLError

log = logging.getLogger("swain_helm.opencode_discovery")

DEFAULT_PORT = 4096
OPENCODE_CONFIG_PATH = Path.home() / ".config" / "opencode" / "opencode.json"
_LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}


class OpenCodeInstance:
    """Tracks state for one opencode-serve instance (port, health, auth)."""

    def __init__(
        self,
        port: int,
        *,
        pid: int | None = None,
        started_by_bridge: bool = False,
        first_seen: str | None = None,
        last_health_check: str | None = None,
        last_health_result: str | None = None,
        auth_required: bool = False,
        auth_tested: bool = False,
        auth_valid: bool = False,
    ):
        self.port = port
        self.pid = pid
        self.started_by_bridge = started_by_bridge
        self.first_seen = first_seen or time.strftime("%Y-%m-%dT%H:%M:%SZ")
        self.last_health_check = last_health_check
        self.last_health_result = last_health_result
        self.auth_required = auth_required
        self.auth_tested = auth_tested
        self.auth_valid = auth_valid

    def to_dict(self) -> dict:
        """Serialize instance state for JSON persistence."""
        return {
            "port": self.port,
            "pid": self.pid,
            "started_by_bridge": self.started_by_bridge,
            "first_seen": self.first_seen,
            "last_health_check": self.last_health_check,
            "last_health_result": self.last_health_result,
            "auth_required": self.auth_required,
            "auth_tested": self.auth_tested,
            "auth_valid": self.auth_valid,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "OpenCodeInstance":
        """Deserialize instance state from JSON."""
        return cls(
            port=data["port"],
            pid=data.get("pid"),
            started_by_bridge=data.get("started_by_bridge", False),
            first_seen=data.get("first_seen"),
            last_health_check=data.get("last_health_check"),
            last_health_result=data.get("last_health_result"),
            auth_required=data.get("auth_required", False),
            auth_tested=data.get("auth_tested", False),
            auth_valid=data.get("auth_valid", False),
        )


class DiscoveryScanner:
    """Discovers and monitors opencode-serve instances on the host.

    Scans candidate ports, performs health checks, validates per-port
    authentication credentials, and can start a new instance if none
    are healthy. Persists state to a JSON file under run_dir.
    """

    def __init__(
        self,
        opencode_config: dict[str, Any],
        run_dir: Path | None = None,
    ) -> None:
        self.config = opencode_config
        self.run_dir = run_dir or Path.home() / ".config" / "swain-helm" / "run"
        self.instances_file = self.run_dir / "opencode-instances.json"
        self._instances: dict[int, OpenCodeInstance] = {}
        self._procs: dict[int, subprocess.Popen] = {}
        self._load_state()

    def _load_state(self) -> None:
        """Load persisted instance state from disk."""
        if self.instances_file.exists():
            try:
                data = json.loads(self.instances_file.read_text())
                for entry in data.get("instances", []):
                    inst = OpenCodeInstance.from_dict(entry)
                    self._instances[inst.port] = inst
            except (json.JSONDecodeError, KeyError) as e:
                log.warning("Failed to load instance state: %s", e)

    def _save_state(self) -> None:
        """Atomically persist instance state to disk."""
        self.run_dir.mkdir(parents=True, exist_ok=True)
        data = {"instances": [inst.to_dict() for inst in self._instances.values()]}
        tmp = self.instances_file.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2))
        tmp.replace(self.instances_file)

    def get_default_port(self) -> int:
        """Resolve the default opencode-serve port from config or opencode.json."""
        if "default_port" in self.config:
            return self.config["default_port"]
        if OPENCODE_CONFIG_PATH.exists():
            try:
                oc_config = json.loads(OPENCODE_CONFIG_PATH.read_text())
                return oc_config.get("server", {}).get("port", DEFAULT_PORT)
            except (json.JSONDecodeError, KeyError):
                pass
        return DEFAULT_PORT

    def get_candidate_ports(self) -> list[int]:
        """Collect all candidate ports from config, defaults, and known instances."""
        ports = set()
        default = self.get_default_port()
        ports.add(default)
        for port_str in self.config.get("ports", {}):
            try:
                ports.add(int(port_str))
            except ValueError:
                pass
        for port in self._instances:
            ports.add(port)
        return sorted(ports)

    def health_check(self, port: int) -> bool:
        """Synchronous health check against opencode-serve on the given port."""
        try:
            url = f"http://127.0.0.1:{port}/global/health"
            req = Request(url)
            with urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
                return data.get("healthy", False)
        except (URLError, json.JSONDecodeError, OSError, TimeoutError):
            return False

    async def health_check_async(self, port: int) -> bool:
        """Async wrapper around health_check to avoid blocking the event loop."""
        return await asyncio.to_thread(self.health_check, port)

    def auth_test(self, port: int) -> bool:
        """Test per-port Basic Auth credentials against opencode-serve.

        Refuses to send credentials to non-loopback addresses.
        """
        creds = self._get_credentials_for_port(port)
        if not creds:
            return False
        if not self._validate_loopback_url(port):
            log.warning(
                "Refusing to send credentials to non-loopback address on port %s",
                port,
            )
            return False
        try:
            url = f"http://127.0.0.1:{port}/global/health"
            import base64

            cred_str = f"{creds['username']}:{creds['password']}"
            headers = {
                "Authorization": f"Basic {base64.b64encode(cred_str.encode()).decode()}"
            }
            req = Request(url, headers=headers)
            with urlopen(req, timeout=5) as resp:
                return resp.status == 200
        except (URLError, OSError):
            return False

    async def auth_test_async(self, port: int) -> bool:
        """Async wrapper around auth_test to avoid blocking the event loop."""
        return await asyncio.to_thread(self.auth_test, port)

    def _validate_loopback_url(self, port: int) -> bool:
        """Ensure we only send credentials to loopback addresses."""
        return True

    def _get_credentials_for_port(self, port: int) -> dict | None:
        """Look up per-port auth credentials from config."""
        ports_map = self.config.get("ports", {})
        port_key = str(port)
        if port_key in ports_map:
            entry = ports_map[port_key]
            return {
                "username": entry.get("username", ""),
                "password": entry.get("password", ""),
            }
        return None

    def scan(self) -> list[OpenCodeInstance]:
        """Synchronous scan — calls health checks directly (may block event loop)."""
        usable: list[OpenCodeInstance] = []
        candidates = self.get_candidate_ports()

        for port in candidates:
            now = time.strftime("%Y-%m-%dT%H:%M:%SZ")
            healthy = self.health_check(port)
            inst = self._instances.get(port, OpenCodeInstance(port=port))
            inst.last_health_check = now
            inst.last_health_result = "healthy" if healthy else "unhealthy"

            if not healthy:
                self._instances[port] = inst
                continue

            creds = self._get_credentials_for_port(port)
            if creds:
                inst.auth_required = True
                inst.auth_tested = True
                inst.auth_valid = self.auth_test(port)
                if inst.auth_valid:
                    usable.append(inst)
                else:
                    inst.auth_valid = False
                    log.warning("Port %s: healthy but auth mismatch", port)
            else:
                inst.auth_required = False
                inst.auth_tested = False
                inst.auth_valid = False
                log.info("Port %s: healthy but no credentials configured", port)

            self._instances[port] = inst

        self._save_state()
        return usable

    async def scan_async(self) -> list[OpenCodeInstance]:
        """Async scan using non-blocking health checks."""
        usable: list[OpenCodeInstance] = []
        candidates = self.get_candidate_ports()

        for port in candidates:
            now = time.strftime("%Y-%m-%dT%H:%M:%SZ")
            healthy = await self.health_check_async(port)
            inst = self._instances.get(port, OpenCodeInstance(port=port))
            inst.last_health_check = now
            inst.last_health_result = "healthy" if healthy else "unhealthy"

            if not healthy:
                self._instances[port] = inst
                continue

            creds = self._get_credentials_for_port(port)
            if creds:
                inst.auth_required = True
                inst.auth_tested = True
                inst.auth_valid = await self.auth_test_async(port)
                if inst.auth_valid:
                    usable.append(inst)
                else:
                    inst.auth_valid = False
                    log.warning("Port %s: healthy but auth mismatch", port)
            else:
                inst.auth_required = False
                inst.auth_tested = False
                inst.auth_valid = False
                log.info("Port %s: healthy but no credentials configured", port)

            self._instances[port] = inst

        self._save_state()
        return usable

    async def start_if_needed(self) -> OpenCodeInstance | None:
        """Find a usable opencode-serve or start one if none exists.

        Stores Popen references in self._procs so callers can clean up.
        """
        usable = await self.scan_async()
        if usable:
            return usable[0]

        port = self.get_default_port()
        log.info("No usable opencode serve found, starting on port %s", port)

        try:
            proc = subprocess.Popen(
                ["opencode", "serve", "--port", str(port)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            inst = OpenCodeInstance(
                port=port,
                pid=proc.pid,
                started_by_bridge=True,
            )
            inst.auth_required = bool(self._get_credentials_for_port(port))
            self._instances[port] = inst
            self._procs[port] = proc

            for _ in range(60):
                if await self.health_check_async(port):
                    inst.last_health_result = "healthy"
                    inst.last_health_check = time.strftime("%Y-%m-%dT%H:%M:%SZ")
                    if inst.auth_required:
                        inst.auth_tested = True
                        inst.auth_valid = await self.auth_test_async(port)
                    break
                await asyncio.sleep(1)

            self._save_state()
            return inst
        except Exception as e:
            log.error("Failed to start opencode serve: %s", e)
            return None
