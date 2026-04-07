# Git CLI Research Synthesis

## Overview

Git is a distributed version control system with over 150 subcommands organized into functional categories. This trove captures the CLI interface structure through manpage and help output analysis.

## Key Findings

### Command Categories

Git's help output organizes commands into 5 functional categories:

1. **Start a working area** - `clone`, `init`
2. **Work on the current change** - `add`, `mv`, `restore`, `rm`
3. **Examine history and state** - `bisect`, `diff`, `grep`, `log`, `show`, `status`
4. **Grow, mark and tweak history** - `backfill`, `branch`, `commit`, `merge`, `rebase`, `reset`, `switch`, `tag`
5. **Collaborate** - `fetch`, `pull`, `push`

### Help System Structure

- **Main help** (`git --help`): Shows synopsis and categorized command list
- **Manpage** (`man git`): Comprehensive documentation with all options and commands
- **Subcommand help** (`git <cmd> --help`): Detailed usage for each subcommand
- **Concept guides** (`git help <concept>`): Topical documentation (tutorial, everyday, workflows)

### Subcommand Discovery

The `git remote` subcommand was analyzed as a representative example. It manages tracked repositories with 10+ sub-subcommands:
- `add`, `rename`, `remove` - remote management
- `set-head`, `set-branches` - branch configuration
- `get-url`, `set-url` - URL management
- `show`, `prune`, `update` - inspection and maintenance

## Gaps

This trove captures only the CLI interface structure. Missing:
- Actual command usage examples
- Workflow patterns (feature branches, code review, releases)
- Integration with remote hosting (GitHub, GitLab)

## Sources

- `git-manpage` - Full manpage output
- `git-help-output` - Top-level help with command categories
- `git-remote-help` - Representative subcommand help
