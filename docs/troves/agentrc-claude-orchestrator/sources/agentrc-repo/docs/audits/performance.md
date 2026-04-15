---
domain: performance
auditor: worker-003 (performance-engineer)
date: 2026-04-12
totals:
  critical: 1
  high: 7
  medium: 9
  low: 5
---

# Performance Audit — agent.rc

## Summary

The TUI dashboard is the dominant performance surface and has several compounding inefficiencies. The biggest issue is that the main dashboard loop (`src/commands/dashboard.rs:41-117`) re-renders the entire frame on every event, including a 10 Hz tick stream produced by `EventHandler`, even when nothing has changed. Each render rebuilds both tables (cloning every `id`, `pane_title`, `message` into owned `String`s), re-iterates `app.statuses` 6+ times for counters, rebuilds a full 3D mesh each frame (torus path regenerates ~6,400 points with trig per frame, O(n²) in resolution), and re-allocates a `Vec<Vec<Option<AnimCell>>>` grid per frame. Every 3 seconds the refresh path additionally (a) re-reads and parses every status JSON via one `read_to_string`+`serde_json::from_str` per task, (b) spawns a `tmux capture-pane` subprocess per pane (fork+exec per worker per refresh), and (c) when the events panel is on, reads and JSON-parses the ENTIRE events.jsonl log file — unbounded growth leads to O(n) work per refresh that scales with the whole session history. The highest-impact single fix is to bound `events::tail` with a reverse/chunked read (constant memory and CPU), and to introduce a "dirty" flag or incremental redraw path so ratatui is only asked to repaint when app state or animation actually advances.

## Findings

## F-01: Events log is fully loaded and JSON-parsed on every 3 s dashboard refresh
- **Severity:** critical
- **Location:** `src/events.rs:61-82` (called from `src/tui/app.rs:131-133`)
- **Description:** `events::tail` reads the entire `events.jsonl` file into memory with `std::fs::read_to_string`, splits into lines, runs `serde_json::from_str` on every single historical line, collects into a `Vec<OrcEvent>`, and then throws away everything except the last `count`. This happens every time `App::refresh()` runs (default every 3 s) and also on `events` CLI calls. For a long-running session with e.g. 50,000 events (plausible across many worker runs) this is O(n) bytes read + O(n) JSON parses + O(n) allocations per refresh — unbounded growth. The dashboard will progressively stutter as the session grows.
- **Proposed remediation:** Implement a tail reader that seeks from EOF: open the file, `seek(End)`, read backwards in 8 KiB chunks into a buffer, find the last `count` newlines, then parse only those `count` lines. Alternatively, maintain an in-memory ring buffer of the most recent events and append to it on each `emit`. A third option: track the file's position after the last successful tail and only read from that offset forward on subsequent calls, capping the in-memory buffer at `count`.
- **Confidence:** high

## F-02: Dashboard redraws on every event tick even when nothing visible changed
- **Severity:** high
- **Location:** `src/commands/dashboard.rs:41-117`, `src/tui/event.rs:19-45`
- **Description:** The main loop calls `terminal.draw(|frame| ui::render(&app, frame))?;` at the top of every iteration, unconditionally, regardless of whether the event that was about to be processed is a keypress, a mouse event, or just a 100 ms tick. `EventHandler` also always pushes `Event::Tick` after every successful `event::poll`, so even input events produce a trailing tick that triggers a second redraw. This pins the TUI at ~10 Hz redraw rate even with no input and no status changes, burning CPU to rebuild rows/cells that will be diffed-away by ratatui's buffer diff. On a battery-powered laptop in front of a mostly-idle dashboard, this is the dominant power draw.
- **Proposed remediation:** Introduce an `App::dirty` flag. Set it in `refresh()`, on key/mouse events, and inside `anim::AnimState::tick()` only when `tick()` actually advances (i.e. after the 100 ms rate-limit gate). At the top of the loop, only call `terminal.draw(...)` if `app.dirty` is true; then clear the flag. Alternative: lower the tick rate to 250 ms and combine with dirty-checking. Keep animation redrawing at 10 Hz only when animation is on and something is moving (non-zero `activity_level` could further cap it).
- **Confidence:** high

## F-03: Torus `render_frame` re-generates 6,400 surface points + sin/cos every render
- **Severity:** high
- **Location:** `src/tui/anim/render.rs:73-107`, `src/tui/anim/shapes.rs:97-126`
- **Description:** When `Shape::Torus` is active (the default), each call to `render_frame` calls `torus_points(resolution)` where `resolution = max(40, width + 2 * height)`. For a typical 60x12 donut area that's `resolution ≈ 84`, producing `84 * 84 = 7056` points. Each point triggers 4 trig calls (`cos_theta`, `sin_theta`, `cos_phi`, `sin_phi`) plus allocations into a `Vec<(Vertex, Vertex)>` of length 7056. Rotation, projection, normal-rotation, lighting dot product are then done for every point. Because `rotate_vertex` only depends on the two current angles, and the torus geometry itself is static, the base points + normals could be cached once per resolution and only the rotation/projection done per frame.
- **Proposed remediation:** (1) Cache torus points per `(resolution)` key in `AnimState` (or a `OnceCell<Vec<(Vertex, Vertex)>>` keyed by resolution) so the sin/cos table is built once, not every frame. (2) Consider capping `resolution` (e.g. min(80, ...)); at some point more points just produce z-fighting, not visual improvement. (3) Consider an even simpler optimization: pre-multiply rotation matrix once per frame instead of calling `rotate_vertex` on each of 7056 points independently — `rotate_vertex` recomputes `angle_y.cos()`, `angle_y.sin()`, `angle_x.cos()`, `angle_x.sin()` every invocation.
- **Confidence:** high

## F-04: `rotate_vertex` recomputes sin/cos of the same two angles for every vertex
- **Severity:** high
- **Location:** `src/tui/anim/render.rs:123-140` (called from `render.rs:39` and `render.rs:88-89`)
- **Description:** `rotate_vertex` calls `angle_y.cos()`, `angle_y.sin()`, `angle_x.cos()`, `angle_x.sin()` internally. It is called once per cube/octahedron vertex (cheap; 8 or 6 calls), but for the torus it is called `resolution * resolution * 2` times (once for the vertex and once for the normal), i.e. ~14,000 trig calls per frame just for the angle table — the same four values over and over. At 10 Hz that's ~140,000 redundant trig calls per second.
- **Proposed remediation:** In `render_frame`, compute `cos_y, sin_y, cos_x, sin_x` once before the inner loop and pass them (or a 3x3 rotation matrix) into a `rotate_vertex_with_table` helper. This collapses 4 transcendental calls per point into a handful of muls/adds.
- **Confidence:** high

## F-05: Status directory + all JSON files re-read + re-parsed every 3 s refresh
- **Severity:** high
- **Location:** `src/commands/status.rs:63-91` (called from `src/tui/app.rs:101`)
- **Description:** `collect_statuses` does a full `read_dir` and a `read_to_string`+`serde_json::from_str` for every `*.json` file on every call. Nothing uses file mtime or size to skip unchanged files. In the dashboard hot path this runs every 3 s for all tasks, including completed/aborted tasks that will never change again. With 50 historical tasks that's 50 syscalls + 50 JSON parses every 3 s forever.
- **Proposed remediation:** Cache `HashMap<PathBuf, (SystemTime, TaskStatus)>` keyed by path and only re-parse a file whose mtime changed. Or, combine with `notify` (already a dep) to build a push-based cache updated on fs events — the `watch` command already demonstrates this pattern. For graveyard tasks, skip re-reading entirely once a terminal state is observed. Another option: read the `status/` directory once at startup and thereafter rely exclusively on an fs watcher to invalidate cached entries.
- **Confidence:** high

## F-06: `tmux capture-pane` subprocess fork+exec per worker per refresh
- **Severity:** high
- **Location:** `src/tui/app.rs:107-124`, `src/tmux/wrapper.rs:142-160`, `src/tmux/wrapper.rs:300-309`
- **Description:** `App::refresh` iterates all statuses with a pane and calls `detect::scan_pane_full` for each. Each call executes `tmux capture-pane -t <pane> -p -S -30` via `std::process::Command::new("tmux").args(...).output()`. This forks, execs the tmux binary, ships the request over the tmux socket, and returns ~30 lines of text — for EVERY worker EVERY refresh (3 s). With 10 workers that's 10 subprocess launches per refresh or ~200/minute. Each fork/exec is milliseconds of wall time. For 20+ workers this becomes user-visible lag on refresh.
- **Proposed remediation:** (a) Batch pane captures into a single `tmux` invocation where possible — tmux supports `display-message` and listing attributes across panes. A simpler win: use `list-panes -F '#{pane_id}\t#{pane_current_command}\t#{pane_title}'` once to get lightweight state for idle/dead detection, and only `capture-pane` for panes whose state was recently ambiguous. (b) Extend the `Tmux` wrapper to keep a persistent control-mode connection (`tmux -C`) over a single child process, piping commands in/out, rather than spawning a fresh tmux process per call. (c) At minimum, throttle captures for completed/aborted workers where the state will not change.
- **Confidence:** high

## F-07: Both worker and graveyard tables re-scan full `app.statuses` for `max_tokens` and counts
- **Severity:** medium
- **Location:** `src/tui/widgets/table.rs:221-228`, `src/tui/widgets/table.rs:263-267`, `src/tui/widgets/table.rs:276-283`, `src/tui/widgets/table.rs:318-322`
- **Description:** `render_workers` iterates `app.statuses` to compute `max_tokens` (line 223) and again to compute `active_count` (line 263). `render_graveyard` does the same two iterations. Combined with `header::render` (`active_count`, `completed_count`, `failed_count`, `total_tokens`, and the `healthy` computation — five full iterations) and `ui::render` itself computing `graveyard_count` (line 41-52), a single frame walks `app.statuses` ~10 times. Every render. Every 100 ms. At 50 statuses that's 500 comparisons per frame × 10 Hz = 5,000/s per core — dwarfed by allocation costs but avoidable.
- **Proposed remediation:** Add a `DerivedStats` struct to `App` populated in `refresh()` (once) or lazily at the start of `render`. It holds `active_count`, `completed_count`, `failed_count`, `graveyard_count`, `total_tokens`, `max_tokens`, `orc_tokens`, `healthy_count`. Pass it into the widgets instead of re-computing.
- **Confidence:** high

## F-08: `build_row` does linear scan `stale_heartbeats.contains(&s.id)` per row (O(n²))
- **Severity:** medium
- **Location:** `src/tui/widgets/table.rs:240`, `src/tui/widgets/table.rs:295`
- **Description:** `app.stale_heartbeats` is a `Vec<String>` and `.contains(&s.id)` scans it linearly. This is called once per row in both `render_workers` and `render_graveyard`. With `N` statuses and `S` stale, this is O(N * S) per frame, reaching O(N²) in the worst case. Today with small N it is invisible; at hundreds of tasks + many stale heartbeats it becomes noticeable.
- **Proposed remediation:** Store `stale_heartbeats` as a `HashSet<String>` (or even an `ahash::AHashSet`) in `App`, and/or pre-compute a boolean per-row during refresh. Same change applies to anywhere that currently uses `Vec<String>::contains`.
- **Confidence:** high

## F-09: Topological sort uses `Vec<String>::contains` inside nested loops — O(n³) at scale
- **Severity:** medium
- **Location:** `src/commands/plan.rs:239-275`
- **Description:** `topo_sort` iterates `remaining` and for each task checks `task.depends_on.iter().all(|dep| emitted.contains(dep) || !ids.contains(dep))` where both `emitted` and `ids` are `Vec<String>`. `.contains` is O(n). The outer `while !remaining.is_empty()` loop wraps this, giving worst-case O(n³) complexity. For 50-200 writer tasks this is still fast, but it scales poorly and there is no reason to use `Vec::contains` when a `HashSet` is readily available and the code already uses `HashSet` in `validate_briefs`.
- **Proposed remediation:** Convert `emitted` and `ids` to `HashSet<&str>` (borrow from `briefs`), reducing total complexity to O(n²). Better, replace the whole algorithm with Kahn's (already implemented as `detect_cycle`) — one topo sort implementation is enough.
- **Confidence:** high

## F-10: `render_donut` and `render_shimmer` allocate a `String` per cell via `ch.to_string()`
- **Severity:** medium
- **Location:** `src/tui/anim/widget.rs:187` and `src/tui/anim/widget.rs:210`
- **Description:** For every visible animation cell (up to ~960 cells at 80x12) and every character of the banner/motto shimmer text, the code calls `c.ch.to_string()` / `ch.to_string()` to produce a heap-allocated `String` that is then passed to `buf.set_string(...)`. Every frame. At 10 Hz animation, that is ~10,000 `String` allocations/s — almost all immediately dropped. `Buffer::set_string` takes `AsRef<str>` so a stack `[u8; 4]` encoded via `ch.encode_utf8(&mut buf)` avoids the heap entirely.
- **Proposed remediation:** Replace `ch.to_string()` with:
```rust
let mut tmp = [0u8; 4];
let s: &str = ch.encode_utf8(&mut tmp);
buf.set_string(x, y, s, style);
```
Or, drop into `Buffer::get_mut((x, y)).set_char(ch).set_style(style)` which is the ratatui idiom for single-char cell writes and avoids set_string's `AsRef<str>` path.
- **Confidence:** high

## F-11: Per-render clones of `id` / `pane_title` / `message` into owned cells
- **Severity:** medium
- **Location:** `src/tui/widgets/table.rs:97` (id), `src/tui/widgets/table.rs:175-180` (pane), `src/tui/widgets/events.rs:44-45` (task/msg)
- **Description:** Every frame, `build_row` does `s.id.clone()`, `.to_string()` on pane title/id, and `format_event_line` does `event.task_id.clone()` and `event.message.clone()` so that `Span::styled(...)` can hold a `'static` string. At 10 Hz for dozens of rows/events, this is hundreds of `String` allocations/s, all discarded when the frame buffer is diffed. ratatui spans will accept `Cow<'_, str>` for most styled text, so `Span::styled(&s.id, ...)` (borrowed) would work if the returned `Row` did not need `'static`.
- **Proposed remediation:** Two options:
  1. Make the table rows borrow from `app`. `Row<'a>`/`Cell<'a>` accept non-`'static` lifetimes — the Row just has to outlive the `Table::render` call, which it does. Change `build_row` to return `Row<'a>` with `a = 'app lifetime`.
  2. Store commonly rendered strings as `Arc<str>` in `TaskStatus` / `OrcEvent` so clones are just a refcount bump. `Arc<str>` for `id`, `pane_title`, `message`, `branch`, `phase`, `last_message` would remove nearly all per-frame string allocations from the rendering path while keeping the types simple.
- **Confidence:** medium

## F-12: `render_donut` calls `depth_to_style` per cell, recomputing the palette branch each time
- **Severity:** low
- **Location:** `src/tui/anim/widget.rs:6-18`, `src/tui/anim/widget.rs:203-214`
- **Description:** `depth_to_style` matches on `activity_level` every call to pick `(front, back)`. Since `activity_level` is constant across the whole frame, this match runs ~1,000 times per frame with an identical answer. The match is cheap, but the pattern is emblematic: the per-cell inner loop re-derives per-frame constants.
- **Proposed remediation:** Hoist `(front, back)` out of the per-cell loop in `render_donut`, compute the style prefix once, then only compute `interp` per cell.
- **Confidence:** high

## F-13: `render_frame` allocates a fresh `Vec<Vec<Option<AnimCell>>>` every frame
- **Severity:** medium
- **Location:** `src/tui/anim/render.rs:19-26`
- **Description:** Each call to `render_frame` does `vec![vec![None; w]; h]`, then fills it, then the grid is iterated once and dropped. That's `h` heap allocations per frame (one per row plus the outer `Vec`), all of them sized for ~60 columns. Over a long session this puts pressure on the allocator unnecessarily.
- **Proposed remediation:** Keep a reusable `Vec<Option<AnimCell>>` buffer of size `w * h` on `AnimState` (or pass `&mut` into `render_frame`). Index as `grid[y * w + x]`. On size changes, resize the buffer in place. Then `render_frame` just clears it with `fill(None)` each frame — one contiguous write instead of many tiny vec allocations.
- **Confidence:** high

## F-14: Orchestrator pane scan uses a blocking tmux subprocess every 3 s unconditionally
- **Severity:** medium
- **Location:** `src/tui/app.rs:120-124`, `src/tui/app.rs:62-74`
- **Description:** The refresh always calls `tmux.capture_pane(orc_pane, 30)` when an orchestrator pane is set — even if the orchestrator output hasn't changed and even if token display is not visible. Token output only changes when Claude Code updates its footer (infrequent), but a subprocess is spawned every 3 s. Additionally, `App::new` scans `tmux.list_panes_with_titles("")` via another subprocess to discover the orchestrator pane on every dashboard launch (once only, so minor), but combined with F-06 this is another per-refresh subprocess that the user sees as a latency spike on low-end hardware.
- **Proposed remediation:** Throttle orchestrator-pane scans to a longer interval (e.g. every 10 s instead of 3 s), or gate on "orchestrator row visible in current layout". Merge with F-06: a persistent tmux control-mode connection would eliminate the fork/exec entirely.
- **Confidence:** medium

## F-15: `EventHandler` always emits a `Tick` after every input event, causing double-redraws
- **Severity:** medium
- **Location:** `src/tui/event.rs:23-42`
- **Description:** The thread loops: poll(100 ms), read() on success, send the event, then unconditionally `tick_tx.send(Event::Tick)`. So typing a single key produces `Key -> Tick` two events → two full redraws. Heavy keyboard usage (j/k scrolling through worker list) doubles the redraw rate. Combined with F-02, each keystroke performs two full rebuilds of the tables, the anim, the header, etc.
- **Proposed remediation:** Only send `Tick` when `event::poll` returned `false` (timeout, nothing arrived) — i.e. restructure as `if poll { process } else { send Tick }`. Or, send `Tick` on a separate timer thread that uses a coalescing strategy (drop ticks if the channel backlog is non-zero). Combined with F-02's dirty-flag fix, this issue largely disappears.
- **Confidence:** high

## F-16: `watch_with_receiver` reads every status file at startup, no mtime/inode cache
- **Severity:** medium
- **Location:** `src/commands/watch.rs:125-138`, `src/commands/watch.rs:140-172`
- **Description:** The seeding loop does a full `read_dir` + `read_to_string` + JSON parse for every status file before the event loop starts. Then inside the event loop, `process_status_change` re-reads + re-parses the whole status file on every `Modify` event, even if only the mtime changed (e.g. heartbeat side effect). For runs with rapid status updates this triggers many redundant full-file reads.
- **Proposed remediation:** Share a `HashMap<PathBuf, TaskStatus>` cache between `watch` and `collect_statuses` (it already keeps `previous_states` but only stores `TaskState`, losing the rest). When a path's mtime matches the cached mtime, skip the read. Buffered reads (`BufReader::new(File::open(path)?)` with serde_json's reader-based API) would also avoid the intermediate `String` for large status files.
- **Confidence:** medium

## F-17: Dashboard animation `tick()` fires on every `Event::Tick` even when animation is hidden
- **Severity:** low
- **Location:** `src/commands/dashboard.rs:106-111`, `src/tui/anim/mod.rs:40-61`
- **Description:** `dashboard.rs` calls `app.anim.tick()` on every `Event::Tick`, unconditionally. `tick()` does its own 100 ms rate limit so the actual state update is bounded, but `Instant::now()` + arithmetic still runs ~10 Hz even when `app.show_animation` is false or the terminal is too small to show the animation (`anim_h == 0`). Not costly per se but a correctness gap — disabling animation does not fully stop the animation state machine.
- **Proposed remediation:** Gate `tick()` on `app.show_animation && anim_height(...) > 0`. Skip the `tick()` entirely when animation is not visible. This also dovetails with F-02: when animation is hidden and statuses haven't changed, the dashboard should not need to redraw at all.
- **Confidence:** high

## F-18: `serde_json::from_str(&content)` is invoked with intermediate `String` allocation for each status file
- **Severity:** low
- **Location:** `src/commands/status.rs:77-83`, `src/commands/watch.rs:22-24`, `src/commands/spawn.rs:185-190`, `src/commands/amend.rs:51-54`, `src/commands/checkpoint.rs:182-184`, `src/commands/worker/done.rs:42-44`, etc.
- **Description:** Several hot-ish code paths do `fs::read_to_string(path)?` then `serde_json::from_str(&content)?`. This allocates an intermediate `String` the size of the file. For small JSON (status files are kilobytes), it is cheap; for `events.jsonl` it is large (see F-01). Using `serde_json::from_reader(BufReader::new(File::open(path)?))` avoids the intermediate allocation and lets serde stream directly from a buffered reader.
- **Proposed remediation:** Replace the `read_to_string` + `from_str` idiom with `from_reader(BufReader::new(File::open(p)?))` for JSON paths. Keep `read_to_string` only where the string itself is needed afterward (e.g. YAML frontmatter where the body is consumed separately).
- **Confidence:** high

## F-19: `format_event_line` rebuilds the same timestamp string, label and `sep` Spans every render
- **Severity:** low
- **Location:** `src/tui/widgets/events.rs:40-58`
- **Description:** For each of the last 5 events, on every render, the code (a) formats the timestamp with `format("%H:%M:%S").to_string()`, (b) clones `task_id` and `message` Strings, and (c) constructs two `Span::styled` "sep" values (the second call `sep.clone()` is particularly redundant because the first construction is already a clone of the template). On every 10 Hz tick this is ~50 new Spans/s + ~15 new Strings/s for static-looking data.
- **Proposed remediation:** Pre-format event lines once (when `recent_events` is refreshed in `App::refresh()`) and cache `Vec<Line<'static>>` in `App`. On render just hand the cached lines to ratatui. Only rebuild when `recent_events` actually changes.
- **Confidence:** high

## F-20: `handle_click` recomputes active/graveyard counts on every mouse down
- **Severity:** low
- **Location:** `src/tui/app.rs:199-249`
- **Description:** Each left-click triggers a fresh O(n) scan of `app.statuses` to split into active vs graveyard. Infrequent (human click rate), but would be zero-cost if F-07's `DerivedStats` existed.
- **Proposed remediation:** Consume `DerivedStats` from F-07. No additional changes needed.
- **Confidence:** high

## F-21: `render_info` allocates string-backed dot-leader per row per frame
- **Severity:** low
- **Location:** `src/tui/anim/widget.rs:55-89`
- **Description:** For each of the 7 metadata rows, `render_info` constructs `String` keys and values via `.into()`, then builds a fresh dot-leader `String` via `std::iter::repeat('·').take(n).collect()` every frame. That's 7 × ~30-character strings allocated per frame just for the dots, on every animation redraw. Minor but avoidable.
- **Proposed remediation:** Pre-build a `&'static str` of the maximum plausible dot-width (e.g. 80) and slice it per row. Or store the 7 metadata rows as `&'static str` tuples (they are essentially static) and format dynamic values into a single reused `String` buffer (`String::clear()` + `write!`).
- **Confidence:** high

## F-22: `events::tail` then iterates `skip()` which still walks the discarded prefix
- **Severity:** low
- **Location:** `src/events.rs:80-82`
- **Description:** After collecting ALL events into `events: Vec<OrcEvent>`, the code computes `skip = events.len().saturating_sub(count)` and then `events.into_iter().skip(skip).collect()`. This is correct but double-traversing: everything allocated, then skipped. If F-01 is implemented as a reverse tail reader, this function collapses to a single pass that never touches discarded history.
- **Proposed remediation:** Same remedy as F-01. If F-01 is deferred, at least `events.drain(..skip)` is cheaper than `skip().collect()` because it reuses the existing `Vec`'s backing allocation rather than allocating a second one.
- **Confidence:** high
