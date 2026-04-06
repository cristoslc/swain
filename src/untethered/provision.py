"""Provisioning script for Untethered Operator MVP.

Registers a Zulip bot, creates a stream for the project, generates a
bridge config file, and prints instructions for starting the bridge.

Usage:
    uv run python -m untethered.provision \
        --zulip-site https://myorg.zulipchat.com \
        --zulip-email swain-bot@myorg.zulipchat.com \
        --zulip-api-key YOUR_KEY \
        --operator-email you@example.com \
        --project swain \
        --project-path /home/user/swain \
        --output bridge.json
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

log = logging.getLogger("untethered.provision")


def provision(
    *,
    zulip_site: str,
    zulip_email: str,
    zulip_api_key: str,
    operator_email: str,
    project_name: str,
    project_path: str,
    output_path: str,
    stream_name: str | None = None,
) -> dict:
    """Provision a bridge config for a single project.

    1. Verify Zulip credentials work.
    2. Create (or verify) a stream for the project.
    3. Write bridge config JSON.
    """
    import zulip

    stream = stream_name or project_name

    client = zulip.Client(
        email=zulip_email,
        api_key=zulip_api_key,
        site=zulip_site,
    )

    # Verify credentials
    result = client.get_profile()
    if result.get("result") != "success":
        log.error("Zulip auth failed: %s", result.get("msg", "unknown error"))
        sys.exit(1)
    log.info("Zulip auth OK — bot: %s", result.get("full_name", zulip_email))

    # Create or subscribe to the project stream
    sub_result = client.add_subscriptions(
        streams=[{"name": stream, "description": f"Untethered Operator — {project_name}"}],
    )
    if sub_result.get("result") != "success":
        log.error("Failed to create stream %r: %s", stream, sub_result.get("msg"))
        sys.exit(1)
    log.info("Stream ready: %s", stream)

    # Post a welcome message to the control topic
    client.send_message({
        "type": "stream",
        "to": stream,
        "topic": "control",
        "content": (
            f"Untethered Operator bridge provisioned for **{project_name}**.\n\n"
            f"Commands:\n"
            f"- `/work [ARTIFACT]` — start a new session.\n"
            f"- `/kill SESSION_ID` — stop a session.\n"
            f"- `/cancel` — cancel the current session (in a session topic).\n"
            f"- `/approve CALL_ID` — approve a tool call.\n"
            f"- `/deny CALL_ID` — deny a tool call."
        ),
    })

    # Write config
    config = {
        "domain": "personal",
        "chat": {
            "server_url": zulip_site,
            "bot_email": zulip_email,
            "bot_api_key": zulip_api_key,
            "operator_email": operator_email,
            "control_topic": "control",
        },
        "projects": [
            {
                "name": project_name,
                "path": project_path,
                "stream": stream,
                "runtime": "claude",
            },
        ],
    }

    output = Path(output_path)
    output.write_text(json.dumps(config, indent=2) + "\n")
    output.chmod(0o600)
    log.info("Config written to %s (permissions: 600)", output)

    print(f"\nProvisioning complete. Start the bridge with:")
    print(f"  uv run python -m untethered.main --config {output_path}")

    return config


def main() -> None:
    parser = argparse.ArgumentParser(description="Provision Untethered Operator bridge")
    parser.add_argument("--zulip-site", required=True, help="Zulip server URL")
    parser.add_argument("--zulip-email", required=True, help="Bot email address")
    parser.add_argument("--zulip-api-key", required=True, help="Bot API key")
    parser.add_argument("--operator-email", required=True, help="Your email for @mentions")
    parser.add_argument("--project", required=True, help="Project name")
    parser.add_argument("--project-path", required=True, help="Path to project directory")
    parser.add_argument("--output", default="bridge.json", help="Output config file path")
    parser.add_argument("--stream", default=None, help="Zulip stream name (defaults to project name)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    provision(
        zulip_site=args.zulip_site,
        zulip_email=args.zulip_email,
        zulip_api_key=args.zulip_api_key,
        operator_email=args.operator_email,
        project_name=args.project,
        project_path=args.project_path,
        output_path=args.output,
        stream_name=args.stream,
    )


if __name__ == "__main__":
    main()
