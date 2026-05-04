use std::os::unix::fs::symlink;
use std::path::PathBuf;

use agentrc::events;
use agentrc::fs::run::RunPaths;
use agentrc::model::event::{EventType, OrcEvent, Severity};
use chrono::{TimeZone, Utc};
use tempfile::TempDir;

/// Set up the `.orchestrator/active` symlink and run directory inside a temp dir,
/// returning the temp dir handle (must stay alive for the duration of the test).
fn setup_active_run(tmp: &TempDir) -> PathBuf {
    let root = tmp.path();
    let run_dir = root.join(".orchestrator/runs/test-run");
    std::fs::create_dir_all(&run_dir).unwrap();
    let active_link = root.join(".orchestrator/active");
    symlink("runs/test-run", &active_link).unwrap();
    run_dir
}

// ── Test 1: emit writes JSONL ──────────────────────────────────────────────

#[test]
fn emit_writes_jsonl() {
    let tmp = TempDir::new().unwrap();
    let run_dir = setup_active_run(&tmp);
    let root = tmp.path();

    events::emit_info(root, EventType::Spawned, "001", "worker spawned").unwrap();
    events::emit_info(
        root,
        EventType::StateChange,
        "002",
        "state changed to running",
    )
    .unwrap();
    events::emit_info(root, EventType::Completed, "003", "task completed").unwrap();

    let events_file = run_dir.join("events.jsonl");
    assert!(events_file.exists(), "events.jsonl should be created");

    let content = std::fs::read_to_string(&events_file).unwrap();
    let lines: Vec<&str> = content.lines().collect();
    assert_eq!(lines.len(), 3, "should have exactly 3 lines");

    // Parse each line as valid OrcEvent JSON
    for (i, line) in lines.iter().enumerate() {
        let event: OrcEvent = serde_json::from_str(line)
            .unwrap_or_else(|e| panic!("line {} is not valid OrcEvent JSON: {}", i + 1, e));
        // Verify basic structure is present
        assert!(
            !event.message.is_empty(),
            "event {} should have a non-empty message",
            i + 1
        );
        assert!(
            event.task_id.is_some(),
            "event {} should have a task_id",
            i + 1
        );
    }

    // Verify specific content of each line
    let e1: OrcEvent = serde_json::from_str(lines[0]).unwrap();
    assert_eq!(e1.message, "worker spawned");
    assert_eq!(e1.task_id.as_deref(), Some("001"));

    let e2: OrcEvent = serde_json::from_str(lines[1]).unwrap();
    assert_eq!(e2.message, "state changed to running");
    assert_eq!(e2.task_id.as_deref(), Some("002"));

    let e3: OrcEvent = serde_json::from_str(lines[2]).unwrap();
    assert_eq!(e3.message, "task completed");
    assert_eq!(e3.task_id.as_deref(), Some("003"));
}

// ── Test 2: tail returns last N events ─────────────────────────────────────

#[test]
fn tail_returns_last_n() {
    let tmp = TempDir::new().unwrap();
    setup_active_run(&tmp);
    let root = tmp.path();

    for i in 1..=10 {
        events::emit_info(root, EventType::StateChange, "001", &format!("event {i}")).unwrap();
    }

    let result = events::tail(root, 3).unwrap();
    assert_eq!(result.len(), 3, "tail(3) should return exactly 3 events");

    assert_eq!(result[0].message, "event 8");
    assert_eq!(result[1].message, "event 9");
    assert_eq!(result[2].message, "event 10");
}

// ── Test 3: serialization roundtrip ────────────────────────────────────────

#[test]
fn event_serialization_roundtrip() {
    let timestamp = Utc.with_ymd_and_hms(2026, 4, 12, 10, 30, 0).unwrap();

    let original = OrcEvent {
        timestamp,
        event_type: EventType::MergeConflict,
        task_id: Some("042".to_string()),
        severity: Severity::Warn,
        message: "merge conflict on src/main.rs".to_string(),
    };

    let json = serde_json::to_string(&original).unwrap();
    let deserialized: OrcEvent = serde_json::from_str(&json).unwrap();

    // Compare all fields individually (types don't derive PartialEq)
    assert_eq!(deserialized.timestamp, original.timestamp);
    assert_eq!(deserialized.task_id, original.task_id);
    assert_eq!(deserialized.message, original.message);

    // EventType and Severity don't derive PartialEq, so compare via debug repr
    assert_eq!(
        format!("{:?}", deserialized.event_type),
        format!("{:?}", original.event_type)
    );
    assert_eq!(
        format!("{:?}", deserialized.severity),
        format!("{:?}", original.severity)
    );

    // Also verify the JSON round-trips identically
    let json_again = serde_json::to_string(&deserialized).unwrap();
    assert_eq!(json, json_again, "re-serialized JSON should be identical");
}

// ── Test 4: events_log path ────────────────────────────────────────────────

#[test]
fn events_log_path() {
    let run = RunPaths::new(PathBuf::from("/some/run/dir"));
    let path = run.events_log();
    assert_eq!(
        path,
        PathBuf::from("/some/run/dir/events.jsonl"),
        "events_log() should return <run_dir>/events.jsonl"
    );
}
