use anyhow::{bail, Context, Result};
use std::process::Command;

/// Typed wrapper around tmux CLI commands.
///
/// Static `build_*` methods return argument vectors for testability without tmux.
/// Instance methods execute commands against a running tmux server.
pub struct Tmux;

impl Default for Tmux {
    fn default() -> Self {
        Self
    }
}

impl Tmux {
    /// Create a new Tmux wrapper.
    pub fn new() -> Self {
        Self
    }

    // ── Static command builders (testable without tmux) ──────────────

    /// Build args for `tmux split-window -h -P -F '#{pane_id}' -t <target>`.
    pub fn build_split_args(target_window: &str) -> Vec<String> {
        vec![
            "split-window".to_string(),
            "-h".to_string(),
            "-P".to_string(),
            "-F".to_string(),
            "#{pane_id}".to_string(),
            "-t".to_string(),
            target_window.to_string(),
        ]
    }

    /// Build args for `tmux send-keys -t <pane_id> <keys> Enter`.
    pub fn build_send_keys_args(pane_id: &str, keys: &str) -> Vec<String> {
        vec![
            "send-keys".to_string(),
            "-t".to_string(),
            pane_id.to_string(),
            keys.to_string(),
            "Enter".to_string(),
        ]
    }

    /// Build args for `tmux kill-pane -t <pane_id>`.
    pub fn build_kill_pane_args(pane_id: &str) -> Vec<String> {
        vec![
            "kill-pane".to_string(),
            "-t".to_string(),
            pane_id.to_string(),
        ]
    }

    /// Build args for `tmux move-pane -s <pane_id> -t <target_window>`.
    pub fn build_move_pane_args(pane_id: &str, target_window: &str) -> Vec<String> {
        vec![
            "move-pane".to_string(),
            "-s".to_string(),
            pane_id.to_string(),
            "-t".to_string(),
            target_window.to_string(),
        ]
    }

    /// Build args for `tmux new-window -n <name>`.
    pub fn build_new_window_args(name: &str) -> Vec<String> {
        vec!["new-window".to_string(), "-n".to_string(), name.to_string()]
    }

    /// Build args for `tmux rename-window <name>`.
    pub fn build_rename_window_args(name: &str) -> Vec<String> {
        vec!["rename-window".to_string(), name.to_string()]
    }

    /// Build args for `tmux display-message -p '#{window_name}'`.
    pub fn build_current_window_name_args() -> Vec<String> {
        vec![
            "display-message".to_string(),
            "-p".to_string(),
            "#{window_name}".to_string(),
        ]
    }

    /// Build args for `tmux capture-pane -t <pane_id> -p -S -<lines>`.
    pub fn build_capture_pane_args(pane_id: &str, lines: u32) -> Vec<String> {
        vec![
            "capture-pane".to_string(),
            "-t".to_string(),
            pane_id.to_string(),
            "-p".to_string(),
            "-S".to_string(),
            format!("-{lines}"),
        ]
    }

    /// Build args for `tmux select-pane -t <pane_id> -T <title>`.
    pub fn build_set_pane_title_args(pane_id: &str, title: &str) -> Vec<String> {
        vec![
            "select-pane".to_string(),
            "-t".to_string(),
            pane_id.to_string(),
            "-T".to_string(),
            title.to_string(),
        ]
    }

    /// Build args for `tmux list-panes -t <window> -F '#{pane_id}\t#{pane_title}'`.
    pub fn build_list_panes_with_titles_args(target_window: &str) -> Vec<String> {
        vec![
            "list-panes".to_string(),
            "-t".to_string(),
            target_window.to_string(),
            "-F".to_string(),
            "#{pane_id}\t#{pane_title}".to_string(),
        ]
    }

    /// Build args for `tmux list-panes -t <window> -F '#{pane_id}'`.
    pub fn build_list_panes_args(target_window: &str) -> Vec<String> {
        vec![
            "list-panes".to_string(),
            "-t".to_string(),
            target_window.to_string(),
            "-F".to_string(),
            "#{pane_id}".to_string(),
        ]
    }

    // ── Static utility ───────────────────────────────────────────────

    /// Returns true if we are running inside a tmux session (TMUX env var is set).
    pub fn is_inside_tmux() -> bool {
        std::env::var("TMUX").is_ok()
    }

    // ── Instance methods (require a running tmux server) ─────────────

    /// Run `tmux <args>` and return trimmed stdout, or an error with stderr.
    fn run_tmux(&self, args: &[&str]) -> Result<String> {
        let output = Command::new("tmux")
            .args(args)
            .output()
            .context("failed to execute tmux")?;

        if !output.status.success() {
            let stderr = String::from_utf8_lossy(&output.stderr);
            bail!(
                "tmux {} failed (exit {}): {}",
                args.join(" "),
                output.status,
                stderr.trim()
            );
        }

        let stdout = String::from_utf8_lossy(&output.stdout).trim().to_string();
        Ok(stdout)
    }

    /// Split the target window horizontally and return the new pane ID.
    pub fn split_window(&self, target_window: &str) -> Result<String> {
        self.run_tmux(&[
            "split-window",
            "-h",
            "-P",
            "-F",
            "#{pane_id}",
            "-t",
            target_window,
        ])
    }

    /// Split the current pane horizontally (right) with a given percentage, return new pane ID.
    pub fn split_right(&self, percentage: u32) -> Result<String> {
        self.run_tmux(&[
            "split-window",
            "-h",
            "-P",
            "-F",
            "#{pane_id}",
            "-l",
            &format!("{percentage}%"),
        ])
    }

    /// Split a target pane vertically (below) with a given percentage, return new pane ID.
    pub fn split_below(&self, target_pane: &str, percentage: u32) -> Result<String> {
        self.run_tmux(&[
            "split-window",
            "-v",
            "-P",
            "-F",
            "#{pane_id}",
            "-t",
            target_pane,
            "-l",
            &format!("{percentage}%"),
        ])
    }

    /// Send keystrokes to the given pane, followed by Enter.
    pub fn send_keys(&self, pane_id: &str, keys: &str) -> Result<()> {
        self.run_tmux(&["send-keys", "-t", pane_id, keys, "Enter"])?;
        Ok(())
    }

    /// Kill the given pane.
    pub fn kill_pane(&self, pane_id: &str) -> Result<()> {
        self.run_tmux(&["kill-pane", "-t", pane_id])?;
        Ok(())
    }

    /// Move a pane to a target window.
    pub fn move_pane(&self, pane_id: &str, target_window: &str) -> Result<()> {
        self.run_tmux(&["move-pane", "-s", pane_id, "-t", target_window])?;
        Ok(())
    }

    /// Apply the tiled layout to the target window.
    pub fn select_layout_tiled(&self, target_window: &str) -> Result<()> {
        self.run_tmux(&["select-layout", "-t", target_window, "tiled"])?;
        Ok(())
    }

    /// Create a new window with the given name.
    pub fn new_window(&self, name: &str) -> Result<()> {
        self.run_tmux(&["new-window", "-n", name])?;
        Ok(())
    }

    /// Create a new window and return the pane ID of its initial pane.
    pub fn new_window_with_pane_id(&self, name: &str) -> Result<String> {
        self.run_tmux(&["new-window", "-P", "-F", "#{pane_id}", "-n", name])
    }

    /// Rename the current tmux window.
    pub fn rename_window(&self, name: &str) -> Result<()> {
        self.run_tmux(&["rename-window", name])?;
        Ok(())
    }

    /// Get the name of the current tmux window.
    pub fn current_window_name(&self) -> Result<String> {
        self.run_tmux(&["display-message", "-p", "#{window_name}"])
    }

    /// Set the title of a tmux pane.
    pub fn set_pane_title(&self, pane_id: &str, title: &str) -> Result<()> {
        self.run_tmux(&["select-pane", "-t", pane_id, "-T", title])?;
        Ok(())
    }

    /// List panes with their IDs and titles for a given window.
    pub fn list_panes_with_titles(&self, target_window: &str) -> Result<Vec<(String, String)>> {
        let output = self.run_tmux(&[
            "list-panes",
            "-t",
            target_window,
            "-F",
            "#{pane_id}\t#{pane_title}",
        ])?;
        let panes = output
            .lines()
            .filter(|l| !l.is_empty())
            .map(|line| {
                let mut parts = line.splitn(2, '\t');
                let id = parts.next().unwrap_or("").to_string();
                let title = parts.next().unwrap_or("").to_string();
                (id, title)
            })
            .collect();
        Ok(panes)
    }

    /// List pane IDs for the given target window.
    pub fn list_panes(&self, target_window: &str) -> Result<Vec<String>> {
        let output = self.run_tmux(&["list-panes", "-t", target_window, "-F", "#{pane_id}"])?;
        let panes = output
            .lines()
            .filter(|l| !l.is_empty())
            .map(|s| s.to_string())
            .collect();
        Ok(panes)
    }

    /// List window names for the current session.
    pub fn list_windows(&self) -> Result<Vec<String>> {
        let output = self.run_tmux(&["list-windows", "-F", "#{window_name}"])?;
        let windows = output
            .lines()
            .filter(|l| !l.is_empty())
            .map(|s| s.to_string())
            .collect();
        Ok(windows)
    }

    /// Capture last N lines of pane scrollback as a string.
    pub fn capture_pane(&self, pane_id: &str, lines: u32) -> Result<String> {
        self.run_tmux(&[
            "capture-pane",
            "-t",
            pane_id,
            "-p",
            "-S",
            &format!("-{lines}"),
        ])
    }

    /// Send a signal on a tmux wait-for channel (non-blocking, used by workers).
    pub fn signal_channel(&self, channel: &str) -> Result<()> {
        self.run_tmux(&["wait-for", "-S", channel])?;
        Ok(())
    }

    /// Block until a tmux wait-for channel is signaled (used by orchestrator).
    pub fn wait_for_channel(&self, channel: &str) -> Result<()> {
        self.run_tmux(&["wait-for", channel])?;
        Ok(())
    }
}
