---
id: swa-002b
status: closed
deps: []
links: []
created: 2026-03-13T03:16:11Z
type: task
priority: 1
assignee: Cristos L-C
parent: swa-uumx
tags: [gh:30]
---
# Fix yazi system-open behavior

Address GitHub issue #30 by making swain-stage/yazi open files with the system default application instead of .


## Notes

**2026-03-13T04:17:57Z**

Completed: swain-stage now launches yazi with bundled config via XDG_CONFIG_HOME, and skills/swain-stage/references/yazi/yazi.toml redirects text-like files to the system opener; verified by bash -n, TOML parse, and get_file_browser_command output.
