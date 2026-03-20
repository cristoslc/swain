# Commands

NemoClaw provides two command interfaces: plugin commands under `openclaw nemoclaw` and the standalone `nemoclaw` binary.

## Plugin Commands

### `openclaw nemoclaw launch`
Bootstrap OpenClaw inside an OpenShell sandbox. Flags: `--force`, `--profile <profile>`.

### `nemoclaw <name> connect`
Open interactive shell inside the sandbox.

### `openclaw nemoclaw status`
Display sandbox health, blueprint run state, inference config. Flag: `--json`.

### `openclaw nemoclaw logs`
Stream blueprint execution and sandbox logs. Flags: `-f/--follow`, `-n/--lines`, `--run-id`.

### `/nemoclaw` Slash Command
Available in OpenClaw chat: `/nemoclaw status`.

## Standalone Host Commands

### `nemoclaw onboard`
Interactive setup wizard. Creates gateway, registers inference providers, builds sandbox image, creates sandbox. Prompts for NVIDIA API key on first run.

### `nemoclaw list`
List all registered sandboxes with model, provider, policy presets.

### `nemoclaw deploy <instance-name>`
(Experimental) Deploy to remote GPU instance through Brev.

### `nemoclaw <name> connect`
Connect to sandbox by name.

### `nemoclaw <name> status`
Show sandbox status, health, inference config.

### `nemoclaw <name> logs`
View sandbox logs. `--follow` for streaming.

### `nemoclaw <name> destroy`
Stop NIM container and delete sandbox.

### `nemoclaw <name> policy-add`
Add policy preset to sandbox.

### `nemoclaw <name> policy-list`
List available and applied policy presets.

### `openshell term`
Open OpenShell TUI to monitor sandbox activity and approve network egress.

### `nemoclaw start` / `nemoclaw stop`
Start/stop auxiliary services (Telegram bridge, cloudflared tunnel).

### `nemoclaw setup-spark`
Set up NemoClaw on DGX Spark (cgroup v2 and Docker fixes for Ubuntu 24.04).
