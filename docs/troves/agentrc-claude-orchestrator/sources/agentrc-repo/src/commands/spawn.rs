use std::path::{Path, PathBuf};

use anyhow::{Context, Result};

use crate::commands::worker;
use crate::fs::bus::OrchestratorPaths;
use crate::fs::frontmatter;
use crate::fs::run::RunPaths;
use crate::git::wrapper::Git;
use crate::model::config::OrchestratorConfig;
use crate::model::error::AppError;
use crate::model::task::{Classification, TaskBriefFrontmatter};
use crate::tmux::wrapper::Tmux;

// ---------------------------------------------------------------------------
// Testable helper functions
// ---------------------------------------------------------------------------

/// Read a task brief markdown file and parse its YAML frontmatter.
pub fn load_task_brief(path: impl AsRef<Path>) -> Result<TaskBriefFrontmatter> {
    let path = path.as_ref();
    let content = std::fs::read_to_string(path)
        .with_context(|| format!("failed to read task brief: {}", path.display()))?;
    let (fm, _body): (TaskBriefFrontmatter, String) =
        frontmatter::parse(&content).map_err(|e| AppError::TaskBriefParseError {
            path: path.to_path_buf(),
            reason: e.to_string(),
        })?;
    Ok(fm)
}

/// Scan the tasks directory for a brief file matching `<task_id>-*.md`.
pub fn find_task_brief(run_paths: &RunPaths, task_id: &str) -> Result<PathBuf> {
    let tasks_dir = run_paths.tasks_dir();
    let prefix = format!("{task_id}-");

    if tasks_dir.is_dir() {
        for entry in std::fs::read_dir(&tasks_dir)
            .with_context(|| format!("failed to read tasks dir: {}", tasks_dir.display()))?
        {
            let entry = entry?;
            let name = entry.file_name().to_string_lossy().to_string();
            if name.starts_with(&prefix) && name.ends_with(".md") {
                return Ok(entry.path());
            }
        }
    }

    Err(AppError::TaskNotFound {
        task_id: task_id.to_string(),
    }
    .into())
}

/// Create a git worktree for a writer task.
///
/// The worktree is placed at `<run>/worktrees/<task_id>` and checked out on a
/// new branch `<branch>` starting from `<base>`.
pub fn setup_worktree(
    project_root: &Path,
    paths: &OrchestratorPaths,
    task_id: &str,
    _slug: &str,
    branch: &str,
    base: &str,
) -> Result<()> {
    let active = paths.active_run().ok_or(AppError::NoActiveRun)?;
    let wt_dir = active.worktree_dir(task_id);

    if wt_dir.exists() {
        return Err(AppError::WorktreeExists { path: wt_dir }.into());
    }

    let git = Git::new(project_root);
    git.create_worktree(&wt_dir, branch, base)
        .with_context(|| format!("failed to create worktree at {}", wt_dir.display()))?;

    Ok(())
}

/// Write an initial status file with state `Spawning` for the given task.
pub fn write_initial_status(project_root: &Path, task_id: &str) -> Result<()> {
    worker::status::run_in(project_root, task_id, "spawning", None, None, None)
}

/// Build the bootstrap prompt text that will be sent to the Claude worker.
pub fn generate_seed_prompt(task_id: &str, brief_path: &str) -> String {
    format!(
        "You are worker {task_id}. Read your task brief at `{brief_path}` and begin work. \
         Use `agentrc worker status --task {task_id} --state in_progress` to report progress. \
         Use `agentrc worker heartbeat --task {task_id}` to send heartbeats. \
         Use `agentrc worker done --task {task_id}` when finished."
    )
}

// ---------------------------------------------------------------------------
// CLI entry point (orchestrates everything including tmux)
// ---------------------------------------------------------------------------

/// Full spawn: parse brief, setup worktree, create pane, launch claude, seed.
///
/// This is the only function in this module that touches tmux.
pub fn run(task_id: &str) -> Result<()> {
    let cwd = std::env::current_dir().context("cannot determine current directory")?;
    let paths = OrchestratorPaths::new(&cwd);
    let active = paths.active_run().ok_or(AppError::NoActiveRun)?;

    // 1. Find and parse the task brief
    let brief_path = find_task_brief(&active, task_id)?;
    let brief = load_task_brief(&brief_path)?;

    // 2. Load config and check max_workers
    let config_path = paths.config();
    let config_content = std::fs::read_to_string(&config_path)
        .with_context(|| format!("failed to read config: {}", config_path.display()))?;
    let config: OrchestratorConfig =
        serde_json::from_str(&config_content).context("failed to parse orchestrator config")?;

    let current_statuses = crate::commands::status::collect_statuses(&cwd)?;
    let active_count = current_statuses
        .iter()
        .filter(|s| {
            matches!(
                s.state,
                crate::model::task::TaskState::Spawning
                    | crate::model::task::TaskState::Ready
                    | crate::model::task::TaskState::InProgress
                    | crate::model::task::TaskState::Blocked
            )
        })
        .count() as u32;

    if active_count >= config.max_workers {
        anyhow::bail!(
            "max workers ({}) reached — {} currently active",
            config.max_workers,
            active_count
        );
    }

    // 3. Setup worktree (writer only)
    if brief.classification == Classification::Writer {
        let default_branch = format!("orc/{}-{}", brief.id, brief.slug);
        let branch = brief.branch.as_deref().unwrap_or(&default_branch);
        setup_worktree(
            &cwd,
            &paths,
            task_id,
            &brief.slug,
            branch,
            &brief.base_branch,
        )?;
    }

    // 4. Write initial status
    write_initial_status(&cwd, task_id)?;

    // 5. Find or create tmux worker window, get a pane
    let tmux = Tmux::new();
    let window_name = "workers";
    let windows = tmux.list_windows().unwrap_or_default();
    let pane_id = if !windows.iter().any(|w| w == window_name) {
        // New window — use its initial pane (no extra empty pane)
        tmux.new_window_with_pane_id(window_name)
            .context("failed to create workers window")?
    } else {
        // Existing window — split to add a pane
        tmux.split_window(window_name)
            .context("failed to split window for worker")?
    };

    // 7. Set semantic pane title
    let pane_title = format!("orc:{}:{}", brief.id, brief.slug);
    let _ = tmux.set_pane_title(&pane_id, &pane_title);

    // 8. Update brief frontmatter with pane_id
    let brief_content = std::fs::read_to_string(&brief_path)?;
    let updated =
        frontmatter::update_field(&brief_content, "pane_id", &pane_id).unwrap_or(brief_content);
    std::fs::write(&brief_path, updated)?;

    // 9. Update status with pane_id and pane_title
    let status_file = active.status_file(task_id);
    if status_file.exists() {
        let content = std::fs::read_to_string(&status_file)?;
        let mut status: crate::model::task::TaskStatus = serde_json::from_str(&content)?;
        status.pane_id = Some(pane_id.clone());
        status.pane_title = Some(pane_title);
        let json = serde_json::to_string_pretty(&status)?;
        std::fs::write(&status_file, json)?;
    }

    // 9. Retile, cd to worktree, launch heartbeat + claude, seed prompt
    let _ = tmux.select_layout_tiled(window_name);

    // Export project root so worker commands can find .orchestrator/ from worktrees
    tmux.send_keys(
        &pane_id,
        &format!("export AGENTRC_PROJECT_ROOT={}", cwd.display()),
    )?;

    // cd to worktree for writers, project root for readers
    let work_dir = if brief.classification == Classification::Writer {
        active.worktree_dir(task_id)
    } else {
        cwd.clone()
    };
    tmux.send_keys(&pane_id, &format!("cd {}", work_dir.display()))?;

    // Launch heartbeat in background
    tmux.send_keys(
        &pane_id,
        &format!(
            "agentrc worker heartbeat --task {} --interval {} &",
            task_id, config.heartbeat_interval_sec
        ),
    )?;

    // Build the seed prompt and launch claude with it as initial message
    let relative_brief = brief_path
        .strip_prefix(&cwd)
        .unwrap_or(&brief_path)
        .to_string_lossy();
    let seed = generate_seed_prompt(task_id, &relative_brief);

    let escaped_seed = seed.replace('\'', "'\\''");
    let mut claude_cmd = format!("claude --dangerously-skip-permissions '{escaped_seed}'");
    for arg in &config.worker_claude_args {
        claude_cmd.push(' ');
        claude_cmd.push_str(arg);
    }
    tmux.send_keys(&pane_id, &claude_cmd)?;

    println!("Spawned task {task_id} in pane {pane_id}");
    let _ = crate::events::emit_info(
        &cwd,
        crate::model::event::EventType::Spawned,
        task_id,
        &format!("spawned in pane {pane_id}"),
    );
    Ok(())
}
