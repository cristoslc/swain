"""Provisioning script for swain-helm.

Registers a Zulip bot, creates a stream for the project, generates
a bridge config file with op:// credential references, writes a
per-project config for the watchdog, and prints instructions for
starting the watchdog daemon.

Usage:
    swain-helm host provision \
        --zulip-site https://myorg.zulipchat.com \
        --zulip-email swain-bot@myorg.zulipchat.com \
        --zulip-api-key YOUR_KEY \
        --operator-email you@example.com \
        --project swain \
        --project-path /home/user/swain
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

DEFAULT_CONFIG_DIR = Path.home() / ".config" / "swain-helm"

log = logging.getLogger("swain_helm.provision")


def provision(
    *,
    zulip_site: str,
    zulip_email: str,
    zulip_api_key: str,
    operator_email: str,
    project_name: str,
    project_path: str,
    config_dir: Path | None = None,
    stream_name: str | None = None,
) -> dict:
    """Provision a bridge config for a single project.

    1. Verify Zulip credentials work.
    2. Create (or verify) a stream for the project.
    3. Write helm.config.json with chat credentials (op:// references).
    4. Write per-project config for the watchdog.
    """
    import zulip

    stream = stream_name or project_name
    cfg_dir = config_dir or DEFAULT_CONFIG_DIR

    client = zulip.Client(
        email=zulip_email,
        api_key=zulip_api_key,
        site=zulip_site,
    )

    result = client.get_profile()
    if result.get("result") != "success":
        log.error("Zulip auth failed: %s", result.get("msg", "unknown error"))
        sys.exit(1)
    log.info("Zulip auth OK — bot: %s", result.get("full_name", zulip_email))

    sub_result = client.add_subscriptions(
        streams=[{"name": stream, "description": f"swain-helm — {project_name}"}],
    )
    if sub_result.get("result") != "success":
        log.error("Failed to create stream %r: %s", stream, sub_result.get("msg"))
        sys.exit(1)
    log.info("Stream ready: %s", stream)

    client.send_message(
        {
            "type": "stream",
            "to": stream,
            "topic": "trunk",
            "content": (
                f"swain-helm bridge provisioned for **{project_name}**.\n\n"
                f"Commands:\n"
                f"- `/work [ARTIFACT]` — start a new session.\n"
                f"- `/kill SESSION_ID` — stop a session.\n"
                f"- `/cancel` — cancel the current session (in a session topic).\n"
                f"- `/approve CALL_ID` — approve a tool call.\n"
                f"- `/deny CALL_ID` — deny a tool call."
            ),
        }
    )

    helm_config = {
        "domain": "personal",
        "chat": {
            "server_url": zulip_site,
            "bot_email": zulip_email,
            "bot_api_key": f"op://Private/{zulip_email}/api_key",
            "operator_email": operator_email,
            "control_topic": "trunk",
        },
        "opencode": {
            "default_port": 4096,
        },
        "scan_paths": [project_path],
    }

    projects_dir = cfg_dir / "projects"
    projects_dir.mkdir(parents=True, exist_ok=True)

    project_config = {
        "name": project_name,
        "path": project_path,
        "stream": stream,
        "runtime": "claude",
        "auto_start": True,
        "worktree_poll_interval_s": 15,
    }

    helm_config["projects"] = [project_config]

    helm_path = cfg_dir / "helm.config.json"
    helm_path.write_text(json.dumps(helm_config, indent=2) + "\n")
    helm_path.chmod(0o600)
    log.info("Helm config written to %s (permissions: 600)", helm_path)

    project_path_file = projects_dir / f"{project_name}.json"
    project_path_file.write_text(json.dumps(project_config, indent=2) + "\n")
    project_path_file.chmod(0o600)
    log.info("Project config written to %s (permissions: 600)", project_path_file)

    print(f"\nProvisioning complete. Start the watchdog with:")
    print(f"  swain-helm host up")

    return helm_config


def main() -> None:
    parser = argparse.ArgumentParser(description="Provision swain-helm bridge")
    parser.add_argument("--zulip-site", required=True, help="Zulip server URL")
    parser.add_argument("--zulip-email", required=True, help="Bot email address")
    parser.add_argument("--zulip-api-key", required=True, help="Bot API key")
    parser.add_argument(
        "--operator-email", required=True, help="Your email for @mentions"
    )
    parser.add_argument("--project", required=True, help="Project name")
    parser.add_argument(
        "--project-path", required=True, help="Path to project directory"
    )
    parser.add_argument(
        "--config-dir",
        default=None,
        help="Config directory (default: ~/.config/swain-helm)",
    )
    parser.add_argument(
        "--stream", default=None, help="Zulip stream name (defaults to project name)"
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )

    config_dir = Path(args.config_dir) if args.config_dir else None

    provision(
        zulip_site=args.zulip_site,
        zulip_email=args.zulip_email,
        zulip_api_key=args.zulip_api_key,
        operator_email=args.operator_email,
        project_name=args.project,
        project_path=args.project_path,
        config_dir=config_dir,
        stream_name=args.stream,
    )


if __name__ == "__main__":
    main()
