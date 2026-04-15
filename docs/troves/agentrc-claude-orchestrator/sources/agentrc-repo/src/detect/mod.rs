use std::fmt;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum DetectedState {
    Thinking,
    ToolUse,
    Running,
    Idle,
    NeedsInput,
    RateLimited,
    Errored,
    Dead,
    Unknown,
}

impl fmt::Display for DetectedState {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            DetectedState::Thinking => write!(f, "thinking"),
            DetectedState::ToolUse => write!(f, "tool_use"),
            DetectedState::Running => write!(f, "running"),
            DetectedState::Idle => write!(f, "idle"),
            DetectedState::NeedsInput => write!(f, "needs_input"),
            DetectedState::RateLimited => write!(f, "rate_limited"),
            DetectedState::Errored => write!(f, "errored"),
            DetectedState::Dead => write!(f, "dead"),
            DetectedState::Unknown => write!(f, "unknown"),
        }
    }
}

impl DetectedState {
    pub fn icon(&self) -> &'static str {
        match self {
            DetectedState::Thinking => "*",
            DetectedState::ToolUse => "@",
            DetectedState::Running => "$",
            DetectedState::Idle => "-",
            DetectedState::NeedsInput => "!",
            DetectedState::RateLimited => "~",
            DetectedState::Errored => "x",
            DetectedState::Dead => "x",
            DetectedState::Unknown => "?",
        }
    }
}

/// Detect worker state from captured pane text.
///
/// Rules applied in priority order — first match wins.
pub fn detect_from_text(text: &str) -> DetectedState {
    let lower = text.to_lowercase();

    // Priority 1: NeedsInput (permission prompts)
    if lower.contains("do you want to proceed")
        || lower.contains("yes, allow")
        || lower.contains("❯ 1. yes")
        || (lower.contains("allow") && lower.contains("permission"))
    {
        return DetectedState::NeedsInput;
    }

    // Priority 2: RateLimited
    if lower.contains("rate limit") || lower.contains("429") || lower.contains("overloaded") {
        return DetectedState::RateLimited;
    }

    // Priority 3: Errored
    if lower.contains("panicked at")
        || lower.contains("sigterm")
        || lower.contains("sigsegv")
        || lower.contains("fatal error")
    {
        return DetectedState::Errored;
    }

    // Priority 4: Thinking
    if lower.contains("precipitating") || lower.contains("thinking") {
        return DetectedState::Thinking;
    }

    // Priority 5: ToolUse
    if lower.contains("reading")
        || lower.contains("writing to")
        || lower.contains("editing")
        || lower.contains("edit(")
    {
        return DetectedState::ToolUse;
    }

    // Priority 6: Running
    if lower.contains("bash(")
        || lower.contains("running")
        || (lower.contains("cargo") && lower.contains("test"))
        || lower.contains("npm ")
    {
        return DetectedState::Running;
    }

    // Priority 7: Idle (Claude prompt at end)
    let trimmed = text.trim_end();
    if trimmed.ends_with('❯') || trimmed.ends_with("> ") {
        return DetectedState::Idle;
    }

    DetectedState::Unknown
}

/// Parse token count from Claude Code's pane output.
///
/// Looks for patterns like `↓ 1.7k tokens`, `↓ 12.4k tokens`, `↓ 500 tokens`.
pub fn parse_tokens_from_text(text: &str) -> Option<u64> {
    for line in text.lines().rev() {
        // Match "N.Nk tokens" or "N tokens"
        if let Some(pos) = line.find("tokens") {
            let before = line[..pos].trim_end();
            // Walk backward to find the number
            let num_str: String = before
                .chars()
                .rev()
                .take_while(|c| {
                    c.is_ascii_digit()
                        || *c == '.'
                        || *c == 'k'
                        || *c == 'K'
                        || *c == 'm'
                        || *c == 'M'
                })
                .collect::<String>()
                .chars()
                .rev()
                .collect();

            if num_str.is_empty() {
                continue;
            }

            let lower = num_str.to_lowercase();
            if lower.ends_with('k') {
                if let Ok(n) = lower.trim_end_matches('k').parse::<f64>() {
                    return Some((n * 1_000.0) as u64);
                }
            } else if lower.ends_with('m') {
                if let Ok(n) = lower.trim_end_matches('m').parse::<f64>() {
                    return Some((n * 1_000_000.0) as u64);
                }
            } else if let Ok(n) = lower.parse::<u64>() {
                return Some(n);
            }
        }
    }
    None
}

/// Result of scanning a pane — state + optional token count.
pub struct PaneScan {
    pub state: DetectedState,
    pub tokens: Option<u64>,
}

/// Scan a live tmux pane and return detected state.
///
/// Returns `DetectedState::Dead` if the pane doesn't exist or capture fails.
pub fn scan_pane(tmux: &crate::tmux::wrapper::Tmux, pane_id: &str) -> DetectedState {
    match tmux.capture_pane(pane_id, 30) {
        Ok(text) => detect_from_text(&text),
        Err(_) => DetectedState::Dead,
    }
}

/// Scan a live tmux pane and return both state and token count.
pub fn scan_pane_full(tmux: &crate::tmux::wrapper::Tmux, pane_id: &str) -> PaneScan {
    match tmux.capture_pane(pane_id, 30) {
        Ok(text) => PaneScan {
            state: detect_from_text(&text),
            tokens: parse_tokens_from_text(&text),
        },
        Err(_) => PaneScan {
            state: DetectedState::Dead,
            tokens: None,
        },
    }
}
