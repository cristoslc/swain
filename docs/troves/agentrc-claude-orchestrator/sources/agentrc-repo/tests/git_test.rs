mod common;

use agentrc::git::wrapper::Git;
use tempfile::TempDir;

#[test]
fn git_is_clean_on_fresh_repo() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    let git = Git::new(tmp.path());
    assert!(git.is_clean().unwrap());
}

#[test]
fn git_is_not_clean_with_uncommitted_changes() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    std::fs::write(tmp.path().join("dirty.txt"), "dirty").unwrap();
    let git = Git::new(tmp.path());
    assert!(!git.is_clean().unwrap());
}

#[test]
fn git_current_branch() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    let git = Git::new(tmp.path());
    let branch = git.current_branch().unwrap();
    assert!(!branch.is_empty());
}

#[test]
fn git_create_and_remove_worktree() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    let git = Git::new(tmp.path());
    let wt_path = tmp.path().join("worktrees/001");
    git.create_worktree(&wt_path, "orc/001-test", "HEAD")
        .unwrap();
    assert!(wt_path.exists());
    assert!(wt_path.join("README.md").exists());
    git.remove_worktree(&wt_path).unwrap();
    assert!(!wt_path.exists());
}

#[test]
fn git_merge_no_ff() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    let git = Git::new(tmp.path());

    // Create a branch with a commit
    let wt_path = tmp.path().join("worktrees/feat");
    git.create_worktree(&wt_path, "feat-branch", "HEAD")
        .unwrap();
    std::fs::write(wt_path.join("feat.txt"), "feature").unwrap();
    let feat_git = Git::new(&wt_path);
    feat_git.add_all().unwrap();
    feat_git.commit("add feature").unwrap();

    // Merge back
    let base_branch = git.current_branch().unwrap();
    git.checkout(&base_branch).unwrap();
    let result = git.merge_no_ff("feat-branch");
    assert!(result.is_ok());
    assert!(tmp.path().join("feat.txt").exists());

    git.remove_worktree(&wt_path).unwrap();
}

#[test]
fn git_log_oneline() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    let git = Git::new(tmp.path());
    let log = git.log_oneline("HEAD", 5).unwrap();
    assert!(!log.is_empty());
    assert!(log[0].contains("initial"));
}

#[test]
fn git_branch_exists() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    let git = Git::new(tmp.path());
    let branch = git.current_branch().unwrap();
    assert!(git.branch_exists(&branch).unwrap());
    assert!(!git.branch_exists("nonexistent-branch").unwrap());
}

#[test]
fn git_detect_default_branch() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    let git = Git::new(tmp.path());
    let default = git.detect_default_branch().unwrap();
    assert!(!default.is_empty());
}
