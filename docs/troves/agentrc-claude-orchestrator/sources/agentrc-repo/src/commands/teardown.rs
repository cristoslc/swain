use std::path::Path;

use anyhow::{bail, Context, Result};

use crate::commands::status::collect_statuses;
use crate::fs::bus::OrchestratorPaths;
use crate::git::wrapper::Git;
use crate::model::error::AppError;
use crate::model::task::{TaskState, TaskStatus};
use crate::tmux::wrapper::Tmux;

/// CLI entry point — uses current directory.
pub fn run(task_id: Option<&str>, all: bool, force: bool) -> Result<()> {
    let cwd = std::env::current_dir().context("cannot determine current directory")?;
    if all {
        teardown_all(&cwd, force)
    } else if let Some(id) = task_id {
        teardown_task(&cwd, id, force)
    } else {
        bail!("provide a task id or use --all")
    }
}

/// Tear down a single task by id.
///
/// 1. Get active run paths.
/// 2. Read status file, check state is completed/failed/aborted (bail if not).
/// 3. Kill tmux pane (best-effort, from `status.pane_id`).
/// 4. Remove worktree if it exists.
/// 5. Print message.
pub fn teardown_task(project_root: &Path, task_id: &str, force: bool) -> Result<()> {
    let paths = OrchestratorPaths::new(project_root);
    let active = paths.active_run().ok_or(AppError::NoActiveRun)?;

    // Read and check status
    let status = read_status(&active, task_id)?;
    if !force {
        ensure_teardown_allowed(&status)?;
    }

    // Kill tmux pane (best-effort)
    if let Some(ref pane_id) = status.pane_id {
        let tmux = Tmux::new();
        let _ = tmux.kill_pane(pane_id);
    }

    // Remove worktree if it exists
    let wt_path = active.worktree_dir(task_id);
    if wt_path.exists() {
        let git = Git::new(project_root);
        git.remove_worktree(&wt_path)
            .with_context(|| format!("failed to remove worktree for task {task_id}"))?;
    }

    println!("teardown: task {task_id} cleaned up");
    Ok(())
}

/// Tear down all completed/failed/aborted tasks in the active run.
///
/// 1. Collect all statuses.
/// 2. For each completed/failed/aborted: call `teardown_task`.
/// 3. Skip in_progress/blocked with a warning message.
pub fn teardown_all(project_root: &Path, force: bool) -> Result<()> {
    let statuses = collect_statuses(project_root)?;

    for status in &statuses {
        if force || is_teardown_allowed(&status.state) {
            teardown_task(project_root, &status.id, force)?;
        } else {
            eprintln!(
                "teardown: skipping task {} (state: {})",
                status.id, status.state
            );
        }
    }

    Ok(())
}

/// Read a task's status file from the active run.
fn read_status(active: &crate::fs::run::RunPaths, task_id: &str) -> Result<TaskStatus> {
    let status_file = active.status_file(task_id);
    if !status_file.exists() {
        return Err(AppError::TaskNotFound {
            task_id: task_id.to_string(),
        }
        .into());
    }

    let content = std::fs::read_to_string(&status_file)
        .with_context(|| format!("failed to read status file: {}", status_file.display()))?;
    let status: TaskStatus =
        serde_json::from_str(&content).map_err(|e| AppError::StatusParseError {
            path: status_file.clone(),
            reason: e.to_string(),
        })?;
    Ok(status)
}

/// Returns true if the task state allows teardown.
fn is_teardown_allowed(state: &TaskState) -> bool {
    matches!(
        state,
        TaskState::Completed | TaskState::Failed | TaskState::Aborted
    )
}

/// Bail if the task's state does not allow teardown.
fn ensure_teardown_allowed(status: &TaskStatus) -> Result<()> {
    if !is_teardown_allowed(&status.state) {
        bail!(
            "cannot tear down task {} in state {} (must be completed, failed, or aborted)",
            status.id,
            status.state
        );
    }
    Ok(())
}
