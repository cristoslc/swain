use anyhow::Result;

use crate::audit;

pub fn run(task_id: &str) -> Result<()> {
    let cwd = std::env::current_dir()?;
    let result = audit::audit_tdd(&cwd, task_id)?;

    println!("TDD Audit — task {}", result.task_id);
    println!("  Total commits:  {}", result.total_commits);
    println!("  Test commits:   {}", result.test_commits);
    println!("  Impl commits:   {}", result.impl_commits);
    println!("  Mixed commits:  {}", result.mixed_commits);
    println!("  Score:          {}", result.score);
    println!(
        "  Compliant:      {}",
        if result.compliant { "YES" } else { "NO" }
    );

    Ok(())
}
