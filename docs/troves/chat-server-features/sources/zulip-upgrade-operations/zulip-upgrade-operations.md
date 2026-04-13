---
source-id: "zulip-upgrade-operations"
title: "Zulip Operational Profile — Upgrade, Rollback, and Backup"
type: web
url: "https://zulip.readthedocs.io/en/stable/production/upgrade.html"
fetched: 2026-04-06T22:00:00Z
---

# Zulip Operational Profile — Upgrade, Rollback, and Backup

## Architecture

Zulip runs five backend services: the Zulip app server (Django/Tornado), PostgreSQL, Memcached, RabbitMQ, and Redis. The standard installer sets all of these up on a single machine. Docker Compose deployment is also supported but adds complexity.

This is **not** a single-binary system. It is a multi-service deployment behind an Nginx reverse proxy.

## Upgrade Process

Zulip provides a scripted upgrade path:

```
/home/zulip/deployments/current/scripts/upgrade-zulip zulip-server-VERSION.tar.gz
```

The script creates a new deployment directory under `/home/zulip/deployments/`, runs database migrations, and swaps symlinks. The process takes a few minutes of downtime.

For Docker deployments, upgrades are more involved and "moderately increase the effort required to install, maintain, and upgrade."

## Rollback

**Minor version rollback is simple.** If the new version breaks, run:

```
/home/zulip/deployments/last/scripts/restart-server
```

This swaps the symlink back to the previous deployment. No database migration reversal needed for minor releases.

**Major version rollback is hard.** Rolling back across major versions requires reversing database migrations manually. The docs warn this is "a more complicated process." In practice, this means taking a database backup before major upgrades and restoring from backup if things go wrong.

## Backup

Zulip provides a built-in backup script:

```
/home/zulip/deployments/current/manage.py backup --output=/path/to/backup.tar.gz
```

This captures the PostgreSQL database, uploaded files, and configuration. Restore is also scripted. The backup is a tarball, not a simple file copy. PostgreSQL dump/restore is the core operation.

## Reliability Track Record

Zulip has been self-hosted by hundreds of organizations since 2015. The upgrade path is well-tested across many versions. The five-service architecture means more things can fail, but each service is a mature, well-understood component.

## Operational Complexity Score

- **Deployment:** Multi-service (5 daemons). Scripted installer handles it, but you are running PostgreSQL, Redis, RabbitMQ, Memcached, and Nginx even for a single user.
- **Upgrades:** Scripted, a few minutes of downtime. Minor rollback is trivial. Major rollback requires backup restore.
- **Backup:** Scripted but involves PostgreSQL dump. Not a simple file copy.
- **Failure modes:** Any of five services can fail independently. RabbitMQ and Redis failures affect async tasks (email, push notifications) but not core chat. PostgreSQL failure is catastrophic.
- **Monitoring:** No built-in health dashboard. You need external monitoring for five services.
