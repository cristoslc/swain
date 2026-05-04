use std::path::Path;

use anyhow::{Context, Result};

use crate::fs::bus::OrchestratorPaths;
use crate::model::error::AppError;
use crate::model::run::RunMetadata;

/// Information about a run, returned by `list_in`.
#[derive(Debug, Clone)]
pub struct RunInfo {
    pub id: String,
    pub active: bool,
}

// ---------------------------------------------------------------------------
// CLI entry points (use cwd)
// ---------------------------------------------------------------------------

pub fn create(slug: &str) -> Result<()> {
    let cwd = std::env::current_dir().context("cannot determine current directory")?;
    create_in(&cwd, slug)
}

pub fn list() -> Result<()> {
    let cwd = std::env::current_dir().context("cannot determine current directory")?;
    let runs = list_in(&cwd)?;
    for r in &runs {
        let marker = if r.active { " (active)" } else { "" };
        println!("{}{}", r.id, marker);
    }
    Ok(())
}

pub fn archive() -> Result<()> {
    let cwd = std::env::current_dir().context("cannot determine current directory")?;
    archive_in(&cwd)
}

// ---------------------------------------------------------------------------
// Testable implementations
// ---------------------------------------------------------------------------

/// Create a new run under `project_root`.
///
/// 1. Ensure no run is currently active.
/// 2. Generate a `RunMetadata` (with timestamped id).
/// 3. Scaffold the run directory tree.
/// 4. Copy the project-level `config.json` into the run as a snapshot.
/// 5. Create a relative `active` symlink pointing at the new run.
pub fn create_in(project_root: &Path, slug: &str) -> Result<()> {
    let paths = OrchestratorPaths::new(project_root);

    // Reject if there is already an active run.
    if let Some(active) = paths.active_run() {
        let run_id = active
            .root()
            .file_name()
            .unwrap_or_default()
            .to_string_lossy()
            .to_string();
        return Err(AppError::RunAlreadyActive { run_id }.into());
    }

    // Build metadata and derive paths.
    let meta = RunMetadata::new(slug);
    let run_paths = paths.run(&meta.id);

    // Scaffold all subdirectories.
    run_paths
        .scaffold()
        .context("failed to scaffold run directory")?;

    // Snapshot the project config into the run.
    std::fs::copy(paths.config(), run_paths.config_snapshot())
        .context("failed to copy config.json into run")?;

    // Create relative symlink: .orchestrator/active -> runs/<run_id>
    let relative_target = format!("runs/{}", meta.id);
    std::os::unix::fs::symlink(&relative_target, paths.active())
        .context("failed to create active symlink")?;

    println!("{}", meta.id);
    Ok(())
}

/// List all runs found under `.orchestrator/runs/`, marking which (if any) is active.
pub fn list_in(project_root: &Path) -> Result<Vec<RunInfo>> {
    let paths = OrchestratorPaths::new(project_root);
    let runs_dir = paths.runs_dir();

    // Determine the active run id (if any).
    let active_id = paths.active_run().map(|rp| {
        rp.root()
            .file_name()
            .unwrap_or_default()
            .to_string_lossy()
            .to_string()
    });

    let mut runs: Vec<RunInfo> = Vec::new();

    if runs_dir.is_dir() {
        for entry in std::fs::read_dir(&runs_dir).context("failed to read runs directory")? {
            let entry = entry?;
            let name = entry.file_name().to_string_lossy().to_string();
            // Only consider directories (each run is a directory).
            if entry.path().is_dir() {
                let active = active_id.as_deref() == Some(name.as_str());
                runs.push(RunInfo { id: name, active });
            }
        }
    }

    runs.sort_by(|a, b| a.id.cmp(&b.id));
    Ok(runs)
}

/// Archive the currently active run by removing the `active` symlink.
pub fn archive_in(project_root: &Path) -> Result<()> {
    let paths = OrchestratorPaths::new(project_root);

    if paths.active_run().is_none() {
        return Err(AppError::NoActiveRun.into());
    }

    std::fs::remove_file(paths.active()).context("failed to remove active symlink")?;
    Ok(())
}
