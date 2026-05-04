use assert_cmd::Command;
use predicates::prelude::*;

#[test]
fn binary_prints_help() {
    Command::cargo_bin("agentrc")
        .unwrap()
        .arg("--help")
        .assert()
        .success()
        .stdout(predicate::str::contains("agentrc"));
}

#[test]
fn binary_has_subcommands() {
    let assert = Command::cargo_bin("agentrc")
        .unwrap()
        .arg("--help")
        .assert()
        .success();

    let output = assert.get_output().stdout.clone();
    let stdout = String::from_utf8(output).unwrap();

    let expected_subcommands = [
        "init",
        "install",
        "spawn",
        "status",
        "teardown",
        "integrate",
        "layout",
        "resume",
        "plan",
        "run",
        "worker",
    ];

    for subcmd in &expected_subcommands {
        assert!(
            stdout.contains(subcmd),
            "Expected help output to contain subcommand '{}', but it was not found.\nHelp output:\n{}",
            subcmd,
            stdout,
        );
    }
}
