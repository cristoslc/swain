mod common;

use agentrc::commands;
use agentrc::commands::worker;
use agentrc::fs::bus::OrchestratorPaths;
use tempfile::TempDir;

fn setup_run_with_tasks() -> (TempDir, OrchestratorPaths) {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), Some("cargo test"), false).unwrap();
    commands::run::create_in(tmp.path(), "test-run").unwrap();
    worker::status::run_in(tmp.path(), "001", "completed", None, Some("done"), None).unwrap();
    worker::status::run_in(
        tmp.path(),
        "002",
        "in_progress",
        Some("testing"),
        Some("running tests"),
        None,
    )
    .unwrap();
    worker::status::run_in(
        tmp.path(),
        "003",
        "blocked",
        None,
        Some("waiting on 001"),
        None,
    )
    .unwrap();
    let paths = OrchestratorPaths::new(tmp.path());
    (tmp, paths)
}

#[test]
fn status_aggregates_all_tasks() {
    let (tmp, _) = setup_run_with_tasks();
    let statuses = commands::status::collect_statuses(tmp.path()).unwrap();
    assert_eq!(statuses.len(), 3);
}

#[test]
fn status_json_output() {
    let (tmp, _) = setup_run_with_tasks();
    let output = commands::status::format_json(tmp.path()).unwrap();
    let parsed: serde_json::Value = serde_json::from_str(&output).unwrap();
    assert!(parsed.is_array());
    assert_eq!(parsed.as_array().unwrap().len(), 3);
}

#[test]
fn status_tty_output_contains_task_info() {
    let (tmp, _) = setup_run_with_tasks();
    let output = commands::status::format_tty(tmp.path()).unwrap();
    assert!(output.contains("001"));
    assert!(output.contains("002"));
    assert!(output.contains("003"));
    assert!(output.contains("completed"));
    assert!(output.contains("in_progress"));
    assert!(output.contains("blocked"));
}

#[test]
fn status_detects_stale_heartbeats() {
    let (tmp, paths) = setup_run_with_tasks();
    let active = paths.active_run().unwrap();
    let hb_file = active.heartbeat_file("002");
    std::fs::write(&hb_file, b"").unwrap();
    // Set mtime to 5 minutes ago
    let old_time = std::time::SystemTime::now() - std::time::Duration::from_secs(300);
    filetime::set_file_mtime(&hb_file, filetime::FileTime::from_system_time(old_time)).unwrap();
    let stale = commands::status::find_stale_heartbeats(tmp.path(), 120).unwrap();
    assert_eq!(stale.len(), 1);
    assert_eq!(stale[0], "002");
}

#[test]
fn status_no_stale_when_heartbeat_fresh() {
    let (tmp, _paths) = setup_run_with_tasks();
    // Touch a fresh heartbeat
    worker::heartbeat::tick(tmp.path(), "002").unwrap();
    let stale = commands::status::find_stale_heartbeats(tmp.path(), 120).unwrap();
    assert!(stale.is_empty());
}

// ── format_duration ─────────────────────────────────────────────────────────

#[test]
fn format_duration_zero_seconds() {
    assert_eq!(commands::status::format_duration(0), "0s");
}

#[test]
fn format_duration_seconds_only() {
    assert_eq!(commands::status::format_duration(45), "45s");
}

#[test]
fn format_duration_minutes_and_seconds() {
    assert_eq!(commands::status::format_duration(65), "1m 5s");
}

#[test]
fn format_duration_hours_and_minutes() {
    assert_eq!(commands::status::format_duration(3661), "1h 1m");
}

#[test]
fn format_duration_exact_minutes() {
    assert_eq!(commands::status::format_duration(120), "2m 0s");
}

#[test]
fn format_duration_negative_returns_zero() {
    assert_eq!(commands::status::format_duration(-10), "0s");
}

// ── Pane title in TTY output ────────────────────────────────────────────────

#[test]
fn status_displays_pane_title_over_raw_id() {
    let (tmp, paths) = setup_run_with_tasks();
    let active = paths.active_run().unwrap();

    // Manually write a status file with pane_title set
    let status_file = active.status_file("002");
    let content = std::fs::read_to_string(&status_file).unwrap();
    let mut status: agentrc::model::task::TaskStatus = serde_json::from_str(&content).unwrap();
    status.pane_id = Some("%42".into());
    status.pane_title = Some("orc:002:review-deps".into());
    let json = serde_json::to_string_pretty(&status).unwrap();
    std::fs::write(&status_file, json).unwrap();

    let output = commands::status::format_tty(tmp.path()).unwrap();
    assert!(
        output.contains("orc:002:review-deps"),
        "TTY output should show pane_title, got:\n{output}"
    );
    // raw pane ID should NOT appear in the table row for task 002
    // (it may appear in other tasks that don't have a title)
    assert!(
        !output.contains("%42"),
        "TTY output should not show raw pane ID when title is set, got:\n{output}"
    );
}

// ── TTY output with elapsed/total columns ───────────────────────────────────

#[test]
fn status_tty_output_has_elapsed_and_total_columns() {
    let (tmp, _) = setup_run_with_tasks();
    let output = commands::status::format_tty(tmp.path()).unwrap();
    assert!(output.contains("ELAPSED"), "should contain ELAPSED header");
    assert!(output.contains("TOTAL"), "should contain TOTAL header");
}

// ── JSON output includes phase_history and computed durations ────────────────

#[test]
fn status_json_includes_phase_history() {
    let (tmp, _) = setup_run_with_tasks();
    let output = commands::status::format_json(tmp.path()).unwrap();
    let parsed: serde_json::Value = serde_json::from_str(&output).unwrap();
    let tasks = parsed.as_array().unwrap();
    // Every task should have phase_history array
    for task in tasks {
        assert!(
            task.get("phase_history").is_some(),
            "should have phase_history"
        );
        assert!(
            task["phase_history"].is_array(),
            "phase_history should be array"
        );
    }
}

#[test]
fn status_json_includes_elapsed_and_total_sec() {
    let (tmp, _) = setup_run_with_tasks();
    let output = commands::status::format_json(tmp.path()).unwrap();
    let parsed: serde_json::Value = serde_json::from_str(&output).unwrap();
    let tasks = parsed.as_array().unwrap();
    for task in tasks {
        assert!(task.get("elapsed_sec").is_some(), "should have elapsed_sec");
        assert!(task.get("total_sec").is_some(), "should have total_sec");
    }
}

#[test]
fn status_json_elapsed_and_total_are_non_negative() {
    let (tmp, _) = setup_run_with_tasks();
    let output = commands::status::format_json(tmp.path()).unwrap();
    let parsed: serde_json::Value = serde_json::from_str(&output).unwrap();
    let tasks = parsed.as_array().unwrap();
    for task in tasks {
        let elapsed = task["elapsed_sec"].as_i64().unwrap();
        let total = task["total_sec"].as_i64().unwrap();
        assert!(elapsed >= 0, "elapsed_sec should be >= 0");
        assert!(total >= 0, "total_sec should be >= 0");
    }
}

// ── TTY token summary ───────────────────────────────────────────────────────

fn setup_run_with_tokens() -> (TempDir, OrchestratorPaths) {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), Some("cargo test"), false).unwrap();
    commands::run::create_in(tmp.path(), "test-run").unwrap();
    worker::status::run_in(
        tmp.path(),
        "001",
        "in_progress",
        None,
        Some("working"),
        Some(12_400),
    )
    .unwrap();
    worker::status::run_in(
        tmp.path(),
        "002",
        "in_progress",
        None,
        Some("working"),
        Some(32_800),
    )
    .unwrap();
    let paths = OrchestratorPaths::new(tmp.path());
    (tmp, paths)
}

#[test]
fn status_tty_shows_total_tokens() {
    let (tmp, _) = setup_run_with_tokens();
    let output = commands::status::format_tty(tmp.path()).unwrap();
    assert!(
        output.contains("Total tokens:"),
        "should contain 'Total tokens:' line, got:\n{output}"
    );
    assert!(
        output.contains("45.2k"),
        "should show 45.2k total, got:\n{output}"
    );
    assert!(
        output.contains("2 workers"),
        "should mention worker count, got:\n{output}"
    );
}

#[test]
fn status_tty_no_token_line_when_no_tokens() {
    let (tmp, _) = setup_run_with_tasks();
    let output = commands::status::format_tty(tmp.path()).unwrap();
    assert!(
        !output.contains("Total tokens:"),
        "should not contain 'Total tokens:' when no tokens reported"
    );
}

// ── TTY themed output: symbols and ANSI colors ─────────────────────────────

#[test]
fn status_tty_contains_symbols() {
    let (tmp, _) = setup_run_with_tasks();
    let output = commands::status::format_tty(tmp.path()).unwrap();
    assert!(
        output.contains('✓'),
        "completed task should show ✓ symbol, got:\n{output}"
    );
    assert!(
        output.contains('●'),
        "in_progress task should show ● symbol, got:\n{output}"
    );
    assert!(
        output.contains('◼'),
        "blocked task should show ◼ symbol, got:\n{output}"
    );
}

#[test]
fn status_tty_contains_ansi() {
    let (tmp, _) = setup_run_with_tasks();
    let output = commands::status::format_tty(tmp.path()).unwrap();
    // Should contain ANSI RGB escape sequences
    assert!(
        output.contains("\x1b[38;2;"),
        "TTY output should contain ANSI RGB color codes, got:\n{output}"
    );
    // Should contain reset sequences
    assert!(
        output.contains("\x1b[0m"),
        "TTY output should contain ANSI reset codes, got:\n{output}"
    );
}
