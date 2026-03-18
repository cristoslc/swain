# Get Started with Docker Sandboxes

**Availability:** Experimental  
**Requires:** Docker Desktop 4.58 or later

This guide walks through the first sandboxed run using Claude Code as the example agent.

## Prerequisites

Before first use, the guide requires:

- Docker Desktop 4.58 or later
- macOS or Windows (experimental)
- a Claude API key

The page also points upgrading users to the migration guide for the newer microVM architecture.

## Configure credentials

The guide recommends setting the API key globally in shell configuration, not inline:

```bash
export ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
```

The reason given is operational: Docker Sandboxes uses a daemon process that runs independently of the current shell session, so inline environment variables or one-off shell exports will not be seen by the daemon.

Documented follow-up steps:

1. add the variable to `~/.bashrc` or `~/.zshrc`
2. reload shell configuration
3. restart Docker Desktop so the daemon picks up the environment

The page allows interactive authentication as a fallback, but calls it less secure and less convenient because it must be repeated per workspace.

## Create and run a sandbox

Core first-run command:

```console
$ docker sandbox run claude [PATH]
```

Behavior described by the docs:

- Docker creates a microVM sandbox
- Docker assigns a name based on the agent and workspace directory
- the workspace is synchronized into the VM
- Claude Code starts inside the sandbox
- the first run takes longer because the VM and template image must be initialized

The path argument is optional and defaults to the current directory.

### Multiple workspaces and read-only mounts

The guide documents multiple workspace paths and read-only mounts:

```console
$ docker sandbox run claude ~/my-project ~/docs:ro
```

## What just happened

The guide explicitly breaks down the result of `docker sandbox run`:

1. Docker created a lightweight microVM with a private Docker daemon.
2. The sandbox got a generated name derived from the workspace path.
3. The workspace synced into the VM.
4. The agent started as a container inside the sandbox VM.

The sandbox persists until removed, so operators can reconnect to it later.

## Basic commands

List sandboxes:

```console
$ docker sandbox ls
```

Open an interactive shell in a running sandbox:

```console
$ docker sandbox exec -it <sandbox-name> bash
```

Remove a sandbox:

```console
$ docker sandbox rm <sandbox-name>
```

Remove multiple sandboxes:

```console
$ docker sandbox rm <sandbox-1> <sandbox-2>
```

Reset a sandbox by removing and recreating it:

```console
$ docker sandbox rm <sandbox-name>
$ docker sandbox run claude [PATH]
```

## Operator warning

The guide includes an explicit safety warning: agents can modify files in the workspace, so operators should review changes before executing code or actions that trigger scripts automatically.

## Next steps

The page routes readers to follow-on topics:

- supported agents
- effective workflows
- custom templates
- network policies
- troubleshooting
