use std::path::Path;

use anyhow::{bail, Context, Result};

use crate::commands::spawn::{find_task_brief, load_task_brief};
use crate::fs::bus::OrchestratorPaths;
use crate::git::wrapper::Git;
use crate::model::config::OrchestratorConfig;
use crate::model::error::AppError;
use crate::model::task::{TaskState, TaskStatus};
use crate::tmux::wrapper::Tmux;

/// CLI entry point.
pub fn run(task_id: &str) -> Result<()> {
    let cwd = std::env::current_dir().context("cannot determine current directory")?;
    run_in(&cwd, task_id)
}

/// Testable entry point.
pub fn run_in(project_root: &Path, task_id: &str) -> Result<()> {
    let (branch, commits_ahead, brief_path) = validate_respawn(project_root, task_id)?;

    let paths = OrchestratorPaths::new(project_root);
    let active = paths.active_run().ok_or(AppError::NoActiveRun)?;
    let git = Git::new(project_root);
    let tmux = Tmux::new();

    // Load config
    let config_path = paths.config();
    let config: OrchestratorConfig = {
        let content = std::fs::read_to_string(&config_path)?;
        serde_json::from_str(&content)?
    };

    // Read current status to get pane_id and redispatch_count
    let status_file = active.status_file(task_id);
    let status_content = std::fs::read_to_string(&status_file)?;
    let mut status: TaskStatus = serde_json::from_str(&status_content)?;

    // Check redispatch limit
    if status.redispatch_count >= config.max_redispatch_attempts {
        bail!(
            "task {} has reached max redispatch attempts ({})",
            task_id,
            config.max_redispatch_attempts
        );
    }

    // Kill old pane if alive
    if let Some(ref pane_id) = status.pane_id {
        let _ = tmux.kill_pane(pane_id);
    }

    // Remove old worktree if exists
    let wt_path = active.worktree_dir(task_id);
    if wt_path.exists() {
        git.remove_worktree(&wt_path)
            .with_context(|| format!("failed to remove old worktree for {task_id}"))?;
    }

    // Re-create worktree from EXISTING branch (preserves commits)
    git.create_worktree_from_branch(&wt_path, &branch)
        .with_context(|| format!("failed to create worktree from branch {branch}"))?;

    // Find or create workers window
    let window_name = "workers";
    let windows = tmux.list_windows().unwrap_or_default();
    let pane_id = if !windows.iter().any(|w| w == window_name) {
        tmux.new_window_with_pane_id(window_name)?
    } else {
        tmux.split_window(window_name)?
    };

    let _ = tmux.select_layout_tiled(window_name);

    // Set semantic pane title
    let brief = load_task_brief(&brief_path)?;
    let pane_title = format!("orc:{}:{}", task_id, brief.slug);
    let _ = tmux.set_pane_title(&pane_id, &pane_title);

    // Export project root, cd to worktree, launch heartbeat
    tmux.send_keys(
        &pane_id,
        &format!("export AGENTRC_PROJECT_ROOT={}", project_root.display()),
    )?;
    tmux.send_keys(&pane_id, &format!("cd {}", wt_path.display()))?;
    tmux.send_keys(
        &pane_id,
        &format!(
            "agentrc worker heartbeat --task {} --interval {} &",
            task_id, config.heartbeat_interval_sec
        ),
    )?;

    // Build and send resume seed
    let relative_brief = brief_path
        .strip_prefix(project_root)
        .unwrap_or(&brief_path)
        .to_string_lossy();
    let seed = generate_resume_seed(task_id, &relative_brief, &branch, commits_ahead);
    let escaped = seed.replace('\'', "'\\''");
    let mut claude_cmd = format!("claude --dangerously-skip-permissions '{escaped}'");
    for arg in &config.worker_claude_args {
        claude_cmd.push(' ');
        claude_cmd.push_str(arg);
    }
    tmux.send_keys(&pane_id, &claude_cmd)?;

    // Update status
    status.state = TaskState::Spawning;
    status.pane_id = Some(pane_id.clone());
    status.pane_title = Some(pane_title);
    status.redispatch_count += 1;
    let json = serde_json::to_string_pretty(&status)?;
    std::fs::write(&status_file, json)?;

    // Update brief with new pane_id
    let brief_content = std::fs::read_to_string(&brief_path)?;
    if let Ok(updated) = crate::fs::frontmatter::update_field(&brief_content, "pane_id", &pane_id) {
        std::fs::write(&brief_path, updated)?;
    }

    println!(
        "Respawned task {task_id} in pane {pane_id} (attempt {})",
        status.redispatch_count
    );
    let _ = crate::events::emit_info(
        project_root,
        crate::model::event::EventType::Respawned,
        task_id,
        &format!(
            "respawned in pane {pane_id} (attempt {})",
            status.redispatch_count
        ),
    );
    Ok(())
}

/// Validate that a task can be respawned. Returns (branch_name, commits_ahead, brief_path).
pub fn validate_respawn(
    project_root: &Path,
    task_id: &str,
) -> Result<(String, u32, std::path::PathBuf)> {
    let paths = OrchestratorPaths::new(project_root);
    let active = paths.active_run().ok_or(AppError::NoActiveRun)?;

    // Check status exists and state is respawnable
    let status_file = active.status_file(task_id);
    if !status_file.exists() {
        bail!("no status file for task {task_id}");
    }
    let content = std::fs::read_to_string(&status_file)?;
    let status: TaskStatus = serde_json::from_str(&content)?;

    if !matches!(
        status.state,
        TaskState::InProgress | TaskState::Failed | TaskState::Aborted
    ) {
        bail!(
            "cannot respawn task {} in state {} (must be in_progress, failed, or aborted)",
            task_id,
            status.state
        );
    }

    // Find brief to get branch name
    let brief_path = find_task_brief(&active, task_id)?;
    let brief = load_task_brief(&brief_path)?;

    let branch = brief
        .branch
        .or(status.branch)
        .unwrap_or_else(|| format!("orc/{}-{}", brief.id, brief.slug));

    // Check branch exists
    let git = Git::new(project_root);
    if !git.branch_exists(&branch).unwrap_or(false) {
        bail!("branch '{branch}' does not exist — nothing to resume from");
    }

    // Load config for base_branch
    let config_path = paths.config();
    let config: OrchestratorConfig = if config_path.exists() {
        let c = std::fs::read_to_string(&config_path)?;
        serde_json::from_str(&c)?
    } else {
        OrchestratorConfig::default()
    };

    let commits_ahead = git
        .log_branch_commits(&branch, &config.base_branch)
        .map(|c| c.len() as u32)
        .unwrap_or(0);

    Ok((branch, commits_ahead, brief_path))
}

/// Generate the resume seed prompt for a respawned worker.
pub fn generate_resume_seed(
    task_id: &str,
    brief_path: &str,
    branch: &str,
    commits_ahead: u32,
) -> String {
    format!(
        "You are worker {task_id} resuming work. Your task brief is at `{brief_path}`. \
         Your branch {branch} has {commits_ahead} commits already. Read the brief \
         AND review your existing commits (git log --oneline) to understand \
         where the previous session stopped. Continue from there. \
         Use `agentrc worker status --task {task_id} --state in_progress` to signal \
         you've resumed. Use `agentrc worker done --task {task_id}` when finished."
    )
}
