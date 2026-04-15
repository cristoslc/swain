use std::io;
use std::time::{Duration, Instant};

use anyhow::{Context, Result};
use crossterm::event::{
    DisableMouseCapture, EnableMouseCapture, KeyCode, KeyModifiers, MouseButton, MouseEventKind,
};
use crossterm::terminal::{
    disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen,
};
use crossterm::ExecutableCommand;
use ratatui::prelude::*;

use crate::tmux::wrapper::Tmux;
use crate::tui::action::Action;
use crate::tui::app::App;
use crate::tui::event::{Event, EventHandler};
use crate::tui::{action, ui};

pub fn run() -> Result<()> {
    let cwd = std::env::current_dir().context("cannot determine current directory")?;
    let mut app = App::new(cwd)?;

    // Save and rename tmux window
    let tmux = Tmux::new();
    let original_window_name = tmux.current_window_name().ok();
    let _ = tmux.rename_window("agent.rc");

    // Setup terminal
    enable_raw_mode()?;
    io::stdout().execute(EnterAlternateScreen)?;
    io::stdout().execute(EnableMouseCapture)?;
    let backend = CrosstermBackend::new(io::stdout());
    let mut terminal = Terminal::new(backend)?;

    app.terminal_height = terminal.size()?.height;

    let events = EventHandler::new(Duration::from_millis(100));
    let refresh_interval = Duration::from_secs(3);

    loop {
        // Draw
        terminal.draw(|frame| ui::render(&app, frame))?;
        app.terminal_height = terminal.size()?.height;

        // Handle events
        match events.next()? {
            Event::Key(key) => {
                if key.modifiers.contains(KeyModifiers::CONTROL) && key.code == KeyCode::Char('c') {
                    app.should_quit = true;
                }

                match key.code {
                    KeyCode::Char('q') => app.should_quit = true,
                    KeyCode::Char('?') => app.show_help = !app.show_help,
                    KeyCode::Up | KeyCode::Char('k') => app.previous(),
                    KeyCode::Down | KeyCode::Char('j') => app.next(),
                    KeyCode::Char('s') => app.cycle_sort(),
                    KeyCode::Char('d') => app.show_animation = !app.show_animation,
                    KeyCode::Char('D') => app.anim.cycle_shape(),
                    KeyCode::Char('e') => app.show_events = !app.show_events,
                    KeyCode::Char(c) => {
                        match action::handle_key(&app, c) {
                            Action::Shell(cmd) => {
                                // Exit TUI, run command, re-enter
                                io::stdout().execute(DisableMouseCapture)?;
                                disable_raw_mode()?;
                                io::stdout().execute(LeaveAlternateScreen)?;
                                io::stdout().execute(DisableMouseCapture)?;

                                let status =
                                    std::process::Command::new(&cmd[0]).args(&cmd[1..]).status();

                                if let Ok(s) = status {
                                    if !s.success() {
                                        eprintln!("Command exited with: {s}");
                                    }
                                }

                                // Pause for user to see output
                                eprintln!("\nPress Enter to return to dashboard...");
                                let mut buf = String::new();
                                let _ = io::stdin().read_line(&mut buf);

                                // Re-enter TUI
                                enable_raw_mode()?;
                                io::stdout().execute(EnterAlternateScreen)?;
                                io::stdout().execute(EnableMouseCapture)?;
                                terminal = Terminal::new(CrosstermBackend::new(io::stdout()))?;
                                app.refresh();
                            }
                            Action::None => {}
                        }
                    }
                    _ => {}
                }
            }
            Event::Mouse(mouse) => match mouse.kind {
                MouseEventKind::ScrollUp => app.previous(),
                MouseEventKind::ScrollDown => app.next(),
                MouseEventKind::Down(MouseButton::Left) => {
                    app.handle_click(mouse.column, mouse.row);
                }
                _ => {}
            },
            Event::Tick => {
                app.anim.tick();
                if app.last_refresh.elapsed() >= refresh_interval {
                    app.refresh();
                }
            }
        }

        if app.should_quit {
            break;
        }
    }

    // Restore terminal
    io::stdout().execute(DisableMouseCapture)?;
    disable_raw_mode()?;
    io::stdout().execute(LeaveAlternateScreen)?;

    // Restore original tmux window name
    if let Some(name) = original_window_name {
        let _ = tmux.rename_window(&name);
    }

    Ok(())
}
