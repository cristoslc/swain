use std::collections::HashMap;
use std::path::Path;
use std::sync::mpsc;
use std::time::SystemTime;

use anyhow::{Context, Result};
use chrono::Local;
use notify::{Event, EventKind, RecommendedWatcher, RecursiveMode, Watcher};

use crate::fs::bus::OrchestratorPaths;
use crate::model::error::AppError;
use crate::model::task::{TaskState, TaskStatus};

const HEARTBEAT_TIMEOUT_SEC: u64 = 120;

/// Process a status file change — reads the file, compares against previous state,
/// and returns a formatted transition line.
pub fn process_status_change(
    path: &Path,
    previous_states: &mut HashMap<String, TaskState>,
) -> Option<String> {
    let content = std::fs::read_to_string(path).ok()?;
    let status: TaskStatus = serde_json::from_str(&content).ok()?;

    let task_id = &status.id;
    let new_state = status.state;
    let phase = status.phase;

    let timestamp = Local::now().format("%H:%M:%S");
    let phase_str = phase
        .as_deref()
        .map(|p| format!(" (phase: {p})"))
        .unwrap_or_default();

    let line = if let Some(old_state) = previous_states.get(task_id) {
        format!("[{timestamp}] {task_id}: {old_state} \u{2192} {new_state}{phase_str}")
    } else {
        format!("[{timestamp}] {task_id}: \u{2192} {new_state}{phase_str}")
    };

    previous_states.insert(task_id.to_string(), new_state);
    Some(line)
}

/// Check a heartbeat file for staleness.
/// Returns `Some(warning)` if the heartbeat is older than `timeout_sec`, `None` if healthy.
pub fn check_heartbeat_staleness(path: &Path, timeout_sec: u64) -> Option<String> {
    let metadata = std::fs::metadata(path).ok()?;
    let modified = metadata.modified().ok()?;
    let age = SystemTime::now().duration_since(modified).ok()?;

    if age.as_secs() >= timeout_sec {
        let task_id = path.file_stem()?.to_str()?;
        let timestamp = Local::now().format("%H:%M:%S");
        Some(format!(
            "[{timestamp}] WARNING: {task_id} stale heartbeat ({}s)",
            age.as_secs()
        ))
    } else {
        None
    }
}

/// CLI entry point — uses current directory.
pub fn run() -> Result<()> {
    let cwd = std::env::current_dir().context("cannot determine current directory")?;
    watch(&cwd)
}

/// Testable entry point: watch the active run's status/ and heartbeats/ directories.
pub fn watch(project_root: &Path) -> Result<()> {
    let paths = OrchestratorPaths::new(project_root);
    let active = paths.active_run().ok_or(AppError::NoActiveRun)?;

    let (tx, rx) = mpsc::channel::<Event>();

    let mut watcher = RecommendedWatcher::new(
        move |res: std::result::Result<Event, notify::Error>| {
            if let Ok(event) = res {
                let _ = tx.send(event);
            }
        },
        notify::Config::default(),
    )
    .context("failed to create file watcher")?;

    let status_dir = active.status_dir();
    let heartbeats_dir = active.heartbeats_dir();

    watcher
        .watch(&status_dir, RecursiveMode::NonRecursive)
        .context("failed to watch status directory")?;
    watcher
        .watch(&heartbeats_dir, RecursiveMode::NonRecursive)
        .context("failed to watch heartbeats directory")?;

    let run_id = active
        .root()
        .file_name()
        .and_then(|n| n.to_str())
        .unwrap_or("unknown");

    println!("Watching run {run_id}... (Ctrl-C to stop)");

    watch_with_receiver(project_root, rx, HEARTBEAT_TIMEOUT_SEC)
}

/// Event processing loop — factored out for testability.
/// Reads events from `rx` and prints status transitions and heartbeat warnings.
/// Returns `Ok(())` when the channel is closed.
pub fn watch_with_receiver(
    project_root: &Path,
    rx: mpsc::Receiver<Event>,
    heartbeat_timeout_sec: u64,
) -> Result<()> {
    let paths = OrchestratorPaths::new(project_root);
    let active = paths.active_run().ok_or(AppError::NoActiveRun)?;

    let status_dir = active.status_dir();
    let heartbeats_dir = active.heartbeats_dir();

    let mut previous_states: HashMap<String, TaskState> = HashMap::new();

    // Seed previous states from existing status files
    if status_dir.is_dir() {
        if let Ok(entries) = std::fs::read_dir(&status_dir) {
            for entry in entries.flatten() {
                let path = entry.path();
                if path.extension().and_then(|e| e.to_str()) == Some("json") {
                    if let Ok(content) = std::fs::read_to_string(&path) {
                        if let Ok(status) = serde_json::from_str::<TaskStatus>(&content) {
                            previous_states.insert(status.id.clone(), status.state);
                        }
                    }
                }
            }
        }
    }

    loop {
        match rx.recv() {
            Ok(event) => {
                // Only process create/modify events
                if !matches!(event.kind, EventKind::Create(_) | EventKind::Modify(_)) {
                    continue;
                }

                for path in &event.paths {
                    if path.starts_with(&status_dir) {
                        if path.extension().and_then(|e| e.to_str()) == Some("json") {
                            if let Some(line) = process_status_change(path, &mut previous_states) {
                                println!("{line}");
                            }
                        }
                    } else if path.starts_with(&heartbeats_dir)
                        && path.extension().and_then(|e| e.to_str()) == Some("alive")
                    {
                        if let Some(warning) =
                            check_heartbeat_staleness(path, heartbeat_timeout_sec)
                        {
                            println!("{warning}");
                        }
                    }
                }
            }
            Err(_) => {
                // Channel closed — clean shutdown
                return Ok(());
            }
        }
    }
}
