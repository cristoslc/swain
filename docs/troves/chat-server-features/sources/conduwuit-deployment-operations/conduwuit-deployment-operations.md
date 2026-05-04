---
source-id: "conduwuit-deployment-operations"
title: "Conduwuit Operational Profile — Deployment, Upgrade, and Backup"
type: web
url: "https://github.com/girlbossceo/conduwuit"
fetched: 2026-04-06T22:00:00Z
---

# Conduwuit Operational Profile — Deployment, Upgrade, and Backup

## Architecture

Conduwuit is a single Rust binary that implements the Matrix homeserver protocol. It uses RocksDB as its embedded database (SQLite support was removed because it was used as an inefficient key-value store). No external services are required: no PostgreSQL, no Redis, no message queue. One binary, one data directory, one TOML config file.

Docker deployment is a single container: `docker run -d -v data:/var/lib/conduwuit -p 6167:6167 girlbossceo/conduwuit:latest`.

## Resource Requirements

- **RAM:** 20-100 MB typical for small instances.
- **CPU:** Minimal. Runs on a Raspberry Pi 4.
- **Disk:** Scales with stored messages and media.

This is the lightest option in the comparison by a wide margin.

## Upgrade Process

Replace the binary or pull the new Docker image. Conduwuit handles any internal database schema changes automatically on startup. There is no separate migration step.

```
docker pull girlbossceo/conduwuit:latest
docker stop conduwuit && docker rm conduwuit
docker run -d ... girlbossceo/conduwuit:latest
```

Downtime is measured in seconds.

## Rollback

Pin the previous Docker tag or keep the old binary. Since RocksDB schema changes are forward-only and generally backward-compatible for minor versions, rollback is usually: stop, swap binary, start.

For major version rollbacks, restore from backup. RocksDB does not have a built-in migration reversal tool.

## Backup

Stop the server and copy the data directory:

```
cp -r /var/lib/conduwuit /backup/conduwuit-$(date +%Y%m%d)
```

Media files are included in the data directory. This is a file-copy backup, no database client tools required. For zero-downtime backup, RocksDB supports checkpoints, but the simplest path is stop-and-copy.

## Reliability Track Record

The project claims "very stable based on our rapidly growing userbase" and suitable as "a daily driver for small, medium, and upper-end medium sized homeservers." The conduwuit fork has been more active than the original Conduit project since 2024. However, community drama around forks (Conduit -> conduwuit -> Continuwuity) raises questions about long-term governance.

Federation support is complete. E2E encryption works. Spaces have basic support. The admin API is limited compared to Synapse.

## Operational Complexity Score

- **Deployment:** Single binary or single Docker container. One config file. No external services.
- **Upgrades:** Replace binary, restart. Seconds of downtime. No separate migration step.
- **Backup:** File copy of one directory. No database client tools needed.
- **Failure modes:** One process. It either runs or it does not. No inter-service failures.
- **Monitoring:** Built-in admin commands via Matrix. Minimal external monitoring needed.
