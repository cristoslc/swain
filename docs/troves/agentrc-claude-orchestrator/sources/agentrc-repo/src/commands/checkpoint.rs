use std::path::Path;

use anyhow::{Context, Result};
use chrono::Utc;
use serde::{Deserialize, Serialize};

use crate::commands::spawn::{find_task_brief, load_task_brief};
use crate::commands::status::collect_statuses;
use crate::fs::bus::OrchestratorPaths;
use crate::git::wrapper::Git;
use crate::model::config::OrchestratorConfig;
use crate::model::error::AppError;
use crate::model::task::TaskState;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Checkpoint {
    pub id: String,
    pub description: Option<String>,
    pub created_at: String,
    pub run_id: String,
    pub base_branch: String,
    pub base_commit: String,
    pub tasks: Vec<TaskCheckpoint>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TaskCheckpoint {
    pub id: String,
    pub slug: String,
    pub state: TaskState,
    pub branch: Option<String>,
    pub branch_exists: bool,
    pub branch_commit: Option<String>,
    pub commits_ahead: u32,
    pub pane_alive: bool,
    pub classification: String,
}

/// CLI entry for save.
pub fn save(message: Option<&str>) -> Result<()> {
    let cwd = std::env::current_dir().context("cannot determine current directory")?;
    let id = save_in(&cwd, message)?;
    println!("Checkpoint saved: {id}");
    Ok(())
}

/// Testable save entry point.
pub fn save_in(project_root: &Path, message: Option<&str>) -> Result<String> {
    let paths = OrchestratorPaths::new(project_root);
    let active = paths.active_run().ok_or(AppError::NoActiveRun)?;
    let git = Git::new(project_root);

    let now = Utc::now();
    let id = now.format("%Y%m%dT%H%M%S").to_string();

    let run_id = active.run_id().to_string();

    // Load config for base_branch
    let config_path = paths.config();
    let config: OrchestratorConfig = if config_path.exists() {
        let content = std::fs::read_to_string(&config_path)?;
        serde_json::from_str(&content)?
    } else {
        OrchestratorConfig::default()
    };

    let base_commit = git.rev_parse("HEAD").unwrap_or_else(|_| "unknown".into());

    // Collect task state
    let statuses = collect_statuses(project_root)?;
    let mut tasks = Vec::new();

    for status in &statuses {
        let brief = find_task_brief(&active, &status.id)
            .ok()
            .and_then(|p| load_task_brief(&p).ok());

        let slug = brief
            .as_ref()
            .map(|b| b.slug.clone())
            .unwrap_or_else(|| "unknown".into());

        let classification = brief
            .as_ref()
            .map(|b| format!("{:?}", b.classification).to_lowercase())
            .unwrap_or_else(|| "unknown".into());

        let branch = status
            .branch
            .clone()
            .or_else(|| brief.as_ref().and_then(|b| b.branch.clone()));

        let (branch_exists, branch_commit, commits_ahead) = if let Some(ref br) = branch {
            let exists = git.branch_exists(br).unwrap_or(false);
            if exists {
                let commit = git.rev_parse(br).unwrap_or_default();
                let ahead = git
                    .log_branch_commits(br, &config.base_branch)
                    .map(|c| c.len() as u32)
                    .unwrap_or(0);
                (true, Some(commit), ahead)
            } else {
                (false, None, 0)
            }
        } else {
            (false, None, 0)
        };

        // pane_alive: false by default — requires live tmux session
        let pane_alive = false;

        tasks.push(TaskCheckpoint {
            id: status.id.clone(),
            slug,
            state: status.state.clone(),
            branch,
            branch_exists,
            branch_commit,
            commits_ahead,
            pane_alive,
            classification,
        });
    }

    let checkpoint = Checkpoint {
        id: id.clone(),
        description: message.map(String::from),
        created_at: now.to_rfc3339(),
        run_id,
        base_branch: config.base_branch.clone(),
        base_commit,
        tasks,
    };

    // Ensure checkpoints dir exists
    let cp_dir = active.checkpoints_dir();
    std::fs::create_dir_all(&cp_dir)?;

    let cp_file = active.checkpoint_file(&id);
    let json = serde_json::to_string_pretty(&checkpoint)?;
    std::fs::write(&cp_file, json)?;
    let _ = crate::events::emit_info(
        project_root,
        crate::model::event::EventType::CheckpointSaved,
        &id,
        message.unwrap_or("checkpoint saved"),
    );

    Ok(id)
}

/// CLI entry for list.
pub fn list() -> Result<()> {
    let cwd = std::env::current_dir().context("cannot determine current directory")?;
    list_in(&cwd)
}

pub fn list_in(project_root: &Path) -> Result<()> {
    let paths = OrchestratorPaths::new(project_root);
    let active = paths.active_run().ok_or(AppError::NoActiveRun)?;
    let cp_dir = active.checkpoints_dir();

    if !cp_dir.is_dir() {
        println!("No checkpoints.");
        return Ok(());
    }

    let mut entries: Vec<_> = std::fs::read_dir(&cp_dir)?
        .filter_map(|e| e.ok())
        .filter(|e| e.path().extension().and_then(|x| x.to_str()) == Some("json"))
        .collect();
    entries.sort_by_key(|e| e.file_name());

    if entries.is_empty() {
        println!("No checkpoints.");
        return Ok(());
    }

    println!("{:<20} {:<8} DESCRIPTION", "ID", "TASKS");
    println!("{}", "-".repeat(60));

    for entry in &entries {
        let content = std::fs::read_to_string(entry.path())?;
        let cp: Checkpoint = serde_json::from_str(&content)?;
        let desc = cp.description.as_deref().unwrap_or("-");
        println!("{:<20} {:<8} {}", cp.id, cp.tasks.len(), desc);
    }

    Ok(())
}

/// CLI entry for restore.
pub fn restore(id: Option<&str>, respawn: bool) -> Result<()> {
    let cwd = std::env::current_dir().context("cannot determine current directory")?;
    restore_in(&cwd, id, respawn)
}

pub fn restore_in(project_root: &Path, id: Option<&str>, respawn: bool) -> Result<()> {
    let paths = OrchestratorPaths::new(project_root);
    let active = paths.active_run().ok_or(AppError::NoActiveRun)?;
    let git = Git::new(project_root);

    // Find checkpoint
    let cp_file = if let Some(id) = id {
        active.checkpoint_file(id)
    } else {
        // Find latest
        let cp_dir = active.checkpoints_dir();
        let mut entries: Vec<_> = std::fs::read_dir(&cp_dir)?
            .filter_map(|e| e.ok())
            .filter(|e| e.path().extension().and_then(|x| x.to_str()) == Some("json"))
            .collect();
        entries.sort_by_key(|e| e.file_name());
        entries
            .last()
            .map(|e| e.path())
            .ok_or_else(|| anyhow::anyhow!("no checkpoints found"))?
    };

    let content = std::fs::read_to_string(&cp_file)
        .with_context(|| format!("failed to read checkpoint: {}", cp_file.display()))?;
    let cp: Checkpoint = serde_json::from_str(&content)?;

    // Print recovery report
    let desc = cp.description.as_deref().unwrap_or("-");
    println!("Checkpoint: {} — \"{}\"", cp.id, desc);
    println!("Base: {} @ {}\n", cp.base_branch, cp.base_commit);
    println!("{:<6} {:<14} {:<30} RECOVERY", "ID", "STATE", "BRANCH");
    println!("{}", "-".repeat(70));

    let mut respawnable = Vec::new();

    for task in &cp.tasks {
        let branch_name = task.branch.as_deref().unwrap_or("-");

        let recovery = if let Some(ref br) = task.branch {
            let exists = git.branch_exists(br).unwrap_or(false);
            if exists {
                let ahead = git
                    .log_branch_commits(br, &cp.base_branch)
                    .map(|c| c.len())
                    .unwrap_or(0);
                if ahead > 0 {
                    if task.state == TaskState::InProgress {
                        respawnable.push(task.id.clone());
                    }
                    format!("ok ({ahead} commit{})", if ahead == 1 { "" } else { "s" })
                } else {
                    "empty (no commits)".to_string()
                }
            } else {
                "LOST (branch missing)".to_string()
            }
        } else {
            "n/a (no branch)".to_string()
        };

        println!(
            "{:<6} {:<14} {:<30} {}",
            task.id, task.state, branch_name, recovery
        );
    }

    if respawn && !respawnable.is_empty() {
        println!("\nRespawning {} in-progress tasks...", respawnable.len());
        for task_id in &respawnable {
            match crate::commands::respawn::run_in(project_root, task_id) {
                Ok(()) => {}
                Err(e) => eprintln!("  failed to respawn {task_id}: {e}"),
            }
        }
    }

    Ok(())
}
