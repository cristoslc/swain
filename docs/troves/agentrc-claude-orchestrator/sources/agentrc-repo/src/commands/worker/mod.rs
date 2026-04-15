pub mod done;
pub mod heartbeat;
pub mod note;
pub mod result;
pub mod status;

use std::path::PathBuf;

use anyhow::{Context, Result};

/// Resolve the project root for worker commands.
///
/// Workers run from inside git worktrees (under `.orchestrator/`), where
/// the orchestrator state directory is not present.  The spawn command sets
/// `AGENTRC_PROJECT_ROOT` so that worker subcommands can find the real root.
/// Falls back to the current directory when the env var is absent (e.g. in
/// tests or when invoked manually from the project root).
pub fn resolve_project_root() -> Result<PathBuf> {
    if let Ok(root) = std::env::var("AGENTRC_PROJECT_ROOT") {
        return Ok(PathBuf::from(root));
    }
    std::env::current_dir().context("cannot determine current directory")
}
