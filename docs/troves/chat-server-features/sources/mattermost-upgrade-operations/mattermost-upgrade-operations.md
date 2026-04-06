---
source-id: "mattermost-upgrade-operations"
title: "Mattermost Operational Profile — Upgrade, Rollback, and Backup"
type: web
url: "https://docs.mattermost.com/administration-guide/upgrade/upgrading-mattermost-server.html"
fetched: 2026-04-06T22:00:00Z
---

# Mattermost Operational Profile — Upgrade, Rollback, and Backup

## Architecture

Mattermost runs as a single Go binary plus PostgreSQL (or MySQL). Two processes total for a minimal deployment. Docker Compose is the common deployment path, bundling the Mattermost app server and PostgreSQL in separate containers.

This is simpler than Zulip (which needs five services) but more complex than conduwuit (which needs one).

## Resource Requirements

- **RAM:** 2-4 GB recommended.
- **CPU:** 1+ cores.
- **Disk:** Scales with messages, files, and database.

## Upgrade Process

The official docs describe a **12-step manual upgrade** for binary installations:

1. Download the new release tarball.
2. Extract files.
3. Stop the Mattermost service.
4. Back up the database and application files.
5. Remove old application files (preserving config, data, logs, plugins).
6. Copy new files into the install directory.
7. Fix ownership and permissions.
8. Set Linux capabilities for low-port binding.
9. Restart the service.
10. Clean up temporary files.
11. Repeat on all cluster nodes for HA.
12. Users refresh their browsers.

For Docker, the upgrade is simpler: update the image tag in `.env`, run `docker compose up -d`.

Database migrations run automatically on startup. Since Mattermost v6.4, each migration has both an "up" and a "down" script, making rollback theoretically possible.

## Rollback

**No explicit rollback procedure is documented.** The official guidance is to take backups before upgrading and restore from backup if needed. The `mattermost db migrate --save-plan` command generates a migration plan that records changes for potential reversion, but the docs do not provide step-by-step rollback instructions.

In practice, rollback means: stop the service, restore the backed-up files, restore the database from dump, start the service.

## Backup

- **Application:** `cp -ra mattermost/ mattermost-back-$(date +'%F-%H-%M')/`
- **Database:** PostgreSQL dump using `pg_dump` or organizational backup tools.
- **Minimum free space:** 2x the Mattermost installation size.

Backup is not a single-file operation. You need to coordinate file backup and database dump.

## Reliability Track Record

Mattermost has been in production since 2015. It is widely deployed in enterprise environments. The single-binary-plus-database architecture is well understood. The open-core model means some features (compliance, advanced auth) require paid licenses.

The 10,000-message search cap on the free tier is a known limitation. The free tier lacks E2E encryption.

## Operational Complexity Score

- **Deployment:** One binary + PostgreSQL. Docker Compose is the easy path.
- **Upgrades:** 12-step manual process for binary; simpler for Docker. Auto-migrations on startup.
- **Backup:** Coordinated file copy + PostgreSQL dump. Not trivial.
- **Failure modes:** Two processes. PostgreSQL failure is catastrophic. App server failure is recoverable by restart.
- **Monitoring:** Built-in system console with basic health metrics. Better than Zulip's monitoring story.
