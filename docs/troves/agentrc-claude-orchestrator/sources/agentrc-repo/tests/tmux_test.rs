use agentrc::tmux::wrapper::Tmux;

#[test]
fn tmux_build_split_command() {
    let args = Tmux::build_split_args("workers-1");
    assert!(args.contains(&"split-window".to_string()));
    assert!(args.contains(&"-h".to_string()));
    assert!(args.contains(&"-P".to_string()));
    assert!(args.contains(&"-t".to_string()));
    assert!(args.contains(&"workers-1".to_string()));
}

#[test]
fn tmux_build_send_keys_command() {
    let args = Tmux::build_send_keys_args("%14", "echo hello");
    assert_eq!(args[0], "send-keys");
    assert_eq!(args[1], "-t");
    assert_eq!(args[2], "%14");
    assert_eq!(args[3], "echo hello");
    assert_eq!(args[4], "Enter");
}

#[test]
fn tmux_build_kill_pane_command() {
    let args = Tmux::build_kill_pane_args("%14");
    assert_eq!(args, vec!["kill-pane", "-t", "%14"]);
}

#[test]
fn tmux_is_inside_checks_env() {
    // TMUX env var may or may not be set depending on test context
    // Just verify the function exists and returns a bool
    let _ = Tmux::is_inside_tmux();
}

#[test]
fn tmux_build_move_pane_command() {
    let args = Tmux::build_move_pane_args("%5", "workers-2");
    assert_eq!(args, vec!["move-pane", "-s", "%5", "-t", "workers-2"]);
}

#[test]
fn tmux_build_new_window_command() {
    let args = Tmux::build_new_window_args("workers-3");
    assert_eq!(args, vec!["new-window", "-n", "workers-3"]);
}

#[test]
fn tmux_build_list_panes_command() {
    let args = Tmux::build_list_panes_args("workers");
    assert_eq!(
        args,
        vec!["list-panes", "-t", "workers", "-F", "#{pane_id}"]
    );
}

#[test]
fn tmux_build_capture_pane_command() {
    let args = Tmux::build_capture_pane_args("%5", 30);
    assert_eq!(
        args,
        vec!["capture-pane", "-t", "%5", "-p", "-S", "-30"]
            .into_iter()
            .map(String::from)
            .collect::<Vec<_>>()
    );
}

#[test]
fn tmux_build_set_pane_title_args() {
    let args = Tmux::build_set_pane_title_args("%28", "orc:001:plan-validate");
    assert_eq!(
        args,
        vec!["select-pane", "-t", "%28", "-T", "orc:001:plan-validate"]
            .into_iter()
            .map(String::from)
            .collect::<Vec<_>>()
    );
}

#[test]
fn tmux_build_rename_window_command() {
    let args = Tmux::build_rename_window_args("agent.rc");
    assert_eq!(
        args,
        vec!["rename-window", "agent.rc"]
            .into_iter()
            .map(String::from)
            .collect::<Vec<_>>()
    );
}

#[test]
fn tmux_build_current_window_name_command() {
    let args = Tmux::build_current_window_name_args();
    assert_eq!(
        args,
        vec!["display-message", "-p", "#{window_name}"]
            .into_iter()
            .map(String::from)
            .collect::<Vec<_>>()
    );
}
