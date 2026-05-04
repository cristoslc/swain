use std::path::{Path, PathBuf};

use anyhow::{anyhow, Context, Result};

/// CLI entry point: find repo root, locate skill source, install into ~/.claude/skills/.
pub fn run() -> Result<()> {
    // Try current_exe first (works when running from repo via cargo run),
    // then fall back to current_dir (works after cargo install, when run from repo)
    let repo_root = std::env::current_exe()
        .ok()
        .and_then(|p| find_repo_root(&p).ok())
        .or_else(|| {
            std::env::current_dir()
                .ok()
                .and_then(|p| find_repo_root(&p).ok())
        })
        .ok_or_else(|| {
            anyhow!("could not find agent.rc repo root — run `agentrc install` from within the cloned agent.rc directory")
        })?;

    let skill_src = repo_root.join("skill").join("agentrc");
    anyhow::ensure!(
        skill_src.is_dir(),
        "skill source not found at {}",
        skill_src.display()
    );

    let home = std::env::var("HOME").context("HOME environment variable not set")?;
    let skills_dir = PathBuf::from(home).join(".claude").join("skills");

    install_skill(&skill_src, &skills_dir)?;
    install_binary_symlink()?;

    // Check prerequisites
    let mut all_ok = true;
    for cmd in &["claude", "tmux", "git"] {
        if check_command_exists(cmd) {
            println!("  [ok] {}", cmd);
        } else {
            println!("  [!!] {} not found", cmd);
            all_ok = false;
        }
    }
    if all_ok {
        println!("agentrc installed successfully.");
    } else {
        println!("agentrc installed, but some prerequisites are missing.");
    }

    Ok(())
}

/// Create `skills_dir` if needed, then symlink `skill_src` into `skills_dir/agentrc`.
pub fn install_skill(skill_src: &Path, skills_dir: &Path) -> Result<()> {
    std::fs::create_dir_all(skills_dir)
        .with_context(|| format!("failed to create {}", skills_dir.display()))?;

    let link_path = skills_dir.join("agentrc");
    let canonical_src = skill_src
        .canonicalize()
        .with_context(|| format!("failed to canonicalize {}", skill_src.display()))?;

    // Remove existing entry (symlink, broken symlink, or directory)
    if let Ok(meta) = link_path.symlink_metadata() {
        if meta.file_type().is_symlink() {
            std::fs::remove_file(&link_path).with_context(|| {
                format!("failed to remove existing symlink {}", link_path.display())
            })?;
        } else if meta.file_type().is_dir() {
            std::fs::remove_dir_all(&link_path).with_context(|| {
                format!("failed to remove existing dir {}", link_path.display())
            })?;
        } else {
            std::fs::remove_file(&link_path).with_context(|| {
                format!("failed to remove existing file {}", link_path.display())
            })?;
        }
    }

    std::os::unix::fs::symlink(&canonical_src, &link_path).with_context(|| {
        format!(
            "failed to symlink {} -> {}",
            link_path.display(),
            canonical_src.display()
        )
    })?;

    println!(
        "Installed skill: {} -> {}",
        link_path.display(),
        canonical_src.display()
    );

    Ok(())
}

/// Symlink the agentrc binary into ~/.local/bin/ so it's on PATH for all shells
/// (including Claude Code's Bash tool which doesn't source .zshrc/.bashrc).
fn install_binary_symlink() -> Result<()> {
    let cargo_bin =
        PathBuf::from(std::env::var("HOME").context("HOME not set")?).join(".cargo/bin/agentrc");

    if !cargo_bin.exists() {
        // Not installed via cargo install — likely running via cargo run, skip
        return Ok(());
    }

    let local_bin =
        PathBuf::from(std::env::var("HOME").context("HOME not set")?).join(".local/bin");
    std::fs::create_dir_all(&local_bin)
        .with_context(|| format!("failed to create {}", local_bin.display()))?;

    let link_path = local_bin.join("agentrc");

    // Remove existing entry
    if link_path.symlink_metadata().is_ok() {
        std::fs::remove_file(&link_path).ok();
    }

    std::os::unix::fs::symlink(&cargo_bin, &link_path).with_context(|| {
        format!(
            "failed to symlink {} -> {}",
            link_path.display(),
            cargo_bin.display()
        )
    })?;

    println!(
        "Binary linked: {} -> {}",
        link_path.display(),
        cargo_bin.display()
    );

    Ok(())
}

/// Returns true if `name` is found on PATH (via `which`).
pub fn check_command_exists(name: &str) -> bool {
    std::process::Command::new("which")
        .arg(name)
        .stdout(std::process::Stdio::null())
        .stderr(std::process::Stdio::null())
        .status()
        .map(|s| s.success())
        .unwrap_or(false)
}

/// Walk up from `from` looking for a directory that contains both `Cargo.toml` and `skill/`.
/// Returns an error if the repo root cannot be found.
fn find_repo_root(from: &Path) -> Result<PathBuf> {
    let mut current = from.to_path_buf();
    loop {
        if current.join("Cargo.toml").is_file() && current.join("skill").is_dir() {
            return Ok(current);
        }
        if !current.pop() {
            break;
        }
    }
    Err(anyhow!(
        "could not find agent.rc repo root — run from within the repo or after cargo install"
    ))
}
