use std::path::Path;

use anyhow::{Context, Result};

use crate::fs::bus::OrchestratorPaths;
use crate::git::wrapper::Git;
use crate::model::config::OrchestratorConfig;

/// CLI entry point — uses current directory.
pub fn run() -> Result<()> {
    let cwd = std::env::current_dir().context("cannot determine current directory")?;
    run_in(&cwd, None, true)
}

/// Testable entry point: scaffold `.orchestrator/` under `project_root`.
pub fn run_in(project_root: &Path, test_command: Option<&str>, verbose: bool) -> Result<()> {
    let paths = OrchestratorPaths::new(project_root);

    // 1. Create directory structure
    std::fs::create_dir_all(paths.runs_dir())
        .context("failed to create .orchestrator/runs/ directory")?;

    // 2. Detect base branch
    let git = Git::new(project_root);
    let base_branch = git
        .detect_default_branch()
        .unwrap_or_else(|_| "main".to_string());

    // 3. Resolve test command: explicit > auto-detect > None
    let resolved_test_command = test_command
        .map(|s| s.to_string())
        .or_else(|| detect_test_command(project_root));

    // 4. Build config and write
    let config = OrchestratorConfig {
        project_root: project_root.to_path_buf(),
        base_branch,
        test_command: resolved_test_command,
        ..OrchestratorConfig::default()
    };

    let json = serde_json::to_string_pretty(&config).context("failed to serialize config")?;
    std::fs::write(paths.config(), &json).context("failed to write config.json")?;

    // 5. Update .gitignore
    add_to_gitignore(project_root)?;

    // 6. Update CLAUDE.md with agentrc section
    update_claude_md(project_root)?;

    // 7. Print summary
    if verbose {
        println!("Initialized .orchestrator/ in {}", project_root.display());
        if let Some(ref cmd) = config.test_command {
            println!("  test command: {cmd}");
        }
        println!("  base branch:  {}", config.base_branch);
    }

    Ok(())
}

/// Detect the project's test command by checking for known project files.
pub fn detect_test_command(project_root: &Path) -> Option<String> {
    if project_root.join("Cargo.toml").is_file() {
        return Some("cargo test".to_string());
    }
    if project_root.join("package.json").is_file() {
        return Some("npm test".to_string());
    }
    if project_root.join("pyproject.toml").is_file() {
        return Some("pytest".to_string());
    }
    if project_root.join("Makefile").is_file() {
        return Some("make test".to_string());
    }
    if project_root.join("go.mod").is_file() {
        return Some("go test ./...".to_string());
    }
    None
}

/// Merge the agentrc section into CLAUDE.md (create if missing, replace if stale).
fn update_claude_md(project_root: &Path) -> Result<()> {
    let claude_md = project_root.join("CLAUDE.md");
    let begin_marker = "<!-- agentrc:begin -->";
    let end_marker = "<!-- agentrc:end -->";

    // Try to load the template from the installed skill directory
    let section =
        load_claude_md_template().unwrap_or_else(|| default_claude_md_section().to_string());

    let existing = if claude_md.is_file() {
        std::fs::read_to_string(&claude_md).context("failed to read CLAUDE.md")?
    } else {
        String::new()
    };

    // If markers exist, replace the block; otherwise append
    let updated = if existing.contains(begin_marker) {
        if let (Some(start), Some(end)) = (existing.find(begin_marker), existing.find(end_marker)) {
            let end = end + end_marker.len();
            let mut new = existing[..start].to_string();
            new.push_str(&section);
            new.push_str(&existing[end..]);
            new
        } else {
            existing
        }
    } else {
        let mut content = existing;
        if !content.is_empty() && !content.ends_with('\n') {
            content.push('\n');
        }
        if !content.is_empty() {
            content.push('\n');
        }
        content.push_str(&section);
        content.push('\n');
        content
    };

    std::fs::write(&claude_md, updated).context("failed to write CLAUDE.md")?;
    Ok(())
}

/// Try to load the template from the skill directory (follows the install symlink).
fn load_claude_md_template() -> Option<String> {
    let home = std::env::var("HOME").ok()?;
    let template =
        std::path::PathBuf::from(home).join(".claude/skills/agentrc/claude-md-section.md");
    std::fs::read_to_string(template).ok()
}

/// Fallback if skill directory isn't installed.
fn default_claude_md_section() -> &'static str {
    "<!-- agentrc:begin -->\n\
     ## agentrc Worker Directives\n\
     \n\
     When performing deep technical work, dispatch to specialized agents \
     (e.g. voltagent-lang:rust-engineer, voltagent-qa-sec:test-automator). \
     Use `model: \"opus\"` for all subagent dispatches.\n\
     <!-- agentrc:end -->"
}

/// Add `.orchestrator/` to `.gitignore` if not already present.
fn add_to_gitignore(project_root: &Path) -> Result<()> {
    let gitignore_path = project_root.join(".gitignore");
    let entry = ".orchestrator/";

    let existing = if gitignore_path.is_file() {
        std::fs::read_to_string(&gitignore_path).context("failed to read .gitignore")?
    } else {
        String::new()
    };

    // Check if already present
    if existing.lines().any(|line| line.trim() == entry) {
        return Ok(());
    }

    // Append (with leading newline if file doesn't end with one)
    let mut content = existing;
    if !content.is_empty() && !content.ends_with('\n') {
        content.push('\n');
    }
    content.push_str(entry);
    content.push('\n');

    std::fs::write(&gitignore_path, content).context("failed to write .gitignore")?;

    Ok(())
}
