---
id: swa-y6fi
status: closed
deps: [swa-8t7a]
links: []
created: 2026-03-18T11:54:33Z
type: task
priority: 2
assignee: cristos
parent: swa-62fm
tags: [spec:SPEC-067]
---
# Remove Tier 2 from scripts/claude-sandbox

Remove --docker flag, entire TIER 2 section (lines ~23-134), USE_DOCKER variable, DOCKERFILE variable, DEVCONTAINER_DIR/DEVCONTAINER_FILE variables, ENV_FLAGS logic, and devcontainer.json generation block. Update header comment to reflect Tier 1 only. Retain --here and --project=DIR flags. AC-9, AC-11.


## Notes

**2026-03-18T11:59:43Z**

Removed: --docker flag, USE_DOCKER, DOCKERFILE, IMAGE_NAME, DEVCONTAINER_DIR/FILE, DOCKER_IMAGE, jq docker-image read, entire Tier 2 block. Kept: --here, --project=DIR, ALLOWED_DOMAINS (still used in Tier 1). --docker now silently passed to EXTRA_ARGS (ignored per AC-9 second option).
