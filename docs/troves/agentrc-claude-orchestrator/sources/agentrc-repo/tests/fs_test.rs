use agentrc::fs::bus::OrchestratorPaths;
use agentrc::fs::frontmatter;
use agentrc::fs::run::RunPaths;
use agentrc::model::task::TaskBriefFrontmatter;
use std::path::Path;
use tempfile::TempDir;

#[test]
fn orchestrator_paths_from_project_root() {
    let paths = OrchestratorPaths::new(Path::new("/home/eric/Code/foo"));
    assert_eq!(
        paths.root().to_str().unwrap(),
        "/home/eric/Code/foo/.orchestrator"
    );
    assert_eq!(
        paths.config().to_str().unwrap(),
        "/home/eric/Code/foo/.orchestrator/config.json"
    );
    assert_eq!(
        paths.active().to_str().unwrap(),
        "/home/eric/Code/foo/.orchestrator/active"
    );
}

#[test]
fn orchestrator_paths_run_scoped() {
    let paths = OrchestratorPaths::new(Path::new("/tmp/project"));
    let run = paths.run("2026-04-11T14-30-auth-refactor");
    assert!(run
        .root()
        .to_str()
        .unwrap()
        .contains("runs/2026-04-11T14-30-auth-refactor"));
    assert!(run.tasks_dir().to_str().unwrap().ends_with("tasks"));
    assert!(run.status_dir().to_str().unwrap().ends_with("status"));
    assert!(run
        .heartbeats_dir()
        .to_str()
        .unwrap()
        .ends_with("heartbeats"));
    assert!(run.notes_dir().to_str().unwrap().ends_with("notes"));
    assert!(run.results_dir().to_str().unwrap().ends_with("results"));
    assert!(run.worktrees_dir().to_str().unwrap().ends_with("worktrees"));
}

#[test]
fn orchestrator_paths_task_files() {
    let paths = OrchestratorPaths::new(Path::new("/tmp/project"));
    let run = paths.run("myrun");
    assert!(run
        .task_brief("001", "add-login")
        .to_str()
        .unwrap()
        .ends_with("001-add-login.md"));
    assert!(run
        .status_file("001")
        .to_str()
        .unwrap()
        .ends_with("001.json"));
    assert!(run
        .heartbeat_file("001")
        .to_str()
        .unwrap()
        .ends_with("001.alive"));
    assert!(run.notes_file("001").to_str().unwrap().ends_with("001.md"));
    assert!(run.result_file("001").to_str().unwrap().ends_with("001.md"));
    assert!(run.worktree_dir("001").to_str().unwrap().ends_with("001"));
}

// ── Checkpoints dir tests ──────────────────────────────────────────────────

mod common;

use agentrc::commands;

#[test]
fn run_paths_has_checkpoints_dir() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), None, false).unwrap();
    commands::run::create_in(tmp.path(), "test-run").unwrap();
    let paths = OrchestratorPaths::new(tmp.path());
    let active = paths.active_run().unwrap();
    let cp_dir = active.checkpoints_dir();
    assert!(cp_dir.ends_with("checkpoints"));
}

// ── Part B: Scaffold and symlink tests ──────────────────────────────────────

#[test]
fn run_scaffold_creates_all_dirs() {
    let tmp = TempDir::new().unwrap();
    let run = RunPaths::new(tmp.path().join("runs/test-run"));
    run.scaffold().unwrap();
    assert!(run.tasks_dir().is_dir());
    assert!(run.status_dir().is_dir());
    assert!(run.heartbeats_dir().is_dir());
    assert!(run.notes_dir().is_dir());
    assert!(run.results_dir().is_dir());
    assert!(run.worktrees_dir().is_dir());
}

#[test]
fn active_run_follows_symlink() {
    let tmp = TempDir::new().unwrap();
    let paths = OrchestratorPaths::new(tmp.path());
    let run_paths = paths.run("test-run");
    run_paths.scaffold().unwrap();
    std::fs::create_dir_all(paths.root()).unwrap();
    std::os::unix::fs::symlink("runs/test-run", paths.active()).unwrap();
    let active = paths.active_run().unwrap();
    assert!(active.tasks_dir().is_dir());
}

#[test]
fn active_run_returns_none_when_no_symlink() {
    let tmp = TempDir::new().unwrap();
    let paths = OrchestratorPaths::new(tmp.path());
    assert!(paths.active_run().is_none());
}

// ── Part C: Frontmatter parser tests ────────────────────────────────────────

#[test]
fn parse_frontmatter_from_task_brief() {
    let content = r#"---
id: "001"
slug: add-login-endpoint
classification: writer
worktree: .orchestrator/active/worktrees/001
base_branch: main
branch: orc/001-add-login-endpoint
pane_id: null
depends_on: []
created_at: 2026-04-11T14:30:00Z
---

# Task 001: Add login endpoint

## Scope
Add POST /auth/login to the existing Express API
"#;
    let (fm, body) = frontmatter::parse::<TaskBriefFrontmatter>(content).unwrap();
    assert_eq!(fm.id, "001");
    assert_eq!(fm.slug, "add-login-endpoint");
    assert!(body.contains("# Task 001"));
    assert!(body.contains("Add POST /auth/login"));
}

#[test]
fn parse_frontmatter_missing_delimiters() {
    let content = "# No frontmatter here\nJust markdown.";
    let result = frontmatter::parse::<TaskBriefFrontmatter>(content);
    assert!(result.is_err());
}

#[test]
fn update_frontmatter_field() {
    let content = r#"---
id: "001"
slug: add-login-endpoint
classification: writer
base_branch: main
pane_id: null
depends_on: []
created_at: 2026-04-11T14:30:00Z
---

# Task body
"#;
    let updated = frontmatter::update_field(content, "pane_id", "%14").unwrap();
    assert!(updated.contains("pane_id: \"%14\""));
    assert!(updated.contains("# Task body"));
}

#[test]
fn update_then_parse_roundtrip() {
    let content = r#"---
id: "001"
slug: test-task
classification: writer
base_branch: main
pane_id: null
depends_on: []
created_at: 2026-04-11T14:30:00Z
---

# Task body
"#;
    let updated = frontmatter::update_field(content, "pane_id", "%14").unwrap();
    let (fm, body): (TaskBriefFrontmatter, String) = frontmatter::parse(&updated).unwrap();
    assert_eq!(fm.pane_id.as_deref(), Some("%14"));
    assert!(body.contains("# Task body"));
}
