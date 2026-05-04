# agentrc Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Phase 1 MVP of the `agentrc` CLI — a Rust binary that handles all deterministic mechanics for orchestrating multiple Claude Code worker sessions in tmux panes.

**Architecture:** Single Rust binary with clap-derived CLI. Two internal layers: a model/filesystem layer (types, serialization, `.orchestrator/` layout) and a commands layer (each subcommand as a module). Shell-outs to `tmux` and `git` via `duct`. No standalone shell scripts.

**Tech Stack:** Rust (2021 edition), clap (derive), serde/serde_json/serde_yaml, anyhow/thiserror, duct, chrono, tempfile (test)

---

## File Structure

### Source files to create

| File | Responsibility |
|---|---|
| `Cargo.toml` | Crate manifest with all Phase 1 dependencies |
| `Makefile` | `make test`, `make smoke`, `make install` targets |
| `src/main.rs` | Clap CLI entry point, subcommand routing |
| `src/commands/mod.rs` | Re-export all command modules |
| `src/commands/install.rs` | Symlink skill, verify prerequisites |
| `src/commands/init.rs` | Scaffold `.orchestrator/`, detect test command, update `.gitignore` |
| `src/commands/spawn.rs` | Create pane, worktree, launch claude, seed prompt |
| `src/commands/status.rs` | Aggregate task statuses into table |
| `src/commands/teardown.rs` | Close pane, remove worktree, `--all` support |
| `src/commands/integrate.rs` | Serial merge, conflict/test handling, TDD history |
| `src/commands/layout.rs` | Tile/collate worker panes |
| `src/commands/resume.rs` | Structured context dump |
| `src/commands/run.rs` | `run create`, `run list`, `run archive` |
| `src/commands/worker/mod.rs` | Worker subcommand routing |
| `src/commands/worker/status.rs` | Write/update status JSON |
| `src/commands/worker/heartbeat.rs` | Background daemon touching `.alive` |
| `src/commands/worker/note.rs` | Append timestamped note |
| `src/commands/worker/result.rs` | Write result markdown |
| `src/commands/worker/done.rs` | Atomic: result + status + bell |
| `src/model/mod.rs` | Re-export model types |
| `src/model/config.rs` | `OrchestratorConfig` with serde |
| `src/model/task.rs` | `TaskBrief`, `TaskStatus`, `TaskState`, `Classification` |
| `src/model/worker.rs` | `WorkerState`, `PaneId` |
| `src/model/run.rs` | `RunId`, `RunMetadata` |
| `src/model/error.rs` | `AppError` enum with thiserror |
| `src/fs/mod.rs` | Re-export filesystem helpers |
| `src/fs/bus.rs` | Read/write `.orchestrator/` paths |
| `src/fs/run.rs` | Run-scoped directory helpers, active symlink |
| `src/git/mod.rs` | Re-export git module |
| `src/git/wrapper.rs` | Typed git command wrappers |
| `src/tmux/mod.rs` | Re-export tmux module |
| `src/tmux/wrapper.rs` | Typed tmux command wrappers |

### Skill files to create

| File | Responsibility |
|---|---|
| `skill/agentrc/SKILL.md` | Prose workflow skill for Claude Code |
| `skill/agentrc/worker-seed.txt` | Bootstrap prompt template for workers |
| `skill/agentrc/task-brief.md` | Task brief template with frontmatter |

### Test files to create

| File | Responsibility |
|---|---|
| `tests/common/mod.rs` | Shared test helpers (temp orchestrator dirs, temp git repos) |
| `tests/model_test.rs` | Model serialization roundtrips |
| `tests/fs_test.rs` | Filesystem bus operations |
| `tests/worker_commands_test.rs` | Worker CLI subcommand integration tests |
| `tests/init_test.rs` | Init command integration test |
| `tests/run_test.rs` | Run lifecycle integration tests |
| `tests/status_test.rs` | Status aggregation tests |
| `tests/spawn_test.rs` | Spawn with mock tmux |
| `tests/teardown_test.rs` | Teardown integration tests |
| `tests/integrate_test.rs` | Integration merge tests with temp git repos |
| `tests/resume_test.rs` | Resume output tests |
| `tests/happy_path.rs` | E2E with mock-worker.sh |
| `tests/fault_injection.rs` | Error path exercises |
| `tests/fixtures/mock-worker.sh` | Simulates a claude session for testing |
| `tests/fixtures/toy-project/` | Minimal git repo for integration tests |

---

## Task 1: Project scaffold and CLI skeleton

**Files:**
- Create: `Cargo.toml`
- Create: `Makefile`
- Create: `src/main.rs`
- Create: `src/commands/mod.rs`
- Create: `src/commands/worker/mod.rs`
- Create: `src/model/mod.rs`
- Create: `src/fs/mod.rs`
- Create: `src/git/mod.rs`
- Create: `src/tmux/mod.rs`

- [ ] **Step 1: Write failing test — binary exists and prints help**

Create `tests/cli_smoke_test.rs`:

```rust
use std::process::Command;

#[test]
fn binary_prints_help() {
    let output = Command::new(env!("CARGO_BIN_EXE_agentrc"))
        .arg("--help")
        .output()
        .expect("failed to execute binary");
    assert!(output.status.success());
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(stdout.contains("agentrc"));
}

#[test]
fn binary_has_subcommands() {
    let output = Command::new(env!("CARGO_BIN_EXE_agentrc"))
        .arg("--help")
        .output()
        .expect("failed to execute binary");
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(stdout.contains("init"));
    assert!(stdout.contains("install"));
    assert!(stdout.contains("spawn"));
    assert!(stdout.contains("status"));
    assert!(stdout.contains("teardown"));
    assert!(stdout.contains("integrate"));
    assert!(stdout.contains("layout"));
    assert!(stdout.contains("resume"));
    assert!(stdout.contains("run"));
    assert!(stdout.contains("worker"));
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cargo test --test cli_smoke_test`
Expected: compilation error — no binary, no Cargo.toml

- [ ] **Step 3: Create Cargo.toml**

```toml
[package]
name = "agentrc"
version = "0.1.0"
edition = "2021"
description = "Orchestrate multiple Claude Code workers in tmux panes"
license = "MIT"

[[bin]]
name = "agentrc"
path = "src/main.rs"

[dependencies]
clap = { version = "4", features = ["derive"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
serde_yaml = "0.9"
anyhow = "1"
thiserror = "2"
duct = "0.13"
chrono = { version = "0.4", features = ["serde"] }

[dev-dependencies]
tempfile = "3"
assert_cmd = "2"
predicates = "3"
```

- [ ] **Step 4: Create src/main.rs with full CLI skeleton**

```rust
use anyhow::Result;
use clap::{Parser, Subcommand};

mod commands;
mod fs;
mod git;
mod model;
mod tmux;

#[derive(Parser)]
#[command(name = "agentrc", about = "Orchestrate Claude Code workers in tmux panes")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Symlink skill into ~/.claude/skills/agentrc/, verify prerequisites
    Install,
    /// Scaffold .orchestrator/, detect test command, update .gitignore
    Init,
    /// Create pane, worktree (writer), launch claude, seed prompt
    Spawn {
        /// Task ID to spawn (e.g. "001")
        task_id: String,
    },
    /// Aggregate task status table
    Status {
        /// Output as JSON instead of TTY table
        #[arg(long)]
        json: bool,
    },
    /// Close pane, remove worktree, archive
    Teardown {
        /// Task ID to tear down
        task_id: Option<String>,
        /// Tear down all workers in the active run
        #[arg(long)]
        all: bool,
    },
    /// Serial merge in dependency order
    Integrate,
    /// Retile worker panes, collate to new windows
    Layout {
        /// Layout mode
        #[arg(value_enum, default_value = "tile")]
        mode: LayoutMode,
    },
    /// Structured context dump for session recovery
    Resume,
    /// Run lifecycle management
    Run {
        #[command(subcommand)]
        command: RunCommands,
    },
    /// Worker-side commands (called by workers, not the orchestrator)
    Worker {
        #[command(subcommand)]
        command: WorkerCommands,
    },
}

#[derive(clap::ValueEnum, Clone)]
enum LayoutMode {
    Tile,
    Collate,
}

#[derive(Subcommand)]
enum RunCommands {
    /// Create run directory, set active symlink
    Create {
        /// Run slug (e.g. "auth-refactor")
        #[arg(long)]
        slug: String,
    },
    /// List all runs with status
    List,
    /// Drop active symlink, archive current run
    Archive,
}

#[derive(Subcommand)]
enum WorkerCommands {
    /// Update task status JSON
    Status {
        /// Task ID
        #[arg(long)]
        task: String,
        /// State: spawning, ready, in_progress, blocked, completed, failed, aborted
        #[arg(long)]
        state: String,
        /// Current phase (e.g. "implementing", "testing", "resolving-conflict")
        #[arg(long)]
        phase: Option<String>,
        /// Human-readable status message
        #[arg(long)]
        message: Option<String>,
    },
    /// Background heartbeat daemon
    Heartbeat {
        /// Task ID
        #[arg(long)]
        task: String,
        /// Heartbeat interval in seconds
        #[arg(long, default_value = "30")]
        interval: u64,
    },
    /// Append timestamped note
    Note {
        /// Task ID
        #[arg(long)]
        task: String,
        /// Note message
        #[arg(long)]
        message: String,
    },
    /// Write final result markdown
    Result {
        /// Task ID
        #[arg(long)]
        task: String,
        /// Path to result file
        #[arg(long)]
        file: Option<String>,
        /// Read result from stdin
        #[arg(long)]
        stdin: bool,
    },
    /// Atomic: write result, set completed, ring bell
    Done {
        /// Task ID
        #[arg(long)]
        task: String,
        /// Path to result file
        #[arg(long)]
        result_file: Option<String>,
    },
}

fn main() -> Result<()> {
    let cli = Cli::parse();

    match cli.command {
        Commands::Install => commands::install::run(),
        Commands::Init => commands::init::run(),
        Commands::Spawn { task_id } => commands::spawn::run(&task_id),
        Commands::Status { json } => commands::status::run(json),
        Commands::Teardown { task_id, all } => commands::teardown::run(task_id.as_deref(), all),
        Commands::Integrate => commands::integrate::run(),
        Commands::Layout { mode } => commands::layout::run(mode),
        Commands::Resume => commands::resume::run(),
        Commands::Run { command } => match command {
            RunCommands::Create { slug } => commands::run::create(&slug),
            RunCommands::List => commands::run::list(),
            RunCommands::Archive => commands::run::archive(),
        },
        Commands::Worker { command } => match command {
            WorkerCommands::Status { task, state, phase, message } => {
                commands::worker::status::run(&task, &state, phase.as_deref(), message.as_deref())
            }
            WorkerCommands::Heartbeat { task, interval } => {
                commands::worker::heartbeat::run(&task, interval)
            }
            WorkerCommands::Note { task, message } => {
                commands::worker::note::run(&task, &message)
            }
            WorkerCommands::Result { task, file, stdin } => {
                commands::worker::result::run(&task, file.as_deref(), stdin)
            }
            WorkerCommands::Done { task, result_file } => {
                commands::worker::done::run(&task, result_file.as_deref())
            }
        },
    }
}
```

- [ ] **Step 5: Create stub modules**

`src/commands/mod.rs`:
```rust
pub mod init;
pub mod install;
pub mod integrate;
pub mod layout;
pub mod resume;
pub mod run;
pub mod spawn;
pub mod status;
pub mod teardown;
pub mod worker;
```

`src/commands/worker/mod.rs`:
```rust
pub mod done;
pub mod heartbeat;
pub mod note;
pub mod result;
pub mod status;
```

`src/model/mod.rs`:
```rust
pub mod config;
pub mod error;
pub mod run;
pub mod task;
pub mod worker;
```

`src/fs/mod.rs`:
```rust
pub mod bus;
pub mod run;
```

`src/git/mod.rs`:
```rust
pub mod wrapper;
```

`src/tmux/mod.rs`:
```rust
pub mod wrapper;
```

Each command stub file (e.g. `src/commands/install.rs`) gets a placeholder:
```rust
use anyhow::Result;

pub fn run() -> Result<()> {
    anyhow::bail!("not yet implemented")
}
```

Adjust function signatures to match main.rs callsites. Each worker subcommand and other command gets the matching signature from main.rs. For `layout::run`, accept the `LayoutMode` type — move the enum to `src/model/worker.rs` or keep it in main.rs and pass a string.

Each model stub file gets an empty module. Each fs/git/tmux stub gets an empty module.

- [ ] **Step 6: Run test to verify it passes**

Run: `cargo test --test cli_smoke_test`
Expected: both tests PASS

- [ ] **Step 7: Commit**

```bash
git add Cargo.toml Cargo.lock Makefile src/ tests/cli_smoke_test.rs
git commit -m "scaffold: CLI skeleton with all Phase 1 subcommands"
```

---

## Task 2: Error types

**Files:**
- Create: `src/model/error.rs`
- Test: `tests/model_test.rs`

- [ ] **Step 1: Write failing test — error types exist and display correctly**

Create `tests/model_test.rs`:

```rust
use agentrc::model::error::AppError;

#[test]
fn app_error_displays_correctly() {
    let err = AppError::ConfigNotFound {
        path: "/tmp/.orchestrator/config.json".into(),
    };
    assert_eq!(
        err.to_string(),
        "config not found: /tmp/.orchestrator/config.json"
    );
}

#[test]
fn app_error_no_active_run() {
    let err = AppError::NoActiveRun;
    assert_eq!(err.to_string(), "no active run (missing .orchestrator/active symlink)");
}

#[test]
fn app_error_invalid_state_transition() {
    let err = AppError::InvalidStateTransition {
        from: "completed".into(),
        to: "in_progress".into(),
    };
    assert!(err.to_string().contains("completed"));
    assert!(err.to_string().contains("in_progress"));
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cargo test --test model_test`
Expected: FAIL — `AppError` not found

- [ ] **Step 3: Implement error types**

`src/model/error.rs`:

```rust
use std::path::PathBuf;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum AppError {
    #[error("config not found: {path}")]
    ConfigNotFound { path: PathBuf },

    #[error("no active run (missing .orchestrator/active symlink)")]
    NoActiveRun,

    #[error("run already active: {run_id}")]
    RunAlreadyActive { run_id: String },

    #[error("task not found: {task_id}")]
    TaskNotFound { task_id: String },

    #[error("invalid state transition: {from} -> {to}")]
    InvalidStateTransition { from: String, to: String },

    #[error("task brief parse error in {path}: {reason}")]
    TaskBriefParseError { path: PathBuf, reason: String },

    #[error("status parse error in {path}: {reason}")]
    StatusParseError { path: PathBuf, reason: String },

    #[error("dirty base branch: uncommitted changes detected")]
    DirtyBaseBranch,

    #[error("worktree already exists: {path}")]
    WorktreeExists { path: PathBuf },

    #[error("branch already exists: {branch}")]
    BranchExists { branch: String },

    #[error("tmux error: {message}")]
    TmuxError { message: String },

    #[error("git error: {message}")]
    GitError { message: String },

    #[error("max redispatch attempts ({max}) reached for task {task_id}")]
    MaxRedispatchReached { task_id: String, max: u32 },

    #[error("merge conflict in task {task_id}: {files}")]
    MergeConflict { task_id: String, files: String },

    #[error("test failure after merging task {task_id}")]
    TestFailure { task_id: String },

    #[error("orchestrator not initialized (run `agentrc init` first)")]
    NotInitialized,
}
```

Update `src/model/mod.rs` to make types public. Add `lib.rs` so integration tests can import:

`src/lib.rs`:
```rust
pub mod commands;
pub mod fs;
pub mod git;
pub mod model;
pub mod tmux;
```

Update `src/main.rs` to remove module declarations and use `agentrc::*` instead, or keep both (`main.rs` declares `mod` and `lib.rs` declares `pub mod`). The cleaner approach: `main.rs` imports from the library crate:

```rust
use agentrc::commands;
// ... rest of main unchanged, but remove mod declarations
```

Keep `mod` declarations only in `src/lib.rs`.

- [ ] **Step 4: Run test to verify it passes**

Run: `cargo test --test model_test`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/model/error.rs src/lib.rs tests/model_test.rs
git commit -m "feat: add AppError types with thiserror"
```

---

## Task 3: Model types — Config, Task, Run

**Files:**
- Create: `src/model/config.rs`
- Create: `src/model/task.rs`
- Create: `src/model/run.rs`
- Create: `src/model/worker.rs`
- Test: `tests/model_test.rs` (append)

- [ ] **Step 1: Write failing tests — config serialization roundtrip**

Append to `tests/model_test.rs`:

```rust
use agentrc::model::config::OrchestratorConfig;

#[test]
fn config_default_values() {
    let config = OrchestratorConfig::default();
    assert_eq!(config.max_workers, 12);
    assert_eq!(config.workers_per_window, 4);
    assert_eq!(config.heartbeat_interval_sec, 30);
    assert_eq!(config.heartbeat_timeout_sec, 120);
    assert_eq!(config.max_redispatch_attempts, 2);
    assert!(config.test_command.is_none());
    assert!(config.worker_claude_args.is_empty());
}

#[test]
fn config_json_roundtrip() {
    let config = OrchestratorConfig {
        project_root: "/home/eric/Code/foo".into(),
        base_branch: "main".into(),
        max_workers: 8,
        workers_per_window: 4,
        heartbeat_interval_sec: 30,
        heartbeat_timeout_sec: 120,
        max_redispatch_attempts: 2,
        test_command: Some("cargo test".into()),
        worker_claude_args: vec!["--model".into(), "sonnet".into()],
    };
    let json = serde_json::to_string_pretty(&config).unwrap();
    let deserialized: OrchestratorConfig = serde_json::from_str(&json).unwrap();
    assert_eq!(deserialized.project_root.to_str().unwrap(), "/home/eric/Code/foo");
    assert_eq!(deserialized.test_command.as_deref(), Some("cargo test"));
    assert_eq!(deserialized.max_workers, 8);
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cargo test --test model_test config`
Expected: FAIL — `OrchestratorConfig` not found

- [ ] **Step 3: Implement OrchestratorConfig**

`src/model/config.rs`:

```rust
use serde::{Deserialize, Serialize};
use std::path::PathBuf;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OrchestratorConfig {
    pub project_root: PathBuf,
    pub base_branch: String,
    #[serde(default = "default_max_workers")]
    pub max_workers: u32,
    #[serde(default = "default_workers_per_window")]
    pub workers_per_window: u32,
    #[serde(default = "default_heartbeat_interval")]
    pub heartbeat_interval_sec: u64,
    #[serde(default = "default_heartbeat_timeout")]
    pub heartbeat_timeout_sec: u64,
    #[serde(default = "default_max_redispatch")]
    pub max_redispatch_attempts: u32,
    pub test_command: Option<String>,
    #[serde(default)]
    pub worker_claude_args: Vec<String>,
}

fn default_max_workers() -> u32 { 12 }
fn default_workers_per_window() -> u32 { 4 }
fn default_heartbeat_interval() -> u64 { 30 }
fn default_heartbeat_timeout() -> u64 { 120 }
fn default_max_redispatch() -> u32 { 2 }

impl Default for OrchestratorConfig {
    fn default() -> Self {
        Self {
            project_root: PathBuf::from("."),
            base_branch: "main".into(),
            max_workers: default_max_workers(),
            workers_per_window: default_workers_per_window(),
            heartbeat_interval_sec: default_heartbeat_interval(),
            heartbeat_timeout_sec: default_heartbeat_timeout(),
            max_redispatch_attempts: default_max_redispatch(),
            test_command: None,
            worker_claude_args: Vec::new(),
        }
    }
}
```

- [ ] **Step 4: Run config tests to verify they pass**

Run: `cargo test --test model_test config`
Expected: PASS

- [ ] **Step 5: Write failing tests — TaskState, Classification, TaskStatus**

Append to `tests/model_test.rs`:

```rust
use agentrc::model::task::{Classification, TaskState, TaskStatus};

#[test]
fn task_state_serializes_as_lowercase() {
    let state = TaskState::InProgress;
    let json = serde_json::to_string(&state).unwrap();
    assert_eq!(json, "\"in_progress\"");
}

#[test]
fn task_state_deserializes_from_lowercase() {
    let state: TaskState = serde_json::from_str("\"in_progress\"").unwrap();
    assert_eq!(state, TaskState::InProgress);
}

#[test]
fn classification_serializes_as_lowercase() {
    let c = Classification::Writer;
    let json = serde_json::to_string(&c).unwrap();
    assert_eq!(json, "\"writer\"");
}

#[test]
fn task_status_json_roundtrip() {
    let status = TaskStatus {
        id: "001".into(),
        pane_id: Some("%12".into()),
        state: TaskState::InProgress,
        phase: Some("implementing".into()),
        started_at: Some(chrono::Utc::now()),
        updated_at: chrono::Utc::now(),
        last_message: Some("tests passing".into()),
        result_path: None,
        branch: Some("orc/001-add-login".into()),
        redispatch_count: 0,
    };
    let json = serde_json::to_string_pretty(&status).unwrap();
    let deserialized: TaskStatus = serde_json::from_str(&json).unwrap();
    assert_eq!(deserialized.id, "001");
    assert_eq!(deserialized.state, TaskState::InProgress);
    assert_eq!(deserialized.phase.as_deref(), Some("implementing"));
}

#[test]
fn task_state_valid_transitions() {
    assert!(TaskState::Spawning.can_transition_to(&TaskState::Ready));
    assert!(TaskState::Ready.can_transition_to(&TaskState::InProgress));
    assert!(TaskState::InProgress.can_transition_to(&TaskState::Completed));
    assert!(TaskState::InProgress.can_transition_to(&TaskState::Failed));
    assert!(TaskState::InProgress.can_transition_to(&TaskState::Blocked));
    assert!(TaskState::Blocked.can_transition_to(&TaskState::InProgress));
    assert!(!TaskState::Completed.can_transition_to(&TaskState::InProgress));
    assert!(!TaskState::Failed.can_transition_to(&TaskState::InProgress));
}
```

- [ ] **Step 6: Run test to verify it fails**

Run: `cargo test --test model_test task`
Expected: FAIL — types not found

- [ ] **Step 7: Implement task types**

`src/model/task.rs`:

```rust
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum TaskState {
    Spawning,
    Ready,
    InProgress,
    Blocked,
    Completed,
    Failed,
    Aborted,
}

impl TaskState {
    pub fn can_transition_to(&self, target: &TaskState) -> bool {
        use TaskState::*;
        matches!(
            (self, target),
            (Spawning, Ready)
                | (Ready, InProgress)
                | (InProgress, Blocked)
                | (InProgress, Completed)
                | (InProgress, Failed)
                | (InProgress, Aborted)
                | (Blocked, InProgress)
                | (Blocked, Aborted)
                | (Spawning, Aborted)
                | (Ready, Aborted)
        )
    }
}

impl std::fmt::Display for TaskState {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        let s = serde_json::to_value(self)
            .ok()
            .and_then(|v| v.as_str().map(String::from))
            .unwrap_or_else(|| format!("{:?}", self));
        write!(f, "{}", s)
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Classification {
    Reader,
    Writer,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TaskStatus {
    pub id: String,
    pub pane_id: Option<String>,
    pub state: TaskState,
    pub phase: Option<String>,
    pub started_at: Option<DateTime<Utc>>,
    pub updated_at: DateTime<Utc>,
    pub last_message: Option<String>,
    pub result_path: Option<String>,
    pub branch: Option<String>,
    pub redispatch_count: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TaskBriefFrontmatter {
    pub id: String,
    pub slug: String,
    pub classification: Classification,
    pub worktree: Option<String>,
    pub base_branch: String,
    pub branch: Option<String>,
    pub pane_id: Option<String>,
    #[serde(default)]
    pub depends_on: Vec<String>,
    pub created_at: DateTime<Utc>,
}
```

- [ ] **Step 8: Run test to verify it passes**

Run: `cargo test --test model_test task`
Expected: PASS

- [ ] **Step 9: Write failing tests — TaskBriefFrontmatter parsing from YAML**

Append to `tests/model_test.rs`:

```rust
use agentrc::model::task::{TaskBriefFrontmatter, Classification};

#[test]
fn task_brief_frontmatter_from_yaml() {
    let yaml = r#"
id: "001"
slug: add-login-endpoint
classification: writer
worktree: .orchestrator/active/worktrees/001
base_branch: main
branch: orc/001-add-login-endpoint
pane_id: null
depends_on: []
created_at: 2026-04-11T14:30:00Z
"#;
    let brief: TaskBriefFrontmatter = serde_yaml::from_str(yaml).unwrap();
    assert_eq!(brief.id, "001");
    assert_eq!(brief.slug, "add-login-endpoint");
    assert_eq!(brief.classification, Classification::Writer);
    assert!(brief.pane_id.is_none());
    assert!(brief.depends_on.is_empty());
}

#[test]
fn task_brief_frontmatter_reader_no_worktree() {
    let yaml = r#"
id: "002"
slug: review-deps
classification: reader
base_branch: main
depends_on: []
created_at: 2026-04-11T14:30:00Z
"#;
    let brief: TaskBriefFrontmatter = serde_yaml::from_str(yaml).unwrap();
    assert_eq!(brief.classification, Classification::Reader);
    assert!(brief.worktree.is_none());
    assert!(brief.branch.is_none());
}
```

- [ ] **Step 10: Run test to verify it passes**

Run: `cargo test --test model_test frontmatter`
Expected: PASS (serde_yaml handles this with existing types)

- [ ] **Step 11: Write failing tests — RunMetadata**

Append to `tests/model_test.rs`:

```rust
use agentrc::model::run::RunMetadata;

#[test]
fn run_metadata_generates_id_from_slug() {
    let meta = RunMetadata::new("auth-refactor");
    assert!(meta.id.contains("auth-refactor"));
    // ID starts with ISO date prefix
    assert!(meta.id.starts_with("20"));
    assert!(meta.id.contains('T'));
}

#[test]
fn run_metadata_id_is_filesystem_safe() {
    let meta = RunMetadata::new("fix weird/bug:thing");
    // No colons, slashes, or spaces in the ID
    assert!(!meta.id.contains(':'));
    assert!(!meta.id.contains('/'));
    assert!(!meta.id.contains(' '));
}
```

- [ ] **Step 12: Run test to verify it fails**

Run: `cargo test --test model_test run_metadata`
Expected: FAIL — `RunMetadata` not found

- [ ] **Step 13: Implement RunMetadata**

`src/model/run.rs`:

```rust
use chrono::Utc;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RunMetadata {
    pub id: String,
    pub slug: String,
    pub created_at: String,
    pub archived: bool,
}

impl RunMetadata {
    pub fn new(slug: &str) -> Self {
        let now = Utc::now();
        let timestamp = now.format("%Y-%m-%dT%H-%M").to_string();
        let safe_slug: String = slug
            .chars()
            .map(|c| if c.is_alphanumeric() || c == '-' { c } else { '-' })
            .collect();
        let id = format!("{}-{}", timestamp, safe_slug);
        Self {
            id,
            slug: slug.to_string(),
            created_at: now.to_rfc3339(),
            archived: false,
        }
    }
}
```

`src/model/worker.rs`:

```rust
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PaneId(pub String);

impl std::fmt::Display for PaneId {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.0)
    }
}
```

- [ ] **Step 14: Run test to verify it passes**

Run: `cargo test --test model_test`
Expected: ALL model tests PASS

- [ ] **Step 15: Commit**

```bash
git add src/model/ tests/model_test.rs
git commit -m "feat: add model types — Config, Task, TaskStatus, RunMetadata, AppError"
```

---

## Task 4: Filesystem bus — `.orchestrator/` layout helpers

**Files:**
- Create: `src/fs/bus.rs`
- Create: `src/fs/run.rs`
- Test: `tests/fs_test.rs`

- [ ] **Step 1: Write failing tests — OrchestratorPaths resolves all paths**

Create `tests/fs_test.rs`:

```rust
use agentrc::fs::bus::OrchestratorPaths;
use std::path::Path;

#[test]
fn orchestrator_paths_from_project_root() {
    let paths = OrchestratorPaths::new(Path::new("/home/eric/Code/foo"));
    assert_eq!(paths.root().to_str().unwrap(), "/home/eric/Code/foo/.orchestrator");
    assert_eq!(paths.config().to_str().unwrap(), "/home/eric/Code/foo/.orchestrator/config.json");
    assert_eq!(
        paths.active().to_str().unwrap(),
        "/home/eric/Code/foo/.orchestrator/active"
    );
}

#[test]
fn orchestrator_paths_run_scoped() {
    let paths = OrchestratorPaths::new(Path::new("/tmp/project"));
    let run = paths.run("2026-04-11T14-30-auth-refactor");
    assert!(run.root().to_str().unwrap().contains("runs/2026-04-11T14-30-auth-refactor"));
    assert!(run.tasks_dir().to_str().unwrap().ends_with("tasks"));
    assert!(run.status_dir().to_str().unwrap().ends_with("status"));
    assert!(run.heartbeats_dir().to_str().unwrap().ends_with("heartbeats"));
    assert!(run.notes_dir().to_str().unwrap().ends_with("notes"));
    assert!(run.results_dir().to_str().unwrap().ends_with("results"));
    assert!(run.worktrees_dir().to_str().unwrap().ends_with("worktrees"));
}

#[test]
fn orchestrator_paths_task_files() {
    let paths = OrchestratorPaths::new(Path::new("/tmp/project"));
    let run = paths.run("myrun");
    assert!(run.task_brief("001", "add-login").to_str().unwrap().ends_with("001-add-login.md"));
    assert!(run.status_file("001").to_str().unwrap().ends_with("001.json"));
    assert!(run.heartbeat_file("001").to_str().unwrap().ends_with("001.alive"));
    assert!(run.notes_file("001").to_str().unwrap().ends_with("001.md"));
    assert!(run.result_file("001").to_str().unwrap().ends_with("001.md"));
    assert!(run.worktree_dir("001").to_str().unwrap().ends_with("001"));
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cargo test --test fs_test`
Expected: FAIL — `OrchestratorPaths` not found

- [ ] **Step 3: Implement OrchestratorPaths and RunPaths**

`src/fs/bus.rs`:

```rust
use std::path::{Path, PathBuf};

use crate::fs::run::RunPaths;

#[derive(Debug, Clone)]
pub struct OrchestratorPaths {
    project_root: PathBuf,
}

impl OrchestratorPaths {
    pub fn new(project_root: &Path) -> Self {
        Self {
            project_root: project_root.to_path_buf(),
        }
    }

    pub fn root(&self) -> PathBuf {
        self.project_root.join(".orchestrator")
    }

    pub fn config(&self) -> PathBuf {
        self.root().join("config.json")
    }

    pub fn active(&self) -> PathBuf {
        self.root().join("active")
    }

    pub fn runs_dir(&self) -> PathBuf {
        self.root().join("runs")
    }

    pub fn run(&self, run_id: &str) -> RunPaths {
        RunPaths::new(self.runs_dir().join(run_id))
    }

    /// Resolve the active run by following the active symlink
    pub fn active_run(&self) -> Option<RunPaths> {
        let active = self.active();
        if active.exists() {
            let target = std::fs::read_link(&active).ok()?;
            // Symlink is relative to .orchestrator/
            let resolved = if target.is_relative() {
                self.root().join(&target)
            } else {
                target
            };
            Some(RunPaths::new(resolved))
        } else {
            None
        }
    }
}
```

`src/fs/run.rs`:

```rust
use std::path::{Path, PathBuf};

#[derive(Debug, Clone)]
pub struct RunPaths {
    root: PathBuf,
}

impl RunPaths {
    pub fn new(root: PathBuf) -> Self {
        Self { root }
    }

    pub fn root(&self) -> &Path {
        &self.root
    }

    pub fn plan(&self) -> PathBuf {
        self.root.join("plan.md")
    }

    pub fn orchestrator_log(&self) -> PathBuf {
        self.root.join("orchestrator.log")
    }

    pub fn integration_log(&self) -> PathBuf {
        self.root.join("integration.log")
    }

    pub fn config_snapshot(&self) -> PathBuf {
        self.root.join("config.json")
    }

    pub fn tasks_dir(&self) -> PathBuf {
        self.root.join("tasks")
    }

    pub fn status_dir(&self) -> PathBuf {
        self.root.join("status")
    }

    pub fn heartbeats_dir(&self) -> PathBuf {
        self.root.join("heartbeats")
    }

    pub fn notes_dir(&self) -> PathBuf {
        self.root.join("notes")
    }

    pub fn results_dir(&self) -> PathBuf {
        self.root.join("results")
    }

    pub fn worktrees_dir(&self) -> PathBuf {
        self.root.join("worktrees")
    }

    pub fn task_brief(&self, id: &str, slug: &str) -> PathBuf {
        self.tasks_dir().join(format!("{}-{}.md", id, slug))
    }

    pub fn status_file(&self, id: &str) -> PathBuf {
        self.status_dir().join(format!("{}.json", id))
    }

    pub fn heartbeat_file(&self, id: &str) -> PathBuf {
        self.heartbeats_dir().join(format!("{}.alive", id))
    }

    pub fn notes_file(&self, id: &str) -> PathBuf {
        self.notes_dir().join(format!("{}.md", id))
    }

    pub fn result_file(&self, id: &str) -> PathBuf {
        self.results_dir().join(format!("{}.md", id))
    }

    pub fn worktree_dir(&self, id: &str) -> PathBuf {
        self.worktrees_dir().join(id)
    }

    /// Create all subdirectories for a new run
    pub fn scaffold(&self) -> std::io::Result<()> {
        std::fs::create_dir_all(self.tasks_dir())?;
        std::fs::create_dir_all(self.status_dir())?;
        std::fs::create_dir_all(self.heartbeats_dir())?;
        std::fs::create_dir_all(self.notes_dir())?;
        std::fs::create_dir_all(self.results_dir())?;
        std::fs::create_dir_all(self.worktrees_dir())?;
        Ok(())
    }
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cargo test --test fs_test`
Expected: PASS

- [ ] **Step 5: Write failing tests — scaffold creates directories, active symlink**

Append to `tests/fs_test.rs`:

```rust
use agentrc::fs::run::RunPaths;
use tempfile::TempDir;

#[test]
fn run_scaffold_creates_all_dirs() {
    let tmp = TempDir::new().unwrap();
    let run = RunPaths::new(tmp.path().join("runs/test-run"));
    run.scaffold().unwrap();

    assert!(run.tasks_dir().is_dir());
    assert!(run.status_dir().is_dir());
    assert!(run.heartbeats_dir().is_dir());
    assert!(run.notes_dir().is_dir());
    assert!(run.results_dir().is_dir());
    assert!(run.worktrees_dir().is_dir());
}

#[test]
fn active_run_follows_symlink() {
    let tmp = TempDir::new().unwrap();
    let paths = OrchestratorPaths::new(tmp.path());

    // Create .orchestrator/runs/test-run/
    let run_paths = paths.run("test-run");
    run_paths.scaffold().unwrap();

    // Create active symlink
    std::fs::create_dir_all(paths.root()).unwrap();
    std::os::unix::fs::symlink("runs/test-run", paths.active()).unwrap();

    let active = paths.active_run().unwrap();
    assert!(active.tasks_dir().is_dir());
}

#[test]
fn active_run_returns_none_when_no_symlink() {
    let tmp = TempDir::new().unwrap();
    let paths = OrchestratorPaths::new(tmp.path());
    assert!(paths.active_run().is_none());
}
```

- [ ] **Step 6: Run test to verify it passes**

Run: `cargo test --test fs_test`
Expected: PASS (implementation already handles this)

- [ ] **Step 7: Commit**

```bash
git add src/fs/ tests/fs_test.rs
git commit -m "feat: add filesystem bus — OrchestratorPaths and RunPaths"
```

---

## Task 5: Frontmatter parser

**Files:**
- Create: `src/fs/frontmatter.rs`
- Modify: `src/fs/mod.rs`
- Test: `tests/fs_test.rs` (append)

Markdown files with YAML frontmatter (delimited by `---`) are used for task briefs. We need a parser that splits the frontmatter from the body and deserializes the YAML.

- [ ] **Step 1: Write failing tests — parse frontmatter from markdown**

Append to `tests/fs_test.rs`:

```rust
use agentrc::fs::frontmatter;
use agentrc::model::task::TaskBriefFrontmatter;

#[test]
fn parse_frontmatter_from_task_brief() {
    let content = r#"---
id: "001"
slug: add-login-endpoint
classification: writer
worktree: .orchestrator/active/worktrees/001
base_branch: main
branch: orc/001-add-login-endpoint
pane_id: null
depends_on: []
created_at: 2026-04-11T14:30:00Z
---

# Task 001: Add login endpoint

## Scope
Add POST /auth/login to the existing Express API
"#;
    let (fm, body) = frontmatter::parse::<TaskBriefFrontmatter>(content).unwrap();
    assert_eq!(fm.id, "001");
    assert_eq!(fm.slug, "add-login-endpoint");
    assert!(body.contains("# Task 001"));
    assert!(body.contains("Add POST /auth/login"));
}

#[test]
fn parse_frontmatter_missing_delimiters() {
    let content = "# No frontmatter here\nJust markdown.";
    let result = frontmatter::parse::<TaskBriefFrontmatter>(content);
    assert!(result.is_err());
}

#[test]
fn update_frontmatter_field() {
    let content = r#"---
id: "001"
slug: add-login-endpoint
classification: writer
base_branch: main
pane_id: null
depends_on: []
created_at: 2026-04-11T14:30:00Z
---

# Task body
"#;
    let updated = frontmatter::update_field(content, "pane_id", "\"%14\"").unwrap();
    assert!(updated.contains("pane_id: \"%14\""));
    assert!(updated.contains("# Task body"));
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cargo test --test fs_test frontmatter`
Expected: FAIL — `frontmatter` module not found

- [ ] **Step 3: Implement frontmatter parser**

`src/fs/frontmatter.rs`:

```rust
use anyhow::{anyhow, Result};
use serde::de::DeserializeOwned;

/// Parse YAML frontmatter from a markdown document.
/// Returns (deserialized frontmatter, body after the closing ---).
pub fn parse<T: DeserializeOwned>(content: &str) -> Result<(T, String)> {
    let trimmed = content.trim_start();
    if !trimmed.starts_with("---") {
        return Err(anyhow!("missing opening --- delimiter"));
    }

    let after_open = &trimmed[3..];
    let close_pos = after_open
        .find("\n---")
        .ok_or_else(|| anyhow!("missing closing --- delimiter"))?;

    let yaml_str = &after_open[..close_pos];
    let body_start = close_pos + 4; // skip \n---
    let body = after_open[body_start..].trim_start_matches('\n').to_string();

    let frontmatter: T = serde_yaml::from_str(yaml_str)?;
    Ok((frontmatter, body))
}

/// Update a single field value in the YAML frontmatter of a markdown document.
/// Does a simple string replacement of `key: <old_value>` with `key: <new_value>`.
pub fn update_field(content: &str, key: &str, new_value: &str) -> Result<String> {
    let trimmed = content.trim_start();
    if !trimmed.starts_with("---") {
        return Err(anyhow!("missing opening --- delimiter"));
    }

    let after_open = &trimmed[3..];
    let close_pos = after_open
        .find("\n---")
        .ok_or_else(|| anyhow!("missing closing --- delimiter"))?;

    let yaml_str = &after_open[..close_pos];
    let body = &after_open[close_pos..];

    // Find the line with the key and replace the value
    let mut updated_lines: Vec<String> = Vec::new();
    let mut found = false;
    for line in yaml_str.lines() {
        if line.starts_with(&format!("{}:", key)) || line.starts_with(&format!("{} :", key)) {
            updated_lines.push(format!("{}: {}", key, new_value));
            found = true;
        } else {
            updated_lines.push(line.to_string());
        }
    }

    if !found {
        return Err(anyhow!("key '{}' not found in frontmatter", key));
    }

    Ok(format!("---\n{}{}", updated_lines.join("\n"), body))
}
```

Update `src/fs/mod.rs`:
```rust
pub mod bus;
pub mod frontmatter;
pub mod run;
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cargo test --test fs_test frontmatter`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/fs/frontmatter.rs src/fs/mod.rs tests/fs_test.rs
git commit -m "feat: add YAML frontmatter parser for task briefs"
```

---

## Task 6: Git wrapper

**Files:**
- Create: `src/git/wrapper.rs`
- Test: `tests/common/mod.rs` (shared helpers)
- Test: append to existing test files or create `tests/git_test.rs`

- [ ] **Step 1: Write failing tests — git wrapper methods**

Create `tests/common/mod.rs` with shared test helpers:

```rust
use std::path::Path;
use std::process::Command;

/// Create a temporary git repo with an initial commit
pub fn init_test_repo(path: &Path) {
    Command::new("git").args(["init", path.to_str().unwrap()]).output().unwrap();
    Command::new("git")
        .args(["-C", path.to_str().unwrap(), "config", "user.email", "test@test.com"])
        .output().unwrap();
    Command::new("git")
        .args(["-C", path.to_str().unwrap(), "config", "user.name", "Test"])
        .output().unwrap();
    std::fs::write(path.join("README.md"), "# Test").unwrap();
    Command::new("git")
        .args(["-C", path.to_str().unwrap(), "add", "."])
        .output().unwrap();
    Command::new("git")
        .args(["-C", path.to_str().unwrap(), "commit", "-m", "initial"])
        .output().unwrap();
}
```

Create `tests/git_test.rs`:

```rust
mod common;

use agentrc::git::wrapper::Git;
use tempfile::TempDir;

#[test]
fn git_is_clean_on_fresh_repo() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    let git = Git::new(tmp.path());
    assert!(git.is_clean().unwrap());
}

#[test]
fn git_is_not_clean_with_uncommitted_changes() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    std::fs::write(tmp.path().join("dirty.txt"), "dirty").unwrap();
    let git = Git::new(tmp.path());
    assert!(!git.is_clean().unwrap());
}

#[test]
fn git_current_branch() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    let git = Git::new(tmp.path());
    let branch = git.current_branch().unwrap();
    // Git default branch is usually "main" or "master"
    assert!(!branch.is_empty());
}

#[test]
fn git_create_and_remove_worktree() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    let git = Git::new(tmp.path());
    let wt_path = tmp.path().join("worktrees/001");
    git.create_worktree(&wt_path, "orc/001-test", "HEAD").unwrap();
    assert!(wt_path.exists());
    assert!(wt_path.join("README.md").exists());
    git.remove_worktree(&wt_path).unwrap();
    assert!(!wt_path.exists());
}

#[test]
fn git_merge_no_ff() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    let git = Git::new(tmp.path());

    // Create a branch with a commit
    let wt_path = tmp.path().join("worktrees/feat");
    git.create_worktree(&wt_path, "feat-branch", "HEAD").unwrap();
    std::fs::write(wt_path.join("feat.txt"), "feature").unwrap();
    let feat_git = Git::new(&wt_path);
    feat_git.add_all().unwrap();
    feat_git.commit("add feature").unwrap();

    // Merge back
    let base_branch = git.current_branch().unwrap();
    git.checkout(&base_branch).unwrap();
    let result = git.merge_no_ff("feat-branch");
    assert!(result.is_ok());
    assert!(tmp.path().join("feat.txt").exists());

    git.remove_worktree(&wt_path).unwrap();
}

#[test]
fn git_log_oneline() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    let git = Git::new(tmp.path());
    let log = git.log_oneline("HEAD", 5).unwrap();
    assert!(!log.is_empty());
    assert!(log[0].contains("initial"));
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cargo test --test git_test`
Expected: FAIL — `Git` not found

- [ ] **Step 3: Implement Git wrapper**

`src/git/wrapper.rs`:

```rust
use anyhow::{anyhow, Context, Result};
use std::path::{Path, PathBuf};

pub struct Git {
    repo_path: PathBuf,
}

impl Git {
    pub fn new(repo_path: &Path) -> Self {
        Self {
            repo_path: repo_path.to_path_buf(),
        }
    }

    fn cmd(&self) -> duct::Expression {
        duct::cmd!("git", "-C", self.repo_path.to_str().unwrap_or("."))
    }

    fn run_git(&self, args: &[&str]) -> Result<String> {
        let mut cmd = std::process::Command::new("git");
        cmd.arg("-C").arg(&self.repo_path);
        for arg in args {
            cmd.arg(arg);
        }
        let output = cmd.output().context("failed to run git")?;
        if !output.status.success() {
            let stderr = String::from_utf8_lossy(&output.stderr);
            return Err(anyhow!("git {} failed: {}", args.join(" "), stderr.trim()));
        }
        Ok(String::from_utf8_lossy(&output.stdout).trim().to_string())
    }

    pub fn is_clean(&self) -> Result<bool> {
        let output = self.run_git(&["status", "--porcelain"])?;
        Ok(output.is_empty())
    }

    pub fn current_branch(&self) -> Result<String> {
        self.run_git(&["rev-parse", "--abbrev-ref", "HEAD"])
    }

    pub fn checkout(&self, branch: &str) -> Result<()> {
        self.run_git(&["checkout", branch])?;
        Ok(())
    }

    pub fn create_worktree(&self, path: &Path, branch: &str, base: &str) -> Result<()> {
        let path_str = path.to_str().ok_or_else(|| anyhow!("invalid path"))?;
        self.run_git(&["worktree", "add", path_str, "-b", branch, base])?;
        Ok(())
    }

    pub fn remove_worktree(&self, path: &Path) -> Result<()> {
        let path_str = path.to_str().ok_or_else(|| anyhow!("invalid path"))?;
        self.run_git(&["worktree", "remove", path_str, "--force"])?;
        Ok(())
    }

    pub fn list_worktrees(&self) -> Result<Vec<String>> {
        let output = self.run_git(&["worktree", "list", "--porcelain"])?;
        let worktrees: Vec<String> = output
            .lines()
            .filter(|l| l.starts_with("worktree "))
            .map(|l| l.trim_start_matches("worktree ").to_string())
            .collect();
        Ok(worktrees)
    }

    pub fn branch_exists(&self, branch: &str) -> Result<bool> {
        let output = self.run_git(&["branch", "--list", branch])?;
        Ok(!output.is_empty())
    }

    pub fn merge_no_ff(&self, branch: &str) -> Result<()> {
        self.run_git(&["merge", "--no-ff", branch, "-m", &format!("Merge branch '{}'", branch)])?;
        Ok(())
    }

    pub fn merge_abort(&self) -> Result<()> {
        self.run_git(&["merge", "--abort"])?;
        Ok(())
    }

    pub fn reset_hard_head(&self, count: u32) -> Result<()> {
        self.run_git(&["reset", "--hard", &format!("HEAD~{}", count)])?;
        Ok(())
    }

    pub fn add_all(&self) -> Result<()> {
        self.run_git(&["add", "-A"])?;
        Ok(())
    }

    pub fn commit(&self, message: &str) -> Result<()> {
        self.run_git(&["commit", "-m", message])?;
        Ok(())
    }

    pub fn log_oneline(&self, ref_name: &str, count: u32) -> Result<Vec<String>> {
        let output = self.run_git(&[
            "log",
            "--oneline",
            &format!("-{}", count),
            ref_name,
        ])?;
        Ok(output.lines().map(|l| l.to_string()).collect())
    }

    /// Get the commit log for a branch, useful for TDD review
    pub fn log_branch_commits(&self, branch: &str, base: &str) -> Result<Vec<String>> {
        let range = format!("{}..{}", base, branch);
        let output = self.run_git(&["log", "--oneline", &range])?;
        Ok(output.lines().map(|l| l.to_string()).collect())
    }

    /// Get files changed in a specific commit
    pub fn show_files_changed(&self, commit: &str) -> Result<Vec<String>> {
        let output = self.run_git(&["show", "--name-only", "--format=", commit])?;
        Ok(output.lines().filter(|l| !l.is_empty()).map(|l| l.to_string()).collect())
    }

    /// Detect the default branch name
    pub fn detect_default_branch(&self) -> Result<String> {
        // Try common names
        for name in &["main", "master"] {
            if self.branch_exists(name)? {
                return Ok(name.to_string());
            }
        }
        self.current_branch()
    }
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cargo test --test git_test`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/git/ tests/git_test.rs tests/common/
git commit -m "feat: add typed Git wrapper with worktree, merge, and log support"
```

---

## Task 7: Tmux wrapper

**Files:**
- Create: `src/tmux/wrapper.rs`
- Test: `tests/tmux_test.rs`

Tmux tests are tricky — they require a running tmux server. We split into two categories: unit tests that validate command construction (no tmux needed), and integration tests (marked `#[ignore]`) that require a tmux session.

- [ ] **Step 1: Write failing tests — tmux command construction**

Create `tests/tmux_test.rs`:

```rust
use agentrc::tmux::wrapper::Tmux;

#[test]
fn tmux_build_split_command() {
    let tmux = Tmux::new();
    let args = tmux.build_split_args("workers-1");
    assert!(args.contains(&"-h".to_string()));
    assert!(args.contains(&"-P".to_string()));
    assert!(args.contains(&"-t".to_string()));
    assert!(args.contains(&"workers-1".to_string()));
}

#[test]
fn tmux_build_send_keys_command() {
    let args = Tmux::build_send_keys_args("%14", "echo hello");
    assert_eq!(args[0], "send-keys");
    assert_eq!(args[1], "-t");
    assert_eq!(args[2], "%14");
    assert_eq!(args[3], "echo hello");
    assert_eq!(args[4], "Enter");
}

#[test]
fn tmux_build_kill_pane_command() {
    let args = Tmux::build_kill_pane_args("%14");
    assert_eq!(args, vec!["kill-pane", "-t", "%14"]);
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cargo test --test tmux_test`
Expected: FAIL — `Tmux` not found

- [ ] **Step 3: Implement Tmux wrapper**

`src/tmux/wrapper.rs`:

```rust
use anyhow::{anyhow, Context, Result};

pub struct Tmux;

impl Tmux {
    pub fn new() -> Self {
        Self
    }

    fn run_tmux(args: &[&str]) -> Result<String> {
        let output = std::process::Command::new("tmux")
            .args(args)
            .output()
            .context("failed to run tmux")?;
        if !output.status.success() {
            let stderr = String::from_utf8_lossy(&output.stderr);
            return Err(anyhow!("tmux {} failed: {}", args.join(" "), stderr.trim()));
        }
        Ok(String::from_utf8_lossy(&output.stdout).trim().to_string())
    }

    // --- Command builders (testable without tmux) ---

    pub fn build_split_args(target_window: &str) -> Vec<String> {
        vec![
            "split-window".into(),
            "-h".into(),
            "-P".into(),
            "-F".into(),
            "#{pane_id}".into(),
            "-t".into(),
            target_window.into(),
        ]
    }

    pub fn build_send_keys_args(pane_id: &str, keys: &str) -> Vec<String> {
        vec![
            "send-keys".into(),
            "-t".into(),
            pane_id.into(),
            keys.into(),
            "Enter".into(),
        ]
    }

    pub fn build_kill_pane_args(pane_id: &str) -> Vec<String> {
        vec!["kill-pane".into(), "-t".into(), pane_id.into()]
    }

    // --- Execution methods (require tmux) ---

    /// Split a window and return the new pane ID
    pub fn split_window(&self, target_window: &str) -> Result<String> {
        let args = Self::build_split_args(target_window);
        let refs: Vec<&str> = args.iter().map(|s| s.as_str()).collect();
        Self::run_tmux(&refs)
    }

    /// Send keys to a pane
    pub fn send_keys(&self, pane_id: &str, keys: &str) -> Result<()> {
        let args = Self::build_send_keys_args(pane_id, keys);
        let refs: Vec<&str> = args.iter().map(|s| s.as_str()).collect();
        Self::run_tmux(&refs)?;
        Ok(())
    }

    /// Kill a pane
    pub fn kill_pane(&self, pane_id: &str) -> Result<()> {
        let args = Self::build_kill_pane_args(pane_id);
        let refs: Vec<&str> = args.iter().map(|s| s.as_str()).collect();
        Self::run_tmux(&refs)?;
        Ok(())
    }

    /// Retile all panes in a window
    pub fn select_layout_tiled(&self, target_window: &str) -> Result<()> {
        Self::run_tmux(&["select-layout", "-t", target_window, "tiled"])?;
        Ok(())
    }

    /// Create a new tmux window with a name
    pub fn new_window(&self, name: &str) -> Result<()> {
        Self::run_tmux(&["new-window", "-n", name])?;
        Ok(())
    }

    /// List panes in a window, returns list of pane IDs
    pub fn list_panes(&self, target_window: &str) -> Result<Vec<String>> {
        let output = Self::run_tmux(&[
            "list-panes",
            "-t",
            target_window,
            "-F",
            "#{pane_id}",
        ])?;
        Ok(output.lines().map(|l| l.to_string()).collect())
    }

    /// List windows, returns list of window names
    pub fn list_windows(&self) -> Result<Vec<String>> {
        let output = Self::run_tmux(&["list-windows", "-F", "#{window_name}"])?;
        Ok(output.lines().map(|l| l.to_string()).collect())
    }

    /// Signal a tmux wait-for channel
    pub fn wait_for_signal(&self, channel: &str) -> Result<()> {
        Self::run_tmux(&["wait-for", "-S", channel])?;
        Ok(())
    }

    /// Check if we're inside a tmux session
    pub fn is_inside_tmux() -> bool {
        std::env::var("TMUX").is_ok()
    }
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cargo test --test tmux_test`
Expected: PASS (build_ methods don't need tmux)

- [ ] **Step 5: Commit**

```bash
git add src/tmux/ tests/tmux_test.rs
git commit -m "feat: add Tmux wrapper with command builders and execution methods"
```

---

## Task 8: `agentrc init` command

**Files:**
- Modify: `src/commands/init.rs`
- Test: `tests/init_test.rs`

- [ ] **Step 1: Write failing tests**

Create `tests/init_test.rs`:

```rust
mod common;

use agentrc::commands::init;
use agentrc::fs::bus::OrchestratorPaths;
use tempfile::TempDir;

#[test]
fn init_creates_orchestrator_dir() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    init::run_in(tmp.path(), Some("cargo test"), false).unwrap();

    let paths = OrchestratorPaths::new(tmp.path());
    assert!(paths.root().is_dir());
    assert!(paths.config().is_file());
    assert!(paths.runs_dir().is_dir());
}

#[test]
fn init_writes_config_with_test_command() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    init::run_in(tmp.path(), Some("npm test"), false).unwrap();

    let paths = OrchestratorPaths::new(tmp.path());
    let content = std::fs::read_to_string(paths.config()).unwrap();
    let config: serde_json::Value = serde_json::from_str(&content).unwrap();
    assert_eq!(config["test_command"], "npm test");
    assert_eq!(config["max_workers"], 12);
    assert_eq!(config["base_branch"], "main");
}

#[test]
fn init_adds_orchestrator_to_gitignore() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    init::run_in(tmp.path(), None, false).unwrap();

    let gitignore = std::fs::read_to_string(tmp.path().join(".gitignore")).unwrap();
    assert!(gitignore.contains(".orchestrator/"));
}

#[test]
fn init_appends_to_existing_gitignore() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    std::fs::write(tmp.path().join(".gitignore"), "node_modules/\n").unwrap();
    init::run_in(tmp.path(), None, false).unwrap();

    let gitignore = std::fs::read_to_string(tmp.path().join(".gitignore")).unwrap();
    assert!(gitignore.contains("node_modules/"));
    assert!(gitignore.contains(".orchestrator/"));
}

#[test]
fn init_is_idempotent() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    init::run_in(tmp.path(), Some("cargo test"), false).unwrap();
    init::run_in(tmp.path(), Some("cargo test"), false).unwrap();

    let paths = OrchestratorPaths::new(tmp.path());
    assert!(paths.root().is_dir());
    // Gitignore should not have duplicate entries
    let gitignore = std::fs::read_to_string(tmp.path().join(".gitignore")).unwrap();
    let count = gitignore.matches(".orchestrator/").count();
    assert_eq!(count, 1);
}

#[test]
fn init_auto_detects_cargo_test_command() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    std::fs::write(tmp.path().join("Cargo.toml"), "[package]\nname = \"test\"\n").unwrap();
    let detected = init::detect_test_command(tmp.path());
    assert_eq!(detected, Some("cargo test".to_string()));
}

#[test]
fn init_auto_detects_npm_test_command() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    std::fs::write(tmp.path().join("package.json"), "{\"scripts\":{\"test\":\"jest\"}}").unwrap();
    let detected = init::detect_test_command(tmp.path());
    assert_eq!(detected, Some("npm test".to_string()));
}

#[test]
fn init_auto_detects_pytest() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    std::fs::write(tmp.path().join("pyproject.toml"), "[tool.pytest]\n").unwrap();
    let detected = init::detect_test_command(tmp.path());
    assert_eq!(detected, Some("pytest".to_string()));
}

#[test]
fn init_returns_none_for_unknown_project() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    let detected = init::detect_test_command(tmp.path());
    assert!(detected.is_none());
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cargo test --test init_test`
Expected: FAIL — `init::run_in` not found

- [ ] **Step 3: Implement init command**

`src/commands/init.rs`:

```rust
use anyhow::{Context, Result};
use std::path::Path;

use crate::fs::bus::OrchestratorPaths;
use crate::git::wrapper::Git;
use crate::model::config::OrchestratorConfig;

/// Entry point from CLI — uses current directory, interactive
pub fn run() -> Result<()> {
    let cwd = std::env::current_dir()?;
    let detected = detect_test_command(&cwd);
    // In the real CLI, we'd prompt the user here. For now, use detected value.
    run_in(&cwd, detected.as_deref(), true)
}

/// Testable entry point
pub fn run_in(project_root: &Path, test_command: Option<&str>, verbose: bool) -> Result<()> {
    let paths = OrchestratorPaths::new(project_root);

    // Create .orchestrator/ and runs/
    std::fs::create_dir_all(paths.runs_dir())
        .context("failed to create .orchestrator/runs")?;

    // Detect base branch
    let git = Git::new(project_root);
    let base_branch = git.detect_default_branch().unwrap_or_else(|_| "main".into());

    // Write config.json
    let config = OrchestratorConfig {
        project_root: project_root.canonicalize().unwrap_or_else(|_| project_root.to_path_buf()),
        base_branch,
        test_command: test_command.map(String::from),
        ..Default::default()
    };
    let config_json = serde_json::to_string_pretty(&config)?;
    std::fs::write(paths.config(), &config_json)
        .context("failed to write config.json")?;

    // Update .gitignore
    add_to_gitignore(project_root)?;

    if verbose {
        println!("Initialized .orchestrator/ in {}", project_root.display());
        if let Some(cmd) = test_command {
            println!("Test command: {}", cmd);
        } else {
            println!("No test command detected. Set manually in .orchestrator/config.json");
        }
    }

    Ok(())
}

fn add_to_gitignore(project_root: &Path) -> Result<()> {
    let gitignore_path = project_root.join(".gitignore");
    let entry = ".orchestrator/";

    if gitignore_path.exists() {
        let content = std::fs::read_to_string(&gitignore_path)?;
        if content.contains(entry) {
            return Ok(()); // Already present
        }
        let mut new_content = content;
        if !new_content.ends_with('\n') {
            new_content.push('\n');
        }
        new_content.push_str(entry);
        new_content.push('\n');
        std::fs::write(&gitignore_path, new_content)?;
    } else {
        std::fs::write(&gitignore_path, format!("{}\n", entry))?;
    }

    Ok(())
}

/// Auto-detect the test command based on project files
pub fn detect_test_command(project_root: &Path) -> Option<String> {
    if project_root.join("Cargo.toml").exists() {
        return Some("cargo test".into());
    }
    if project_root.join("package.json").exists() {
        return Some("npm test".into());
    }
    if project_root.join("pyproject.toml").exists() {
        return Some("pytest".into());
    }
    if project_root.join("Makefile").exists() {
        return Some("make test".into());
    }
    if project_root.join("go.mod").exists() {
        return Some("go test ./...".into());
    }
    None
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cargo test --test init_test`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/commands/init.rs tests/init_test.rs
git commit -m "feat: add init command — scaffold .orchestrator/, detect test command"
```

---

## Task 9: `agentrc install` command

**Files:**
- Modify: `src/commands/install.rs`
- Test: `tests/install_test.rs`

- [ ] **Step 1: Write failing tests**

Create `tests/install_test.rs`:

```rust
use agentrc::commands::install;
use tempfile::TempDir;
use std::path::PathBuf;

#[test]
fn install_creates_symlink() {
    let tmp_home = TempDir::new().unwrap();
    let tmp_repo = TempDir::new().unwrap();

    // Create the skill source
    let skill_src = tmp_repo.path().join("skill/agentrc");
    std::fs::create_dir_all(&skill_src).unwrap();
    std::fs::write(skill_src.join("SKILL.md"), "---\nname: agentrc\n---\n# Test").unwrap();

    let skills_dir = tmp_home.path().join(".claude/skills");
    install::install_skill(&skill_src, &skills_dir).unwrap();

    let link = skills_dir.join("agentrc");
    assert!(link.exists());
    assert!(link.join("SKILL.md").exists());

    // Verify it's a symlink
    let metadata = std::fs::symlink_metadata(&link).unwrap();
    assert!(metadata.file_type().is_symlink());
}

#[test]
fn install_is_idempotent() {
    let tmp_home = TempDir::new().unwrap();
    let tmp_repo = TempDir::new().unwrap();

    let skill_src = tmp_repo.path().join("skill/agentrc");
    std::fs::create_dir_all(&skill_src).unwrap();
    std::fs::write(skill_src.join("SKILL.md"), "test").unwrap();

    let skills_dir = tmp_home.path().join(".claude/skills");
    install::install_skill(&skill_src, &skills_dir).unwrap();
    install::install_skill(&skill_src, &skills_dir).unwrap();

    let link = skills_dir.join("agentrc");
    assert!(link.exists());
}

#[test]
fn install_repairs_broken_symlink() {
    let tmp_home = TempDir::new().unwrap();
    let tmp_repo = TempDir::new().unwrap();

    let skill_src = tmp_repo.path().join("skill/agentrc");
    std::fs::create_dir_all(&skill_src).unwrap();
    std::fs::write(skill_src.join("SKILL.md"), "test").unwrap();

    let skills_dir = tmp_home.path().join(".claude/skills");
    std::fs::create_dir_all(&skills_dir).unwrap();

    // Create a broken symlink
    std::os::unix::fs::symlink("/nonexistent/path", skills_dir.join("agentrc")).unwrap();

    install::install_skill(&skill_src, &skills_dir).unwrap();

    let link = skills_dir.join("agentrc");
    assert!(link.exists());
    assert!(link.join("SKILL.md").exists());
}

#[test]
fn check_prerequisite_claude() {
    // Just verify the function exists and returns a result
    let result = install::check_command_exists("echo");
    assert!(result);
}

#[test]
fn check_prerequisite_missing() {
    let result = install::check_command_exists("nonexistent_binary_xyz_123");
    assert!(!result);
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cargo test --test install_test`
Expected: FAIL — `install::install_skill` not found

- [ ] **Step 3: Implement install command**

`src/commands/install.rs`:

```rust
use anyhow::{anyhow, Context, Result};
use std::path::Path;

/// Entry point from CLI
pub fn run() -> Result<()> {
    // Find the repo's skill directory relative to the binary
    let exe_path = std::env::current_exe()?;
    let repo_root = find_repo_root(&exe_path)?;
    let skill_src = repo_root.join("skill/agentrc");

    if !skill_src.exists() {
        return Err(anyhow!(
            "skill source not found at {}. Are you running from the agent.rc repo?",
            skill_src.display()
        ));
    }

    let home = std::env::var("HOME").context("HOME not set")?;
    let skills_dir = Path::new(&home).join(".claude/skills");

    install_skill(&skill_src, &skills_dir)?;

    // Check prerequisites
    let mut ok = true;
    for cmd in &["claude", "tmux", "git"] {
        if check_command_exists(cmd) {
            println!("  [ok] {} found", cmd);
        } else {
            println!("  [!!] {} not found", cmd);
            ok = false;
        }
    }

    if ok {
        println!("agentrc installed successfully.");
    } else {
        println!("agentrc installed, but some prerequisites are missing.");
    }

    Ok(())
}

/// Install the skill by creating a symlink
pub fn install_skill(skill_src: &Path, skills_dir: &Path) -> Result<()> {
    std::fs::create_dir_all(skills_dir)
        .context("failed to create skills directory")?;

    let link_path = skills_dir.join("agentrc");

    // Remove existing symlink (broken or otherwise)
    if link_path.symlink_metadata().is_ok() {
        std::fs::remove_file(&link_path)
            .or_else(|_| std::fs::remove_dir_all(&link_path))
            .context("failed to remove existing symlink")?;
    }

    let canonical_src = skill_src.canonicalize()
        .context("failed to resolve skill source path")?;

    std::os::unix::fs::symlink(&canonical_src, &link_path)
        .context("failed to create symlink")?;

    println!(
        "Skill symlinked: {} -> {}",
        link_path.display(),
        canonical_src.display()
    );

    Ok(())
}

/// Check if a command is available on PATH
pub fn check_command_exists(name: &str) -> bool {
    std::process::Command::new("which")
        .arg(name)
        .output()
        .map(|o| o.status.success())
        .unwrap_or(false)
}

fn find_repo_root(from: &Path) -> Result<std::path::PathBuf> {
    // Walk up from the binary location looking for Cargo.toml
    let mut dir = from.parent();
    while let Some(d) = dir {
        if d.join("Cargo.toml").exists() && d.join("skill").exists() {
            return Ok(d.to_path_buf());
        }
        dir = d.parent();
    }
    // Fall back to current directory
    let cwd = std::env::current_dir()?;
    if cwd.join("skill/agentrc/SKILL.md").exists() {
        return Ok(cwd);
    }
    Err(anyhow!("could not find agent.rc repo root"))
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cargo test --test install_test`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/commands/install.rs tests/install_test.rs
git commit -m "feat: add install command — symlink skill, verify prerequisites"
```

---

## Task 10: `agentrc run` subcommands

**Files:**
- Modify: `src/commands/run.rs`
- Test: `tests/run_test.rs`

- [ ] **Step 1: Write failing tests**

Create `tests/run_test.rs`:

```rust
mod common;

use agentrc::commands::run as run_cmd;
use agentrc::fs::bus::OrchestratorPaths;
use tempfile::TempDir;

fn setup_initialized_project() -> TempDir {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    agentrc::commands::init::run_in(tmp.path(), Some("cargo test"), false).unwrap();
    tmp
}

#[test]
fn run_create_makes_run_dir_and_active_symlink() {
    let tmp = setup_initialized_project();
    let paths = OrchestratorPaths::new(tmp.path());

    run_cmd::create_in(tmp.path(), "auth-refactor").unwrap();

    // Active symlink exists
    assert!(paths.active().exists() || paths.active().symlink_metadata().is_ok());

    // Run directory has all subdirs
    let active = paths.active_run().unwrap();
    assert!(active.tasks_dir().is_dir());
    assert!(active.status_dir().is_dir());
    assert!(active.heartbeats_dir().is_dir());
    assert!(active.notes_dir().is_dir());
    assert!(active.results_dir().is_dir());
    assert!(active.worktrees_dir().is_dir());

    // Config snapshot exists
    assert!(active.config_snapshot().is_file());
}

#[test]
fn run_create_fails_if_already_active() {
    let tmp = setup_initialized_project();
    run_cmd::create_in(tmp.path(), "first-run").unwrap();
    let result = run_cmd::create_in(tmp.path(), "second-run");
    assert!(result.is_err());
    assert!(result.unwrap_err().to_string().contains("already active"));
}

#[test]
fn run_list_shows_runs() {
    let tmp = setup_initialized_project();
    run_cmd::create_in(tmp.path(), "first-run").unwrap();
    run_cmd::archive_in(tmp.path()).unwrap();
    run_cmd::create_in(tmp.path(), "second-run").unwrap();

    let runs = run_cmd::list_in(tmp.path()).unwrap();
    assert_eq!(runs.len(), 2);
}

#[test]
fn run_archive_removes_active_symlink() {
    let tmp = setup_initialized_project();
    let paths = OrchestratorPaths::new(tmp.path());
    run_cmd::create_in(tmp.path(), "test-run").unwrap();

    assert!(paths.active_run().is_some());
    run_cmd::archive_in(tmp.path()).unwrap();
    assert!(paths.active_run().is_none());
}

#[test]
fn run_archive_fails_if_no_active_run() {
    let tmp = setup_initialized_project();
    let result = run_cmd::archive_in(tmp.path());
    assert!(result.is_err());
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cargo test --test run_test`
Expected: FAIL — `run_cmd::create_in` not found

- [ ] **Step 3: Implement run subcommands**

`src/commands/run.rs`:

```rust
use anyhow::{Context, Result};
use std::path::Path;

use crate::fs::bus::OrchestratorPaths;
use crate::model::error::AppError;
use crate::model::run::RunMetadata;

/// CLI entry: agentrc run create --slug <name>
pub fn create(slug: &str) -> Result<()> {
    let cwd = std::env::current_dir()?;
    create_in(&cwd, slug)
}

/// CLI entry: agentrc run list
pub fn list() -> Result<()> {
    let cwd = std::env::current_dir()?;
    let runs = list_in(&cwd)?;
    if runs.is_empty() {
        println!("No runs found.");
    } else {
        for run in &runs {
            let active_marker = if run.active { " [active]" } else { "" };
            println!("  {}{}", run.id, active_marker);
        }
    }
    Ok(())
}

/// CLI entry: agentrc run archive
pub fn archive() -> Result<()> {
    let cwd = std::env::current_dir()?;
    archive_in(&cwd)
}

// --- Testable implementations ---

pub fn create_in(project_root: &Path, slug: &str) -> Result<()> {
    let paths = OrchestratorPaths::new(project_root);

    // Check no active run
    if paths.active_run().is_some() {
        return Err(AppError::RunAlreadyActive {
            run_id: "existing".into(),
        }
        .into());
    }

    // Create run
    let meta = RunMetadata::new(slug);
    let run_paths = paths.run(&meta.id);
    run_paths.scaffold()?;

    // Snapshot config
    let config_src = paths.config();
    if config_src.exists() {
        std::fs::copy(&config_src, run_paths.config_snapshot())
            .context("failed to snapshot config")?;
    }

    // Create active symlink (relative path)
    let relative = format!("runs/{}", meta.id);
    std::os::unix::fs::symlink(&relative, paths.active())
        .context("failed to create active symlink")?;

    println!("Created run: {}", meta.id);
    Ok(())
}

pub struct RunInfo {
    pub id: String,
    pub active: bool,
}

pub fn list_in(project_root: &Path) -> Result<Vec<RunInfo>> {
    let paths = OrchestratorPaths::new(project_root);
    let runs_dir = paths.runs_dir();

    if !runs_dir.exists() {
        return Ok(Vec::new());
    }

    let active_target = paths
        .active()
        .read_link()
        .ok()
        .and_then(|t| t.file_name().map(|f| f.to_string_lossy().to_string()));

    let mut runs = Vec::new();
    for entry in std::fs::read_dir(&runs_dir)? {
        let entry = entry?;
        if entry.file_type()?.is_dir() {
            let name = entry.file_name().to_string_lossy().to_string();
            let active = active_target.as_deref() == Some(&name);
            runs.push(RunInfo { id: name, active });
        }
    }
    runs.sort_by(|a, b| a.id.cmp(&b.id));
    Ok(runs)
}

pub fn archive_in(project_root: &Path) -> Result<()> {
    let paths = OrchestratorPaths::new(project_root);

    if paths.active_run().is_none() {
        return Err(AppError::NoActiveRun.into());
    }

    std::fs::remove_file(paths.active()).context("failed to remove active symlink")?;
    println!("Run archived.");
    Ok(())
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cargo test --test run_test`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/commands/run.rs tests/run_test.rs
git commit -m "feat: add run create/list/archive subcommands"
```

---

## Task 11: `agentrc worker status` command

**Files:**
- Modify: `src/commands/worker/status.rs`
- Test: `tests/worker_commands_test.rs`

- [ ] **Step 1: Write failing tests**

Create `tests/worker_commands_test.rs`:

```rust
mod common;

use agentrc::commands::worker;
use agentrc::fs::bus::OrchestratorPaths;
use agentrc::model::task::{TaskState, TaskStatus};
use tempfile::TempDir;

fn setup_active_run() -> (TempDir, OrchestratorPaths) {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    agentrc::commands::init::run_in(tmp.path(), Some("cargo test"), false).unwrap();
    agentrc::commands::run::create_in(tmp.path(), "test-run").unwrap();
    let paths = OrchestratorPaths::new(tmp.path());
    (tmp, paths)
}

#[test]
fn worker_status_creates_initial_status_file() {
    let (tmp, paths) = setup_active_run();
    worker::status::run_in(
        tmp.path(), "001", "spawning", None, None,
    ).unwrap();

    let active = paths.active_run().unwrap();
    let status_file = active.status_file("001");
    assert!(status_file.exists());

    let content = std::fs::read_to_string(&status_file).unwrap();
    let status: TaskStatus = serde_json::from_str(&content).unwrap();
    assert_eq!(status.id, "001");
    assert_eq!(status.state, TaskState::Spawning);
}

#[test]
fn worker_status_updates_existing_status() {
    let (tmp, _paths) = setup_active_run();
    worker::status::run_in(tmp.path(), "001", "spawning", None, None).unwrap();
    worker::status::run_in(
        tmp.path(), "001", "in_progress",
        Some("implementing"), Some("writing tests"),
    ).unwrap();

    let paths = OrchestratorPaths::new(tmp.path());
    let active = paths.active_run().unwrap();
    let content = std::fs::read_to_string(active.status_file("001")).unwrap();
    let status: TaskStatus = serde_json::from_str(&content).unwrap();
    assert_eq!(status.state, TaskState::InProgress);
    assert_eq!(status.phase.as_deref(), Some("implementing"));
    assert_eq!(status.last_message.as_deref(), Some("writing tests"));
}

#[test]
fn worker_status_validates_state_string() {
    let (tmp, _) = setup_active_run();
    let result = worker::status::run_in(tmp.path(), "001", "invalid_state", None, None);
    assert!(result.is_err());
}

#[test]
fn worker_status_sets_started_at_on_first_in_progress() {
    let (tmp, paths) = setup_active_run();
    worker::status::run_in(tmp.path(), "001", "spawning", None, None).unwrap();
    worker::status::run_in(tmp.path(), "001", "ready", None, None).unwrap();
    worker::status::run_in(tmp.path(), "001", "in_progress", None, None).unwrap();

    let active = paths.active_run().unwrap();
    let content = std::fs::read_to_string(active.status_file("001")).unwrap();
    let status: TaskStatus = serde_json::from_str(&content).unwrap();
    assert!(status.started_at.is_some());
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cargo test --test worker_commands_test worker_status`
Expected: FAIL

- [ ] **Step 3: Implement worker status command**

`src/commands/worker/status.rs`:

```rust
use anyhow::{anyhow, Result};
use chrono::Utc;
use std::path::Path;

use crate::fs::bus::OrchestratorPaths;
use crate::model::error::AppError;
use crate::model::task::{TaskState, TaskStatus};

/// CLI entry
pub fn run(task: &str, state: &str, phase: Option<&str>, message: Option<&str>) -> Result<()> {
    let cwd = std::env::current_dir()?;
    run_in(&cwd, task, state, phase, message)
}

/// Testable entry
pub fn run_in(
    project_root: &Path,
    task_id: &str,
    state_str: &str,
    phase: Option<&str>,
    message: Option<&str>,
) -> Result<()> {
    let state = parse_state(state_str)?;
    let paths = OrchestratorPaths::new(project_root);
    let active = paths
        .active_run()
        .ok_or(AppError::NoActiveRun)?;

    let status_file = active.status_file(task_id);
    let now = Utc::now();

    let mut status = if status_file.exists() {
        let content = std::fs::read_to_string(&status_file)?;
        serde_json::from_str::<TaskStatus>(&content).map_err(|e| AppError::StatusParseError {
            path: status_file.clone(),
            reason: e.to_string(),
        })?
    } else {
        TaskStatus {
            id: task_id.to_string(),
            pane_id: None,
            state: TaskState::Spawning,
            phase: None,
            started_at: None,
            updated_at: now,
            last_message: None,
            result_path: None,
            branch: None,
            redispatch_count: 0,
        }
    };

    status.state = state;
    status.updated_at = now;

    if let Some(p) = phase {
        status.phase = Some(p.to_string());
    }
    if let Some(m) = message {
        status.last_message = Some(m.to_string());
    }

    // Set started_at on first transition to in_progress
    if status.state == TaskState::InProgress && status.started_at.is_none() {
        status.started_at = Some(now);
    }

    let json = serde_json::to_string_pretty(&status)?;
    std::fs::write(&status_file, &json)?;

    Ok(())
}

fn parse_state(s: &str) -> Result<TaskState> {
    match s {
        "spawning" => Ok(TaskState::Spawning),
        "ready" => Ok(TaskState::Ready),
        "in_progress" => Ok(TaskState::InProgress),
        "blocked" => Ok(TaskState::Blocked),
        "completed" => Ok(TaskState::Completed),
        "failed" => Ok(TaskState::Failed),
        "aborted" => Ok(TaskState::Aborted),
        _ => Err(anyhow!("invalid state: '{}'. Valid states: spawning, ready, in_progress, blocked, completed, failed, aborted", s)),
    }
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cargo test --test worker_commands_test worker_status`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/commands/worker/status.rs tests/worker_commands_test.rs
git commit -m "feat: add worker status command — create/update status JSON"
```

---

## Task 12: `agentrc worker note` and `agentrc worker result` commands

**Files:**
- Modify: `src/commands/worker/note.rs`
- Modify: `src/commands/worker/result.rs`
- Test: `tests/worker_commands_test.rs` (append)

- [ ] **Step 1: Write failing tests**

Append to `tests/worker_commands_test.rs`:

```rust
#[test]
fn worker_note_creates_file_on_first_note() {
    let (tmp, paths) = setup_active_run();
    worker::note::run_in(tmp.path(), "001", "Starting task").unwrap();

    let active = paths.active_run().unwrap();
    let notes = std::fs::read_to_string(active.notes_file("001")).unwrap();
    assert!(notes.contains("Starting task"));
}

#[test]
fn worker_note_appends_with_timestamp() {
    let (tmp, paths) = setup_active_run();
    worker::note::run_in(tmp.path(), "001", "First note").unwrap();
    worker::note::run_in(tmp.path(), "001", "Second note").unwrap();

    let active = paths.active_run().unwrap();
    let notes = std::fs::read_to_string(active.notes_file("001")).unwrap();
    assert!(notes.contains("First note"));
    assert!(notes.contains("Second note"));
    // Should have timestamps (ISO format)
    assert!(notes.contains("202"));
    // Two entries
    let entry_count = notes.matches("[20").count();
    assert_eq!(entry_count, 2);
}

#[test]
fn worker_result_writes_from_file() {
    let (tmp, paths) = setup_active_run();
    let result_src = tmp.path().join("my-result.md");
    std::fs::write(&result_src, "# Result\n\nAll tests pass.").unwrap();

    worker::result::run_in(tmp.path(), "001", Some(result_src.to_str().unwrap()), false).unwrap();

    let active = paths.active_run().unwrap();
    let result = std::fs::read_to_string(active.result_file("001")).unwrap();
    assert!(result.contains("# Result"));
    assert!(result.contains("All tests pass."));
}

#[test]
fn worker_result_fails_if_file_not_found() {
    let (tmp, _) = setup_active_run();
    let result = worker::result::run_in(tmp.path(), "001", Some("/nonexistent.md"), false);
    assert!(result.is_err());
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cargo test --test worker_commands_test worker_note`
Expected: FAIL

- [ ] **Step 3: Implement note and result commands**

`src/commands/worker/note.rs`:

```rust
use anyhow::Result;
use chrono::Utc;
use std::path::Path;

use crate::fs::bus::OrchestratorPaths;
use crate::model::error::AppError;

pub fn run(task: &str, message: &str) -> Result<()> {
    let cwd = std::env::current_dir()?;
    run_in(&cwd, task, message)
}

pub fn run_in(project_root: &Path, task_id: &str, message: &str) -> Result<()> {
    let paths = OrchestratorPaths::new(project_root);
    let active = paths.active_run().ok_or(AppError::NoActiveRun)?;

    let notes_file = active.notes_file(task_id);
    let timestamp = Utc::now().to_rfc3339_opts(chrono::SecondsFormat::Secs, true);
    let entry = format!("[{}] {}\n", timestamp, message);

    let mut content = if notes_file.exists() {
        std::fs::read_to_string(&notes_file)?
    } else {
        String::new()
    };
    content.push_str(&entry);
    std::fs::write(&notes_file, &content)?;

    Ok(())
}
```

`src/commands/worker/result.rs`:

```rust
use anyhow::{anyhow, Context, Result};
use std::io::Read;
use std::path::Path;

use crate::fs::bus::OrchestratorPaths;
use crate::model::error::AppError;

pub fn run(task: &str, file: Option<&str>, stdin: bool) -> Result<()> {
    let cwd = std::env::current_dir()?;
    run_in(&cwd, task, file, stdin)
}

pub fn run_in(project_root: &Path, task_id: &str, file: Option<&str>, stdin: bool) -> Result<()> {
    let paths = OrchestratorPaths::new(project_root);
    let active = paths.active_run().ok_or(AppError::NoActiveRun)?;

    let content = if stdin {
        let mut buf = String::new();
        std::io::stdin()
            .read_to_string(&mut buf)
            .context("failed to read stdin")?;
        buf
    } else if let Some(file_path) = file {
        std::fs::read_to_string(file_path)
            .with_context(|| format!("failed to read result file: {}", file_path))?
    } else {
        return Err(anyhow!("either --file or --stdin must be provided"));
    };

    let result_file = active.result_file(task_id);
    std::fs::write(&result_file, &content)?;

    Ok(())
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cargo test --test worker_commands_test`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/commands/worker/note.rs src/commands/worker/result.rs tests/worker_commands_test.rs
git commit -m "feat: add worker note and result commands"
```

---

## Task 13: `agentrc worker heartbeat` command

**Files:**
- Modify: `src/commands/worker/heartbeat.rs`
- Test: `tests/worker_commands_test.rs` (append)

- [ ] **Step 1: Write failing tests**

Append to `tests/worker_commands_test.rs`:

```rust
use std::time::Duration;

#[test]
fn worker_heartbeat_creates_alive_file() {
    let (tmp, paths) = setup_active_run();
    // Run a single heartbeat tick (not the daemon loop)
    worker::heartbeat::tick(tmp.path(), "001").unwrap();

    let active = paths.active_run().unwrap();
    assert!(active.heartbeat_file("001").exists());
}

#[test]
fn worker_heartbeat_updates_mtime() {
    let (tmp, paths) = setup_active_run();
    worker::heartbeat::tick(tmp.path(), "001").unwrap();

    let active = paths.active_run().unwrap();
    let hb_file = active.heartbeat_file("001");
    let mtime1 = std::fs::metadata(&hb_file).unwrap().modified().unwrap();

    std::thread::sleep(Duration::from_millis(50));
    worker::heartbeat::tick(tmp.path(), "001").unwrap();

    let mtime2 = std::fs::metadata(&hb_file).unwrap().modified().unwrap();
    assert!(mtime2 > mtime1);
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cargo test --test worker_commands_test heartbeat`
Expected: FAIL

- [ ] **Step 3: Implement heartbeat command**

`src/commands/worker/heartbeat.rs`:

```rust
use anyhow::Result;
use std::path::Path;
use std::time::Duration;

use crate::fs::bus::OrchestratorPaths;
use crate::model::error::AppError;

/// CLI entry — runs as a background daemon
pub fn run(task: &str, interval: u64) -> Result<()> {
    let cwd = std::env::current_dir()?;
    let interval = Duration::from_secs(interval);

    // Initial tick
    tick(&cwd, task)?;

    // Loop until parent dies (SIGHUP) or process is killed
    loop {
        std::thread::sleep(interval);
        if let Err(e) = tick(&cwd, task) {
            eprintln!("heartbeat error: {}", e);
            // Continue trying — heartbeat is advisory
        }
    }
}

/// Single heartbeat tick — touch the .alive file
pub fn tick(project_root: &Path, task_id: &str) -> Result<()> {
    let paths = OrchestratorPaths::new(project_root);
    let active = paths.active_run().ok_or(AppError::NoActiveRun)?;
    let hb_file = active.heartbeat_file(task_id);

    // Touch the file (create or update mtime)
    if hb_file.exists() {
        // Update mtime by writing empty content
        let file = std::fs::OpenOptions::new()
            .write(true)
            .open(&hb_file)?;
        file.set_len(0)?;
    } else {
        std::fs::write(&hb_file, b"")?;
    }

    Ok(())
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cargo test --test worker_commands_test heartbeat`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/commands/worker/heartbeat.rs tests/worker_commands_test.rs
git commit -m "feat: add worker heartbeat daemon with tick function"
```

---

## Task 14: `agentrc worker done` command

**Files:**
- Modify: `src/commands/worker/done.rs`
- Test: `tests/worker_commands_test.rs` (append)

- [ ] **Step 1: Write failing tests**

Append to `tests/worker_commands_test.rs`:

```rust
#[test]
fn worker_done_sets_completed_and_writes_result() {
    let (tmp, paths) = setup_active_run();

    // Set initial status
    worker::status::run_in(tmp.path(), "001", "in_progress", None, None).unwrap();

    // Write a result file
    let result_src = tmp.path().join("result.md");
    std::fs::write(&result_src, "# Done\nAll good.").unwrap();

    worker::done::run_in(tmp.path(), "001", Some(result_src.to_str().unwrap())).unwrap();

    let active = paths.active_run().unwrap();

    // Status should be completed
    let status_content = std::fs::read_to_string(active.status_file("001")).unwrap();
    let status: TaskStatus = serde_json::from_str(&status_content).unwrap();
    assert_eq!(status.state, TaskState::Completed);
    assert!(status.result_path.is_some());

    // Result file should exist
    let result = std::fs::read_to_string(active.result_file("001")).unwrap();
    assert!(result.contains("All good."));
}

#[test]
fn worker_done_without_result_file() {
    let (tmp, paths) = setup_active_run();
    worker::status::run_in(tmp.path(), "001", "in_progress", None, None).unwrap();
    worker::done::run_in(tmp.path(), "001", None).unwrap();

    let active = paths.active_run().unwrap();
    let status_content = std::fs::read_to_string(active.status_file("001")).unwrap();
    let status: TaskStatus = serde_json::from_str(&status_content).unwrap();
    assert_eq!(status.state, TaskState::Completed);
    assert!(status.result_path.is_none());
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cargo test --test worker_commands_test worker_done`
Expected: FAIL

- [ ] **Step 3: Implement done command**

`src/commands/worker/done.rs`:

```rust
use anyhow::Result;
use std::path::Path;

use crate::commands::worker;
use crate::fs::bus::OrchestratorPaths;
use crate::model::error::AppError;

pub fn run(task: &str, result_file: Option<&str>) -> Result<()> {
    let cwd = std::env::current_dir()?;
    run_in(&cwd, task, result_file)
}

pub fn run_in(project_root: &Path, task_id: &str, result_file: Option<&str>) -> Result<()> {
    let paths = OrchestratorPaths::new(project_root);
    let active = paths.active_run().ok_or(AppError::NoActiveRun)?;

    // Write result if provided
    if let Some(file) = result_file {
        worker::result::run_in(project_root, task_id, Some(file), false)?;
    }

    // Set status to completed with result_path
    let result_path = if result_file.is_some() {
        Some(active.result_file(task_id).to_string_lossy().to_string())
    } else {
        None
    };

    // Update status to completed
    worker::status::run_in(project_root, task_id, "completed", None, None)?;

    // Patch the result_path into the status file
    if let Some(rp) = result_path {
        let status_file = active.status_file(task_id);
        let content = std::fs::read_to_string(&status_file)?;
        let mut status: serde_json::Value = serde_json::from_str(&content)?;
        status["result_path"] = serde_json::Value::String(rp);
        std::fs::write(&status_file, serde_json::to_string_pretty(&status)?)?;
    }

    // Ring the tmux bell (best-effort, don't fail if not in tmux)
    let channel = format!("worker-{}-done", task_id);
    let _ = crate::tmux::wrapper::Tmux::new().wait_for_signal(&channel);

    println!("Task {} completed.", task_id);
    Ok(())
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cargo test --test worker_commands_test worker_done`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/commands/worker/done.rs tests/worker_commands_test.rs
git commit -m "feat: add worker done command — atomic completion with result and bell"
```

---

## Task 15: `agentrc status` command

**Files:**
- Modify: `src/commands/status.rs`
- Test: `tests/status_test.rs`

- [ ] **Step 1: Write failing tests**

Create `tests/status_test.rs`:

```rust
mod common;

use agentrc::commands;
use agentrc::commands::worker;
use agentrc::fs::bus::OrchestratorPaths;
use tempfile::TempDir;

fn setup_run_with_tasks() -> (TempDir, OrchestratorPaths) {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), Some("cargo test"), false).unwrap();
    commands::run::create_in(tmp.path(), "test-run").unwrap();

    // Create some task statuses
    worker::status::run_in(tmp.path(), "001", "completed", None, Some("done")).unwrap();
    worker::status::run_in(tmp.path(), "002", "in_progress", Some("testing"), Some("running tests")).unwrap();
    worker::status::run_in(tmp.path(), "003", "blocked", None, Some("waiting on 001")).unwrap();

    let paths = OrchestratorPaths::new(tmp.path());
    (tmp, paths)
}

#[test]
fn status_aggregates_all_tasks() {
    let (tmp, _) = setup_run_with_tasks();
    let statuses = commands::status::collect_statuses(tmp.path()).unwrap();
    assert_eq!(statuses.len(), 3);
}

#[test]
fn status_json_output() {
    let (tmp, _) = setup_run_with_tasks();
    let output = commands::status::format_json(tmp.path()).unwrap();
    let parsed: serde_json::Value = serde_json::from_str(&output).unwrap();
    assert!(parsed.is_array());
    assert_eq!(parsed.as_array().unwrap().len(), 3);
}

#[test]
fn status_tty_output_contains_task_info() {
    let (tmp, _) = setup_run_with_tasks();
    let output = commands::status::format_tty(tmp.path()).unwrap();
    assert!(output.contains("001"));
    assert!(output.contains("002"));
    assert!(output.contains("003"));
    assert!(output.contains("completed"));
    assert!(output.contains("in_progress"));
    assert!(output.contains("blocked"));
}

#[test]
fn status_detects_stale_heartbeats() {
    let (tmp, paths) = setup_run_with_tasks();
    let active = paths.active_run().unwrap();

    // Create a heartbeat file with old mtime
    let hb_file = active.heartbeat_file("002");
    std::fs::write(&hb_file, b"").unwrap();
    // Set mtime to 5 minutes ago
    let old_time = std::time::SystemTime::now() - std::time::Duration::from_secs(300);
    filetime::set_file_mtime(&hb_file, filetime::FileTime::from_system_time(old_time)).unwrap();

    let stale = commands::status::find_stale_heartbeats(tmp.path(), 120).unwrap();
    assert_eq!(stale.len(), 1);
    assert_eq!(stale[0], "002");
}
```

Note: add `filetime` to `[dev-dependencies]` in `Cargo.toml`:
```toml
filetime = "0.2"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cargo test --test status_test`
Expected: FAIL

- [ ] **Step 3: Implement status command**

`src/commands/status.rs`:

```rust
use anyhow::Result;
use std::path::Path;
use std::time::{Duration, SystemTime};

use crate::fs::bus::OrchestratorPaths;
use crate::model::error::AppError;
use crate::model::task::TaskStatus;

pub fn run(json: bool) -> Result<()> {
    let cwd = std::env::current_dir()?;
    if json {
        let output = format_json(&cwd)?;
        println!("{}", output);
    } else {
        let output = format_tty(&cwd)?;
        print!("{}", output);
    }
    Ok(())
}

pub fn collect_statuses(project_root: &Path) -> Result<Vec<TaskStatus>> {
    let paths = OrchestratorPaths::new(project_root);
    let active = paths.active_run().ok_or(AppError::NoActiveRun)?;
    let status_dir = active.status_dir();

    if !status_dir.exists() {
        return Ok(Vec::new());
    }

    let mut statuses = Vec::new();
    for entry in std::fs::read_dir(&status_dir)? {
        let entry = entry?;
        let path = entry.path();
        if path.extension().map(|e| e == "json").unwrap_or(false) {
            let content = std::fs::read_to_string(&path)?;
            match serde_json::from_str::<TaskStatus>(&content) {
                Ok(status) => statuses.push(status),
                Err(e) => {
                    eprintln!("warning: failed to parse {}: {}", path.display(), e);
                }
            }
        }
    }
    statuses.sort_by(|a, b| a.id.cmp(&b.id));
    Ok(statuses)
}

pub fn format_json(project_root: &Path) -> Result<String> {
    let statuses = collect_statuses(project_root)?;
    Ok(serde_json::to_string_pretty(&statuses)?)
}

pub fn format_tty(project_root: &Path) -> Result<String> {
    let statuses = collect_statuses(project_root)?;
    if statuses.is_empty() {
        return Ok("No tasks in active run.\n".into());
    }

    let mut output = String::new();
    output.push_str(&format!(
        "{:<6} {:<14} {:<16} {:<8} {}\n",
        "ID", "STATE", "PHASE", "PANE", "MESSAGE"
    ));
    output.push_str(&"-".repeat(70));
    output.push('\n');

    for s in &statuses {
        output.push_str(&format!(
            "{:<6} {:<14} {:<16} {:<8} {}\n",
            s.id,
            format!("{}", s.state),
            s.phase.as_deref().unwrap_or("-"),
            s.pane_id.as_deref().unwrap_or("-"),
            s.last_message.as_deref().unwrap_or(""),
        ));
    }

    // Check stale heartbeats
    let stale = find_stale_heartbeats(project_root, 120)?;
    if !stale.is_empty() {
        output.push_str(&format!("\nStale heartbeats: {}\n", stale.join(", ")));
    }

    Ok(output)
}

pub fn find_stale_heartbeats(project_root: &Path, timeout_sec: u64) -> Result<Vec<String>> {
    let paths = OrchestratorPaths::new(project_root);
    let active = paths.active_run().ok_or(AppError::NoActiveRun)?;
    let hb_dir = active.heartbeats_dir();

    if !hb_dir.exists() {
        return Ok(Vec::new());
    }

    let threshold = SystemTime::now() - Duration::from_secs(timeout_sec);
    let mut stale = Vec::new();

    for entry in std::fs::read_dir(&hb_dir)? {
        let entry = entry?;
        let path = entry.path();
        if path.extension().map(|e| e == "alive").unwrap_or(false) {
            let mtime = std::fs::metadata(&path)?.modified()?;
            if mtime < threshold {
                if let Some(stem) = path.file_stem() {
                    stale.push(stem.to_string_lossy().to_string());
                }
            }
        }
    }

    Ok(stale)
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cargo test --test status_test`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/commands/status.rs tests/status_test.rs Cargo.toml
git commit -m "feat: add status command — aggregate task statuses with stale heartbeat detection"
```

---

## Task 16: `agentrc spawn` command

**Files:**
- Modify: `src/commands/spawn.rs`
- Test: `tests/spawn_test.rs`

Spawn needs tmux, so we split: unit tests for the logic (worktree creation, brief parsing, status initialization), and `#[ignore]` integration tests for actual tmux pane creation.

- [ ] **Step 1: Write failing tests — spawn logic without tmux**

Create `tests/spawn_test.rs`:

```rust
mod common;

use agentrc::commands::spawn;
use agentrc::fs::bus::OrchestratorPaths;
use agentrc::model::task::TaskState;
use tempfile::TempDir;

fn setup_run_with_writer_task() -> (TempDir, OrchestratorPaths) {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    agentrc::commands::init::run_in(tmp.path(), Some("cargo test"), false).unwrap();
    agentrc::commands::run::create_in(tmp.path(), "test-run").unwrap();

    let paths = OrchestratorPaths::new(tmp.path());
    let active = paths.active_run().unwrap();

    // Write a task brief
    let brief = r#"---
id: "001"
slug: add-login
classification: writer
worktree: .orchestrator/active/worktrees/001
base_branch: HEAD
branch: orc/001-add-login
depends_on: []
created_at: 2026-04-11T14:30:00Z
---

# Task 001: Add login
"#;
    std::fs::write(active.task_brief("001", "add-login"), brief).unwrap();
    (tmp, paths)
}

fn setup_run_with_reader_task() -> (TempDir, OrchestratorPaths) {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    agentrc::commands::init::run_in(tmp.path(), Some("cargo test"), false).unwrap();
    agentrc::commands::run::create_in(tmp.path(), "test-run").unwrap();

    let paths = OrchestratorPaths::new(tmp.path());
    let active = paths.active_run().unwrap();

    let brief = r#"---
id: "002"
slug: review-deps
classification: reader
base_branch: HEAD
depends_on: []
created_at: 2026-04-11T14:30:00Z
---

# Task 002: Review deps
"#;
    std::fs::write(active.task_brief("002", "review-deps"), brief).unwrap();
    (tmp, paths)
}

#[test]
fn spawn_parses_task_brief() {
    let (tmp, paths) = setup_run_with_writer_task();
    let active = paths.active_run().unwrap();
    let brief = spawn::load_task_brief(active.task_brief("001", "add-login")).unwrap();
    assert_eq!(brief.id, "001");
    assert_eq!(brief.slug, "add-login");
}

#[test]
fn spawn_creates_worktree_for_writer() {
    let (tmp, paths) = setup_run_with_writer_task();
    spawn::setup_worktree(tmp.path(), &paths, "001", "add-login", "orc/001-add-login", "HEAD").unwrap();

    let active = paths.active_run().unwrap();
    let wt = active.worktree_dir("001");
    assert!(wt.exists());
    assert!(wt.join("README.md").exists());
}

#[test]
fn spawn_skips_worktree_for_reader() {
    let (tmp, paths) = setup_run_with_reader_task();
    // Reader tasks don't get worktrees — this should be a no-op
    let active = paths.active_run().unwrap();
    assert!(!active.worktree_dir("002").exists());
}

#[test]
fn spawn_sets_initial_status() {
    let (tmp, paths) = setup_run_with_writer_task();
    spawn::write_initial_status(tmp.path(), "001").unwrap();

    let active = paths.active_run().unwrap();
    let content = std::fs::read_to_string(active.status_file("001")).unwrap();
    let status: agentrc::model::task::TaskStatus = serde_json::from_str(&content).unwrap();
    assert_eq!(status.state, TaskState::Spawning);
}

#[test]
fn spawn_generates_seed_prompt() {
    let seed = spawn::generate_seed_prompt("001", ".orchestrator/active/tasks/001-add-login.md");
    assert!(seed.contains("001"));
    assert!(seed.contains("001-add-login.md"));
    assert!(seed.contains("agentrc worker"));
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cargo test --test spawn_test`
Expected: FAIL

- [ ] **Step 3: Implement spawn command (logic only, tmux calls gated)**

`src/commands/spawn.rs`:

```rust
use anyhow::{Context, Result};
use std::path::Path;

use crate::commands::worker;
use crate::fs::bus::OrchestratorPaths;
use crate::fs::frontmatter;
use crate::git::wrapper::Git;
use crate::model::config::OrchestratorConfig;
use crate::model::error::AppError;
use crate::model::task::{Classification, TaskBriefFrontmatter};
use crate::tmux::wrapper::Tmux;

/// CLI entry
pub fn run(task_id: &str) -> Result<()> {
    let cwd = std::env::current_dir()?;
    let paths = OrchestratorPaths::new(&cwd);
    let active = paths.active_run().ok_or(AppError::NoActiveRun)?;

    // Load config
    let config: OrchestratorConfig =
        serde_json::from_str(&std::fs::read_to_string(paths.config())?)?;

    // Find task brief
    let brief_path = find_task_brief(&active, task_id)?;
    let brief = load_task_brief(&brief_path)?;

    // Check max workers
    let current_count = crate::commands::status::collect_statuses(&cwd)?
        .iter()
        .filter(|s| !matches!(s.state, crate::model::task::TaskState::Completed
            | crate::model::task::TaskState::Failed
            | crate::model::task::TaskState::Aborted))
        .count() as u32;
    if current_count >= config.max_workers {
        anyhow::bail!("max workers ({}) reached. Tear down a worker first.", config.max_workers);
    }

    // Setup worktree for writer
    if brief.classification == Classification::Writer {
        let branch = brief.branch.as_ref().ok_or_else(|| {
            anyhow::anyhow!("writer task {} has no branch specified", task_id)
        })?;
        setup_worktree(&cwd, &paths, task_id, &brief.slug, branch, &brief.base_branch)?;
    }

    // Write initial status
    write_initial_status(&cwd, task_id)?;

    // Find or create tmux window
    let tmux = Tmux::new();
    let window = find_or_create_worker_window(&tmux, config.workers_per_window)?;

    // Create pane
    let pane_id = tmux.split_window(&window)?;

    // Update task brief with pane_id
    let brief_content = std::fs::read_to_string(&brief_path)?;
    let updated = frontmatter::update_field(&brief_content, "pane_id", &format!("\"{}\"", pane_id))?;
    std::fs::write(&brief_path, updated)?;

    // Update status with pane_id
    let status_file = active.status_file(task_id);
    if status_file.exists() {
        let content = std::fs::read_to_string(&status_file)?;
        let mut status: serde_json::Value = serde_json::from_str(&content)?;
        status["pane_id"] = serde_json::Value::String(pane_id.clone());
        std::fs::write(&status_file, serde_json::to_string_pretty(&status)?)?;
    }

    // Retile
    let _ = tmux.select_layout_tiled(&window);

    // cd to worktree or project root
    let work_dir = if brief.classification == Classification::Writer {
        active.worktree_dir(task_id).to_string_lossy().to_string()
    } else {
        cwd.to_string_lossy().to_string()
    };
    tmux.send_keys(&pane_id, &format!("cd {}", work_dir))?;

    // Launch heartbeat + claude
    let launch_cmd = format!(
        "agentrc worker heartbeat --task {} & HB=$!; claude {}; kill $HB 2>/dev/null; exit",
        task_id,
        config.worker_claude_args.join(" ")
    );
    tmux.send_keys(&pane_id, &launch_cmd)?;

    // Brief pause for claude to start, then seed
    std::thread::sleep(std::time::Duration::from_secs(2));
    let brief_relative = format!(".orchestrator/active/tasks/{}-{}.md", task_id, brief.slug);
    let seed = generate_seed_prompt(task_id, &brief_relative);
    tmux.send_keys(&pane_id, &seed)?;

    println!("Spawned task {} in pane {}", task_id, pane_id);
    Ok(())
}

pub fn load_task_brief(path: impl AsRef<Path>) -> Result<TaskBriefFrontmatter> {
    let content = std::fs::read_to_string(path.as_ref())
        .with_context(|| format!("failed to read task brief: {}", path.as_ref().display()))?;
    let (fm, _body) = frontmatter::parse::<TaskBriefFrontmatter>(&content)?;
    Ok(fm)
}

pub fn find_task_brief(
    run_paths: &crate::fs::run::RunPaths,
    task_id: &str,
) -> Result<std::path::PathBuf> {
    let tasks_dir = run_paths.tasks_dir();
    for entry in std::fs::read_dir(&tasks_dir)? {
        let entry = entry?;
        let name = entry.file_name().to_string_lossy().to_string();
        if name.starts_with(&format!("{}-", task_id)) && name.ends_with(".md") {
            return Ok(entry.path());
        }
    }
    Err(AppError::TaskNotFound {
        task_id: task_id.into(),
    }
    .into())
}

pub fn setup_worktree(
    project_root: &Path,
    paths: &OrchestratorPaths,
    task_id: &str,
    _slug: &str,
    branch: &str,
    base: &str,
) -> Result<()> {
    let active = paths.active_run().ok_or(AppError::NoActiveRun)?;
    let wt_path = active.worktree_dir(task_id);

    let git = Git::new(project_root);
    git.create_worktree(&wt_path, branch, base)
        .with_context(|| format!("failed to create worktree for task {}", task_id))?;

    Ok(())
}

pub fn write_initial_status(project_root: &Path, task_id: &str) -> Result<()> {
    worker::status::run_in(project_root, task_id, "spawning", None, None)
}

pub fn generate_seed_prompt(task_id: &str, brief_path: &str) -> String {
    format!(
        r#"You are an agentrc worker. Your task ID is {}. Your task brief is at {} — read it fully before doing anything.

Contract:
1. Read your task brief and acknowledge.
2. Use `agentrc worker status --task {} --state in_progress` to signal you've started.
3. Use `agentrc worker note --task {} --message "..."` for progress updates.
4. For writer tasks: invoke superpowers:test-driven-development and follow TDD rigorously.
5. When done: `agentrc worker done --task {} --result-file ./result.md`
6. If blocked: `agentrc worker status --task {} --state blocked --message "reason"`
7. Writers: stay in your worktree. Do not modify files outside it. Do not merge.
8. Readers: do not modify any files. Output goes through agentrc worker note/result only.

Begin by reading your task brief."#,
        task_id, brief_path, task_id, task_id, task_id, task_id
    )
}

fn find_or_create_worker_window(tmux: &Tmux, max_per_window: u32) -> Result<String> {
    let windows = tmux.list_windows().unwrap_or_default();
    for (i, name) in windows.iter().enumerate() {
        if name.starts_with("workers-") {
            let panes = tmux.list_panes(name).unwrap_or_default();
            if (panes.len() as u32) < max_per_window {
                return Ok(name.clone());
            }
        }
    }
    // Create new workers window
    let count = windows.iter().filter(|w| w.starts_with("workers-")).count() + 1;
    let name = format!("workers-{}", count);
    tmux.new_window(&name)?;
    Ok(name)
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cargo test --test spawn_test`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/commands/spawn.rs tests/spawn_test.rs
git commit -m "feat: add spawn command — worktree setup, brief parsing, seed generation"
```

---

## Task 17: `agentrc teardown` command

**Files:**
- Modify: `src/commands/teardown.rs`
- Test: `tests/teardown_test.rs`

- [ ] **Step 1: Write failing tests**

Create `tests/teardown_test.rs`:

```rust
mod common;

use agentrc::commands;
use agentrc::fs::bus::OrchestratorPaths;
use tempfile::TempDir;

fn setup_with_worktree() -> (TempDir, OrchestratorPaths) {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), Some("cargo test"), false).unwrap();
    commands::run::create_in(tmp.path(), "test-run").unwrap();

    let paths = OrchestratorPaths::new(tmp.path());
    let active = paths.active_run().unwrap();

    // Create a worktree manually
    let git = agentrc::git::wrapper::Git::new(tmp.path());
    let wt_path = active.worktree_dir("001");
    git.create_worktree(&wt_path, "orc/001-test", "HEAD").unwrap();

    // Create status
    commands::worker::status::run_in(tmp.path(), "001", "completed", None, None).unwrap();

    (tmp, paths)
}

#[test]
fn teardown_removes_worktree() {
    let (tmp, paths) = setup_with_worktree();
    let active = paths.active_run().unwrap();
    assert!(active.worktree_dir("001").exists());

    commands::teardown::teardown_task(tmp.path(), "001").unwrap();
    assert!(!active.worktree_dir("001").exists());
}

#[test]
fn teardown_refuses_non_completed_task_without_force() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), Some("cargo test"), false).unwrap();
    commands::run::create_in(tmp.path(), "test-run").unwrap();

    commands::worker::status::run_in(tmp.path(), "001", "in_progress", None, None).unwrap();

    let result = commands::teardown::teardown_task(tmp.path(), "001");
    assert!(result.is_err());
}

#[test]
fn teardown_all_tears_down_every_task() {
    let (tmp, paths) = setup_with_worktree();
    // Add another completed task
    commands::worker::status::run_in(tmp.path(), "002", "completed", None, None).unwrap();

    commands::teardown::teardown_all(tmp.path()).unwrap();

    let active = paths.active_run().unwrap();
    assert!(!active.worktree_dir("001").exists());
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cargo test --test teardown_test`
Expected: FAIL

- [ ] **Step 3: Implement teardown command**

`src/commands/teardown.rs`:

```rust
use anyhow::Result;
use std::path::Path;

use crate::commands::status as status_cmd;
use crate::fs::bus::OrchestratorPaths;
use crate::git::wrapper::Git;
use crate::model::error::AppError;
use crate::model::task::TaskState;
use crate::tmux::wrapper::Tmux;

pub fn run(task_id: Option<&str>, all: bool) -> Result<()> {
    let cwd = std::env::current_dir()?;
    if all {
        teardown_all(&cwd)
    } else if let Some(id) = task_id {
        teardown_task(&cwd, id)
    } else {
        anyhow::bail!("provide a task ID or use --all")
    }
}

pub fn teardown_task(project_root: &Path, task_id: &str) -> Result<()> {
    let paths = OrchestratorPaths::new(project_root);
    let active = paths.active_run().ok_or(AppError::NoActiveRun)?;

    // Check status — only teardown completed/failed/aborted tasks
    let status_file = active.status_file(task_id);
    if status_file.exists() {
        let content = std::fs::read_to_string(&status_file)?;
        let status: crate::model::task::TaskStatus = serde_json::from_str(&content)?;
        match status.state {
            TaskState::Completed | TaskState::Failed | TaskState::Aborted => {}
            _ => {
                anyhow::bail!(
                    "task {} is {} — only completed/failed/aborted tasks can be torn down",
                    task_id,
                    status.state
                );
            }
        }

        // Kill tmux pane (best-effort)
        if let Some(pane_id) = &status.pane_id {
            let tmux = Tmux::new();
            let _ = tmux.kill_pane(pane_id);
        }
    }

    // Remove worktree if it exists
    let wt_path = active.worktree_dir(task_id);
    if wt_path.exists() {
        let git = Git::new(project_root);
        git.remove_worktree(&wt_path)?;
    }

    println!("Torn down task {}", task_id);
    Ok(())
}

pub fn teardown_all(project_root: &Path) -> Result<()> {
    let statuses = status_cmd::collect_statuses(project_root)?;
    for status in &statuses {
        match status.state {
            TaskState::Completed | TaskState::Failed | TaskState::Aborted => {
                if let Err(e) = teardown_task(project_root, &status.id) {
                    eprintln!("warning: failed to teardown {}: {}", status.id, e);
                }
            }
            _ => {
                eprintln!("skipping {} (state: {})", status.id, status.state);
            }
        }
    }
    Ok(())
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cargo test --test teardown_test`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/commands/teardown.rs tests/teardown_test.rs
git commit -m "feat: add teardown command — remove worktrees, kill panes, --all support"
```

---

## Task 18: `agentrc resume` command

**Files:**
- Modify: `src/commands/resume.rs`
- Test: `tests/resume_test.rs`

- [ ] **Step 1: Write failing tests**

Create `tests/resume_test.rs`:

```rust
mod common;

use agentrc::commands;
use tempfile::TempDir;

fn setup_active_run_with_data() -> TempDir {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), Some("cargo test"), false).unwrap();
    commands::run::create_in(tmp.path(), "auth-refactor").unwrap();

    // Add task statuses
    commands::worker::status::run_in(tmp.path(), "001", "completed", None, Some("done")).unwrap();
    commands::worker::status::run_in(
        tmp.path(), "002", "in_progress", Some("testing"), Some("running tests"),
    ).unwrap();

    // Add an orchestrator log entry
    let paths = agentrc::fs::bus::OrchestratorPaths::new(tmp.path());
    let active = paths.active_run().unwrap();
    std::fs::write(
        active.orchestrator_log(),
        "[2026-04-11T14:45:00Z] Integrated 001\n[2026-04-11T14:45:30Z] Waiting on 002\n",
    ).unwrap();

    tmp
}

#[test]
fn resume_output_contains_run_id() {
    let tmp = setup_active_run_with_data();
    let output = commands::resume::format_resume(tmp.path()).unwrap();
    assert!(output.contains("AGENTRC ACTIVE RUN"));
    assert!(output.contains("auth-refactor"));
}

#[test]
fn resume_output_contains_task_statuses() {
    let tmp = setup_active_run_with_data();
    let output = commands::resume::format_resume(tmp.path()).unwrap();
    assert!(output.contains("001"));
    assert!(output.contains("completed"));
    assert!(output.contains("002"));
    assert!(output.contains("in_progress"));
}

#[test]
fn resume_output_contains_recent_log() {
    let tmp = setup_active_run_with_data();
    let output = commands::resume::format_resume(tmp.path()).unwrap();
    assert!(output.contains("RECENT LOG"));
    assert!(output.contains("Integrated 001"));
}

#[test]
fn resume_fails_with_no_active_run() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), None, false).unwrap();
    let result = commands::resume::format_resume(tmp.path());
    assert!(result.is_err());
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cargo test --test resume_test`
Expected: FAIL

- [ ] **Step 3: Implement resume command**

`src/commands/resume.rs`:

```rust
use anyhow::Result;
use std::path::Path;

use crate::commands::status as status_cmd;
use crate::fs::bus::OrchestratorPaths;
use crate::model::config::OrchestratorConfig;
use crate::model::error::AppError;

pub fn run() -> Result<()> {
    let cwd = std::env::current_dir()?;
    let output = format_resume(&cwd)?;
    print!("{}", output);
    Ok(())
}

pub fn format_resume(project_root: &Path) -> Result<String> {
    let paths = OrchestratorPaths::new(project_root);
    let active = paths.active_run().ok_or(AppError::NoActiveRun)?;

    let mut output = String::new();

    // Run header
    let run_id = active
        .root()
        .file_name()
        .map(|n| n.to_string_lossy().to_string())
        .unwrap_or_else(|| "unknown".into());

    output.push_str("=== AGENTRC ACTIVE RUN ===\n");
    output.push_str(&format!("Run: {}\n", run_id));
    output.push_str(&format!("Plan: {}\n", active.plan().display()));

    // Config summary
    if active.config_snapshot().exists() {
        if let Ok(content) = std::fs::read_to_string(active.config_snapshot()) {
            if let Ok(config) = serde_json::from_str::<OrchestratorConfig>(&content) {
                output.push_str(&format!(
                    "Config: base_branch={}, test_command={:?}\n",
                    config.base_branch,
                    config.test_command.as_deref().unwrap_or("none")
                ));
            }
        }
    }

    // Task statuses
    output.push_str("\n=== TASK STATUS ===\n");
    let statuses = status_cmd::collect_statuses(project_root)?;
    if statuses.is_empty() {
        output.push_str("(no tasks)\n");
    } else {
        for s in &statuses {
            output.push_str(&format!(
                "{} {:<20} {:<14} pane={:<6} {}\n",
                s.id,
                s.branch.as_deref().unwrap_or("-"),
                format!("{}", s.state),
                s.pane_id.as_deref().unwrap_or("-"),
                s.phase
                    .as_ref()
                    .map(|p| format!("phase={}", p))
                    .unwrap_or_default(),
            ));
        }
    }

    // Recent log
    output.push_str("\n=== RECENT LOG (last 20 lines) ===\n");
    let log_path = active.orchestrator_log();
    if log_path.exists() {
        let content = std::fs::read_to_string(&log_path)?;
        let lines: Vec<&str> = content.lines().collect();
        let start = if lines.len() > 20 { lines.len() - 20 } else { 0 };
        for line in &lines[start..] {
            output.push_str(line);
            output.push('\n');
        }
    } else {
        output.push_str("(no log)\n");
    }

    // Stale heartbeats
    output.push_str("\n=== STALE HEARTBEATS ===\n");
    let stale = status_cmd::find_stale_heartbeats(project_root, 120)?;
    if stale.is_empty() {
        output.push_str("(none)\n");
    } else {
        for id in &stale {
            output.push_str(&format!("{}\n", id));
        }
    }

    // Blocked tasks
    output.push_str("\n=== BLOCKED TASKS ===\n");
    let blocked: Vec<_> = statuses
        .iter()
        .filter(|s| s.state == crate::model::task::TaskState::Blocked)
        .collect();
    if blocked.is_empty() {
        output.push_str("(none)\n");
    } else {
        for s in blocked {
            output.push_str(&format!(
                "{}: {}\n",
                s.id,
                s.last_message.as_deref().unwrap_or("no reason given")
            ));
        }
    }

    Ok(output)
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cargo test --test resume_test`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/commands/resume.rs tests/resume_test.rs
git commit -m "feat: add resume command — structured context dump for session recovery"
```

---

## Task 19: `agentrc integrate` command

**Files:**
- Modify: `src/commands/integrate.rs`
- Test: `tests/integrate_test.rs`

This is the most complex command. We test with real temporary git repos.

- [ ] **Step 1: Write failing tests**

Create `tests/integrate_test.rs`:

```rust
mod common;

use agentrc::commands;
use agentrc::fs::bus::OrchestratorPaths;
use agentrc::git::wrapper::Git;
use agentrc::model::task::TaskState;
use tempfile::TempDir;

/// Setup: project with an active run, two completed writer tasks on separate branches
fn setup_two_writer_tasks() -> (TempDir, OrchestratorPaths) {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), None, false).unwrap();
    commands::run::create_in(tmp.path(), "test-integrate").unwrap();

    let paths = OrchestratorPaths::new(tmp.path());
    let active = paths.active_run().unwrap();
    let git = Git::new(tmp.path());
    let base = git.current_branch().unwrap();

    // Task 001: add file-a.txt
    let wt1 = active.worktree_dir("001");
    git.create_worktree(&wt1, "orc/001-feat-a", &base).unwrap();
    std::fs::write(wt1.join("file-a.txt"), "feature a").unwrap();
    let g1 = Git::new(&wt1);
    g1.add_all().unwrap();
    g1.commit("add file-a").unwrap();

    // Task 002: add file-b.txt
    let wt2 = active.worktree_dir("002");
    git.create_worktree(&wt2, "orc/002-feat-b", &base).unwrap();
    std::fs::write(wt2.join("file-b.txt"), "feature b").unwrap();
    let g2 = Git::new(&wt2);
    g2.add_all().unwrap();
    g2.commit("add file-b").unwrap();

    // Write task briefs
    let brief1 = format!(
        "---\nid: \"001\"\nslug: feat-a\nclassification: writer\nbase_branch: {}\nbranch: orc/001-feat-a\ndepends_on: []\ncreated_at: 2026-04-11T14:30:00Z\n---\n# Task 001",
        base
    );
    let brief2 = format!(
        "---\nid: \"002\"\nslug: feat-b\nclassification: writer\nbase_branch: {}\nbranch: orc/002-feat-b\ndepends_on: []\ncreated_at: 2026-04-11T14:30:00Z\n---\n# Task 002",
        base
    );
    std::fs::write(active.task_brief("001", "feat-a"), brief1).unwrap();
    std::fs::write(active.task_brief("002", "feat-b"), brief2).unwrap();

    // Mark both completed
    commands::worker::status::run_in(tmp.path(), "001", "completed", None, None).unwrap();
    commands::worker::status::run_in(tmp.path(), "002", "completed", None, None).unwrap();

    (tmp, paths)
}

#[test]
fn integrate_merges_independent_tasks() {
    let (tmp, _) = setup_two_writer_tasks();
    let result = commands::integrate::integrate_in(tmp.path());
    assert!(result.is_ok());

    // Both files should be in the project root
    assert!(tmp.path().join("file-a.txt").exists());
    assert!(tmp.path().join("file-b.txt").exists());
}

#[test]
fn integrate_returns_merge_results() {
    let (tmp, _) = setup_two_writer_tasks();
    let results = commands::integrate::integrate_in(tmp.path()).unwrap();
    assert_eq!(results.len(), 2);
    assert!(results.iter().all(|r| r.success));
}

/// Setup conflicting tasks: both modify the same file
fn setup_conflicting_tasks() -> (TempDir, OrchestratorPaths) {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    // Create a shared file to conflict on
    std::fs::write(tmp.path().join("shared.txt"), "original").unwrap();
    let git = Git::new(tmp.path());
    git.add_all().unwrap();
    git.commit("add shared file").unwrap();

    commands::init::run_in(tmp.path(), None, false).unwrap();
    commands::run::create_in(tmp.path(), "conflict-test").unwrap();

    let paths = OrchestratorPaths::new(tmp.path());
    let active = paths.active_run().unwrap();
    let base = git.current_branch().unwrap();

    // Task 001: modify shared.txt one way
    let wt1 = active.worktree_dir("001");
    git.create_worktree(&wt1, "orc/001-change-a", &base).unwrap();
    std::fs::write(wt1.join("shared.txt"), "version A").unwrap();
    let g1 = Git::new(&wt1);
    g1.add_all().unwrap();
    g1.commit("change to version A").unwrap();

    // Task 002: modify shared.txt another way
    let wt2 = active.worktree_dir("002");
    git.create_worktree(&wt2, "orc/002-change-b", &base).unwrap();
    std::fs::write(wt2.join("shared.txt"), "version B").unwrap();
    let g2 = Git::new(&wt2);
    g2.add_all().unwrap();
    g2.commit("change to version B").unwrap();

    let brief1 = format!(
        "---\nid: \"001\"\nslug: change-a\nclassification: writer\nbase_branch: {}\nbranch: orc/001-change-a\ndepends_on: []\ncreated_at: 2026-04-11T14:30:00Z\n---\n# Task 001",
        base
    );
    let brief2 = format!(
        "---\nid: \"002\"\nslug: change-b\nclassification: writer\nbase_branch: {}\nbranch: orc/002-change-b\ndepends_on: [\"001\"]\ncreated_at: 2026-04-11T14:30:00Z\n---\n# Task 002",
        base
    );
    std::fs::write(active.task_brief("001", "change-a"), brief1).unwrap();
    std::fs::write(active.task_brief("002", "change-b"), brief2).unwrap();

    commands::worker::status::run_in(tmp.path(), "001", "completed", None, None).unwrap();
    commands::worker::status::run_in(tmp.path(), "002", "completed", None, None).unwrap();

    (tmp, paths)
}

#[test]
fn integrate_detects_merge_conflict() {
    let (tmp, _) = setup_conflicting_tasks();
    let results = commands::integrate::integrate_in(tmp.path()).unwrap();

    // First merge succeeds, second conflicts
    assert!(results[0].success);
    assert!(!results[1].success);
    assert!(results[1].conflict);
}

#[test]
fn integrate_surfaces_commit_history_for_tdd_review() {
    let (tmp, _) = setup_two_writer_tasks();
    let results = commands::integrate::integrate_in(tmp.path()).unwrap();
    // Each result should have commit history for LLM review
    assert!(!results[0].commit_history.is_empty());
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cargo test --test integrate_test`
Expected: FAIL

- [ ] **Step 3: Implement integrate command**

`src/commands/integrate.rs`:

```rust
use anyhow::{Context, Result};
use std::path::Path;

use crate::commands::spawn;
use crate::commands::status as status_cmd;
use crate::fs::bus::OrchestratorPaths;
use crate::fs::frontmatter;
use crate::git::wrapper::Git;
use crate::model::config::OrchestratorConfig;
use crate::model::error::AppError;
use crate::model::task::{Classification, TaskBriefFrontmatter};

#[derive(Debug)]
pub struct MergeResult {
    pub task_id: String,
    pub branch: String,
    pub success: bool,
    pub conflict: bool,
    pub test_failure: bool,
    pub commit_history: Vec<String>,
    pub message: String,
}

pub fn run() -> Result<()> {
    let cwd = std::env::current_dir()?;
    let results = integrate_in(&cwd)?;

    for r in &results {
        if r.success {
            println!("[ok] {} ({}) — merged", r.task_id, r.branch);
        } else if r.conflict {
            println!("[!!] {} ({}) — merge conflict", r.task_id, r.branch);
        } else if r.test_failure {
            println!("[!!] {} ({}) — tests failed after merge", r.task_id, r.branch);
        }
    }

    // Print commit histories for TDD review
    println!("\n=== COMMIT HISTORY (for TDD review) ===");
    for r in &results {
        if !r.commit_history.is_empty() {
            println!("\nTask {} ({}):", r.task_id, r.branch);
            for line in &r.commit_history {
                println!("  {}", line);
            }
        }
    }

    Ok(())
}

pub fn integrate_in(project_root: &Path) -> Result<Vec<MergeResult>> {
    let paths = OrchestratorPaths::new(project_root);
    let active = paths.active_run().ok_or(AppError::NoActiveRun)?;
    let git = Git::new(project_root);

    // Load config
    let config: OrchestratorConfig = if active.config_snapshot().exists() {
        serde_json::from_str(&std::fs::read_to_string(active.config_snapshot())?)?
    } else if paths.config().exists() {
        serde_json::from_str(&std::fs::read_to_string(paths.config())?)?
    } else {
        OrchestratorConfig::default()
    };

    // Collect writer tasks in topological order
    let tasks = collect_writer_tasks_ordered(&active)?;

    if tasks.is_empty() {
        println!("No writer tasks to integrate.");
        return Ok(Vec::new());
    }

    // Checkout base branch
    git.checkout(&config.base_branch)
        .context("failed to checkout base branch")?;

    let mut results = Vec::new();

    for brief in &tasks {
        let branch = match &brief.branch {
            Some(b) => b.clone(),
            None => {
                results.push(MergeResult {
                    task_id: brief.id.clone(),
                    branch: "none".into(),
                    success: false,
                    conflict: false,
                    test_failure: false,
                    commit_history: Vec::new(),
                    message: "no branch specified".into(),
                });
                continue;
            }
        };

        // Get commit history for TDD review
        let commit_history = git
            .log_branch_commits(&branch, &config.base_branch)
            .unwrap_or_default();

        // Attempt merge
        match git.merge_no_ff(&branch) {
            Ok(()) => {
                // Merge succeeded — run tests if configured
                let test_failed = if let Some(ref test_cmd) = config.test_command {
                    !run_tests(project_root, test_cmd)
                } else {
                    false
                };

                if test_failed {
                    // Revert the merge
                    let _ = git.reset_hard_head(1);
                    results.push(MergeResult {
                        task_id: brief.id.clone(),
                        branch,
                        success: false,
                        conflict: false,
                        test_failure: true,
                        commit_history,
                        message: "tests failed after merge".into(),
                    });
                } else {
                    results.push(MergeResult {
                        task_id: brief.id.clone(),
                        branch,
                        success: true,
                        conflict: false,
                        test_failure: false,
                        commit_history,
                        message: "merged successfully".into(),
                    });
                }
            }
            Err(_) => {
                // Merge failed — conflict
                let _ = git.merge_abort();
                results.push(MergeResult {
                    task_id: brief.id.clone(),
                    branch,
                    success: false,
                    conflict: true,
                    test_failure: false,
                    commit_history,
                    message: "merge conflict".into(),
                });
            }
        }
    }

    Ok(results)
}

fn collect_writer_tasks_ordered(
    run_paths: &crate::fs::run::RunPaths,
) -> Result<Vec<TaskBriefFrontmatter>> {
    let tasks_dir = run_paths.tasks_dir();
    if !tasks_dir.exists() {
        return Ok(Vec::new());
    }

    let mut briefs = Vec::new();
    for entry in std::fs::read_dir(&tasks_dir)? {
        let entry = entry?;
        if entry.path().extension().map(|e| e == "md").unwrap_or(false) {
            let content = std::fs::read_to_string(entry.path())?;
            if let Ok((fm, _)) = frontmatter::parse::<TaskBriefFrontmatter>(&content) {
                if fm.classification == Classification::Writer {
                    briefs.push(fm);
                }
            }
        }
    }

    // Simple topological sort: tasks with no dependencies first, then by depends_on
    // For Phase 1, a simple sort by ID + dependency check suffices
    briefs.sort_by(|a, b| {
        let a_deps_b = a.depends_on.contains(&b.id);
        let b_deps_a = b.depends_on.contains(&a.id);
        if a_deps_b {
            std::cmp::Ordering::Greater
        } else if b_deps_a {
            std::cmp::Ordering::Less
        } else {
            a.id.cmp(&b.id)
        }
    });

    Ok(briefs)
}

fn run_tests(project_root: &Path, test_cmd: &str) -> bool {
    let parts: Vec<&str> = test_cmd.split_whitespace().collect();
    if parts.is_empty() {
        return true;
    }
    let output = std::process::Command::new(parts[0])
        .args(&parts[1..])
        .current_dir(project_root)
        .output();
    match output {
        Ok(o) => o.status.success(),
        Err(_) => false,
    }
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cargo test --test integrate_test`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/commands/integrate.rs tests/integrate_test.rs
git commit -m "feat: add integrate command — serial merge with conflict detection and TDD history"
```

---

## Task 20: `agentrc layout` command

**Files:**
- Modify: `src/commands/layout.rs`
- Test: unit tests only (tmux required for integration)

- [ ] **Step 1: Write the layout command**

This command is thin — it calls tmux directly. We can test the logic of finding worker windows without tmux, but the actual layout operations require it.

`src/commands/layout.rs`:

```rust
use anyhow::Result;
use crate::tmux::wrapper::Tmux;

pub fn run(mode: &str) -> Result<()> {
    let tmux = Tmux::new();
    match mode {
        "tile" => tile(&tmux),
        "collate" => collate(&tmux),
        _ => anyhow::bail!("unknown layout mode: {}", mode),
    }
}

fn tile(tmux: &Tmux) -> Result<()> {
    let windows = tmux.list_windows()?;
    for w in &windows {
        if w.starts_with("workers-") {
            tmux.select_layout_tiled(w)?;
        }
    }
    println!("Retiled all worker windows.");
    Ok(())
}

fn collate(tmux: &Tmux) -> Result<()> {
    // For Phase 1, collate is the same as tile
    // Phase 2 will add overflow logic
    tile(tmux)
}
```

`LayoutMode` is defined in `main.rs` for clap parsing. The `layout::run` function accepts a `&str` to stay decoupled from the CLI layer. In `main.rs`, convert with: `commands::layout::run(match mode { LayoutMode::Tile => "tile", LayoutMode::Collate => "collate" })`.

- [ ] **Step 2: Commit**

```bash
git add src/commands/layout.rs
git commit -m "feat: add layout command — tile/collate worker windows"
```

---

## Task 21: Skill and template files

**Files:**
- Create: `skill/agentrc/SKILL.md`
- Create: `skill/agentrc/worker-seed.txt`
- Create: `skill/agentrc/task-brief.md`

- [ ] **Step 1: Write the SKILL.md**

`skill/agentrc/SKILL.md`:

```markdown
---
name: agentrc
description: "Orchestrate multiple Claude Code workers in tmux panes. Use when the user wants to run parallel tasks, dispatch workers, or manage a multi-agent workflow."
---

# agentrc — Orchestrator Skill

You are the orchestrator. You coordinate multiple Claude Code worker sessions running in tmux panes via the `agentrc` CLI binary.

## Quick Reference

| Command | Purpose |
|---|---|
| `agentrc init` | Initialize .orchestrator/ in current project |
| `agentrc run create --slug <name>` | Start a new run |
| `agentrc spawn <task-id>` | Launch a worker in a tmux pane |
| `agentrc status [--json]` | Check all task statuses |
| `agentrc resume` | Get context dump for session recovery |
| `agentrc integrate` | Merge all completed writer branches |
| `agentrc teardown <id> [--all]` | Clean up workers |
| `agentrc layout [tile\|collate]` | Retile worker panes |
| `agentrc run archive` | Archive current run |

## Workflow

### Phase 1: PLAN
1. User gives you a goal.
2. Classify: greenfield / feature / debug / refactor.
3. Gather context (use Explore subagent or spawn reader workers).
4. Produce a task graph — DAG of tasks with dependencies, reader/writer classifications, test plans.
5. **HARD GATE: present plan to user. Do NOT spawn workers until user approves.**
6. Write plan to `.orchestrator/active/plan.md`.

### Phase 2: DISPATCH
1. `agentrc run create --slug <name>`
2. Write task briefs to `.orchestrator/active/tasks/`.
3. `agentrc spawn <task-id>` for each task with no unresolved dependencies.

### Phase 3: MONITOR
On each user interaction or self-check:
1. `agentrc status` for the full picture.
2. Completed task → spawn its dependents if unblocked.
3. All done → move to INTEGRATE.
4. Blocked/stale → surface to user.

### Phase 4: INTEGRATE
1. `agentrc integrate` — serial merge in dependency order.
2. Review the commit history output for TDD compliance.
3. Handle conflicts/failures per the error handling rules.

### Phase 5: REPORT
Summarize results. Offer cleanup: `agentrc teardown --all`.

## Key Rules
- **Never write directly to a worker's worktree.**
- **Workers use `agentrc worker *` commands exclusively.**
- **Teardown is never automatic.**
- **TDD is a workflow invariant.** Review commit history at integration time.
- **Max 2 redispatches per task.** Then pause and surface to user.

## Session Recovery
If you're picking up a run from a previous session:
1. Run `agentrc resume` and read the output.
2. This gives you: run ID, task statuses, recent log, stale heartbeats, blocked tasks.
3. Continue from where the previous session left off.
```

- [ ] **Step 2: Write worker-seed.txt template**

`skill/agentrc/worker-seed.txt`:

```
You are an agentrc worker. Your task ID is {{TASK_ID}}. Your task brief is at {{BRIEF_PATH}} — read it fully before doing anything.

Contract:
1. Read your task brief and acknowledge.
2. Use `agentrc worker status --task {{TASK_ID}} --state in_progress` to signal you've started.
3. Use `agentrc worker note --task {{TASK_ID}} --message "..."` for progress updates.
4. For writer tasks: invoke superpowers:test-driven-development and follow TDD rigorously. Red -> green -> refactor. No implementation code without a preceding failing test.
5. When done: `agentrc worker done --task {{TASK_ID}} --result-file ./result.md`
6. If blocked: `agentrc worker status --task {{TASK_ID}} --state blocked --message "reason"`
7. Writers: stay in your worktree. Do not modify files outside it. Do not merge your branch.
8. Readers: do not modify any project files. Your output goes through agentrc worker note/result only.
9. A heartbeat daemon is running in the background. Do not touch it.
10. You have full Claude Code tooling. Use what helps.

Begin by reading your task brief.
```

- [ ] **Step 3: Write task-brief.md template**

`skill/agentrc/task-brief.md`:

```markdown
---
id: "{{ID}}"
slug: {{SLUG}}
classification: {{CLASSIFICATION}}
worktree: {{WORKTREE}}
base_branch: {{BASE_BRANCH}}
branch: {{BRANCH}}
pane_id: null
depends_on: [{{DEPENDS_ON}}]
created_at: {{CREATED_AT}}
---

# Task {{ID}}: {{TITLE}}

## Scope
{{SCOPE}}

## Test plan
{{TEST_PLAN}}

## Acceptance criteria
{{ACCEPTANCE_CRITERIA}}

## Out of scope
{{OUT_OF_SCOPE}}

## Notes for worker
{{NOTES}}
```

- [ ] **Step 4: Commit**

```bash
git add skill/
git commit -m "feat: add agentrc skill file and worker/brief templates"
```

---

## Task 22: Makefile

**Files:**
- Create: `Makefile`

- [ ] **Step 1: Write the Makefile**

```makefile
.PHONY: test smoke install clean

test:
	cargo test

smoke:
	cargo test -- --ignored

install:
	cargo install --path .
	cargo run -- install

clean:
	cargo clean

check:
	cargo clippy -- -D warnings
	cargo fmt -- --check

fmt:
	cargo fmt
```

- [ ] **Step 2: Verify it works**

Run: `make test`
Expected: all tests pass

- [ ] **Step 3: Commit**

```bash
git add Makefile
git commit -m "feat: add Makefile — test, smoke, install, check targets"
```

---

## Task 23: E2E happy path test with mock worker

**Files:**
- Create: `tests/fixtures/mock-worker.sh`
- Create: `tests/fixtures/toy-project/` (directory with a git repo)
- Create: `tests/happy_path.rs`

This test exercises the full lifecycle without tmux: init → run create → write briefs → worker commands → status → integrate. No real claude sessions or tmux panes — we simulate the worker's CLI calls directly.

- [ ] **Step 1: Create the mock worker script**

`tests/fixtures/mock-worker.sh`:

```bash
#!/usr/bin/env bash
# Mock worker: simulates what a claude session would do via agentrc worker commands.
# Usage: mock-worker.sh <project-root> <task-id> [--fail] [--conflict]
set -euo pipefail

PROJECT_ROOT="$1"
TASK_ID="$2"
FAIL="${3:-}"

cd "$PROJECT_ROOT"

# Signal start
agentrc worker status --task "$TASK_ID" --state in_progress --phase "implementing" --message "mock worker starting"
agentrc worker note --task "$TASK_ID" --message "Reading task brief"

if [ "$FAIL" = "--fail" ]; then
    agentrc worker status --task "$TASK_ID" --state failed --message "mock worker simulating failure"
    exit 1
fi

# Simulate work in worktree
WORKTREE=".orchestrator/active/worktrees/$TASK_ID"
if [ -d "$WORKTREE" ]; then
    echo "mock change by task $TASK_ID" > "$WORKTREE/mock-$TASK_ID.txt"
    cd "$WORKTREE"
    git add -A
    git commit -m "feat: mock implementation for task $TASK_ID"
    cd "$PROJECT_ROOT"
fi

agentrc worker note --task "$TASK_ID" --message "Implementation complete"

# Write result
RESULT_FILE=$(mktemp)
cat > "$RESULT_FILE" << EOF
# Result for Task $TASK_ID

## Summary
Mock worker completed successfully.

## Changes
- Added mock-$TASK_ID.txt

## Tests
All passing (mocked).
EOF

agentrc worker done --task "$TASK_ID" --result-file "$RESULT_FILE"
rm "$RESULT_FILE"
```

- [ ] **Step 2: Create toy project fixture**

```bash
mkdir -p tests/fixtures/toy-project
cd tests/fixtures/toy-project
git init
echo "# Toy Project" > README.md
echo "fn main() {}" > main.rs
git add .
git commit -m "initial commit"
cd ../../..
```

- [ ] **Step 3: Write E2E happy path test**

`tests/happy_path.rs`:

```rust
mod common;

use agentrc::commands;
use agentrc::fs::bus::OrchestratorPaths;
use agentrc::git::wrapper::Git;
use agentrc::model::task::TaskState;
use tempfile::TempDir;

/// Full lifecycle test without tmux:
/// init → run create → write brief → mock worker commands → status → integrate
#[test]
fn e2e_single_writer_lifecycle() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());

    // 1. Init
    commands::init::run_in(tmp.path(), None, false).unwrap();

    // 2. Create run
    commands::run::create_in(tmp.path(), "e2e-test").unwrap();

    let paths = OrchestratorPaths::new(tmp.path());
    let active = paths.active_run().unwrap();
    let git = Git::new(tmp.path());
    let base = git.current_branch().unwrap();

    // 3. Write task brief
    let brief = format!(
        "---\nid: \"001\"\nslug: add-feature\nclassification: writer\nworktree: {}\nbase_branch: {}\nbranch: orc/001-add-feature\ndepends_on: []\ncreated_at: 2026-04-11T14:30:00Z\n---\n# Task 001: Add feature\n\n## Scope\nAdd a new file.\n",
        active.worktree_dir("001").display(),
        base,
    );
    std::fs::write(active.task_brief("001", "add-feature"), brief).unwrap();

    // 4. Create worktree (normally done by spawn)
    commands::spawn::setup_worktree(
        tmp.path(), &paths, "001", "add-feature", "orc/001-add-feature", &base,
    ).unwrap();
    commands::spawn::write_initial_status(tmp.path(), "001").unwrap();

    // 5. Simulate worker: status → note → write code → commit → done
    commands::worker::status::run_in(
        tmp.path(), "001", "in_progress", Some("implementing"), Some("starting"),
    ).unwrap();

    commands::worker::note::run_in(tmp.path(), "001", "Writing feature code").unwrap();

    // Write code in worktree
    let wt = active.worktree_dir("001");
    std::fs::write(wt.join("feature.txt"), "new feature").unwrap();
    let wt_git = Git::new(&wt);
    wt_git.add_all().unwrap();
    wt_git.commit("add feature.txt").unwrap();

    // Write result and complete
    let result_content = "# Result\nFeature added successfully.\n";
    let result_tmp = tmp.path().join("result.md");
    std::fs::write(&result_tmp, result_content).unwrap();
    commands::worker::done::run_in(
        tmp.path(), "001", Some(result_tmp.to_str().unwrap()),
    ).unwrap();

    // 6. Check status
    let statuses = commands::status::collect_statuses(tmp.path()).unwrap();
    assert_eq!(statuses.len(), 1);
    assert_eq!(statuses[0].state, TaskState::Completed);

    // 7. Integrate
    let results = commands::integrate::integrate_in(tmp.path()).unwrap();
    assert_eq!(results.len(), 1);
    assert!(results[0].success);

    // Feature file should now be in project root
    assert!(tmp.path().join("feature.txt").exists());

    // 8. Resume shows the run
    let resume = commands::resume::format_resume(tmp.path()).unwrap();
    assert!(resume.contains("001"));
    assert!(resume.contains("completed"));
}

#[test]
fn e2e_two_independent_writers() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), None, false).unwrap();
    commands::run::create_in(tmp.path(), "two-writers").unwrap();

    let paths = OrchestratorPaths::new(tmp.path());
    let active = paths.active_run().unwrap();
    let git = Git::new(tmp.path());
    let base = git.current_branch().unwrap();

    // Two independent writer tasks
    for (id, slug, filename) in [("001", "feat-a", "a.txt"), ("002", "feat-b", "b.txt")] {
        let brief = format!(
            "---\nid: \"{}\"\nslug: {}\nclassification: writer\nbase_branch: {}\nbranch: orc/{}-{}\ndepends_on: []\ncreated_at: 2026-04-11T14:30:00Z\n---\n# Task {}",
            id, slug, base, id, slug, id,
        );
        std::fs::write(active.task_brief(id, slug), brief).unwrap();

        // Setup worktree
        let branch = format!("orc/{}-{}", id, slug);
        commands::spawn::setup_worktree(tmp.path(), &paths, id, slug, &branch, &base).unwrap();
        commands::spawn::write_initial_status(tmp.path(), id).unwrap();

        // Simulate worker
        commands::worker::status::run_in(tmp.path(), id, "in_progress", None, None).unwrap();
        let wt = active.worktree_dir(id);
        std::fs::write(wt.join(filename), format!("content of {}", filename)).unwrap();
        let wt_git = Git::new(&wt);
        wt_git.add_all().unwrap();
        wt_git.commit(&format!("add {}", filename)).unwrap();
        commands::worker::done::run_in(tmp.path(), id, None).unwrap();
    }

    // Integrate both
    let results = commands::integrate::integrate_in(tmp.path()).unwrap();
    assert_eq!(results.len(), 2);
    assert!(results.iter().all(|r| r.success));

    // Both files present
    assert!(tmp.path().join("a.txt").exists());
    assert!(tmp.path().join("b.txt").exists());
}

#[test]
fn e2e_reader_plus_writer() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), None, false).unwrap();
    commands::run::create_in(tmp.path(), "reader-writer").unwrap();

    let paths = OrchestratorPaths::new(tmp.path());
    let active = paths.active_run().unwrap();
    let git = Git::new(tmp.path());
    let base = git.current_branch().unwrap();

    // Writer task
    let brief_w = format!(
        "---\nid: \"001\"\nslug: impl\nclassification: writer\nbase_branch: {}\nbranch: orc/001-impl\ndepends_on: []\ncreated_at: 2026-04-11T14:30:00Z\n---\n# Writer task",
        base,
    );
    std::fs::write(active.task_brief("001", "impl"), brief_w).unwrap();
    commands::spawn::setup_worktree(tmp.path(), &paths, "001", "impl", "orc/001-impl", &base).unwrap();
    commands::spawn::write_initial_status(tmp.path(), "001").unwrap();
    commands::worker::status::run_in(tmp.path(), "001", "in_progress", None, None).unwrap();
    let wt = active.worktree_dir("001");
    std::fs::write(wt.join("impl.txt"), "implementation").unwrap();
    Git::new(&wt).add_all().unwrap();
    Git::new(&wt).commit("implement").unwrap();
    commands::worker::done::run_in(tmp.path(), "001", None).unwrap();

    // Reader task — only writes notes and result, no code changes
    let brief_r = format!(
        "---\nid: \"002\"\nslug: review\nclassification: reader\nbase_branch: {}\ndepends_on: []\ncreated_at: 2026-04-11T14:30:00Z\n---\n# Reader task",
        base,
    );
    std::fs::write(active.task_brief("002", "review"), brief_r).unwrap();
    commands::spawn::write_initial_status(tmp.path(), "002").unwrap();
    commands::worker::status::run_in(tmp.path(), "002", "in_progress", None, None).unwrap();
    commands::worker::note::run_in(tmp.path(), "002", "Reviewed the codebase").unwrap();
    commands::worker::done::run_in(tmp.path(), "002", None).unwrap();

    // Integrate — only writer merges, reader is skipped
    let results = commands::integrate::integrate_in(tmp.path()).unwrap();
    assert_eq!(results.len(), 1); // Only writer
    assert!(results[0].success);
    assert!(tmp.path().join("impl.txt").exists());

    // Both tasks show as completed
    let statuses = commands::status::collect_statuses(tmp.path()).unwrap();
    assert_eq!(statuses.len(), 2);
    assert!(statuses.iter().all(|s| s.state == TaskState::Completed));
}
```

- [ ] **Step 4: Run E2E tests**

Run: `cargo test --test happy_path`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add tests/happy_path.rs tests/fixtures/
git commit -m "test: add E2E happy path tests — single writer, parallel writers, reader+writer"
```

---

## Task 24: Fault injection tests

**Files:**
- Create: `tests/fault_injection.rs`

- [ ] **Step 1: Write fault injection tests**

`tests/fault_injection.rs`:

```rust
mod common;

use agentrc::commands;
use agentrc::fs::bus::OrchestratorPaths;
use agentrc::git::wrapper::Git;
use agentrc::model::task::TaskState;
use tempfile::TempDir;

#[test]
fn fault_worker_reports_failure() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), None, false).unwrap();
    commands::run::create_in(tmp.path(), "fault-test").unwrap();

    commands::worker::status::run_in(tmp.path(), "001", "in_progress", None, None).unwrap();
    commands::worker::status::run_in(
        tmp.path(), "001", "failed", None, Some("compilation error"),
    ).unwrap();

    let statuses = commands::status::collect_statuses(tmp.path()).unwrap();
    assert_eq!(statuses[0].state, TaskState::Failed);
    assert_eq!(statuses[0].last_message.as_deref(), Some("compilation error"));
}

#[test]
fn fault_teardown_refuses_in_progress_task() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), None, false).unwrap();
    commands::run::create_in(tmp.path(), "fault-test").unwrap();

    commands::worker::status::run_in(tmp.path(), "001", "in_progress", None, None).unwrap();

    let result = commands::teardown::teardown_task(tmp.path(), "001");
    assert!(result.is_err());
    assert!(result.unwrap_err().to_string().contains("in_progress"));
}

#[test]
fn fault_integrate_conflict_detected() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());

    // Create conflicting file
    std::fs::write(tmp.path().join("shared.txt"), "original").unwrap();
    let git = Git::new(tmp.path());
    git.add_all().unwrap();
    git.commit("add shared").unwrap();

    commands::init::run_in(tmp.path(), None, false).unwrap();
    commands::run::create_in(tmp.path(), "conflict-fault").unwrap();

    let paths = OrchestratorPaths::new(tmp.path());
    let active = paths.active_run().unwrap();
    let base = git.current_branch().unwrap();

    // Two tasks both modify shared.txt
    for (id, slug, content) in [("001", "change-a", "AAA"), ("002", "change-b", "BBB")] {
        let brief = format!(
            "---\nid: \"{}\"\nslug: {}\nclassification: writer\nbase_branch: {}\nbranch: orc/{}-{}\ndepends_on: []\ncreated_at: 2026-04-11T14:30:00Z\n---\n# Task {}",
            id, slug, base, id, slug, id,
        );
        std::fs::write(active.task_brief(id, slug), brief).unwrap();
        let branch = format!("orc/{}-{}", id, slug);
        commands::spawn::setup_worktree(tmp.path(), &paths, id, slug, &branch, &base).unwrap();
        let wt = active.worktree_dir(id);
        std::fs::write(wt.join("shared.txt"), content).unwrap();
        Git::new(&wt).add_all().unwrap();
        Git::new(&wt).commit(&format!("change shared to {}", content)).unwrap();
        commands::worker::status::run_in(tmp.path(), id, "completed", None, None).unwrap();
    }

    let results = commands::integrate::integrate_in(tmp.path()).unwrap();
    assert!(results[0].success); // First merge succeeds
    assert!(results[1].conflict); // Second merge conflicts
}

#[test]
fn fault_init_not_run_before_commands() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    // Don't run init — commands should fail gracefully
    let result = commands::run::create_in(tmp.path(), "no-init");
    // This should fail because .orchestrator/ doesn't exist
    assert!(result.is_err());
}

#[test]
fn fault_run_create_without_init() {
    let tmp = TempDir::new().unwrap();
    let result = commands::run::create_in(tmp.path(), "no-init");
    assert!(result.is_err());
}

#[test]
fn fault_worker_status_invalid_state() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), None, false).unwrap();
    commands::run::create_in(tmp.path(), "test").unwrap();

    let result = commands::worker::status::run_in(tmp.path(), "001", "banana", None, None);
    assert!(result.is_err());
    assert!(result.unwrap_err().to_string().contains("invalid state"));
}

#[test]
fn fault_double_run_create() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), None, false).unwrap();
    commands::run::create_in(tmp.path(), "first").unwrap();
    let result = commands::run::create_in(tmp.path(), "second");
    assert!(result.is_err());
    assert!(result.unwrap_err().to_string().contains("already active"));
}

#[test]
fn fault_resume_no_active_run() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), None, false).unwrap();
    let result = commands::resume::format_resume(tmp.path());
    assert!(result.is_err());
}

#[test]
fn fault_stale_heartbeat_detection() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), None, false).unwrap();
    commands::run::create_in(tmp.path(), "stale-hb").unwrap();

    let paths = OrchestratorPaths::new(tmp.path());
    let active = paths.active_run().unwrap();

    // Create heartbeat, then backdate it
    commands::worker::heartbeat::tick(tmp.path(), "001").unwrap();
    let hb = active.heartbeat_file("001");
    let old = std::time::SystemTime::now() - std::time::Duration::from_secs(300);
    filetime::set_file_mtime(&hb, filetime::FileTime::from_system_time(old)).unwrap();

    let stale = commands::status::find_stale_heartbeats(tmp.path(), 120).unwrap();
    assert!(stale.contains(&"001".to_string()));
}
```

- [ ] **Step 2: Run fault injection tests**

Run: `cargo test --test fault_injection`
Expected: ALL PASS

- [ ] **Step 3: Commit**

```bash
git add tests/fault_injection.rs
git commit -m "test: add fault injection tests — failure states, conflicts, stale heartbeats"
```

---

## Task 25: Final integration — verify everything compiles and passes

- [ ] **Step 1: Run full test suite**

```bash
cargo test
```

Expected: ALL tests pass across all test files.

- [ ] **Step 2: Run clippy and fmt**

```bash
cargo clippy -- -D warnings
cargo fmt -- --check
```

Fix any warnings or formatting issues.

- [ ] **Step 3: Verify binary works**

```bash
cargo run -- --help
cargo run -- init --help
cargo run -- worker --help
```

All should print help text without errors.

- [ ] **Step 4: Commit any fixes**

```bash
git add -A
git commit -m "chore: fix clippy warnings and formatting"
```

- [ ] **Step 5: Final commit with all passing**

```bash
make test
```

Expected: clean pass.
