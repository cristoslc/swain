use agentrc::detect::{detect_from_text, parse_tokens_from_text, DetectedState};

#[test]
fn detect_needs_input_permission_prompt() {
    let text = "some output\n Do you want to proceed?\n ❯ 1. Yes\n   2. No";
    assert_eq!(detect_from_text(text), DetectedState::NeedsInput);
}

#[test]
fn detect_thinking() {
    let text = "Reading file...\n\n✶ Precipitating… (thinking with high effort)";
    assert_eq!(detect_from_text(text), DetectedState::Thinking);
}

#[test]
fn detect_tool_use_reading() {
    let text = "  Reading 3 files… (ctrl+o to expand)\n";
    assert_eq!(detect_from_text(text), DetectedState::ToolUse);
}

#[test]
fn detect_tool_use_writing() {
    let text = "  Writing to src/main.rs\n";
    assert_eq!(detect_from_text(text), DetectedState::ToolUse);
}

#[test]
fn detect_running_bash() {
    let text = "  Bash(cargo test)\n  running…\n";
    assert_eq!(detect_from_text(text), DetectedState::Running);
}

#[test]
fn detect_rate_limited() {
    let text = "Error: 429 Too Many Requests\nrate limit exceeded";
    assert_eq!(detect_from_text(text), DetectedState::RateLimited);
}

#[test]
fn detect_errored() {
    let text = "thread 'main' panicked at 'index out of bounds'";
    assert_eq!(detect_from_text(text), DetectedState::Errored);
}

#[test]
fn detect_idle_prompt() {
    let text = "Task completed.\n\n❯ \n";
    assert_eq!(detect_from_text(text), DetectedState::Idle);
}

#[test]
fn detect_unknown_empty() {
    let text = "";
    assert_eq!(detect_from_text(text), DetectedState::Unknown);
}

#[test]
fn detect_priority_needs_input_over_thinking() {
    // NeedsInput is higher priority than Thinking
    let text = "thinking…\n Do you want to proceed?\n ❯ 1. Yes";
    assert_eq!(detect_from_text(text), DetectedState::NeedsInput);
}

#[test]
fn parse_tokens_k_format() {
    let text = "✽ Reticulating… (1m 10s · ↓ 1.7k tokens)";
    assert_eq!(parse_tokens_from_text(text), Some(1700));
}

#[test]
fn parse_tokens_large_k() {
    let text = "✽ Working… (5m · ↓ 24.5k tokens)";
    assert_eq!(parse_tokens_from_text(text), Some(24500));
}

#[test]
fn parse_tokens_plain_number() {
    let text = "✽ Thinking… (10s · ↓ 500 tokens)";
    assert_eq!(parse_tokens_from_text(text), Some(500));
}

#[test]
fn parse_tokens_m_format() {
    let text = "✽ Processing… (30m · ↓ 1.2M tokens)";
    assert_eq!(parse_tokens_from_text(text), Some(1200000));
}

#[test]
fn parse_tokens_none_when_absent() {
    let text = "Just some regular output\nno token info here";
    assert_eq!(parse_tokens_from_text(text), None);
}
