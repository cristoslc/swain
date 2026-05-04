# Phase 3 — Dashboard & Resilience: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an interactive ratatui dashboard with agent state detection, checkpoint save/restore, and auto-respawn to agentrc.

**Architecture:** Two parallel tracks. Track A: agent state detection module (`src/detect/`) feeds into a ratatui TUI (`src/tui/`). Track B: checkpoint save/restore (`src/commands/checkpoint.rs`) feeds into auto-respawn (`src/commands/respawn.rs`). A standalone README task runs in parallel.

**Tech Stack:** Rust 2021, ratatui 0.29, crossterm 0.28, tui-scrollview 0.4, tui-input 0.11. Existing: clap 4, serde, chrono, anyhow, thiserror.

---

## Task 001: Agent State Detection

**Track A, no dependencies. Parallel with 003 and 005.**

**Files:**
- Create: `src/detect/mod.rs`
- Modify: `src/lib.rs`
- Modify: `src/tmux/wrapper.rs`
- Modify: `src/model/task.rs`
- Modify: `src/commands/worker/status.rs`
- Modify: `src/main.rs`
- Create: `tests/detect_test.rs`

### Part A: Tmux capture_pane helper

- [ ] **Step 1: Write test for capture_pane command builder**

In `tests/tmux_test.rs`, add:

```rust
#[test]
fn tmux_build_capture_pane_command() {
    let args = Tmux::build_capture_pane_args("%5", 30);
    assert_eq!(
        args,
        vec!["capture-pane", "-t", "%5", "-p", "-S", "-30"]
            .into_iter()
            .map(String::from)
            .collect::<Vec<_>>()
    );
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cargo test tmux_build_capture_pane_command -- --nocapture`
Expected: FAIL — `build_capture_pane_args` not found.

- [ ] **Step 3: Implement build_capture_pane_args and capture_pane**

In `src/tmux/wrapper.rs`, add to the static command builders section:

```rust
/// Build args for `tmux capture-pane -t <pane_id> -p -S -<lines>`.
pub fn build_capture_pane_args(pane_id: &str, lines: u32) -> Vec<String> {
    vec![
        "capture-pane".to_string(),
        "-t".to_string(),
        pane_id.to_string(),
        "-p".to_string(),
        "-S".to_string(),
        format!("-{lines}"),
    ]
}
```

In the instance methods section, add:

```rust
/// Capture last N lines of pane scrollback as a string.
pub fn capture_pane(&self, pane_id: &str, lines: u32) -> Result<String> {
    self.run_tmux(&[
        "capture-pane",
        "-t",
        pane_id,
        "-p",
        "-S",
        &format!("-{lines}"),
    ])
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cargo test tmux_build_capture_pane_command -- --nocapture`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/tmux/wrapper.rs tests/tmux_test.rs
git commit -m "feat: add capture_pane to tmux wrapper"
```

### Part B: DetectedState enum and scan logic

- [ ] **Step 6: Write tests for state detection from text**

Create `tests/detect_test.rs`:

```rust
use agentrc::detect::{detect_from_text, DetectedState};

#[test]
fn detect_needs_input_permission_prompt() {
    let text = "some output\n Do you want to proceed?\n ❯ 1. Yes\n   2. No";
    assert_eq!(detect_from_text(text), DetectedState::NeedsInput);
}

#[test]
fn detect_thinking() {
    let text = "Reading file...\n\n✶ Precipitating… (thinking with high effort)";
    assert_eq!(detect_from_text(text), DetectedState::Thinking);
}

#[test]
fn detect_tool_use_reading() {
    let text = "  Reading 3 files… (ctrl+o to expand)\n";
    assert_eq!(detect_from_text(text), DetectedState::ToolUse);
}

#[test]
fn detect_tool_use_writing() {
    let text = "  Writing to src/main.rs\n";
    assert_eq!(detect_from_text(text), DetectedState::ToolUse);
}

#[test]
fn detect_running_bash() {
    let text = "  Bash(cargo test)\n  running…\n";
    assert_eq!(detect_from_text(text), DetectedState::Running);
}

#[test]
fn detect_rate_limited() {
    let text = "Error: 429 Too Many Requests\nrate limit exceeded";
    assert_eq!(detect_from_text(text), DetectedState::RateLimited);
}

#[test]
fn detect_errored() {
    let text = "thread 'main' panicked at 'index out of bounds'";
    assert_eq!(detect_from_text(text), DetectedState::Errored);
}

#[test]
fn detect_idle_prompt() {
    let text = "Task completed.\n\n❯ \n";
    assert_eq!(detect_from_text(text), DetectedState::Idle);
}

#[test]
fn detect_unknown_empty() {
    let text = "";
    assert_eq!(detect_from_text(text), DetectedState::Unknown);
}

#[test]
fn detect_priority_needs_input_over_thinking() {
    // NeedsInput is higher priority than Thinking
    let text = "thinking…\n Do you want to proceed?\n ❯ 1. Yes";
    assert_eq!(detect_from_text(text), DetectedState::NeedsInput);
}
```

- [ ] **Step 7: Run tests to verify they fail**

Run: `cargo test detect_ -- --nocapture`
Expected: FAIL — module `detect` not found.

- [ ] **Step 8: Implement detect module**

Create `src/detect/mod.rs`:

```rust
use std::fmt;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum DetectedState {
    Thinking,
    ToolUse,
    Running,
    Idle,
    NeedsInput,
    RateLimited,
    Errored,
    Dead,
    Unknown,
}

impl fmt::Display for DetectedState {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            DetectedState::Thinking => write!(f, "thinking"),
            DetectedState::ToolUse => write!(f, "tool_use"),
            DetectedState::Running => write!(f, "running"),
            DetectedState::Idle => write!(f, "idle"),
            DetectedState::NeedsInput => write!(f, "needs_input"),
            DetectedState::RateLimited => write!(f, "rate_limited"),
            DetectedState::Errored => write!(f, "errored"),
            DetectedState::Dead => write!(f, "dead"),
            DetectedState::Unknown => write!(f, "unknown"),
        }
    }
}

impl DetectedState {
    pub fn icon(&self) -> &'static str {
        match self {
            DetectedState::Thinking => "*",
            DetectedState::ToolUse => "@",
            DetectedState::Running => "$",
            DetectedState::Idle => "-",
            DetectedState::NeedsInput => "!",
            DetectedState::RateLimited => "~",
            DetectedState::Errored => "x",
            DetectedState::Dead => "x",
            DetectedState::Unknown => "?",
        }
    }
}

/// Detect worker state from captured pane text.
///
/// Rules applied in priority order — first match wins.
pub fn detect_from_text(text: &str) -> DetectedState {
    let lower = text.to_lowercase();

    // Priority 1: NeedsInput (permission prompts)
    if lower.contains("do you want to proceed")
        || lower.contains("yes, allow")
        || lower.contains("❯ 1. yes")
        || (lower.contains("allow") && lower.contains("permission"))
    {
        return DetectedState::NeedsInput;
    }

    // Priority 2: RateLimited
    if lower.contains("rate limit")
        || lower.contains("429")
        || lower.contains("overloaded")
    {
        return DetectedState::RateLimited;
    }

    // Priority 3: Errored
    if lower.contains("panicked at")
        || lower.contains("sigterm")
        || lower.contains("sigsegv")
        || lower.contains("fatal error")
    {
        return DetectedState::Errored;
    }

    // Priority 4: Thinking
    if lower.contains("precipitating")
        || lower.contains("thinking")
    {
        return DetectedState::Thinking;
    }

    // Priority 5: ToolUse
    if lower.contains("reading")
        || lower.contains("writing to")
        || lower.contains("editing")
        || lower.contains("edit(")
    {
        return DetectedState::ToolUse;
    }

    // Priority 6: Running
    if lower.contains("bash(")
        || lower.contains("running")
        || (lower.contains("cargo") && lower.contains("test"))
        || lower.contains("npm ")
    {
        return DetectedState::Running;
    }

    // Priority 7: Idle (Claude prompt at end)
    let trimmed = text.trim_end();
    if trimmed.ends_with("❯") || trimmed.ends_with("> ") {
        return DetectedState::Idle;
    }

    DetectedState::Unknown
}

/// Scan a live tmux pane and return detected state.
///
/// Returns `DetectedState::Dead` if the pane doesn't exist or capture fails.
pub fn scan_pane(tmux: &crate::tmux::wrapper::Tmux, pane_id: &str) -> DetectedState {
    match tmux.capture_pane(pane_id, 30) {
        Ok(text) => detect_from_text(&text),
        Err(_) => DetectedState::Dead,
    }
}
```

Add to `src/lib.rs`:

```rust
pub mod detect;
```

- [ ] **Step 9: Run tests to verify they pass**

Run: `cargo test detect_ -- --nocapture`
Expected: All 10 PASS

- [ ] **Step 10: Commit**

```bash
git add src/detect/mod.rs src/lib.rs tests/detect_test.rs
git commit -m "feat: add agent state detection module with priority-ordered pattern matching"
```

### Part C: Add token_usage to TaskStatus and worker status CLI

- [ ] **Step 11: Write test for token_usage on TaskStatus**

In `tests/worker_commands_test.rs`, add:

```rust
#[test]
fn worker_status_records_token_usage() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), None, false).unwrap();
    commands::run::create_in(tmp.path(), "test-run").unwrap();

    commands::worker::status::run_in(
        tmp.path(), "001", "in_progress", Some("coding"), Some("working"), Some(12400),
    ).unwrap();

    let paths = OrchestratorPaths::new(tmp.path());
    let active = paths.active_run().unwrap();
    let content = std::fs::read_to_string(active.status_file("001")).unwrap();
    let status: TaskStatus = serde_json::from_str(&content).unwrap();
    assert_eq!(status.token_usage, Some(12400));
}
```

- [ ] **Step 12: Run test to verify it fails**

Run: `cargo test worker_status_records_token_usage -- --nocapture`
Expected: FAIL — `run_in` signature doesn't accept tokens parameter.

- [ ] **Step 13: Add token_usage field and extend worker status**

In `src/model/task.rs`, add to `TaskStatus`:

```rust
#[serde(default)]
pub token_usage: Option<u64>,
```

In `src/commands/worker/status.rs`, update the `run_in` signature to accept `tokens: Option<u64>`:

```rust
pub fn run_in(
    project_root: &Path,
    task_id: &str,
    state_str: &str,
    phase: Option<&str>,
    message: Option<&str>,
    tokens: Option<u64>,
) -> Result<()> {
```

Add after the message handling block:

```rust
if let Some(t) = tokens {
    status.token_usage = Some(t);
}
```

Update the default `TaskStatus` construction to include `token_usage: None`.

Update all callers of `run_in` to pass `None` for the new tokens parameter:
- `src/commands/worker/status.rs:run()` — pass `None` (CLI tokens arg added next)
- `src/commands/worker/done.rs:run_in()` — passes through to `status::run_in`, add `None`
- `src/commands/spawn.rs:write_initial_status()` — passes through, add `None`

In `src/main.rs`, add to `WorkerCommands::Status`:

```rust
/// Cumulative token usage
#[arg(long)]
tokens: Option<u64>,
```

And in the match arm, pass it through:

```rust
WorkerCommands::Status {
    task,
    state,
    phase,
    message,
    tokens,
} => commands::worker::status::run(&task, &state, phase.as_deref(), message.as_deref(), tokens),
```

Update `src/commands/worker/status.rs:run()` to accept and pass through tokens:

```rust
pub fn run(task: &str, state: &str, phase: Option<&str>, message: Option<&str>, tokens: Option<u64>) -> Result<()> {
    let root = super::resolve_project_root()?;
    run_in(&root, task, state, phase, message, tokens)
}
```

- [ ] **Step 14: Fix all existing test call sites**

Every existing test calling `run_in` with 5 args needs a 6th `None` arg. Search `tests/` for `status::run_in` and update each call. There will be approximately 15-20 call sites across `worker_commands_test.rs`, `happy_path.rs`, `fault_injection.rs`, `teardown_test.rs`, `status_test.rs`, and `spawn_test.rs`.

- [ ] **Step 15: Run all tests to verify they pass**

Run: `cargo test`
Expected: All pass.

- [ ] **Step 16: Commit**

```bash
git add src/model/task.rs src/commands/worker/status.rs src/commands/worker/done.rs src/commands/spawn.rs src/main.rs tests/
git commit -m "feat: add token_usage field to TaskStatus and --tokens flag to worker status"
```

---

## Task 002: Ratatui Dashboard

**Track A, depends on 001. Runs after 001 completes.**

**Files:**
- Modify: `Cargo.toml` (add ratatui, crossterm, tui-scrollview, tui-input)
- Create: `src/tui/mod.rs`
- Create: `src/tui/app.rs`
- Create: `src/tui/event.rs`
- Create: `src/tui/ui.rs`
- Create: `src/tui/widgets/mod.rs`
- Create: `src/tui/widgets/header.rs`
- Create: `src/tui/widgets/table.rs`
- Create: `src/tui/widgets/detail.rs`
- Create: `src/tui/widgets/help.rs`
- Create: `src/tui/action.rs`
- Modify: `src/lib.rs` (add `pub mod tui`)
- Modify: `src/main.rs` (replace Dashboard command)
- Delete content: `src/commands/dashboard.rs` (replace entirely)
- Create: `tests/dashboard_test.rs`

### Part A: Add dependencies and scaffold TUI module

- [ ] **Step 1: Add ratatui dependencies to Cargo.toml**

Add to `[dependencies]`:

```toml
ratatui = "0.29"
crossterm = "0.28"
```

Do NOT add tui-scrollview or tui-input yet — add them only when needed.

- [ ] **Step 2: Create TUI module scaffold**

Create `src/tui/mod.rs`:

```rust
pub mod app;
pub mod event;
pub mod ui;
pub mod widgets;
pub mod action;
```

Create `src/tui/widgets/mod.rs`:

```rust
pub mod header;
pub mod table;
pub mod detail;
pub mod help;
```

Add to `src/lib.rs`:

```rust
pub mod tui;
```

- [ ] **Step 3: Verify it compiles**

Run: `cargo check`
Expected: warnings about empty files, but no errors. Create minimal empty structs/functions in each file to satisfy the compiler.

- [ ] **Step 4: Commit**

```bash
git add Cargo.toml Cargo.lock src/lib.rs src/tui/
git commit -m "feat: scaffold ratatui TUI module with empty widgets"
```

### Part B: Event loop and App state

- [ ] **Step 5: Implement event handler**

Create `src/tui/event.rs`:

```rust
use std::sync::mpsc;
use std::thread;
use std::time::Duration;

use anyhow::Result;
use crossterm::event::{self, Event as CrosstermEvent, KeyEvent};

pub enum Event {
    Key(KeyEvent),
    Tick,
}

pub struct EventHandler {
    rx: mpsc::Receiver<Event>,
}

impl EventHandler {
    pub fn new(tick_rate: Duration) -> Self {
        let (tx, rx) = mpsc::channel();

        let tick_tx = tx.clone();
        thread::spawn(move || loop {
            if event::poll(tick_rate).unwrap_or(false) {
                if let Ok(CrosstermEvent::Key(key)) = event::read() {
                    if tick_tx.send(Event::Key(key)).is_err() {
                        break;
                    }
                }
            }
            if tick_tx.send(Event::Tick).is_err() {
                break;
            }
        });

        Self { rx }
    }

    pub fn next(&self) -> Result<Event> {
        Ok(self.rx.recv()?)
    }
}
```

- [ ] **Step 6: Implement App state**

Create `src/tui/app.rs`:

```rust
use std::collections::HashMap;
use std::path::PathBuf;
use std::time::Instant;

use anyhow::{Context, Result};

use crate::commands::status::{collect_statuses, find_stale_heartbeats};
use crate::detect::{self, DetectedState};
use crate::fs::bus::OrchestratorPaths;
use crate::model::config::OrchestratorConfig;
use crate::model::task::TaskStatus;
use crate::tmux::wrapper::Tmux;

pub enum SortOrder {
    Id,
    State,
    Elapsed,
}

pub struct App {
    pub project_root: PathBuf,
    pub run_id: String,
    pub statuses: Vec<TaskStatus>,
    pub detected: HashMap<String, DetectedState>,
    pub stale_heartbeats: Vec<String>,
    pub selected: usize,
    pub sort_order: SortOrder,
    pub show_help: bool,
    pub should_quit: bool,
    pub last_refresh: Instant,
    pub config: OrchestratorConfig,
}

impl App {
    pub fn new(project_root: PathBuf) -> Result<Self> {
        let paths = OrchestratorPaths::new(&project_root);
        let config_path = paths.config();
        let config: OrchestratorConfig = if config_path.exists() {
            let content = std::fs::read_to_string(&config_path)
                .context("failed to read config")?;
            serde_json::from_str(&content).context("failed to parse config")?
        } else {
            OrchestratorConfig::default()
        };

        let run_id = paths
            .active_run()
            .map(|r| r.run_id().to_string())
            .unwrap_or_else(|| "none".into());

        let mut app = App {
            project_root,
            run_id,
            statuses: Vec::new(),
            detected: HashMap::new(),
            stale_heartbeats: Vec::new(),
            selected: 0,
            sort_order: SortOrder::Id,
            show_help: false,
            should_quit: false,
            last_refresh: Instant::now(),
            config,
        };
        app.refresh();
        Ok(app)
    }

    pub fn refresh(&mut self) {
        self.statuses = collect_statuses(&self.project_root).unwrap_or_default();
        self.stale_heartbeats = find_stale_heartbeats(
            &self.project_root,
            self.config.heartbeat_timeout_sec,
        )
        .unwrap_or_default();

        // Passive detection for each task with a pane
        let tmux = Tmux::new();
        self.detected.clear();
        for s in &self.statuses {
            if let Some(ref pane_id) = s.pane_id {
                let state = detect::scan_pane(&tmux, pane_id);
                self.detected.insert(s.id.clone(), state);
            }
        }

        // Clamp selection
        if !self.statuses.is_empty() && self.selected >= self.statuses.len() {
            self.selected = self.statuses.len() - 1;
        }

        self.last_refresh = Instant::now();
    }

    pub fn selected_status(&self) -> Option<&TaskStatus> {
        self.statuses.get(self.selected)
    }

    pub fn next(&mut self) {
        if !self.statuses.is_empty() {
            self.selected = (self.selected + 1) % self.statuses.len();
        }
    }

    pub fn previous(&mut self) {
        if !self.statuses.is_empty() {
            self.selected = if self.selected == 0 {
                self.statuses.len() - 1
            } else {
                self.selected - 1
            };
        }
    }

    pub fn cycle_sort(&mut self) {
        self.sort_order = match self.sort_order {
            SortOrder::Id => SortOrder::State,
            SortOrder::State => SortOrder::Elapsed,
            SortOrder::Elapsed => SortOrder::Id,
        };
    }

    pub fn active_count(&self) -> usize {
        self.statuses.iter().filter(|s| {
            matches!(
                s.state,
                crate::model::task::TaskState::InProgress
                    | crate::model::task::TaskState::Spawning
                    | crate::model::task::TaskState::Ready
            )
        }).count()
    }

    pub fn completed_count(&self) -> usize {
        self.statuses.iter().filter(|s| {
            s.state == crate::model::task::TaskState::Completed
        }).count()
    }

    pub fn failed_count(&self) -> usize {
        self.statuses.iter().filter(|s| {
            matches!(
                s.state,
                crate::model::task::TaskState::Failed
                    | crate::model::task::TaskState::Aborted
            )
        }).count()
    }
}
```

- [ ] **Step 7: Verify it compiles**

Run: `cargo check`
Expected: PASS (warnings OK)

- [ ] **Step 8: Commit**

```bash
git add src/tui/app.rs src/tui/event.rs
git commit -m "feat: implement TUI app state and crossterm event handler"
```

### Part C: Widgets and render

- [ ] **Step 9: Implement header widget**

Create `src/tui/widgets/header.rs`:

```rust
use ratatui::prelude::*;
use ratatui::widgets::Paragraph;

use crate::tui::app::App;

pub fn render(app: &App, area: Rect, buf: &mut Buffer) {
    let active = app.active_count();
    let done = app.completed_count();
    let failed = app.failed_count();
    let total = app.statuses.len();
    let healthy = total.saturating_sub(app.stale_heartbeats.len());

    let text = format!(
        " agentrc  run: {}  |  {} active  {} done  {} failed  |  heartbeats: {}/{}",
        app.run_id, active, done, failed, healthy, total,
    );

    Paragraph::new(text)
        .style(Style::default().fg(Color::Cyan).add_modifier(Modifier::BOLD))
        .render(area, buf);
}
```

- [ ] **Step 10: Implement worker table widget**

Create `src/tui/widgets/table.rs`:

```rust
use chrono::Utc;
use ratatui::prelude::*;
use ratatui::widgets::{Block, Borders, Row, Table, TableState};

use crate::detect::DetectedState;
use crate::model::task::TaskState;
use crate::tui::app::App;

pub fn render(app: &App, area: Rect, buf: &mut Buffer) {
    let header = Row::new(vec!["ID", "STATE", "ACTIVITY", "TOKENS", "ELAPSED", "BRANCH"])
        .style(Style::default().add_modifier(Modifier::BOLD))
        .bottom_margin(0);

    let now = Utc::now();

    let rows: Vec<Row> = app
        .statuses
        .iter()
        .map(|s| {
            let state_style = match s.state {
                TaskState::InProgress => Style::default().fg(Color::Green),
                TaskState::Completed => Style::default().fg(Color::Blue),
                TaskState::Failed | TaskState::Aborted => Style::default().fg(Color::Red),
                TaskState::Blocked => Style::default().fg(Color::Yellow),
                _ => Style::default(),
            };

            let detected = app.detected.get(&s.id).copied().unwrap_or(DetectedState::Unknown);
            let activity = format!("{} {}", detected.icon(), detected);
            let activity_style = if detected == DetectedState::NeedsInput {
                Style::default().fg(Color::Red).add_modifier(Modifier::BOLD)
            } else {
                Style::default()
            };

            let tokens = s
                .token_usage
                .map(|t| {
                    if t >= 1000 {
                        format!("{:.1}k", t as f64 / 1000.0)
                    } else {
                        format!("{t}")
                    }
                })
                .unwrap_or_else(|| "-".into());

            let elapsed = s
                .started_at
                .map(|started| {
                    let secs = (now - started).num_seconds().max(0);
                    if secs < 60 {
                        format!("{secs}s")
                    } else if secs < 3600 {
                        format!("{}m {}s", secs / 60, secs % 60)
                    } else {
                        format!("{}h {}m", secs / 3600, (secs % 3600) / 60)
                    }
                })
                .unwrap_or_else(|| "-".into());

            let branch = if app.stale_heartbeats.contains(&s.id) {
                "WARN"
            } else if matches!(s.state, TaskState::Failed | TaskState::Aborted) {
                "FAIL"
            } else {
                "ok"
            };

            let branch_style = match branch {
                "WARN" => Style::default().fg(Color::Yellow),
                "FAIL" => Style::default().fg(Color::Red),
                _ => Style::default().fg(Color::Green),
            };

            Row::new(vec![
                Cell::from(s.id.clone()),
                Cell::from(format!("{}", s.state)).style(state_style),
                Cell::from(activity).style(activity_style),
                Cell::from(tokens),
                Cell::from(elapsed),
                Cell::from(branch.to_string()).style(branch_style),
            ])
        })
        .collect();

    let widths = [
        Constraint::Length(5),
        Constraint::Length(14),
        Constraint::Length(14),
        Constraint::Length(8),
        Constraint::Length(9),
        Constraint::Length(6),
    ];

    let table = Table::new(rows, widths)
        .header(header)
        .block(Block::default().borders(Borders::TOP | Borders::BOTTOM))
        .row_highlight_style(Style::default().add_modifier(Modifier::REVERSED));

    let mut state = TableState::default();
    state.select(Some(app.selected));

    StatefulWidget::render(table, area, buf, &mut state);
}
```

- [ ] **Step 11: Implement detail bar widget**

Create `src/tui/widgets/detail.rs`:

```rust
use chrono::Utc;
use ratatui::prelude::*;
use ratatui::widgets::Paragraph;

use crate::tui::app::App;

pub fn render(app: &App, area: Rect, buf: &mut Buffer) {
    let text = if let Some(s) = app.selected_status() {
        let pane = s.pane_id.as_deref().unwrap_or("-");
        let phase = s.phase.as_deref().unwrap_or("-");
        let branch = s.branch.as_deref().unwrap_or("-");
        let msg = s.last_message.as_deref().unwrap_or("");
        let hb_age = if app.stale_heartbeats.contains(&s.id) {
            "STALE".to_string()
        } else {
            "ok".to_string()
        };

        format!(
            " {} | {} | Pane: {} | Phase: {} | HB: {}\n Last: {}",
            s.id, branch, pane, phase, hb_age, msg,
        )
    } else {
        " No tasks".to_string()
    };

    Paragraph::new(text)
        .style(Style::default().fg(Color::Gray))
        .render(area, buf);
}
```

- [ ] **Step 12: Implement help overlay widget**

Create `src/tui/widgets/help.rs`:

```rust
use ratatui::prelude::*;
use ratatui::widgets::{Block, Borders, Clear, Paragraph};

pub fn render(area: Rect, buf: &mut Buffer) {
    let help_text = vec![
        "Keyboard Shortcuts",
        "",
        "  ↑/k, ↓/j   Navigate workers",
        "  z           Zoom into worker pane",
        "  t           Teardown selected worker",
        "  r           Respawn selected worker",
        "  a           Amend task brief",
        "  i           Integrate completed branches",
        "  c           Save checkpoint",
        "  s           Cycle sort order",
        "  ?           Toggle this help",
        "  q           Quit dashboard",
    ];

    let text = help_text.join("\n");

    // Center the overlay
    let width = 44;
    let height = help_text.len() as u16 + 2;
    let x = area.x + (area.width.saturating_sub(width)) / 2;
    let y = area.y + (area.height.saturating_sub(height)) / 2;
    let overlay = Rect::new(x, y, width.min(area.width), height.min(area.height));

    Clear.render(overlay, buf);
    Paragraph::new(text)
        .block(Block::default().title(" Help ").borders(Borders::ALL))
        .style(Style::default().fg(Color::White))
        .render(overlay, buf);
}
```

- [ ] **Step 13: Implement main render function**

Create `src/tui/ui.rs`:

```rust
use ratatui::prelude::*;

use crate::tui::app::App;
use crate::tui::widgets;

pub fn render(app: &App, frame: &mut Frame) {
    let area = frame.area();

    // Layout: header (1), table (fill), detail (2), keys (2)
    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Length(1),   // header
            Constraint::Min(4),      // table
            Constraint::Length(2),    // detail
            Constraint::Length(2),    // key hints
        ])
        .split(area);

    widgets::header::render(app, chunks[0], frame.buffer_mut());
    widgets::table::render(app, chunks[1], frame.buffer_mut());
    widgets::detail::render(app, chunks[2], frame.buffer_mut());

    // Key hints
    let keys = if app.show_help {
        " Press ? to close help"
    } else {
        " ↑↓ select  z zoom  t teardown  r respawn  a amend  i integrate  c checkpoint  s sort  ? help  q quit"
    };
    let keys_paragraph = ratatui::widgets::Paragraph::new(keys)
        .style(Style::default().fg(Color::DarkGray));
    keys_paragraph.render(chunks[3], frame.buffer_mut());

    // Help overlay on top
    if app.show_help {
        widgets::help::render(area, frame.buffer_mut());
    }
}
```

- [ ] **Step 14: Verify it compiles**

Run: `cargo check`
Expected: PASS

- [ ] **Step 15: Commit**

```bash
git add src/tui/
git commit -m "feat: implement TUI widgets — header, worker table, detail bar, help overlay"
```

### Part D: Action dispatch and main entry point

- [ ] **Step 16: Implement action dispatch**

Create `src/tui/action.rs`:

```rust
use anyhow::Result;

use crate::tui::app::App;

/// Actions that shell out need to exit the TUI first, run, then re-enter.
/// We return the command to run so the main loop can handle terminal restore/re-init.
pub enum Action {
    None,
    Shell(Vec<String>),
}

pub fn handle_key(app: &App, key: char) -> Action {
    let selected = match app.selected_status() {
        Some(s) => s,
        None => return Action::None,
    };

    match key {
        'z' => {
            // Zoom: attach to worker pane
            if let Some(ref pane_id) = selected.pane_id {
                Action::Shell(vec![
                    "tmux".into(),
                    "select-pane".into(),
                    "-t".into(),
                    pane_id.clone(),
                ])
            } else {
                Action::None
            }
        }
        't' => {
            Action::Shell(vec![
                "agentrc".into(),
                "teardown".into(),
                selected.id.clone(),
                "--force".into(),
            ])
        }
        'r' => {
            Action::Shell(vec![
                "agentrc".into(),
                "respawn".into(),
                selected.id.clone(),
            ])
        }
        'a' => {
            // Amend with a default message — in future, prompt for input
            Action::Shell(vec![
                "agentrc".into(),
                "amend".into(),
                selected.id.clone(),
                "--message".into(),
                "Brief updated by orchestrator".into(),
            ])
        }
        'i' => {
            Action::Shell(vec!["agentrc".into(), "integrate".into()])
        }
        'c' => {
            Action::Shell(vec![
                "agentrc".into(),
                "checkpoint".into(),
                "save".into(),
            ])
        }
        _ => Action::None,
    }
}
```

- [ ] **Step 17: Wire up the main dashboard command**

Replace `src/commands/dashboard.rs` entirely:

```rust
use std::io;
use std::time::{Duration, Instant};

use anyhow::{Context, Result};
use crossterm::event::{KeyCode, KeyModifiers};
use crossterm::terminal::{
    disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen,
};
use crossterm::ExecutableCommand;
use ratatui::prelude::*;

use crate::tui::action::Action;
use crate::tui::app::App;
use crate::tui::event::{Event, EventHandler};
use crate::tui::{action, ui};

pub fn run() -> Result<()> {
    let cwd = std::env::current_dir().context("cannot determine current directory")?;
    let mut app = App::new(cwd)?;

    // Setup terminal
    enable_raw_mode()?;
    io::stdout().execute(EnterAlternateScreen)?;
    let backend = CrosstermBackend::new(io::stdout());
    let mut terminal = Terminal::new(backend)?;

    let events = EventHandler::new(Duration::from_millis(250));
    let refresh_interval = Duration::from_secs(3);

    loop {
        // Draw
        terminal.draw(|frame| ui::render(&app, frame))?;

        // Handle events
        match events.next()? {
            Event::Key(key) => {
                if key.modifiers.contains(KeyModifiers::CONTROL) && key.code == KeyCode::Char('c')
                {
                    app.should_quit = true;
                }

                match key.code {
                    KeyCode::Char('q') => app.should_quit = true,
                    KeyCode::Char('?') => app.show_help = !app.show_help,
                    KeyCode::Up | KeyCode::Char('k') => app.previous(),
                    KeyCode::Down | KeyCode::Char('j') => app.next(),
                    KeyCode::Char('s') => app.cycle_sort(),
                    KeyCode::Char(c) => {
                        match action::handle_key(&app, c) {
                            Action::Shell(cmd) => {
                                // Exit TUI, run command, re-enter
                                disable_raw_mode()?;
                                io::stdout().execute(LeaveAlternateScreen)?;

                                let status = std::process::Command::new(&cmd[0])
                                    .args(&cmd[1..])
                                    .status();

                                if let Ok(s) = status {
                                    if !s.success() {
                                        eprintln!("Command exited with: {s}");
                                    }
                                }

                                // Pause for user to see output
                                eprintln!("\nPress Enter to return to dashboard...");
                                let mut buf = String::new();
                                let _ = io::stdin().read_line(&mut buf);

                                // Re-enter TUI
                                enable_raw_mode()?;
                                io::stdout().execute(EnterAlternateScreen)?;
                                terminal = Terminal::new(CrosstermBackend::new(io::stdout()))?;
                                app.refresh();
                            }
                            Action::None => {}
                        }
                    }
                    _ => {}
                }
            }
            Event::Tick => {
                if app.last_refresh.elapsed() >= refresh_interval {
                    app.refresh();
                }
            }
        }

        if app.should_quit {
            break;
        }
    }

    // Restore terminal
    disable_raw_mode()?;
    io::stdout().execute(LeaveAlternateScreen)?;

    Ok(())
}
```

- [ ] **Step 18: Update main.rs to use new dashboard**

Replace the `Dashboard` variant and its match arm. Change from:

```rust
/// Orchestrator dashboard with live status and action menu
Dashboard {
    #[command(subcommand)]
    command: DashboardCommands,
},
```

To:

```rust
/// Interactive dashboard for monitoring and managing workers
Dashboard,
```

Remove `DashboardCommands` enum entirely.

Update the match arm from:

```rust
Commands::Dashboard { command } => match command {
    DashboardCommands::Setup => commands::dashboard::setup(),
    DashboardCommands::Live => commands::dashboard::live(),
    DashboardCommands::Menu => commands::dashboard::menu(),
},
```

To:

```rust
Commands::Dashboard => commands::dashboard::run(),
```

- [ ] **Step 19: Verify it compiles and runs**

Run: `cargo build`
Expected: PASS

Run manually: `cargo run -- dashboard`
Expected: TUI appears with worker table (empty if no active run). Press `q` to quit.

- [ ] **Step 20: Commit**

```bash
git add Cargo.toml Cargo.lock src/commands/dashboard.rs src/tui/ src/main.rs
git commit -m "feat: replace dashboard with interactive ratatui TUI"
```

### Part E: Write integration test

- [ ] **Step 21: Write a test verifying App state loads correctly**

Create `tests/dashboard_test.rs`:

```rust
mod common;

use agentrc::commands;
use agentrc::tui::app::App;
use tempfile::TempDir;

#[test]
fn dashboard_app_loads_with_active_run() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), Some("cargo test"), false).unwrap();
    commands::run::create_in(tmp.path(), "test-run").unwrap();
    commands::worker::status::run_in(tmp.path(), "001", "in_progress", None, None, None).unwrap();
    commands::worker::status::run_in(tmp.path(), "002", "completed", None, None, None).unwrap();

    let app = App::new(tmp.path().to_path_buf()).unwrap();
    assert_eq!(app.statuses.len(), 2);
    assert_eq!(app.active_count(), 1);
    assert_eq!(app.completed_count(), 1);
    assert_eq!(app.failed_count(), 0);
}

#[test]
fn dashboard_app_navigation_wraps() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), Some("cargo test"), false).unwrap();
    commands::run::create_in(tmp.path(), "test-run").unwrap();
    commands::worker::status::run_in(tmp.path(), "001", "in_progress", None, None, None).unwrap();
    commands::worker::status::run_in(tmp.path(), "002", "completed", None, None, None).unwrap();

    let mut app = App::new(tmp.path().to_path_buf()).unwrap();
    assert_eq!(app.selected, 0);
    app.next();
    assert_eq!(app.selected, 1);
    app.next();
    assert_eq!(app.selected, 0); // wraps
    app.previous();
    assert_eq!(app.selected, 1); // wraps backward
}
```

- [ ] **Step 22: Run tests**

Run: `cargo test dashboard_ -- --nocapture`
Expected: All PASS

- [ ] **Step 23: Run full test suite**

Run: `cargo test`
Expected: All pass.

- [ ] **Step 24: Commit**

```bash
git add tests/dashboard_test.rs
git commit -m "test: add dashboard app state and navigation tests"
```

---

## Task 003: Checkpoint Save/Restore

**Track B, no dependencies. Parallel with 001 and 005.**

**Files:**
- Create: `src/commands/checkpoint.rs`
- Modify: `src/commands/mod.rs`
- Modify: `src/fs/run.rs`
- Modify: `src/main.rs`
- Modify: `src/commands/init.rs` (add checkpoints dir to scaffold)
- Create: `tests/checkpoint_test.rs`

### Part A: Checkpoint data model and RunPaths extension

- [ ] **Step 1: Write test for checkpoints_dir path**

In `tests/fs_test.rs`, add:

```rust
#[test]
fn run_paths_has_checkpoints_dir() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), None, false).unwrap();
    commands::run::create_in(tmp.path(), "test-run").unwrap();
    let paths = OrchestratorPaths::new(tmp.path());
    let active = paths.active_run().unwrap();
    let cp_dir = active.checkpoints_dir();
    assert!(cp_dir.ends_with("checkpoints"));
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cargo test run_paths_has_checkpoints_dir -- --nocapture`
Expected: FAIL — `checkpoints_dir` not found.

- [ ] **Step 3: Add checkpoints_dir to RunPaths**

In `src/fs/run.rs`, add:

```rust
pub fn checkpoints_dir(&self) -> PathBuf {
    self.root.join("checkpoints")
}

pub fn checkpoint_file(&self, id: &str) -> PathBuf {
    self.checkpoints_dir().join(format!("{id}.json"))
}
```

In `RunPaths::scaffold()`, add `self.checkpoints_dir()` to the dirs array.

- [ ] **Step 4: Run test to verify it passes**

Run: `cargo test run_paths_has_checkpoints_dir -- --nocapture`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/fs/run.rs tests/fs_test.rs
git commit -m "feat: add checkpoints_dir to RunPaths and scaffold"
```

### Part B: Checkpoint save

- [ ] **Step 6: Write test for checkpoint save**

Create `tests/checkpoint_test.rs`:

```rust
mod common;

use agentrc::commands;
use agentrc::fs::bus::OrchestratorPaths;
use tempfile::TempDir;

#[test]
fn checkpoint_save_creates_file() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), Some("cargo test"), false).unwrap();
    commands::run::create_in(tmp.path(), "test-run").unwrap();

    // Create a task with a branch
    let paths = OrchestratorPaths::new(tmp.path());
    let active = paths.active_run().unwrap();
    let git = agentrc::git::wrapper::Git::new(tmp.path());
    let wt_path = active.worktree_dir("001");
    git.create_worktree(&wt_path, "orc/001-test", "HEAD").unwrap();
    commands::worker::status::run_in(tmp.path(), "001", "in_progress", None, None, None).unwrap();

    // Save checkpoint
    let id = commands::checkpoint::save_in(tmp.path(), Some("test checkpoint")).unwrap();

    // Verify file exists
    let cp_file = active.checkpoint_file(&id);
    assert!(cp_file.exists());

    // Verify content
    let content = std::fs::read_to_string(&cp_file).unwrap();
    let cp: serde_json::Value = serde_json::from_str(&content).unwrap();
    assert_eq!(cp["description"], "test checkpoint");
    assert_eq!(cp["tasks"][0]["id"], "001");
    assert_eq!(cp["tasks"][0]["state"], "in_progress");
    assert_eq!(cp["tasks"][0]["branch_exists"], true);
}

#[test]
fn checkpoint_save_without_message() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), Some("cargo test"), false).unwrap();
    commands::run::create_in(tmp.path(), "test-run").unwrap();

    let id = commands::checkpoint::save_in(tmp.path(), None).unwrap();
    let paths = OrchestratorPaths::new(tmp.path());
    let active = paths.active_run().unwrap();
    assert!(active.checkpoint_file(&id).exists());
}
```

- [ ] **Step 7: Run tests to verify they fail**

Run: `cargo test checkpoint_ -- --nocapture`
Expected: FAIL — module not found.

- [ ] **Step 8: Implement checkpoint save**

Create `src/commands/checkpoint.rs`:

```rust
use std::path::Path;

use anyhow::{Context, Result};
use chrono::Utc;
use serde::{Deserialize, Serialize};

use crate::commands::spawn::{find_task_brief, load_task_brief};
use crate::commands::status::collect_statuses;
use crate::fs::bus::OrchestratorPaths;
use crate::git::wrapper::Git;
use crate::model::config::OrchestratorConfig;
use crate::model::error::AppError;
use crate::model::task::TaskState;
use crate::tmux::wrapper::Tmux;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Checkpoint {
    pub id: String,
    pub description: Option<String>,
    pub created_at: String,
    pub run_id: String,
    pub base_branch: String,
    pub base_commit: String,
    pub tasks: Vec<TaskCheckpoint>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TaskCheckpoint {
    pub id: String,
    pub slug: String,
    pub state: TaskState,
    pub branch: Option<String>,
    pub branch_exists: bool,
    pub branch_commit: Option<String>,
    pub commits_ahead: u32,
    pub pane_alive: bool,
    pub classification: String,
}

/// CLI entry for save.
pub fn save(message: Option<&str>) -> Result<()> {
    let cwd = std::env::current_dir().context("cannot determine current directory")?;
    let id = save_in(&cwd, message)?;
    println!("Checkpoint saved: {id}");
    Ok(())
}

/// Testable save entry point.
pub fn save_in(project_root: &Path, message: Option<&str>) -> Result<String> {
    let paths = OrchestratorPaths::new(project_root);
    let active = paths.active_run().ok_or(AppError::NoActiveRun)?;
    let git = Git::new(project_root);
    let tmux = Tmux::new();

    let now = Utc::now();
    let id = now.format("%Y%m%dT%H%M%S").to_string();

    let run_id = active.run_id().to_string();

    // Load config for base_branch
    let config_path = paths.config();
    let config: OrchestratorConfig = if config_path.exists() {
        let content = std::fs::read_to_string(&config_path)?;
        serde_json::from_str(&content)?
    } else {
        OrchestratorConfig::default()
    };

    let base_commit = git
        .rev_parse("HEAD")
        .unwrap_or_else(|_| "unknown".into());

    // Collect task state
    let statuses = collect_statuses(project_root)?;
    let mut tasks = Vec::new();

    for status in &statuses {
        let brief = find_task_brief(&active, &status.id)
            .ok()
            .and_then(|p| load_task_brief(&p).ok());

        let slug = brief
            .as_ref()
            .map(|b| b.slug.clone())
            .unwrap_or_else(|| "unknown".into());

        let classification = brief
            .as_ref()
            .map(|b| format!("{:?}", b.classification).to_lowercase())
            .unwrap_or_else(|| "unknown".into());

        let branch = status.branch.clone().or_else(|| {
            brief.as_ref().and_then(|b| b.branch.clone())
        });

        let (branch_exists, branch_commit, commits_ahead) = if let Some(ref br) = branch {
            let exists = git.branch_exists(br).unwrap_or(false);
            if exists {
                let commit = git.rev_parse(br).unwrap_or_default();
                let ahead = git
                    .log_branch_commits(br, &config.base_branch)
                    .map(|c| c.len() as u32)
                    .unwrap_or(0);
                (true, Some(commit), ahead)
            } else {
                (false, None, 0)
            }
        } else {
            (false, None, 0)
        };

        let pane_alive = status
            .pane_id
            .as_ref()
            .map(|p| tmux.capture_pane(p, 1).is_ok())
            .unwrap_or(false);

        tasks.push(TaskCheckpoint {
            id: status.id.clone(),
            slug,
            state: status.state.clone(),
            branch,
            branch_exists,
            branch_commit,
            commits_ahead,
            pane_alive,
            classification,
        });
    }

    let checkpoint = Checkpoint {
        id: id.clone(),
        description: message.map(String::from),
        created_at: now.to_rfc3339(),
        run_id,
        base_branch: config.base_branch.clone(),
        base_commit,
        tasks,
    };

    // Ensure checkpoints dir exists
    let cp_dir = active.checkpoints_dir();
    std::fs::create_dir_all(&cp_dir)?;

    let cp_file = active.checkpoint_file(&id);
    let json = serde_json::to_string_pretty(&checkpoint)?;
    std::fs::write(&cp_file, json)?;

    Ok(id)
}

/// CLI entry for list.
pub fn list() -> Result<()> {
    let cwd = std::env::current_dir().context("cannot determine current directory")?;
    list_in(&cwd)
}

pub fn list_in(project_root: &Path) -> Result<()> {
    let paths = OrchestratorPaths::new(project_root);
    let active = paths.active_run().ok_or(AppError::NoActiveRun)?;
    let cp_dir = active.checkpoints_dir();

    if !cp_dir.is_dir() {
        println!("No checkpoints.");
        return Ok(());
    }

    let mut entries: Vec<_> = std::fs::read_dir(&cp_dir)?
        .filter_map(|e| e.ok())
        .filter(|e| e.path().extension().and_then(|x| x.to_str()) == Some("json"))
        .collect();
    entries.sort_by_key(|e| e.file_name());

    if entries.is_empty() {
        println!("No checkpoints.");
        return Ok(());
    }

    println!("{:<20} {:<8} {}", "ID", "TASKS", "DESCRIPTION");
    println!("{}", "-".repeat(60));

    for entry in &entries {
        let content = std::fs::read_to_string(entry.path())?;
        let cp: Checkpoint = serde_json::from_str(&content)?;
        let desc = cp.description.as_deref().unwrap_or("-");
        println!("{:<20} {:<8} {}", cp.id, cp.tasks.len(), desc);
    }

    Ok(())
}

/// CLI entry for restore.
pub fn restore(id: Option<&str>, respawn: bool) -> Result<()> {
    let cwd = std::env::current_dir().context("cannot determine current directory")?;
    restore_in(&cwd, id, respawn)
}

pub fn restore_in(project_root: &Path, id: Option<&str>, _respawn: bool) -> Result<()> {
    let paths = OrchestratorPaths::new(project_root);
    let active = paths.active_run().ok_or(AppError::NoActiveRun)?;
    let git = Git::new(project_root);

    // Find checkpoint
    let cp_file = if let Some(id) = id {
        active.checkpoint_file(id)
    } else {
        // Find latest
        let cp_dir = active.checkpoints_dir();
        let mut entries: Vec<_> = std::fs::read_dir(&cp_dir)?
            .filter_map(|e| e.ok())
            .filter(|e| e.path().extension().and_then(|x| x.to_str()) == Some("json"))
            .collect();
        entries.sort_by_key(|e| e.file_name());
        entries
            .last()
            .map(|e| e.path())
            .ok_or_else(|| anyhow::anyhow!("no checkpoints found"))?
    };

    let content = std::fs::read_to_string(&cp_file)
        .with_context(|| format!("failed to read checkpoint: {}", cp_file.display()))?;
    let cp: Checkpoint = serde_json::from_str(&content)?;

    // Print recovery report
    let desc = cp.description.as_deref().unwrap_or("-");
    println!("Checkpoint: {} — \"{}\"", cp.id, desc);
    println!("Base: {} @ {}\n", cp.base_branch, cp.base_commit);
    println!(
        "{:<6} {:<14} {:<30} {}",
        "ID", "STATE", "BRANCH", "RECOVERY"
    );
    println!("{}", "-".repeat(70));

    let mut respawnable = Vec::new();

    for task in &cp.tasks {
        let branch_name = task.branch.as_deref().unwrap_or("-");

        let recovery = if let Some(ref br) = task.branch {
            let exists = git.branch_exists(br).unwrap_or(false);
            if exists {
                let ahead = git
                    .log_branch_commits(br, &cp.base_branch)
                    .map(|c| c.len())
                    .unwrap_or(0);
                if ahead > 0 {
                    if task.state == TaskState::InProgress {
                        respawnable.push(task.id.clone());
                    }
                    format!("ok ({ahead} commit{})", if ahead == 1 { "" } else { "s" })
                } else {
                    "empty (no commits)".to_string()
                }
            } else {
                "LOST (branch missing)".to_string()
            }
        } else {
            "n/a (no branch)".to_string()
        };

        println!(
            "{:<6} {:<14} {:<30} {}",
            task.id, task.state, branch_name, recovery
        );
    }

    if _respawn && !respawnable.is_empty() {
        println!("\nRespawning {} in-progress tasks...", respawnable.len());
        for task_id in &respawnable {
            println!("  respawning {task_id}...");
            // Will call respawn::run_in() once that module exists
            // For now, just print the intent
            println!("  (respawn not yet implemented — run `agentrc respawn {task_id}` manually)");
        }
    }

    Ok(())
}
```

Add to `src/commands/mod.rs`:

```rust
pub mod checkpoint;
```

Add `rev_parse` to `src/git/wrapper.rs`:

```rust
/// Get the commit hash for a ref.
pub fn rev_parse(&self, rev: &str) -> Result<String> {
    let output = Command::new("git")
        .args(["rev-parse", "--short", rev])
        .current_dir(&self.root)
        .output()
        .context("failed to run git rev-parse")?;
    if !output.status.success() {
        anyhow::bail!("git rev-parse failed for '{rev}'");
    }
    Ok(String::from_utf8_lossy(&output.stdout).trim().to_string())
}
```

- [ ] **Step 9: Wire CLI in main.rs**

Add to the `Commands` enum:

```rust
/// Save and restore run checkpoints
Checkpoint {
    #[command(subcommand)]
    command: CheckpointCommands,
},
```

Add enum:

```rust
#[derive(Subcommand)]
enum CheckpointCommands {
    /// Save a checkpoint of the current run
    Save {
        /// Description of the checkpoint
        #[arg(short, long)]
        message: Option<String>,
    },
    /// List checkpoints for the active run
    List,
    /// Restore from a checkpoint
    Restore {
        /// Checkpoint ID (latest if omitted)
        id: Option<String>,
        /// Auto-respawn in-progress tasks
        #[arg(long)]
        respawn: bool,
    },
}
```

Add match arm:

```rust
Commands::Checkpoint { command } => match command {
    CheckpointCommands::Save { message } => {
        commands::checkpoint::save(message.as_deref())
    }
    CheckpointCommands::List => commands::checkpoint::list(),
    CheckpointCommands::Restore { id, respawn } => {
        commands::checkpoint::restore(id.as_deref(), respawn)
    }
},
```

- [ ] **Step 10: Run tests to verify they pass**

Run: `cargo test checkpoint_ -- --nocapture`
Expected: All PASS

- [ ] **Step 11: Run full test suite**

Run: `cargo test`
Expected: All pass.

- [ ] **Step 12: Commit**

```bash
git add src/commands/checkpoint.rs src/commands/mod.rs src/git/wrapper.rs src/main.rs tests/checkpoint_test.rs
git commit -m "feat: add checkpoint save/restore/list commands"
```

---

## Task 004: Auto-Respawn

**Track B, depends on 003. Runs after 003 completes.**

**Files:**
- Create: `src/commands/respawn.rs`
- Modify: `src/commands/mod.rs`
- Modify: `src/main.rs`
- Create: `tests/respawn_test.rs`

- [ ] **Step 1: Write tests for respawn**

Create `tests/respawn_test.rs`:

```rust
mod common;

use agentrc::commands;
use agentrc::fs::bus::OrchestratorPaths;
use agentrc::git::wrapper::Git;
use tempfile::TempDir;

fn setup_in_progress_task(tmp: &TempDir) -> OrchestratorPaths {
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), Some("cargo test"), false).unwrap();
    commands::run::create_in(tmp.path(), "test-run").unwrap();

    let paths = OrchestratorPaths::new(tmp.path());
    let active = paths.active_run().unwrap();
    let git = Git::new(tmp.path());

    // Create worktree with a commit on the branch
    let wt_path = active.worktree_dir("001");
    git.create_worktree(&wt_path, "orc/001-test-task", "HEAD").unwrap();
    std::fs::write(wt_path.join("work.txt"), "some work").unwrap();
    let _ = std::process::Command::new("git")
        .args(["add", "work.txt"])
        .current_dir(&wt_path)
        .output();
    let _ = std::process::Command::new("git")
        .args(["commit", "-m", "work in progress"])
        .current_dir(&wt_path)
        .output();

    // Write brief
    let brief_content = format!(
        "---\nid: \"001\"\nslug: test-task\nclassification: writer\nbase_branch: master\nbranch: orc/001-test-task\npane_id: null\ndepends_on: []\ncreated_at: 2026-04-12T00:00:00Z\n---\n\n# Task 001\n"
    );
    std::fs::write(active.tasks_dir().join("001-test-task.md"), &brief_content).unwrap();

    commands::worker::status::run_in(tmp.path(), "001", "in_progress", None, None, None).unwrap();

    paths
}

#[test]
fn respawn_validates_in_progress_state() {
    let tmp = TempDir::new().unwrap();
    let _paths = setup_in_progress_task(&tmp);

    // Should succeed for in_progress task
    let result = commands::respawn::validate_respawn(tmp.path(), "001");
    assert!(result.is_ok());
}

#[test]
fn respawn_rejects_completed_task() {
    let tmp = TempDir::new().unwrap();
    let _paths = setup_in_progress_task(&tmp);
    commands::worker::status::run_in(tmp.path(), "001", "completed", None, None, None).unwrap();

    let result = commands::respawn::validate_respawn(tmp.path(), "001");
    assert!(result.is_err());
}

#[test]
fn respawn_rejects_missing_branch() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), Some("cargo test"), false).unwrap();
    commands::run::create_in(tmp.path(), "test-run").unwrap();
    commands::worker::status::run_in(tmp.path(), "001", "failed", None, None, None).unwrap();

    // No branch exists
    let result = commands::respawn::validate_respawn(tmp.path(), "001");
    assert!(result.is_err());
}

#[test]
fn respawn_generates_resume_seed() {
    let seed = commands::respawn::generate_resume_seed("001", "path/to/brief.md", "orc/001-test", 3);
    assert!(seed.contains("resuming work"));
    assert!(seed.contains("001"));
    assert!(seed.contains("3 commits"));
    assert!(seed.contains("git log"));
}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cargo test respawn_ -- --nocapture`
Expected: FAIL — module not found.

- [ ] **Step 3: Implement respawn command**

Create `src/commands/respawn.rs`:

```rust
use std::path::Path;

use anyhow::{bail, Context, Result};

use crate::commands::spawn::{find_task_brief, load_task_brief};
use crate::commands::status::collect_statuses;
use crate::fs::bus::OrchestratorPaths;
use crate::git::wrapper::Git;
use crate::model::config::OrchestratorConfig;
use crate::model::error::AppError;
use crate::model::task::{Classification, TaskState};
use crate::tmux::wrapper::Tmux;

/// CLI entry point.
pub fn run(task_id: &str) -> Result<()> {
    let cwd = std::env::current_dir().context("cannot determine current directory")?;
    run_in(&cwd, task_id)
}

/// Testable entry point.
pub fn run_in(project_root: &Path, task_id: &str) -> Result<()> {
    let (branch, commits_ahead, brief_path) = validate_respawn(project_root, task_id)?;

    let paths = OrchestratorPaths::new(project_root);
    let active = paths.active_run().ok_or(AppError::NoActiveRun)?;
    let git = Git::new(project_root);
    let tmux = Tmux::new();

    // Load config
    let config_path = paths.config();
    let config: OrchestratorConfig = {
        let content = std::fs::read_to_string(&config_path)?;
        serde_json::from_str(&content)?
    };

    // Read current status to get pane_id and redispatch_count
    let status_file = active.status_file(task_id);
    let status_content = std::fs::read_to_string(&status_file)?;
    let mut status: crate::model::task::TaskStatus = serde_json::from_str(&status_content)?;

    // Check redispatch limit
    if status.redispatch_count >= config.max_redispatch_attempts {
        bail!(
            "task {} has reached max redispatch attempts ({})",
            task_id,
            config.max_redispatch_attempts
        );
    }

    // Kill old pane if alive
    if let Some(ref pane_id) = status.pane_id {
        let _ = tmux.kill_pane(pane_id);
    }

    // Remove old worktree if exists
    let wt_path = active.worktree_dir(task_id);
    if wt_path.exists() {
        git.remove_worktree(&wt_path)
            .with_context(|| format!("failed to remove old worktree for {task_id}"))?;
    }

    // Re-create worktree from EXISTING branch (preserves commits)
    git.create_worktree_from_branch(&wt_path, &branch)
        .with_context(|| format!("failed to create worktree from branch {branch}"))?;

    // Find or create workers window
    let window_name = "workers";
    let windows = tmux.list_windows().unwrap_or_default();
    let pane_id = if !windows.iter().any(|w| w == window_name) {
        tmux.new_window_with_pane_id(window_name)?
    } else {
        tmux.split_window(window_name)?
    };

    let _ = tmux.select_layout_tiled(window_name);

    // Export project root, cd to worktree, launch heartbeat
    tmux.send_keys(
        &pane_id,
        &format!("export AGENTRC_PROJECT_ROOT={}", project_root.display()),
    )?;
    tmux.send_keys(&pane_id, &format!("cd {}", wt_path.display()))?;
    tmux.send_keys(
        &pane_id,
        &format!(
            "agentrc worker heartbeat --task {} --interval {} &",
            task_id, config.heartbeat_interval_sec
        ),
    )?;

    // Build and send resume seed
    let relative_brief = brief_path
        .strip_prefix(project_root)
        .unwrap_or(&brief_path)
        .to_string_lossy();
    let seed = generate_resume_seed(task_id, &relative_brief, &branch, commits_ahead);
    let escaped = seed.replace('\'', "'\\''");
    let mut claude_cmd = format!("claude --dangerously-skip-permissions '{escaped}'");
    for arg in &config.worker_claude_args {
        claude_cmd.push(' ');
        claude_cmd.push_str(arg);
    }
    tmux.send_keys(&pane_id, &claude_cmd)?;

    // Update status
    status.state = TaskState::Spawning;
    status.pane_id = Some(pane_id.clone());
    status.redispatch_count += 1;
    let json = serde_json::to_string_pretty(&status)?;
    std::fs::write(&status_file, json)?;

    // Update brief with new pane_id
    let brief_content = std::fs::read_to_string(&brief_path)?;
    if let Ok(updated) =
        crate::fs::frontmatter::update_field(&brief_content, "pane_id", &pane_id)
    {
        std::fs::write(&brief_path, updated)?;
    }

    println!("Respawned task {task_id} in pane {pane_id} (attempt {})", status.redispatch_count);
    Ok(())
}

/// Validate that a task can be respawned. Returns (branch_name, commits_ahead, brief_path).
pub fn validate_respawn(
    project_root: &Path,
    task_id: &str,
) -> Result<(String, u32, std::path::PathBuf)> {
    let paths = OrchestratorPaths::new(project_root);
    let active = paths.active_run().ok_or(AppError::NoActiveRun)?;

    // Check status exists and state is respawnable
    let status_file = active.status_file(task_id);
    if !status_file.exists() {
        bail!("no status file for task {task_id}");
    }
    let content = std::fs::read_to_string(&status_file)?;
    let status: crate::model::task::TaskStatus = serde_json::from_str(&content)?;

    if !matches!(
        status.state,
        TaskState::InProgress | TaskState::Failed | TaskState::Aborted
    ) {
        bail!(
            "cannot respawn task {} in state {} (must be in_progress, failed, or aborted)",
            task_id,
            status.state
        );
    }

    // Find brief to get branch name
    let brief_path = find_task_brief(&active, task_id)?;
    let brief = load_task_brief(&brief_path)?;

    let branch = brief
        .branch
        .or(status.branch)
        .unwrap_or_else(|| format!("orc/{}-{}", brief.id, brief.slug));

    // Check branch exists
    let git = Git::new(project_root);
    if !git.branch_exists(&branch).unwrap_or(false) {
        bail!("branch '{branch}' does not exist — nothing to resume from");
    }

    // Load config for base_branch
    let config_path = paths.config();
    let config: OrchestratorConfig = if config_path.exists() {
        let c = std::fs::read_to_string(&config_path)?;
        serde_json::from_str(&c)?
    } else {
        OrchestratorConfig::default()
    };

    let commits_ahead = git
        .log_branch_commits(&branch, &config.base_branch)
        .map(|c| c.len() as u32)
        .unwrap_or(0);

    Ok((branch, commits_ahead, brief_path))
}

/// Generate the resume seed prompt for a respawned worker.
pub fn generate_resume_seed(
    task_id: &str,
    brief_path: &str,
    branch: &str,
    commits_ahead: u32,
) -> String {
    format!(
        "You are worker {task_id} resuming work. Your task brief is at `{brief_path}`. \
         Your branch {branch} has {commits_ahead} commits already. Read the brief \
         AND review your existing commits (git log --oneline) to understand \
         where the previous session stopped. Continue from there. \
         Use `agentrc worker status --task {task_id} --state in_progress` to signal \
         you've resumed. Use `agentrc worker done --task {task_id}` when finished."
    )
}
```

Add `create_worktree_from_branch` to `src/git/wrapper.rs`:

```rust
/// Create a worktree checked out on an existing branch.
pub fn create_worktree_from_branch(&self, path: &Path, branch: &str) -> Result<()> {
    let output = Command::new("git")
        .args([
            "worktree",
            "add",
            &path.to_string_lossy(),
            branch,
        ])
        .current_dir(&self.root)
        .output()
        .context("failed to run git worktree add")?;
    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        anyhow::bail!("git worktree add failed: {}", stderr.trim());
    }
    Ok(())
}
```

Add to `src/commands/mod.rs`:

```rust
pub mod respawn;
```

- [ ] **Step 4: Wire CLI in main.rs**

Add to `Commands` enum:

```rust
/// Respawn a dead or failed worker from its existing branch
Respawn {
    /// Task identifier to respawn
    task_id: String,
},
```

Add match arm:

```rust
Commands::Respawn { task_id } => commands::respawn::run(&task_id),
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cargo test respawn_ -- --nocapture`
Expected: All 4 PASS

- [ ] **Step 6: Run full test suite**

Run: `cargo test`
Expected: All pass.

- [ ] **Step 7: Commit**

```bash
git add src/commands/respawn.rs src/commands/mod.rs src/git/wrapper.rs src/main.rs tests/respawn_test.rs
git commit -m "feat: add respawn command — re-launch workers from existing branches"
```

### Part B: Wire respawn into checkpoint restore

- [ ] **Step 8: Update checkpoint restore to call respawn**

In `src/commands/checkpoint.rs`, replace the placeholder respawn print with:

```rust
if _respawn && !respawnable.is_empty() {
    println!("\nRespawning {} in-progress tasks...", respawnable.len());
    for task_id in &respawnable {
        match crate::commands::respawn::run_in(project_root, task_id) {
            Ok(()) => {}
            Err(e) => eprintln!("  failed to respawn {task_id}: {e}"),
        }
    }
}
```

- [ ] **Step 9: Run full test suite**

Run: `cargo test`
Expected: All pass.

- [ ] **Step 10: Commit**

```bash
git add src/commands/checkpoint.rs
git commit -m "feat: wire respawn into checkpoint restore --respawn"
```

---

## Task 005: README

**Standalone, no dependencies. Parallel with all other tasks.**

**Files:**
- Create: `README.md`

- [ ] **Step 1: Write README.md**

Create `README.md` at project root. Content should include:

1. Title: `# agentrc` with one-liner description
2. What it does: 4-5 bullet points covering parallel workers, worktree isolation, TDD enforcement, interactive dashboard, checkpoint/resume
3. Quick start: step-by-step from install to first run
4. Command reference: grouped table (orchestrator, worker, run management, dashboard/monitoring)
5. Architecture: brief two-layer explanation (skill + binary) with pointer to full spec
6. Configuration: `.orchestrator/config.json` fields with defaults
7. Requirements: Rust, tmux, claude CLI, git
8. Screenshots placeholder: section with note about screenshots coming soon

Keep the total under 300 lines. No badges, no contributing guide, no changelog. Practical reference for team members.

- [ ] **Step 2: Verify it renders correctly**

Run: `head -50 README.md` to sanity check formatting.

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: add project README with features, install, and command reference"
```
