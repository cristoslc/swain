mod common;

use std::collections::HashMap;
use std::time::{Duration, SystemTime};

use agentrc::commands;
use agentrc::commands::watch;
use agentrc::commands::worker;
use agentrc::fs::bus::OrchestratorPaths;
use agentrc::model::task::TaskState;
use tempfile::TempDir;

fn setup_run() -> (TempDir, OrchestratorPaths) {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), Some("cargo test"), false).unwrap();
    commands::run::create_in(tmp.path(), "test-run").unwrap();
    let paths = OrchestratorPaths::new(tmp.path());
    (tmp, paths)
}

// --- Test 1: Status change detected with old→new transition ---

#[test]
fn status_change_shows_transition() {
    let (tmp, _paths) = setup_run();

    // Create initial status
    worker::status::run_in(tmp.path(), "001", "in_progress", Some("build"), None, None).unwrap();

    let status_dir = OrchestratorPaths::new(tmp.path())
        .active_run()
        .unwrap()
        .status_dir();
    let status_file = status_dir.join("001.json");

    // Seed previous state as "spawning"
    let mut previous = HashMap::new();
    previous.insert("001".to_string(), TaskState::Spawning);

    let line = watch::process_status_change(&status_file, &mut previous);
    let line = line.expect("should produce output");

    // Should contain old→new transition
    assert!(
        line.contains("spawning") && line.contains("in_progress"),
        "expected 'spawning → in_progress' transition, got: {line}"
    );
    assert!(line.contains("001"), "expected task id in output: {line}");
    assert!(line.contains("build"), "expected phase in output: {line}");
    // Previous state should be updated
    assert_eq!(previous.get("001"), Some(&TaskState::InProgress));
}

// --- Test 2: Heartbeat stale alert ---

#[test]
fn heartbeat_stale_produces_warning() {
    let (_tmp, paths) = setup_run();
    let active = paths.active_run().unwrap();
    let hb_file = active.heartbeat_file("003");

    // Create heartbeat file
    std::fs::write(&hb_file, b"").unwrap();

    // Set mtime to 5 minutes ago
    let old_time = SystemTime::now() - Duration::from_secs(300);
    filetime::set_file_mtime(&hb_file, filetime::FileTime::from_system_time(old_time)).unwrap();

    let warning = watch::check_heartbeat_staleness(&hb_file, 120);
    let warning = warning.expect("should produce a warning");

    assert!(
        warning.contains("WARNING"),
        "expected WARNING in output: {warning}"
    );
    assert!(
        warning.contains("003"),
        "expected task id in warning: {warning}"
    );
    assert!(
        warning.contains("stale heartbeat"),
        "expected 'stale heartbeat' in warning: {warning}"
    );
    // Should include the age in seconds
    assert!(
        warning.contains("300") || warning.contains("29"),
        "expected approximate age in warning: {warning}"
    );
}

// --- Test 3: Heartbeat healthy — no warning ---

#[test]
fn heartbeat_fresh_produces_no_warning() {
    let (tmp, paths) = setup_run();
    let active = paths.active_run().unwrap();

    // Create a fresh heartbeat
    worker::heartbeat::tick(tmp.path(), "003").unwrap();
    let hb_file = active.heartbeat_file("003");

    let result = watch::check_heartbeat_staleness(&hb_file, 120);
    assert!(
        result.is_none(),
        "fresh heartbeat should not produce a warning"
    );
}

// --- Test 4: Unknown task — still prints event gracefully ---

#[test]
fn unknown_task_status_change_still_prints() {
    let (tmp, _paths) = setup_run();

    // Write a status for a task that was never seen before
    worker::status::run_in(tmp.path(), "099", "in_progress", None, None, None).unwrap();

    let status_dir = OrchestratorPaths::new(tmp.path())
        .active_run()
        .unwrap()
        .status_dir();
    let status_file = status_dir.join("099.json");

    // Empty previous map — never seen this task
    let mut previous = HashMap::new();

    let line = watch::process_status_change(&status_file, &mut previous);
    let line = line.expect("should produce output even for unknown task");

    assert!(line.contains("099"), "expected task id: {line}");
    assert!(line.contains("in_progress"), "expected new state: {line}");
    // Should now be tracked
    assert_eq!(previous.get("099"), Some(&TaskState::InProgress));
}

// --- Test 5: Graceful shutdown via channel close ---

#[test]
fn watch_exits_on_channel_close() {
    // This test verifies the watch_with_receiver function exits cleanly
    // when the channel is closed (simulating shutdown).
    let (tmp, _paths) = setup_run();

    let (tx, rx) = std::sync::mpsc::channel::<notify::Event>();
    drop(tx); // close the sending end immediately

    // Should return Ok(()), not hang or panic
    let result = watch::watch_with_receiver(tmp.path(), rx, 120);
    assert!(
        result.is_ok(),
        "watch should exit cleanly when channel closes"
    );
}

// --- Test 6: No active run returns error ---

#[test]
fn watch_no_active_run_returns_error() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    // Init but don't create a run
    commands::init::run_in(tmp.path(), Some("cargo test"), false).unwrap();

    let result = watch::watch(tmp.path());
    assert!(result.is_err());
    let err_msg = format!("{}", result.unwrap_err());
    assert!(
        err_msg.contains("no active run") || err_msg.contains("NoActiveRun"),
        "expected NoActiveRun error, got: {err_msg}"
    );
}

// --- Test: Status change with no previous state shows initial state ---

#[test]
fn status_change_first_seen_shows_arrow_to_new_state() {
    let (tmp, _paths) = setup_run();

    worker::status::run_in(tmp.path(), "005", "completed", Some("done"), None, None).unwrap();

    let status_dir = OrchestratorPaths::new(tmp.path())
        .active_run()
        .unwrap()
        .status_dir();
    let status_file = status_dir.join("005.json");

    let mut previous = HashMap::new();
    let line = watch::process_status_change(&status_file, &mut previous);
    let line = line.expect("should produce output");

    // For first-seen tasks, should show "→ new_state" (no old state)
    assert!(
        line.contains("completed"),
        "expected new state in output: {line}"
    );
    assert!(line.contains("005"), "expected task id: {line}");
}
