use std::path::Path;

use anyhow::{Context, Result};

use crate::commands::worker;
use crate::fs::bus::OrchestratorPaths;
use crate::model::error::AppError;
use crate::model::task::TaskStatus;
use crate::tmux::wrapper::Tmux;

/// CLI entry point — resolves project root from env var or cwd.
pub fn run(task: &str, result_file: Option<&str>) -> Result<()> {
    let root = super::resolve_project_root()?;
    run_in(&root, task, result_file)
}

/// Testable entry point: atomically complete a task under `project_root`.
///
/// 1. If `result_file` is provided, write it via `worker::result::run_in`.
/// 2. Set the task status to "completed" via `worker::status::run_in`.
/// 3. If a result was written, patch the status JSON to add `result_path`.
/// 4. Ring the tmux bell (best-effort).
/// 5. Print a completion message.
pub fn run_in(project_root: &Path, task_id: &str, result_file: Option<&str>) -> Result<()> {
    // Step 1: write result file if provided
    let has_result = result_file.is_some();
    if let Some(file) = result_file {
        worker::result::run_in(project_root, task_id, Some(file), false)?;
    }

    // Step 2: set status to completed
    worker::status::run_in(project_root, task_id, "completed", None, None, None)?;

    // Step 3: patch status JSON with result_path if result was written
    if has_result {
        let paths = OrchestratorPaths::new(project_root);
        let active = paths.active_run().ok_or(AppError::NoActiveRun)?;
        let status_file = active.status_file(task_id);
        let result_path = active.result_file(task_id);

        let content = std::fs::read_to_string(&status_file)
            .with_context(|| format!("failed to read status file: {}", status_file.display()))?;
        let mut status: TaskStatus = serde_json::from_str(&content)
            .with_context(|| format!("failed to parse status file: {}", status_file.display()))?;

        status.result_path = Some(result_path);

        let json =
            serde_json::to_string_pretty(&status).context("failed to serialize task status")?;
        std::fs::write(&status_file, &json)
            .with_context(|| format!("failed to write status file: {}", status_file.display()))?;
    }

    // Step 4: ring tmux bell (best-effort)
    let channel = format!("worker-{}-done", task_id);
    let _ = Tmux::new().signal_channel(&channel);

    // Step 5: print completion message
    println!("Task {} completed.", task_id);

    Ok(())
}
