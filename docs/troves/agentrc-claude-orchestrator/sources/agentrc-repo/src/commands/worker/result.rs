use std::io::Read;
use std::path::Path;

use anyhow::{Context, Result};

use crate::fs::bus::OrchestratorPaths;
use crate::model::error::AppError;

/// CLI entry point — resolves project root from env var or cwd.
pub fn run(task: &str, file: Option<&str>, stdin: bool) -> Result<()> {
    let root = super::resolve_project_root()?;
    run_in(&root, task, file, stdin)
}

/// Testable entry point: write a result file for a task under `project_root`.
///
/// 1. Get the active run paths.
/// 2. Read content from the given file path, or from stdin if `stdin` is true.
/// 3. Error if neither a file nor stdin is provided.
/// 4. Write to the result file.
pub fn run_in(project_root: &Path, task_id: &str, file: Option<&str>, stdin: bool) -> Result<()> {
    let content = if let Some(path) = file {
        std::fs::read_to_string(path)
            .with_context(|| format!("failed to read result source file: {path}"))?
    } else if stdin {
        let mut buf = String::new();
        std::io::stdin()
            .read_to_string(&mut buf)
            .context("failed to read result from stdin")?;
        buf
    } else {
        anyhow::bail!("either --file or --stdin must be provided");
    };

    let paths = OrchestratorPaths::new(project_root);
    let active = paths.active_run().ok_or(AppError::NoActiveRun)?;
    let result_file = active.result_file(task_id);

    std::fs::write(&result_file, &content)
        .with_context(|| format!("failed to write result file: {}", result_file.display()))?;

    Ok(())
}
