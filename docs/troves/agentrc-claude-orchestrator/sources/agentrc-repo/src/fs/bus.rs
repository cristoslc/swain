use std::path::{Path, PathBuf};

use crate::fs::run::RunPaths;

/// Path helpers for the `.orchestrator/` directory layout at the project root.
///
/// This struct does not perform any I/O on construction — it only computes paths.
/// Use the returned paths to read/write files or check existence.
#[derive(Debug, Clone)]
pub struct OrchestratorPaths {
    root: PathBuf,
}

impl OrchestratorPaths {
    pub fn new(project_root: &Path) -> Self {
        Self {
            root: project_root.join(".orchestrator"),
        }
    }

    /// The `.orchestrator/` directory itself.
    pub fn root(&self) -> &Path {
        &self.root
    }

    /// `.orchestrator/config.json`
    pub fn config(&self) -> PathBuf {
        self.root.join("config.json")
    }

    /// `.orchestrator/active` — symlink pointing at the current run directory.
    pub fn active(&self) -> PathBuf {
        self.root.join("active")
    }

    /// `.orchestrator/runs/`
    pub fn runs_dir(&self) -> PathBuf {
        self.root.join("runs")
    }

    /// Returns [`RunPaths`] for a specific run by id.
    pub fn run(&self, run_id: &str) -> RunPaths {
        RunPaths::new(self.runs_dir().join(run_id))
    }

    /// Follows the `active` symlink and returns [`RunPaths`] if it exists.
    ///
    /// The symlink target is relative to `.orchestrator/`, so we resolve it
    /// with `self.root().join(&target)` when the target is a relative path.
    pub fn active_run(&self) -> Option<RunPaths> {
        let link = self.active();
        let target = std::fs::read_link(&link).ok()?;
        let resolved = if target.is_relative() {
            self.root.join(&target)
        } else {
            target
        };
        Some(RunPaths::new(resolved))
    }
}
