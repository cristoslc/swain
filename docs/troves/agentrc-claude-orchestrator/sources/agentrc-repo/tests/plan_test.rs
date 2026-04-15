mod common;

use agentrc::commands;
use tempfile::TempDir;

/// Helper: create a project with an active run and return (tmpdir, tasks_dir path)
fn setup_project_with_run() -> (TempDir, std::path::PathBuf) {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), None, false).unwrap();
    commands::run::create_in(tmp.path(), "test-plan").unwrap();

    let paths = agentrc::fs::bus::OrchestratorPaths::new(tmp.path());
    let active = paths.active_run().unwrap();
    let tasks_dir = active.tasks_dir();

    (tmp, tasks_dir)
}

/// Helper: write a task brief with given id, slug, and depends_on list
fn write_brief(tasks_dir: &std::path::Path, id: &str, slug: &str, depends_on: &[&str]) {
    let deps = if depends_on.is_empty() {
        "[]".to_string()
    } else {
        let items: Vec<String> = depends_on.iter().map(|d| format!("\"{}\"", d)).collect();
        format!("[{}]", items.join(", "))
    };
    let content = format!(
        "---\nid: \"{id}\"\nslug: {slug}\nclassification: writer\nbase_branch: main\nbranch: orc/{id}-{slug}\ndepends_on: {deps}\ncreated_at: 2026-04-11T14:30:00Z\n---\n# Task {id}"
    );
    let filename = format!("{id}-{slug}.md");
    std::fs::write(tasks_dir.join(filename), content).unwrap();
}

// ---- Test 1: Empty plan ----
#[test]
fn validate_empty_plan_returns_error() {
    let (tmp, _tasks_dir) = setup_project_with_run();
    // No briefs written — tasks dir exists but is empty
    let result = commands::plan::validate_in(tmp.path()).unwrap();
    assert!(!result.is_valid(), "empty plan should be invalid");
    assert!(
        result.errors.iter().any(|e| e.contains("No tasks")),
        "should mention no tasks: {:?}",
        result.errors
    );
}

// ---- Test 2: Single task, no deps ----
#[test]
fn validate_single_task_no_deps_is_valid() {
    let (tmp, tasks_dir) = setup_project_with_run();
    write_brief(&tasks_dir, "001", "solo", &[]);
    let result = commands::plan::validate_in(tmp.path()).unwrap();
    assert!(
        result.is_valid(),
        "single task should be valid: {:?}",
        result.errors
    );
    assert_eq!(result.task_count, 1);
}

// ---- Test 3: Valid DAG with 3 tasks ----
#[test]
fn validate_valid_dag_three_tasks() {
    let (tmp, tasks_dir) = setup_project_with_run();
    write_brief(&tasks_dir, "001", "first", &[]);
    write_brief(&tasks_dir, "002", "second", &["001"]);
    write_brief(&tasks_dir, "003", "third", &["002"]);
    let result = commands::plan::validate_in(tmp.path()).unwrap();
    assert!(
        result.is_valid(),
        "valid DAG should pass: {:?}",
        result.errors
    );
    assert_eq!(result.task_count, 3);
}

// ---- Test 4: Duplicate IDs ----
#[test]
fn validate_duplicate_ids_returns_error() {
    let (tmp, tasks_dir) = setup_project_with_run();
    write_brief(&tasks_dir, "001", "first", &[]);
    // Write another brief with the same ID but different slug
    write_brief(&tasks_dir, "001", "duplicate", &[]);
    let result = commands::plan::validate_in(tmp.path()).unwrap();
    assert!(!result.is_valid(), "duplicate IDs should be invalid");
    assert!(
        result
            .errors
            .iter()
            .any(|e| e.contains("Duplicate") && e.contains("001")),
        "should report duplicate ID: {:?}",
        result.errors
    );
}

// ---- Test 5: Self-reference ----
#[test]
fn validate_self_reference_returns_error() {
    let (tmp, tasks_dir) = setup_project_with_run();
    write_brief(&tasks_dir, "001", "selfdep", &["001"]);
    let result = commands::plan::validate_in(tmp.path()).unwrap();
    assert!(!result.is_valid(), "self-reference should be invalid");
    assert!(
        result
            .errors
            .iter()
            .any(|e| e.contains("Self-reference") && e.contains("001")),
        "should report self-reference: {:?}",
        result.errors
    );
}

// ---- Test 6: Missing dependency ----
#[test]
fn validate_missing_dependency_returns_error() {
    let (tmp, tasks_dir) = setup_project_with_run();
    write_brief(&tasks_dir, "001", "first", &[]);
    write_brief(&tasks_dir, "002", "second", &["999"]); // 999 doesn't exist
    let result = commands::plan::validate_in(tmp.path()).unwrap();
    assert!(!result.is_valid(), "missing dep should be invalid");
    assert!(
        result
            .errors
            .iter()
            .any(|e| e.contains("Missing dependency") && e.contains("999")),
        "should report missing dep: {:?}",
        result.errors
    );
}

// ---- Test 7: Cycle detection ----
#[test]
fn validate_cycle_returns_error() {
    let (tmp, tasks_dir) = setup_project_with_run();
    write_brief(&tasks_dir, "001", "alpha", &["003"]); // 001 depends on 003
    write_brief(&tasks_dir, "002", "beta", &["001"]); // 002 depends on 001
    write_brief(&tasks_dir, "003", "gamma", &["002"]); // 003 depends on 002 → cycle
    let result = commands::plan::validate_in(tmp.path()).unwrap();
    assert!(!result.is_valid(), "cycle should be invalid");
    assert!(
        result.errors.iter().any(|e| e.contains("Cycle detected")),
        "should report cycle: {:?}",
        result.errors
    );
    // The cycle message should mention the involved task IDs
    let cycle_err = result.errors.iter().find(|e| e.contains("Cycle")).unwrap();
    assert!(
        cycle_err.contains("001"),
        "cycle should mention 001: {cycle_err}"
    );
    assert!(
        cycle_err.contains("002"),
        "cycle should mention 002: {cycle_err}"
    );
    assert!(
        cycle_err.contains("003"),
        "cycle should mention 003: {cycle_err}"
    );
}

// ---- Test 8: Diamond DAG (no false positive) ----
#[test]
fn validate_diamond_dag_is_valid() {
    let (tmp, tasks_dir) = setup_project_with_run();
    // A→B, A→C, B→D, C→D  (diamond shape, no cycle)
    write_brief(&tasks_dir, "001", "a-root", &[]);
    write_brief(&tasks_dir, "002", "b-left", &["001"]);
    write_brief(&tasks_dir, "003", "c-right", &["001"]);
    write_brief(&tasks_dir, "004", "d-sink", &["002", "003"]);
    let result = commands::plan::validate_in(tmp.path()).unwrap();
    assert!(
        result.is_valid(),
        "diamond DAG should be valid: {:?}",
        result.errors
    );
    assert_eq!(result.task_count, 4);
}
