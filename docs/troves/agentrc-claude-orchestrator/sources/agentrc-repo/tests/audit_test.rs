mod common;

use std::os::unix::fs::symlink;
use std::path::{Path, PathBuf};
use std::process::Command;

use tempfile::TempDir;

use agentrc::audit::{audit_tdd, classify_commit, CommitKind};

// ── Helpers ────────────────────────────────────────────────────────────────

/// Run a git command inside the given repo, panicking on failure.
fn git(repo: &Path, args: &[&str]) {
    let output = Command::new("git")
        .arg("-C")
        .arg(repo)
        .args(args)
        .output()
        .unwrap();
    assert!(
        output.status.success(),
        "git -C {} {} failed: {}",
        repo.display(),
        args.join(" "),
        String::from_utf8_lossy(&output.stderr)
    );
}

/// Set up a test repo with orchestrator directory structure and a task brief.
///
/// Returns the project root path (same as `tmp.path()`).
/// The task brief uses id "001", slug "test-task", base_branch "master",
/// and branch "feature".
fn setup_audit_test_repo(tmp: &TempDir) -> PathBuf {
    let root = tmp.path().to_path_buf();

    // Initialise git repo with an initial commit on master
    common::init_test_repo(&root);

    // Create orchestrator directory structure
    let run_dir = root.join(".orchestrator/runs/test-run");
    let tasks_dir = run_dir.join("tasks");
    std::fs::create_dir_all(&tasks_dir).unwrap();

    // Create the active symlink: .orchestrator/active -> runs/test-run
    let active_link = root.join(".orchestrator/active");
    symlink("runs/test-run", &active_link).unwrap();

    // Write the task brief
    let brief_content = "\
---
id: \"001\"
slug: test-task
classification: writer
base_branch: master
branch: feature
depends_on: []
created_at: 2026-04-12T10:00:00Z
---
# Test task for TDD audit
";
    std::fs::write(tasks_dir.join("001-test-task.md"), brief_content).unwrap();

    root
}

/// Create a feature branch, add commits, then return to master.
///
/// `commits` is a list of `(filename, content, commit_message)` tuples.
/// Each file will be created relative to the repo root and committed individually.
fn create_branch_with_commits(root: &Path, branch: &str, commits: &[(&str, &str, &str)]) {
    git(root, &["checkout", "-b", branch]);

    for (filename, content, message) in commits {
        let file_path = root.join(filename);
        if let Some(parent) = file_path.parent() {
            std::fs::create_dir_all(parent).unwrap();
        }
        std::fs::write(&file_path, content).unwrap();
        git(root, &["add", filename]);
        git(root, &["commit", "-m", message]);
    }

    git(root, &["checkout", "master"]);
}

// ── Test 1: audit_with_test_commits ────────────────────────────────────────
//
// A branch with both test and impl commits should be compliant.

#[test]
fn audit_with_test_commits() {
    let tmp = TempDir::new().unwrap();
    let root = setup_audit_test_repo(&tmp);

    // Create a feature branch with a mix of test and impl commits
    create_branch_with_commits(
        &root,
        "feature",
        &[
            (
                "tests/widget_test.rs",
                "#[test]\nfn it_works() {}",
                "add widget tests",
            ),
            ("src/widget.rs", "pub struct Widget;", "implement widget"),
            (
                "tests/parser_test.rs",
                "#[test]\nfn parse_ok() {}",
                "add parser tests",
            ),
            ("src/parser.rs", "pub fn parse() {}", "implement parser"),
        ],
    );

    let result = audit_tdd(&root, "001").unwrap();

    assert_eq!(result.task_id, "001");
    assert_eq!(result.total_commits, 4);
    assert_eq!(result.test_commits, 2);
    assert_eq!(result.impl_commits, 2);
    assert_eq!(result.mixed_commits, 0);
    assert!(
        result.compliant,
        "branch with test commits should be compliant"
    );
    assert!(
        result.score.contains("2/4"),
        "score should contain '2/4': got '{}'",
        result.score
    );
}

// ── Test 2: audit_no_tests ─────────────────────────────────────────────────
//
// A branch with only impl commits (no test commits) should not be compliant.

#[test]
fn audit_no_tests() {
    let tmp = TempDir::new().unwrap();
    let root = setup_audit_test_repo(&tmp);

    // Create a feature branch with only impl commits
    create_branch_with_commits(
        &root,
        "feature",
        &[
            ("src/widget.rs", "pub struct Widget;", "implement widget"),
            ("src/parser.rs", "pub fn parse() {}", "implement parser"),
            ("src/main.rs", "fn main() {}", "add main"),
        ],
    );

    let result = audit_tdd(&root, "001").unwrap();

    assert_eq!(result.task_id, "001");
    assert_eq!(result.total_commits, 3);
    assert_eq!(result.test_commits, 0);
    assert_eq!(result.impl_commits, 3);
    assert_eq!(result.mixed_commits, 0);
    assert!(
        !result.compliant,
        "branch with no test commits should NOT be compliant"
    );
    assert!(
        result.score.contains("0/3"),
        "score should contain '0/3': got '{}'",
        result.score
    );
}

// ── Test 3: audit_empty_branch ─────────────────────────────────────────────
//
// A branch with zero commits ahead of base should not be compliant.

#[test]
fn audit_empty_branch() {
    let tmp = TempDir::new().unwrap();
    let root = setup_audit_test_repo(&tmp);

    // Create a feature branch but don't add any commits
    git(&root, &["checkout", "-b", "feature"]);
    git(&root, &["checkout", "master"]);

    let result = audit_tdd(&root, "001").unwrap();

    assert_eq!(result.task_id, "001");
    assert_eq!(result.total_commits, 0);
    assert_eq!(result.test_commits, 0);
    assert_eq!(result.impl_commits, 0);
    assert_eq!(result.mixed_commits, 0);
    assert!(!result.compliant, "empty branch should NOT be compliant");
}

// ── Test 4: classify_test_file ─────────────────────────────────────────────
//
// A commit touching only files under tests/ should be classified as Test.

#[test]
fn classify_test_file() {
    let files = vec!["tests/foo.rs".to_string()];
    let kind = classify_commit(&files);
    assert!(
        matches!(kind, CommitKind::Test),
        "commit with only tests/foo.rs should be Test, got {:?}",
        kind
    );
}

#[test]
fn classify_test_file_nested() {
    let files = vec![
        "tests/integration/api_test.rs".to_string(),
        "tests/common/mod.rs".to_string(),
    ];
    let kind = classify_commit(&files);
    assert!(
        matches!(kind, CommitKind::Test),
        "commit with only tests/ files should be Test, got {:?}",
        kind
    );
}

// ── Test 5: classify_impl_file ─────────────────────────────────────────────
//
// A commit touching only files under src/ should be classified as Impl.

#[test]
fn classify_impl_file() {
    let files = vec!["src/foo.rs".to_string()];
    let kind = classify_commit(&files);
    assert!(
        matches!(kind, CommitKind::Impl),
        "commit with only src/foo.rs should be Impl, got {:?}",
        kind
    );
}

#[test]
fn classify_impl_file_nested() {
    let files = vec![
        "src/commands/run.rs".to_string(),
        "src/model/task.rs".to_string(),
    ];
    let kind = classify_commit(&files);
    assert!(
        matches!(kind, CommitKind::Impl),
        "commit with only src/ files should be Impl, got {:?}",
        kind
    );
}

// ── Additional classify edge cases ─────────────────────────────────────────

#[test]
fn classify_mixed_commit() {
    let files = vec![
        "src/widget.rs".to_string(),
        "tests/widget_test.rs".to_string(),
    ];
    let kind = classify_commit(&files);
    assert!(
        matches!(kind, CommitKind::Mixed),
        "commit with both src/ and tests/ files should be Mixed, got {:?}",
        kind
    );
}

// ── Test: audit with mixed commits ─────────────────────────────────────────
//
// Verify that commits touching both src/ and tests/ are counted as mixed.

#[test]
fn audit_with_mixed_commits() {
    let tmp = TempDir::new().unwrap();
    let root = setup_audit_test_repo(&tmp);

    // Create a feature branch with a mixed commit (src + tests in one commit)
    git(&root, &["checkout", "-b", "feature"]);

    // Commit 1: mixed (both src/ and tests/)
    std::fs::create_dir_all(root.join("src")).unwrap();
    std::fs::create_dir_all(root.join("tests")).unwrap();
    std::fs::write(root.join("src/widget.rs"), "pub struct Widget;").unwrap();
    std::fs::write(root.join("tests/widget_test.rs"), "#[test] fn ok() {}").unwrap();
    git(&root, &["add", "src/widget.rs", "tests/widget_test.rs"]);
    git(&root, &["commit", "-m", "add widget with tests"]);

    // Commit 2: pure test
    std::fs::write(root.join("tests/extra_test.rs"), "#[test] fn extra() {}").unwrap();
    git(&root, &["add", "tests/extra_test.rs"]);
    git(&root, &["commit", "-m", "add extra tests"]);

    git(&root, &["checkout", "master"]);

    let result = audit_tdd(&root, "001").unwrap();

    assert_eq!(result.total_commits, 2);
    assert_eq!(result.mixed_commits, 1);
    assert_eq!(result.test_commits, 1);
    assert_eq!(result.impl_commits, 0);
    assert!(
        result.compliant,
        "branch with test commits should be compliant even with mixed"
    );
}
