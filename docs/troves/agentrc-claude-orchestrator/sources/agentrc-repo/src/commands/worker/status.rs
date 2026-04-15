use std::path::Path;

use anyhow::{Context, Result};
use chrono::Utc;

use crate::fs::bus::OrchestratorPaths;
use crate::model::error::AppError;
use crate::model::task::{PhaseEntry, TaskState, TaskStatus};

/// CLI entry point — resolves project root from env var or cwd.
pub fn run(
    task: &str,
    state: &str,
    phase: Option<&str>,
    message: Option<&str>,
    tokens: Option<u64>,
) -> Result<()> {
    let root = super::resolve_project_root()?;
    run_in(&root, task, state, phase, message, tokens)
}

/// Testable entry point: create or update a worker status file under `project_root`.
///
/// 1. Parse `state_str` to [`TaskState`] (fail if invalid).
/// 2. Get the active run paths.
/// 3. If the status file exists, deserialize the existing [`TaskStatus`]; else create a new one.
/// 4. Update state, `updated_at`, phase (if provided), `last_message` (if provided).
/// 5. If transitioning to `InProgress` and `started_at` is `None`, set `started_at`.
/// 6. Serialize and write.
pub fn run_in(
    project_root: &Path,
    task_id: &str,
    state_str: &str,
    phase: Option<&str>,
    message: Option<&str>,
    tokens: Option<u64>,
) -> Result<()> {
    let new_state = parse_state(state_str)?;

    let paths = OrchestratorPaths::new(project_root);
    let active = paths.active_run().ok_or(AppError::NoActiveRun)?;
    let status_file = active.status_file(task_id);

    let now = Utc::now();

    let mut status = if status_file.exists() {
        let content = std::fs::read_to_string(&status_file)
            .with_context(|| format!("failed to read status file: {}", status_file.display()))?;
        serde_json::from_str::<TaskStatus>(&content).map_err(|e| AppError::StatusParseError {
            path: status_file.clone(),
            reason: e.to_string(),
        })?
    } else {
        TaskStatus {
            id: task_id.to_string(),
            pane_id: None,
            pane_title: None,
            state: TaskState::Spawning,
            phase: None,
            started_at: None,
            updated_at: now,
            last_message: None,
            result_path: None,
            branch: None,
            redispatch_count: 0,
            phase_history: Vec::new(),
            token_usage: None,
        }
    };

    // Update fields
    status.state = new_state;
    status.updated_at = now;

    if let Some(p) = phase {
        status.phase = Some(p.to_string());
    }

    if let Some(m) = message {
        status.last_message = Some(m.to_string());
    }

    if let Some(t) = tokens {
        status.token_usage = Some(t);
    }

    // Set started_at on first transition to InProgress
    if status.state == TaskState::InProgress && status.started_at.is_none() {
        status.started_at = Some(now);
    }

    // Append phase history entry
    let phase_label = status
        .phase
        .clone()
        .unwrap_or_else(|| status.state.to_string());
    status.phase_history.push(PhaseEntry {
        phase: phase_label,
        entered_at: now,
    });

    // Write the status file
    let json = serde_json::to_string_pretty(&status).context("failed to serialize task status")?;
    std::fs::write(&status_file, &json)
        .with_context(|| format!("failed to write status file: {}", status_file.display()))?;

    Ok(())
}

/// Parse a string into a [`TaskState`], returning an error for unrecognised values.
fn parse_state(s: &str) -> Result<TaskState> {
    match s {
        "spawning" => Ok(TaskState::Spawning),
        "ready" => Ok(TaskState::Ready),
        "in_progress" => Ok(TaskState::InProgress),
        "blocked" => Ok(TaskState::Blocked),
        "completed" => Ok(TaskState::Completed),
        "failed" => Ok(TaskState::Failed),
        "aborted" => Ok(TaskState::Aborted),
        other => anyhow::bail!("invalid task state: {other}"),
    }
}
