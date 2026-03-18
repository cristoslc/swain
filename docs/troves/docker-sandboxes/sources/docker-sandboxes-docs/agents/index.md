# Supported Agents

**Availability:** Experimental  
**Requires:** Docker Desktop 4.58 or later

Docker Sandboxes supports multiple coding agents, all of which run inside isolated microVMs with private Docker daemons.

## Supported agents

| Agent | Command | Status | Notes |
| --- | --- | --- | --- |
| Claude Code | `claude` | Experimental | Most tested implementation |
| Codex | `codex` | Experimental | |
| Copilot | `copilot` | Experimental | |
| Gemini | `gemini` | Experimental | |
| Docker Agent | `cagent` | Experimental | Also available as a standalone tool |
| Kiro | `kiro` | Experimental | |
| OpenCode | `opencode` | Experimental | |
| Custom shell | `shell` | Experimental | Minimal environment for manual setup |

## Experimental status

The page warns that all supported agents are experimental. Documented implications:

- breaking changes may occur between Docker Desktop versions
- features may be incomplete or change significantly
- stability and performance are not production-ready
- support and documentation are limited

The page recommends using sandboxes for development and testing rather than production workloads.

## Agent selection

The agent type is chosen when the sandbox is created:

```console
$ docker sandbox create AGENT [PATH] [PATH...]
```

The agent binding is permanent for that sandbox. To switch agent types, the docs imply recreating the sandbox rather than retargeting it in place.

## Shared template environment

All agent templates are described as inheriting a common base environment:

- Ubuntu 25.10
- Docker CLI with Buildx and Compose
- Git and GitHub CLI
- Node.js
- Go
- Python 3
- `uv`
- `make`
- `jq`
- `ripgrep`
- non-root agent user with `sudo`
- private Docker daemon inside the sandbox
- package managers including `apt`, `pip`, and `npm`

Individual agent templates then add their specific CLIs on top.

## Credentials and requirements

The page notes:

- credentials are agent-specific
- authentication must be configured for the chosen agent
- there is no generic fallback authentication mechanism

Requirements summarized on the page:

- Docker Desktop 4.58 or later
- macOS with `virtualization.framework` or Windows with `Hyper-V`
- API keys or credentials for the selected agent
