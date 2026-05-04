use agentrc::commands::install;
use tempfile::TempDir;

#[test]
fn install_creates_symlink() {
    let tmp_home = TempDir::new().unwrap();
    let tmp_repo = TempDir::new().unwrap();
    let skill_src = tmp_repo.path().join("skill/agentrc");
    std::fs::create_dir_all(&skill_src).unwrap();
    std::fs::write(
        skill_src.join("SKILL.md"),
        "---\nname: agentrc\n---\n# Test",
    )
    .unwrap();
    let skills_dir = tmp_home.path().join(".claude/skills");
    install::install_skill(&skill_src, &skills_dir).unwrap();
    let link = skills_dir.join("agentrc");
    assert!(link.exists());
    assert!(link.join("SKILL.md").exists());
    let metadata = std::fs::symlink_metadata(&link).unwrap();
    assert!(metadata.file_type().is_symlink());
}

#[test]
fn install_is_idempotent() {
    let tmp_home = TempDir::new().unwrap();
    let tmp_repo = TempDir::new().unwrap();
    let skill_src = tmp_repo.path().join("skill/agentrc");
    std::fs::create_dir_all(&skill_src).unwrap();
    std::fs::write(skill_src.join("SKILL.md"), "test").unwrap();
    let skills_dir = tmp_home.path().join(".claude/skills");
    install::install_skill(&skill_src, &skills_dir).unwrap();
    install::install_skill(&skill_src, &skills_dir).unwrap();
    let link = skills_dir.join("agentrc");
    assert!(link.exists());
}

#[test]
fn install_repairs_broken_symlink() {
    let tmp_home = TempDir::new().unwrap();
    let tmp_repo = TempDir::new().unwrap();
    let skill_src = tmp_repo.path().join("skill/agentrc");
    std::fs::create_dir_all(&skill_src).unwrap();
    std::fs::write(skill_src.join("SKILL.md"), "test").unwrap();
    let skills_dir = tmp_home.path().join(".claude/skills");
    std::fs::create_dir_all(&skills_dir).unwrap();
    std::os::unix::fs::symlink("/nonexistent/path", skills_dir.join("agentrc")).unwrap();
    install::install_skill(&skill_src, &skills_dir).unwrap();
    let link = skills_dir.join("agentrc");
    assert!(link.exists());
    assert!(link.join("SKILL.md").exists());
}

#[test]
fn check_prerequisite_exists() {
    assert!(install::check_command_exists("echo"));
}

#[test]
fn check_prerequisite_missing() {
    assert!(!install::check_command_exists("nonexistent_binary_xyz_123"));
}
