use agentrc::commands::layout::{compute_collation, CollateAction};

#[test]
fn collate_under_limit_no_new_windows() {
    // 3 panes, workers_per_window=4 → no new windows, just tile
    let panes = vec!["%1".into(), "%2".into(), "%3".into()];
    let existing_windows = vec!["workers".into()];
    let actions = compute_collation(&panes, &existing_windows, 4);

    // No moves, no new windows — just tile existing
    assert!(
        actions.iter().all(|a| matches!(a, CollateAction::Tile(_))),
        "expected only tile actions, got: {:?}",
        actions
    );
    assert_eq!(actions.len(), 1); // tile "workers"
}

#[test]
fn collate_at_limit_no_overflow() {
    // 4 panes, workers_per_window=4 → exactly fits, no overflow
    let panes = vec!["%1".into(), "%2".into(), "%3".into(), "%4".into()];
    let existing_windows = vec!["workers".into()];
    let actions = compute_collation(&panes, &existing_windows, 4);

    assert!(
        actions.iter().all(|a| matches!(a, CollateAction::Tile(_))),
        "expected only tile actions, got: {:?}",
        actions
    );
    assert_eq!(actions.len(), 1);
}

#[test]
fn collate_over_limit_creates_window_and_moves_panes() {
    // 6 panes, workers_per_window=4 → creates 1 new window, moves 2 panes
    let panes: Vec<String> = (1..=6).map(|i| format!("%{}", i)).collect();
    let existing_windows = vec!["workers".into()];
    let actions = compute_collation(&panes, &existing_windows, 4);

    let create_count = actions
        .iter()
        .filter(|a| matches!(a, CollateAction::CreateWindow(_)))
        .count();
    let move_count = actions
        .iter()
        .filter(|a| matches!(a, CollateAction::MovePane { .. }))
        .count();
    let tile_count = actions
        .iter()
        .filter(|a| matches!(a, CollateAction::Tile(_)))
        .count();

    assert_eq!(create_count, 1, "should create 1 new window");
    assert_eq!(move_count, 2, "should move 2 panes to the new window");
    assert_eq!(tile_count, 2, "should tile both windows");
}

#[test]
fn collate_large_overflow() {
    // 10 panes, workers_per_window=3 → ceil(10/3)=4 total windows, 3 new
    let panes: Vec<String> = (1..=10).map(|i| format!("%{}", i)).collect();
    let existing_windows = vec!["workers".into()];
    let actions = compute_collation(&panes, &existing_windows, 3);

    let create_count = actions
        .iter()
        .filter(|a| matches!(a, CollateAction::CreateWindow(_)))
        .count();
    let move_count = actions
        .iter()
        .filter(|a| matches!(a, CollateAction::MovePane { .. }))
        .count();
    let tile_count = actions
        .iter()
        .filter(|a| matches!(a, CollateAction::Tile(_)))
        .count();

    assert_eq!(create_count, 3, "should create 3 new windows");
    assert_eq!(move_count, 7, "should move 7 panes (keep 3 in original)");
    assert_eq!(tile_count, 4, "should tile all 4 windows");
}

#[test]
fn collate_window_naming() {
    // New windows should be named workers-2, workers-3, etc.
    let panes: Vec<String> = (1..=10).map(|i| format!("%{}", i)).collect();
    let existing_windows = vec!["workers".into()];
    let actions = compute_collation(&panes, &existing_windows, 3);

    let created_names: Vec<&str> = actions
        .iter()
        .filter_map(|a| match a {
            CollateAction::CreateWindow(name) => Some(name.as_str()),
            _ => None,
        })
        .collect();

    assert_eq!(created_names, vec!["workers-2", "workers-3", "workers-4"]);
}

#[test]
fn collate_idempotent_already_distributed() {
    // Already distributed across 2 windows: 4 in workers, 2 in workers-2
    // workers_per_window=4 → no changes needed beyond tiling
    let panes: Vec<String> = (1..=6).map(|i| format!("%{}", i)).collect();
    let existing_windows = vec!["workers".into(), "workers-2".into()];
    // With 6 panes and 2 existing windows, ceil(6/4)=2 windows needed = exactly existing
    let actions = compute_collation(&panes, &existing_windows, 4);

    let create_count = actions
        .iter()
        .filter(|a| matches!(a, CollateAction::CreateWindow(_)))
        .count();

    assert_eq!(create_count, 0, "should not create any new windows");
}

#[test]
fn collate_move_targets_correct_windows() {
    // 7 panes, workers_per_window=3 → ceil(7/3)=3 windows, 2 new
    // First window keeps 3, second gets 3, third gets 1
    let panes: Vec<String> = (1..=7).map(|i| format!("%{}", i)).collect();
    let existing_windows = vec!["workers".into()];
    let actions = compute_collation(&panes, &existing_windows, 3);

    let moves: Vec<(&str, &str)> = actions
        .iter()
        .filter_map(|a| match a {
            CollateAction::MovePane { pane_id, target } => {
                Some((pane_id.as_str(), target.as_str()))
            }
            _ => None,
        })
        .collect();

    // Panes 4,5,6 go to workers-2; pane 7 goes to workers-3
    assert_eq!(moves.len(), 4);
    for (pane, target) in &moves[..3] {
        assert_eq!(*target, "workers-2", "pane {} should go to workers-2", pane);
    }
    assert_eq!(moves[3].1, "workers-3");
}
