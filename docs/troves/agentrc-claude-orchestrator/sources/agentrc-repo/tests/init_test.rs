mod common;

use agentrc::commands::init;
use agentrc::fs::bus::OrchestratorPaths;
use tempfile::TempDir;

#[test]
fn init_creates_orchestrator_dir() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    init::run_in(tmp.path(), Some("cargo test"), false).unwrap();
    let paths = OrchestratorPaths::new(tmp.path());
    assert!(paths.root().is_dir());
    assert!(paths.config().is_file());
    assert!(paths.runs_dir().is_dir());
}

#[test]
fn init_writes_config_with_test_command() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    init::run_in(tmp.path(), Some("npm test"), false).unwrap();
    let paths = OrchestratorPaths::new(tmp.path());
    let content = std::fs::read_to_string(paths.config()).unwrap();
    let config: serde_json::Value = serde_json::from_str(&content).unwrap();
    assert_eq!(config["test_command"], "npm test");
    assert_eq!(config["max_workers"], 12);
    assert!(config["base_branch"].is_string());
}

#[test]
fn init_adds_orchestrator_to_gitignore() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    init::run_in(tmp.path(), None, false).unwrap();
    let gitignore = std::fs::read_to_string(tmp.path().join(".gitignore")).unwrap();
    assert!(gitignore.contains(".orchestrator/"));
}

#[test]
fn init_appends_to_existing_gitignore() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    std::fs::write(tmp.path().join(".gitignore"), "node_modules/\n").unwrap();
    init::run_in(tmp.path(), None, false).unwrap();
    let gitignore = std::fs::read_to_string(tmp.path().join(".gitignore")).unwrap();
    assert!(gitignore.contains("node_modules/"));
    assert!(gitignore.contains(".orchestrator/"));
}

#[test]
fn init_is_idempotent() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    init::run_in(tmp.path(), Some("cargo test"), false).unwrap();
    init::run_in(tmp.path(), Some("cargo test"), false).unwrap();
    let paths = OrchestratorPaths::new(tmp.path());
    assert!(paths.root().is_dir());
    let gitignore = std::fs::read_to_string(tmp.path().join(".gitignore")).unwrap();
    let count = gitignore.matches(".orchestrator/").count();
    assert_eq!(count, 1);
}

#[test]
fn init_auto_detects_cargo_test_command() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    std::fs::write(
        tmp.path().join("Cargo.toml"),
        "[package]\nname = \"test\"\n",
    )
    .unwrap();
    let detected = init::detect_test_command(tmp.path());
    assert_eq!(detected, Some("cargo test".to_string()));
}

#[test]
fn init_auto_detects_npm_test_command() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    std::fs::write(
        tmp.path().join("package.json"),
        r#"{"scripts":{"test":"jest"}}"#,
    )
    .unwrap();
    let detected = init::detect_test_command(tmp.path());
    assert_eq!(detected, Some("npm test".to_string()));
}

#[test]
fn init_auto_detects_pytest() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    std::fs::write(tmp.path().join("pyproject.toml"), "[tool.pytest]\n").unwrap();
    let detected = init::detect_test_command(tmp.path());
    assert_eq!(detected, Some("pytest".to_string()));
}

#[test]
fn init_returns_none_for_unknown_project() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    let detected = init::detect_test_command(tmp.path());
    assert!(detected.is_none());
}

#[test]
fn init_auto_detects_through_run_in() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    std::fs::write(
        tmp.path().join("Cargo.toml"),
        "[package]\nname = \"test\"\n",
    )
    .unwrap();
    init::run_in(tmp.path(), None, false).unwrap();
    let paths = OrchestratorPaths::new(tmp.path());
    let content = std::fs::read_to_string(paths.config()).unwrap();
    let config: serde_json::Value = serde_json::from_str(&content).unwrap();
    assert_eq!(config["test_command"], "cargo test");
}
