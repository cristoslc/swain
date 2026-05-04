use std::path::Path;

use anyhow::{Context, Result};

use crate::commands::status::{collect_statuses, find_stale_heartbeats};
use crate::fs::bus::OrchestratorPaths;
use crate::model::config::OrchestratorConfig;
use crate::model::error::AppError;
use crate::model::task::TaskState;

/// CLI entry point — formats and prints the resume context dump.
pub fn run() -> Result<()> {
    let cwd = std::env::current_dir().context("cannot determine current directory")?;
    let output = format_resume(&cwd)?;
    print!("{output}");
    Ok(())
}

/// Build the full structured context dump for an active run.
///
/// Designed for LLM ingestion: reads status files, orchestrator log,
/// heartbeats, and config to produce a self-contained summary.
pub fn format_resume(project_root: &Path) -> Result<String> {
    let paths = OrchestratorPaths::new(project_root);
    let active = paths.active_run().ok_or(AppError::NoActiveRun)?;

    let run_id = active
        .root()
        .file_name()
        .unwrap_or_default()
        .to_string_lossy()
        .to_string();

    // Load the config snapshot from the run directory.
    let config: OrchestratorConfig = {
        let config_path = active.config_snapshot();
        let content = std::fs::read_to_string(&config_path).with_context(|| {
            format!("failed to read config snapshot: {}", config_path.display())
        })?;
        serde_json::from_str(&content).with_context(|| {
            format!("failed to parse config snapshot: {}", config_path.display())
        })?
    };

    let statuses = collect_statuses(project_root)?;
    let stale = find_stale_heartbeats(project_root, config.heartbeat_timeout_sec)?;

    let mut output = String::new();

    // === AGENTRC ACTIVE RUN ===
    output.push_str("=== AGENTRC ACTIVE RUN ===\n");
    output.push_str(&format!("Run: {run_id}\n"));
    output.push_str(&format!("Plan: {}\n", active.plan().display()));
    let test_cmd = config.test_command.as_deref().unwrap_or("none");
    output.push_str(&format!(
        "Config: base_branch={}, test_command={}\n",
        config.base_branch, test_cmd
    ));

    // === TASK STATUS ===
    output.push('\n');
    output.push_str("=== TASK STATUS ===\n");
    if statuses.is_empty() {
        output.push_str("(no tasks)\n");
    } else {
        for s in &statuses {
            let branch = s.branch.as_deref().unwrap_or("-");
            let pane = s
                .pane_title
                .as_deref()
                .or(s.pane_id.as_deref())
                .unwrap_or("-");
            let phase = s.phase.as_deref().unwrap_or("-");
            let msg = s.last_message.as_deref().unwrap_or("-");
            output.push_str(&format!(
                "{} {} {} pane={} phase={} msg={}\n",
                s.id, branch, s.state, pane, phase, msg
            ));
        }
    }

    // === RECENT LOG ===
    output.push('\n');
    output.push_str("=== RECENT LOG (last 20 lines) ===\n");
    let log_path = active.orchestrator_log();
    if log_path.is_file() {
        let log_content = std::fs::read_to_string(&log_path)
            .with_context(|| format!("failed to read orchestrator log: {}", log_path.display()))?;
        let lines: Vec<&str> = log_content.lines().collect();
        let start = lines.len().saturating_sub(20);
        for line in &lines[start..] {
            output.push_str(line);
            output.push('\n');
        }
    } else {
        output.push_str("(no log)\n");
    }

    // === STALE HEARTBEATS ===
    output.push('\n');
    output.push_str("=== STALE HEARTBEATS ===\n");
    if stale.is_empty() {
        output.push_str("(none)\n");
    } else {
        for id in &stale {
            output.push_str(&format!("{id}\n"));
        }
    }

    // === BLOCKED TASKS ===
    output.push('\n');
    output.push_str("=== BLOCKED TASKS ===\n");
    let blocked: Vec<_> = statuses
        .iter()
        .filter(|s| s.state == TaskState::Blocked)
        .collect();
    if blocked.is_empty() {
        output.push_str("(none)\n");
    } else {
        for s in &blocked {
            let msg = s.last_message.as_deref().unwrap_or("-");
            output.push_str(&format!("{} msg={}\n", s.id, msg));
        }
    }

    Ok(output)
}
