use std::io::Write;
use std::path::Path;

use anyhow::{Context, Result};
use chrono::Utc;

use crate::fs::bus::OrchestratorPaths;
use crate::model::error::AppError;
use crate::model::event::{EventType, OrcEvent, Severity};

pub fn emit(project_root: &Path, event: OrcEvent) -> Result<()> {
    let paths = OrchestratorPaths::new(project_root);
    let run = paths.active_run().ok_or(AppError::NoActiveRun)?;
    let log_path = run.events_log();

    let mut file = std::fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(&log_path)
        .with_context(|| format!("failed to open events log: {}", log_path.display()))?;

    let line = serde_json::to_string(&event).context("failed to serialize event")?;
    writeln!(file, "{line}")
        .with_context(|| format!("failed to write to events log: {}", log_path.display()))?;

    Ok(())
}

pub fn emit_info(
    project_root: &Path,
    event_type: EventType,
    task_id: &str,
    message: &str,
) -> Result<()> {
    let event = OrcEvent {
        timestamp: Utc::now(),
        event_type,
        task_id: Some(task_id.to_string()),
        severity: Severity::Info,
        message: message.to_string(),
    };
    emit(project_root, event)
}

pub fn emit_warn(
    project_root: &Path,
    event_type: EventType,
    task_id: Option<&str>,
    message: &str,
) -> Result<()> {
    let event = OrcEvent {
        timestamp: Utc::now(),
        event_type,
        task_id: task_id.map(|s| s.to_string()),
        severity: Severity::Warn,
        message: message.to_string(),
    };
    emit(project_root, event)
}

pub fn tail(project_root: &Path, count: usize) -> Result<Vec<OrcEvent>> {
    let paths = OrchestratorPaths::new(project_root);
    let run = paths.active_run().ok_or(AppError::NoActiveRun)?;
    let log_path = run.events_log();

    if !log_path.exists() {
        return Ok(Vec::new());
    }

    let content = std::fs::read_to_string(&log_path)
        .with_context(|| format!("failed to read events log: {}", log_path.display()))?;

    // Skip unparseable lines (e.g. truncated writes from crashes)
    let events: Vec<OrcEvent> = content
        .lines()
        .filter(|line| !line.trim().is_empty())
        .filter_map(|line| serde_json::from_str(line).ok())
        .collect();

    let skip = events.len().saturating_sub(count);
    Ok(events.into_iter().skip(skip).collect())
}
