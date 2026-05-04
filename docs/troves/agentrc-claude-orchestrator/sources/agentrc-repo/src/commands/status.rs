use std::path::Path;
use std::time::SystemTime;

use anyhow::{Context, Result};
use chrono::Utc;
use serde::Serialize;

use crate::fs::bus::OrchestratorPaths;
use crate::model::error::AppError;
use crate::model::task::{PhaseEntry, TaskState, TaskStatus};
use crate::tui::widgets::table::format_tokens;

// ---------------------------------------------------------------------------
// ANSI RGB color helpers for themed CLI output
// ---------------------------------------------------------------------------

const RESET: &str = "\x1b[0m";

/// Build an ANSI 24-bit foreground color escape sequence.
fn rgb(r: u8, g: u8, b: u8) -> String {
    format!("\x1b[38;2;{r};{g};{b}m")
}

/// Return a Unicode symbol representing the task state.
fn state_symbol(state: &TaskState) -> &'static str {
    match state {
        TaskState::Spawning => "\u{25CC}",   // ◌
        TaskState::Ready => "\u{25CB}",      // ○
        TaskState::InProgress => "\u{25CF}", // ●
        TaskState::Blocked => "\u{25FC}",    // ◼
        TaskState::Completed => "\u{2713}",  // ✓
        TaskState::Failed => "\u{2717}",     // ✗
        TaskState::Aborted => "\u{2298}",    // ⊘
    }
}

/// Return an ANSI RGB escape sequence for the given task state.
fn state_color(state: &TaskState) -> String {
    match state {
        TaskState::Spawning => rgb(70, 70, 85),      // TEXT_MUTED
        TaskState::Ready => rgb(200, 200, 210),      // TEXT
        TaskState::InProgress => rgb(120, 210, 120), // OK
        TaskState::Blocked => rgb(230, 180, 80),     // WARN
        TaskState::Completed => rgb(120, 150, 220),  // DONE
        TaskState::Failed | TaskState::Aborted => rgb(220, 100, 100), // ERR
    }
}

/// CLI entry point — uses current directory.
pub fn run(json: bool) -> Result<()> {
    let cwd = std::env::current_dir().context("cannot determine current directory")?;
    if json {
        let output = format_json(&cwd)?;
        println!("{output}");
    } else {
        let output = format_tty(&cwd)?;
        print!("{output}");
    }
    Ok(())
}

/// Read all `.json` files from the active run's status dir, deserialize, and sort by id.
pub fn collect_statuses(project_root: &Path) -> Result<Vec<TaskStatus>> {
    let paths = OrchestratorPaths::new(project_root);
    let active = paths.active_run().ok_or(AppError::NoActiveRun)?;
    let status_dir = active.status_dir();

    let mut statuses: Vec<TaskStatus> = Vec::new();

    if status_dir.is_dir() {
        for entry in std::fs::read_dir(&status_dir)
            .with_context(|| format!("failed to read status dir: {}", status_dir.display()))?
        {
            let entry = entry?;
            let path = entry.path();
            if path.extension().and_then(|e| e.to_str()) == Some("json") {
                let content = std::fs::read_to_string(&path)
                    .with_context(|| format!("failed to read {}", path.display()))?;
                let status: TaskStatus =
                    serde_json::from_str(&content).map_err(|e| AppError::StatusParseError {
                        path: path.clone(),
                        reason: e.to_string(),
                    })?;
                statuses.push(status);
            }
        }
    }

    statuses.sort_by(|a, b| a.id.cmp(&b.id));
    Ok(statuses)
}

/// Enriched status for JSON output: includes phase_history and computed durations.
#[derive(Serialize)]
struct EnrichedStatus {
    #[serde(flatten)]
    status: TaskStatus,
    elapsed_sec: i64,
    total_sec: i64,
}

/// Compute elapsed seconds since the last phase_history entry, or 0 if empty.
fn elapsed_sec(history: &[PhaseEntry]) -> i64 {
    history
        .last()
        .map(|e| (Utc::now() - e.entered_at).num_seconds().max(0))
        .unwrap_or(0)
}

/// Compute total seconds since the first phase_history entry, or 0 if empty.
fn total_sec(history: &[PhaseEntry]) -> i64 {
    history
        .first()
        .map(|e| (Utc::now() - e.entered_at).num_seconds().max(0))
        .unwrap_or(0)
}

/// Collect statuses and serialize as a JSON array with enriched duration fields.
pub fn format_json(project_root: &Path) -> Result<String> {
    let statuses = collect_statuses(project_root)?;
    let enriched: Vec<EnrichedStatus> = statuses
        .into_iter()
        .map(|s| {
            let elapsed = elapsed_sec(&s.phase_history);
            let total = total_sec(&s.phase_history);
            EnrichedStatus {
                status: s,
                elapsed_sec: elapsed,
                total_sec: total,
            }
        })
        .collect();
    let json = serde_json::to_string_pretty(&enriched).context("failed to serialize statuses")?;
    Ok(json)
}

/// Collect statuses and format as an aligned table with columns:
/// ID, STATE, PHASE, ELAPSED, TOTAL, PANE, MESSAGE.
/// Appends stale heartbeat warnings at the end.
pub fn format_tty(project_root: &Path) -> Result<String> {
    let statuses = collect_statuses(project_root)?;
    let stale = find_stale_heartbeats(project_root, 120)?;

    let mut output = String::new();

    let dim = rgb(120, 120, 135); // TEXT_DIM
    let text = rgb(200, 200, 210); // TEXT
    let pane_color = rgb(180, 140, 220); // PANE
    let accent = rgb(230, 180, 80); // ACCENT
    let warn = rgb(230, 180, 80); // WARN

    // Header — column names in TEXT_DIM
    output.push_str(&format!(
        "{dim}{:<8} {:<14} {:<12} {:<10} {:<10} {:<25} {}{RESET}\n",
        "ID", "STATE", "PHASE", "ELAPSED", "TOTAL", "PANE", "MESSAGE",
    ));
    // Separator in TEXT_DIM
    output.push_str(&format!("{dim}{}{RESET}\n", "-".repeat(105)));

    for s in &statuses {
        let phase = s.phase.as_deref().unwrap_or("-");
        let pane = s
            .pane_title
            .as_deref()
            .or(s.pane_id.as_deref())
            .unwrap_or("-");
        let msg = s.last_message.as_deref().unwrap_or("-");
        let elapsed = format_duration(elapsed_sec(&s.phase_history));
        let total = format_duration(total_sec(&s.phase_history));

        let sc = state_color(&s.state);
        let sym = state_symbol(&s.state);
        // "◌ spawning" — symbol + space + state text, padded to 14 visible chars
        let state_text = format!("{sym} {}", s.state);

        output.push_str(&format!(
            "{text}{:<8}{RESET} {sc}{:<14}{RESET} {text}{:<12}{RESET} \
             {dim}{:<10}{RESET} {dim}{:<10}{RESET} \
             {pane_color}{:<25}{RESET} {text}{}{RESET}\n",
            s.id, state_text, phase, elapsed, total, pane, msg,
        ));
    }

    // Total token summary
    let total_tokens: u64 = statuses.iter().filter_map(|s| s.token_usage).sum();
    let workers_with_tokens = statuses.iter().filter(|s| s.token_usage.is_some()).count();
    if workers_with_tokens > 0 {
        output.push_str(&format!(
            "\n{dim}Total tokens:{RESET} {accent}{}{RESET} {dim}across {} workers{RESET}\n",
            format_tokens(total_tokens),
            workers_with_tokens,
        ));
    }

    if !stale.is_empty() {
        output.push('\n');
        for id in &stale {
            output.push_str(&format!(
                "{warn}WARNING: stale heartbeat for task {id}{RESET}\n"
            ));
        }
    }

    Ok(output)
}

/// Format a duration in seconds as a human-readable string.
///
/// - Under 60s: "45s"
/// - Under 1h: "2m 15s"
/// - 1h+: "1h 3m" (seconds omitted)
/// - Negative or zero: "0s"
pub fn format_duration(secs: i64) -> String {
    if secs <= 0 {
        return "0s".to_string();
    }
    let s = secs as u64;
    let hours = s / 3600;
    let minutes = (s % 3600) / 60;
    let seconds = s % 60;

    if hours > 0 {
        format!("{hours}h {minutes}m")
    } else if minutes > 0 {
        format!("{minutes}m {seconds}s")
    } else {
        format!("{seconds}s")
    }
}

/// Read heartbeats dir, check mtime of each `.alive` file against the timeout
/// threshold, and return a list of stale task IDs.
pub fn find_stale_heartbeats(project_root: &Path, timeout_sec: u64) -> Result<Vec<String>> {
    let paths = OrchestratorPaths::new(project_root);
    let active = paths.active_run().ok_or(AppError::NoActiveRun)?;
    let hb_dir = active.heartbeats_dir();

    let mut stale: Vec<String> = Vec::new();
    let now = SystemTime::now();

    if hb_dir.is_dir() {
        for entry in std::fs::read_dir(&hb_dir)
            .with_context(|| format!("failed to read heartbeats dir: {}", hb_dir.display()))?
        {
            let entry = entry?;
            let path = entry.path();
            if path.extension().and_then(|e| e.to_str()) == Some("alive") {
                let metadata = std::fs::metadata(&path)
                    .with_context(|| format!("failed to stat {}", path.display()))?;
                let modified = metadata
                    .modified()
                    .with_context(|| format!("failed to get mtime for {}", path.display()))?;
                if let Ok(age) = now.duration_since(modified) {
                    if age.as_secs() >= timeout_sec {
                        if let Some(stem) = path.file_stem().and_then(|s| s.to_str()) {
                            stale.push(stem.to_string());
                        }
                    }
                }
            }
        }
    }

    stale.sort();
    Ok(stale)
}
