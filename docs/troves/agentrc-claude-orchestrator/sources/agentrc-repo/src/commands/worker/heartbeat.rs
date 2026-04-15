use std::fs::OpenOptions;
use std::path::Path;
use std::time::Duration;

use anyhow::{Context, Result};

use crate::fs::bus::OrchestratorPaths;
use crate::model::error::AppError;

/// CLI entry point — daemon loop that ticks once per `interval` seconds until killed.
pub fn run(task: &str, interval: u64) -> Result<()> {
    let root = super::resolve_project_root()?;
    let duration = Duration::from_secs(interval);
    loop {
        tick(&root, task)?;
        std::thread::sleep(duration);
    }
}

/// Single heartbeat tick: touch (create or update mtime) the `.alive` file for `task_id`.
pub fn tick(project_root: &Path, task_id: &str) -> Result<()> {
    let paths = OrchestratorPaths::new(project_root);
    let active = paths.active_run().ok_or(AppError::NoActiveRun)?;
    let hb_file = active.heartbeat_file(task_id);

    let f = OpenOptions::new()
        .create(true)
        .truncate(true)
        .write(true)
        .open(&hb_file)
        .with_context(|| format!("failed to touch heartbeat file: {}", hb_file.display()))?;
    f.set_len(0)
        .with_context(|| format!("failed to truncate heartbeat file: {}", hb_file.display()))?;

    Ok(())
}
