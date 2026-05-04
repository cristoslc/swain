use std::io;
use std::path::{Path, PathBuf};

/// Path helpers scoped to a single orchestrator run directory.
///
/// A run directory lives at `.orchestrator/runs/<run_id>/` and contains
/// subdirectories for tasks, status, heartbeats, notes, results, and worktrees.
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

    /// Extract the run ID (directory name) from the root path.
    pub fn run_id(&self) -> &str {
        self.root
            .file_name()
            .and_then(|s| s.to_str())
            .unwrap_or("unknown")
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

    pub fn events_log(&self) -> PathBuf {
        self.root.join("events.jsonl")
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
        self.tasks_dir().join(format!("{id}-{slug}.md"))
    }

    pub fn status_file(&self, id: &str) -> PathBuf {
        self.status_dir().join(format!("{id}.json"))
    }

    pub fn heartbeat_file(&self, id: &str) -> PathBuf {
        self.heartbeats_dir().join(format!("{id}.alive"))
    }

    pub fn notes_file(&self, id: &str) -> PathBuf {
        self.notes_dir().join(format!("{id}.md"))
    }

    pub fn result_file(&self, id: &str) -> PathBuf {
        self.results_dir().join(format!("{id}.md"))
    }

    pub fn worktree_dir(&self, id: &str) -> PathBuf {
        self.worktrees_dir().join(id)
    }

    pub fn checkpoints_dir(&self) -> PathBuf {
        self.root.join("checkpoints")
    }

    pub fn checkpoint_file(&self, id: &str) -> PathBuf {
        self.checkpoints_dir().join(format!("{id}.json"))
    }

    /// Create all subdirectories for this run.
    pub fn scaffold(&self) -> io::Result<()> {
        let dirs = [
            self.tasks_dir(),
            self.status_dir(),
            self.heartbeats_dir(),
            self.notes_dir(),
            self.results_dir(),
            self.worktrees_dir(),
            self.checkpoints_dir(),
        ];
        for dir in &dirs {
            std::fs::create_dir_all(dir)?;
        }
        Ok(())
    }
}
