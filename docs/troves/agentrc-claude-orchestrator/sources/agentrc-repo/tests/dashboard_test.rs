mod common;

use agentrc::commands;
use agentrc::tui::app::App;
use agentrc::tui::widgets::table::format_tokens;
use tempfile::TempDir;

#[test]
fn dashboard_app_loads_with_active_run() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), Some("cargo test"), false).unwrap();
    commands::run::create_in(tmp.path(), "test-run").unwrap();
    commands::worker::status::run_in(tmp.path(), "001", "in_progress", None, None, None).unwrap();
    commands::worker::status::run_in(tmp.path(), "002", "completed", None, None, None).unwrap();

    let app = App::new(tmp.path().to_path_buf()).unwrap();
    assert_eq!(app.statuses.len(), 2);
    assert_eq!(app.active_count(), 1);
    assert_eq!(app.completed_count(), 1);
    assert_eq!(app.failed_count(), 0);
}

#[test]
fn dashboard_app_navigation_wraps() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), Some("cargo test"), false).unwrap();
    commands::run::create_in(tmp.path(), "test-run").unwrap();
    commands::worker::status::run_in(tmp.path(), "001", "in_progress", None, None, None).unwrap();
    commands::worker::status::run_in(tmp.path(), "002", "completed", None, None, None).unwrap();

    let mut app = App::new(tmp.path().to_path_buf()).unwrap();
    assert_eq!(app.selected, 0);
    app.next();
    assert_eq!(app.selected, 1);
    app.next();
    assert_eq!(app.selected, 0); // wraps
    app.previous();
    assert_eq!(app.selected, 1); // wraps backward
}

// ── format_tokens ───────────────────────────────────────────────────────────

#[test]
fn format_tokens_thousands() {
    assert_eq!(format_tokens(12400), "12.4k");
}

#[test]
fn format_tokens_millions() {
    assert_eq!(format_tokens(1_500_000), "1.5M");
}

#[test]
fn format_tokens_small() {
    assert_eq!(format_tokens(500), "500");
}

// ── App::total_tokens ───────────────────────────────────────────────────────

#[test]
fn app_total_tokens_aggregates() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), Some("cargo test"), false).unwrap();
    commands::run::create_in(tmp.path(), "test-run").unwrap();
    commands::worker::status::run_in(tmp.path(), "001", "in_progress", None, None, Some(10_000))
        .unwrap();
    commands::worker::status::run_in(tmp.path(), "002", "in_progress", None, None, Some(5_000))
        .unwrap();
    commands::worker::status::run_in(tmp.path(), "003", "in_progress", None, None, None).unwrap();

    let app = App::new(tmp.path().to_path_buf()).unwrap();
    assert_eq!(app.total_tokens(), 15_000);
}

// ── Scroll support ──────────────────────────────────────────────────────────

#[test]
fn scroll_down_moves_next() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), Some("cargo test"), false).unwrap();
    commands::run::create_in(tmp.path(), "test-run").unwrap();
    commands::worker::status::run_in(tmp.path(), "001", "in_progress", None, None, None).unwrap();
    commands::worker::status::run_in(tmp.path(), "002", "completed", None, None, None).unwrap();

    let mut app = App::new(tmp.path().to_path_buf()).unwrap();
    assert_eq!(app.selected, 0);
    // ScrollDown is wired to app.next()
    app.next();
    assert_eq!(app.selected, 1);
}

#[test]
fn scroll_up_moves_previous() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), Some("cargo test"), false).unwrap();
    commands::run::create_in(tmp.path(), "test-run").unwrap();
    commands::worker::status::run_in(tmp.path(), "001", "in_progress", None, None, None).unwrap();
    commands::worker::status::run_in(tmp.path(), "002", "completed", None, None, None).unwrap();

    let mut app = App::new(tmp.path().to_path_buf()).unwrap();
    assert_eq!(app.selected, 0);
    // Move forward first so we have room to scroll up
    app.next();
    assert_eq!(app.selected, 1);
    // ScrollUp is wired to app.previous()
    app.previous();
    assert_eq!(app.selected, 0);
}

#[test]
fn mouse_event_variant_exists() {
    use agentrc::tui::event::Event;
    use crossterm::event::{MouseEvent, MouseEventKind};

    // Construct an Event::Mouse with a scroll-down event to prove the variant exists
    let mouse = MouseEvent {
        kind: MouseEventKind::ScrollDown,
        column: 0,
        row: 0,
        modifiers: crossterm::event::KeyModifiers::NONE,
    };
    let event = Event::Mouse(mouse);

    // Pattern-match to confirm the variant is accessible
    assert!(matches!(event, Event::Mouse(_)));
}
