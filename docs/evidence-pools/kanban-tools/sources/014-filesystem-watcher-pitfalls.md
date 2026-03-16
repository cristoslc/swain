---
source-id: "014"
title: "Filesystem watcher pitfalls — duplicate events, platform quirks, debouncing"
type: web
url: "https://stackoverflow.com/questions/182197/how-do-i-watch-a-file-for-changes"
fetched: 2026-03-15T03:00:00Z
hash: "pending"
---

# Filesystem Watcher Pitfalls

Synthesized from Stack Overflow discussions, watchdog docs, and .NET FileSystemWatcher documentation.

## Common problems

1. **Duplicate events**: A single file save often triggers 2-3 change events (temp write, rename, metadata update). Every watcher library suffers from this on every platform.
2. **Platform inconsistencies**: macOS FSEvents is directory-level (not file-level) and may batch events. Linux inotify is file-level but has a default 8192-watch limit. Windows ReadDirectoryChangesW can miss events under heavy load.
3. **Atomic saves**: Many editors (vim, VS Code) write to a temp file then rename. This produces a delete + create rather than a modify event. Watchers must handle both patterns.
4. **Git operations**: `git checkout`, `git rebase`, `git stash pop` can trigger many simultaneous file changes. The watcher must debounce or batch these to avoid treating each as a separate transition.

## Standard mitigations

- **Debounce**: Wait 100-500ms after the last event before processing. watchfiles does this internally. watchdog requires manual implementation.
- **Content hashing**: On change event, hash file content and compare to cached hash. Only process if content actually changed. Eliminates phantom events from metadata-only changes.
- **Frontmatter diffing**: Parse YAML frontmatter before and after, compare specific fields. This is the swain-specific need — a file may be edited (body changed) without any lifecycle transition.

## The "for a few files, just poll" argument

Stack Overflow consensus: if you're watching fewer than ~100 files, polling every 1-2 seconds with content hashing is simpler and equally reliable. Filesystem watchers shine for large directory trees. Swain's `docs/` folder is typically small enough for either approach.

## Relevance to reactive loop

The watcher component must handle all of these pitfalls. The recommended approach for swain: use watchfiles for the event source (handles debouncing), but add a frontmatter cache layer that only fires "transition events" when the `status` (or configured `column_field`) value actually changes.
