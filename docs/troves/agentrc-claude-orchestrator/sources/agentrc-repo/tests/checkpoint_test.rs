mod common;

use agentrc::commands;
use agentrc::fs::bus::OrchestratorPaths;
use tempfile::TempDir;

#[test]
fn checkpoint_save_creates_file() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), Some("cargo test"), false).unwrap();
    commands::run::create_in(tmp.path(), "test-run").unwrap();

    // Create a task with a branch
    let paths = OrchestratorPaths::new(tmp.path());
    let active = paths.active_run().unwrap();
    let git = agentrc::git::wrapper::Git::new(tmp.path());
    let wt_path = active.worktree_dir("001");
    git.create_worktree(&wt_path, "orc/001-test", "HEAD")
        .unwrap();

    // Write a task brief so checkpoint can read branch info
    let brief_content = r#"---
id: "001"
slug: test
classification: writer
base_branch: master
branch: orc/001-test
pane_id: null
depends_on: []
created_at: 2026-04-12T00:00:00Z
---

# Task 001: Test
"#;
    std::fs::write(active.tasks_dir().join("001-test.md"), brief_content).unwrap();

    commands::worker::status::run_in(tmp.path(), "001", "in_progress", None, None, None).unwrap();

    // Save checkpoint
    let id = commands::checkpoint::save_in(tmp.path(), Some("test checkpoint")).unwrap();

    // Verify file exists
    let cp_file = active.checkpoint_file(&id);
    assert!(cp_file.exists());

    // Verify content
    let content = std::fs::read_to_string(&cp_file).unwrap();
    let cp: serde_json::Value = serde_json::from_str(&content).unwrap();
    assert_eq!(cp["description"], "test checkpoint");
    assert_eq!(cp["tasks"][0]["id"], "001");
    assert_eq!(cp["tasks"][0]["state"], "in_progress");
    assert_eq!(cp["tasks"][0]["branch_exists"], true);
}

#[test]
fn checkpoint_save_without_message() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), Some("cargo test"), false).unwrap();
    commands::run::create_in(tmp.path(), "test-run").unwrap();

    let id = commands::checkpoint::save_in(tmp.path(), None).unwrap();
    let paths = OrchestratorPaths::new(tmp.path());
    let active = paths.active_run().unwrap();
    assert!(active.checkpoint_file(&id).exists());
}
