use std::path::Path;

use anyhow::{Context, Result};

use crate::commands::spawn;
use crate::fs::bus::OrchestratorPaths;
use crate::fs::frontmatter;
use crate::model::config::OrchestratorConfig;
use crate::model::error::AppError;
use crate::tmux::wrapper::Tmux;

/// System-managed frontmatter fields that are preserved across brief replacements.
const SYSTEM_FIELDS: &[&str] = &["pane_id", "worktree", "created_at"];

/// Amend a task brief, either by replacing its body or appending a message.
///
/// - `brief_path`: replace body with contents of file, preserving system frontmatter
/// - `message`: append an amendment section to the existing brief
///
/// Increments `redispatch_count` in the task's status JSON and sends a notification
/// to the worker pane if it is alive.
pub fn run_in(
    project_root: &Path,
    task_id: &str,
    brief_path: Option<&str>,
    message: Option<&str>,
) -> Result<()> {
    if brief_path.is_none() && message.is_none() {
        return Err(AppError::AmendSourceRequired.into());
    }

    let paths = OrchestratorPaths::new(project_root);
    let active = paths.active_run().ok_or(AppError::NoActiveRun)?;

    // Find the task brief
    let task_brief_path = spawn::find_task_brief(&active, task_id)?;

    // Read config for max_redispatch_attempts
    let config_path = paths.config();
    let config: OrchestratorConfig = if config_path.exists() {
        let content = std::fs::read_to_string(&config_path)
            .with_context(|| format!("failed to read config: {}", config_path.display()))?;
        serde_json::from_str(&content).context("failed to parse orchestrator config")?
    } else {
        OrchestratorConfig::default()
    };

    // Read status to check redispatch limit
    let status_file = active.status_file(task_id);
    let mut status: crate::model::task::TaskStatus = if status_file.exists() {
        let content = std::fs::read_to_string(&status_file)
            .with_context(|| format!("failed to read status: {}", status_file.display()))?;
        serde_json::from_str(&content).context("failed to parse task status")?
    } else {
        anyhow::bail!("no status file for task {task_id}");
    };

    // Check redispatch limit before amending
    if status.redispatch_count >= config.max_redispatch_attempts {
        return Err(AppError::MaxRedispatchReached {
            task_id: task_id.to_string(),
            max: config.max_redispatch_attempts,
        }
        .into());
    }

    // Read the original brief content
    let original_content = std::fs::read_to_string(&task_brief_path)
        .with_context(|| format!("failed to read task brief: {}", task_brief_path.display()))?;

    // Apply the amendment
    let updated_content = if let Some(new_brief_file) = brief_path {
        replace_brief(&original_content, new_brief_file)?
    } else if let Some(msg) = message {
        append_amendment(&original_content, msg)
    } else {
        unreachable!()
    };

    // Write the updated brief
    std::fs::write(&task_brief_path, &updated_content)
        .with_context(|| format!("failed to write task brief: {}", task_brief_path.display()))?;

    // Increment redispatch_count
    status.redispatch_count += 1;
    status.updated_at = chrono::Utc::now();
    let json = serde_json::to_string_pretty(&status).context("failed to serialize task status")?;
    std::fs::write(&status_file, &json)
        .with_context(|| format!("failed to write status: {}", status_file.display()))?;

    // Notify worker pane if alive (best-effort)
    if let Some(ref pane_id) = status.pane_id {
        let tmux = Tmux::new();
        let notification = format!(
            "# AMENDMENT: Your task brief has been updated. Re-read {}.",
            task_brief_path.display()
        );
        // Best-effort: don't fail the amend if tmux send-keys fails
        let _ = tmux.send_keys(pane_id, &notification);
    }

    Ok(())
}

/// Replace the brief body with contents from a new file, preserving system frontmatter fields.
fn replace_brief(original_content: &str, new_brief_file: &str) -> Result<String> {
    let new_content = std::fs::read_to_string(new_brief_file)
        .with_context(|| format!("failed to read replacement brief: {new_brief_file}"))?;

    // Extract system field values from the original brief
    let mut system_values: Vec<(&str, String)> = Vec::new();
    for &field in SYSTEM_FIELDS {
        if let Ok(Some(value)) = frontmatter::get_field(original_content, field) {
            system_values.push((field, value));
        }
    }

    // Start with the new content and upsert each system field from the original
    let mut result = new_content;
    for (field, value) in &system_values {
        result = frontmatter::upsert_field(&result, field, value)?;
    }

    Ok(result)
}

/// Append an amendment section to the existing brief.
fn append_amendment(original_content: &str, message: &str) -> String {
    let mut result = original_content.to_string();
    if !result.ends_with('\n') {
        result.push('\n');
    }
    result.push_str(&format!("\n## Amendment\n\n{message}\n"));
    result
}
