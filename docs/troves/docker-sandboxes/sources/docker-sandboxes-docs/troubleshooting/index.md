# Troubleshooting

**Availability:** Experimental  
**Requires:** Docker Desktop 4.58 or later

This page collects common operational failures when using Docker Sandboxes.

## `'sandbox' is not a docker command`

The docs attribute this to the CLI plugin being missing or not installed in the expected location.

Suggested checks:

```console
$ ls -la ~/.docker/cli-plugins/docker-sandbox
```

The file should exist and be executable. If Docker Desktop is already installed, the page recommends restarting it so it can detect the plugin.

## Experimental features disabled by administrator

If Docker Desktop is centrally managed, sandboxes can fail because beta features are locked off. The page gives an example settings-management JSON shape that must allow beta features.

## Authentication failure

For agent authentication errors, the page points first to invalid, expired, or misconfigured API keys.

## Workspace contains API key configuration

A documented Claude-specific conflict occurs when the workspace contains `.claude.json` with a `primaryApiKey` field. The page offers two approaches:

- remove `primaryApiKey` from `.claude.json`
- proceed, understanding workspace credentials will be ignored in favor of sandbox credentials

The example retained in the docs uses `apiKeyHelper` and `ANTHROPIC_BASE_URL` without a workspace-owned primary key.

## Permission denied on workspace files

The page ties permission problems to either Docker Desktop file-sharing configuration or Unix file permissions.

Checks shown in the docs:

```console
$ ls -la <workspace>
$ cd <workspace>
$ pwd
```

Potential fix:

```console
$ chmod -R u+r <workspace>
```

On Docker Desktop, the page also instructs operators to ensure the workspace or a parent directory is included in File Sharing settings and then restart Docker Desktop.

## Windows crashes when launching multiple sandboxes

The Windows-specific failure mode described here is instability when starting too many sandboxes at once. Recovery guidance:

1. open Task Manager
2. find `docker.openvmm.exe`
3. end those processes
4. restart Docker Desktop if needed

The operational advice is to launch sandboxes one at a time rather than concurrently.

## Persistent corruption or stuck state

The page offers a full reset command:

```console
$ docker sandbox reset
```

This stops all running VMs and deletes all sandbox data while leaving the daemon running. The docs recommend using it for persistent failures or to reclaim disk space globally.
