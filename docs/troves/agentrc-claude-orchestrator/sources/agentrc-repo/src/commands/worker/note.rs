use std::path::Path;

use anyhow::{Context, Result};
use chrono::Utc;

use crate::fs::bus::OrchestratorPaths;
use crate::model::error::AppError;

/// CLI entry point — resolves project root from env var or cwd.
pub fn run(task: &str, message: &str) -> Result<()> {
    let root = super::resolve_project_root()?;
    run_in(&root, task, message)
}

/// Testable entry point: append a timestamped note for a task under `project_root`.
///
/// 1. Get the active run paths.
/// 2. Format entry as `[<ISO timestamp>] <message>\n`.
/// 3. If the notes file exists, read existing content and append; else start fresh.
/// 4. Write the file.
pub fn run_in(project_root: &Path, task_id: &str, message: &str) -> Result<()> {
    let paths = OrchestratorPaths::new(project_root);
    let active = paths.active_run().ok_or(AppError::NoActiveRun)?;
    let notes_file = active.notes_file(task_id);

    let now = Utc::now();
    let entry = format!("[{}] {}\n", now.to_rfc3339(), message);

    let mut content = if notes_file.exists() {
        std::fs::read_to_string(&notes_file)
            .with_context(|| format!("failed to read notes file: {}", notes_file.display()))?
    } else {
        String::new()
    };

    content.push_str(&entry);

    std::fs::write(&notes_file, &content)
        .with_context(|| format!("failed to write notes file: {}", notes_file.display()))?;

    Ok(())
}
