use std::path::Path;
use std::process::Command;

/// Run a git command and assert it succeeds, panicking with stderr on failure.
fn run_git_checked(args: &[&str]) {
    let output = Command::new("git").args(args).output().unwrap();
    assert!(
        output.status.success(),
        "git {} failed: {}",
        args.join(" "),
        String::from_utf8_lossy(&output.stderr)
    );
}

/// Create a temporary git repo with an initial commit
pub fn init_test_repo(path: &Path) {
    let p = path.to_str().unwrap();
    run_git_checked(&["init", p]);
    run_git_checked(&["-C", p, "config", "user.email", "test@test.com"]);
    run_git_checked(&["-C", p, "config", "user.name", "Test"]);
    std::fs::write(path.join("README.md"), "# Test").unwrap();
    run_git_checked(&["-C", p, "add", "."]);
    run_git_checked(&["-C", p, "commit", "-m", "initial"]);
}
