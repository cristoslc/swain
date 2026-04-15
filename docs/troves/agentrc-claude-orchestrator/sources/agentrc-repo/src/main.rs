use anyhow::Result;
use clap::{Parser, Subcommand, ValueEnum};

use agentrc::commands;

#[derive(Parser)]
#[command(
    name = "agentrc",
    about = "Orchestrate multiple Claude Code worker sessions in tmux panes"
)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Install agentrc prerequisites and configuration
    Install,
    /// Initialize a new agentrc project in the current directory
    Init,
    /// Spawn a new worker for the given task
    Spawn {
        /// Task identifier to spawn a worker for
        task_id: String,
    },
    /// Respawn a dead or failed worker from its existing branch
    Respawn {
        /// Task identifier to respawn
        task_id: String,
    },
    /// Show status of active workers
    Status {
        /// Output status as JSON
        #[arg(long)]
        json: bool,
    },
    /// Tear down worker session(s)
    Teardown {
        /// Specific task to tear down (omit for interactive selection)
        task_id: Option<String>,
        /// Tear down all active workers
        #[arg(long)]
        all: bool,
        /// Force teardown regardless of task state
        #[arg(long)]
        force: bool,
    },
    /// Interactive dashboard for monitoring and managing workers
    Dashboard,
    /// Save and restore run checkpoints
    Checkpoint {
        #[command(subcommand)]
        command: CheckpointCommands,
    },
    /// Audit TDD commit patterns for a task
    Audit {
        /// Task identifier to audit
        task_id: String,
    },
    /// Amend a task brief mid-run and notify the worker
    Amend {
        /// Task identifier to amend
        task_id: String,
        /// Path to a replacement brief file
        #[arg(long)]
        brief: Option<String>,
        /// Text to append as an amendment section
        #[arg(long)]
        message: Option<String>,
    },
    /// Integrate completed work back into the main branch
    Integrate {
        /// Preview merge plan without making changes
        #[arg(long)]
        dry_run: bool,
    },
    /// Arrange tmux panes
    Layout {
        /// Layout mode
        #[arg(value_enum, default_value_t = LayoutMode::Tile)]
        mode: LayoutMode,
    },
    /// Resume previously suspended workers
    Resume,
    /// Watch active run for status changes and heartbeat alerts in real time
    Watch,
    /// Show the event log
    Events {
        /// Number of events to show
        #[arg(long, default_value_t = 20)]
        tail: usize,
    },
    /// Plan management and validation
    Plan {
        #[command(subcommand)]
        command: PlanCommands,
    },
    /// Manage runs (groups of tasks)
    Run {
        #[command(subcommand)]
        command: RunCommands,
    },
    /// Worker-internal commands (used by spawned workers)
    Worker {
        #[command(subcommand)]
        command: WorkerCommands,
    },
}

#[derive(Clone, ValueEnum)]
enum LayoutMode {
    Tile,
    Collate,
}

#[derive(Subcommand)]
enum PlanCommands {
    /// Validate the task DAG in the active run
    Validate,
}

#[derive(Subcommand)]
enum RunCommands {
    /// Create a new run
    Create {
        /// Slug identifier for the run
        #[arg(long)]
        slug: String,
    },
    /// List all runs
    List,
    /// Archive a run
    Archive,
}

#[derive(Subcommand)]
enum CheckpointCommands {
    /// Save a checkpoint of the current run
    Save {
        /// Description of the checkpoint
        #[arg(short, long)]
        message: Option<String>,
    },
    /// List checkpoints for the active run
    List,
    /// Restore from a checkpoint
    Restore {
        /// Checkpoint ID (latest if omitted)
        id: Option<String>,
        /// Auto-respawn in-progress tasks
        #[arg(long)]
        respawn: bool,
    },
}

#[derive(Subcommand)]
enum WorkerCommands {
    /// Report worker status
    Status {
        /// Task identifier
        #[arg(long)]
        task: String,
        /// Worker state
        #[arg(long)]
        state: String,
        /// Current phase
        #[arg(long)]
        phase: Option<String>,
        /// Status message
        #[arg(long)]
        message: Option<String>,
        /// Cumulative token usage
        #[arg(long)]
        tokens: Option<u64>,
    },
    /// Send a heartbeat for a worker
    Heartbeat {
        /// Task identifier
        #[arg(long)]
        task: String,
        /// Heartbeat interval in seconds
        #[arg(long, default_value_t = 30)]
        interval: u64,
    },
    /// Record a note for a task
    Note {
        /// Task identifier
        #[arg(long)]
        task: String,
        /// Note message
        #[arg(long)]
        message: String,
    },
    /// Record a result for a task
    Result {
        /// Task identifier
        #[arg(long)]
        task: String,
        /// Path to result file
        #[arg(long)]
        file: Option<String>,
        /// Read result from stdin
        #[arg(long)]
        stdin: bool,
    },
    /// Mark a task as done
    Done {
        /// Task identifier
        #[arg(long)]
        task: String,
        /// Path to result file
        #[arg(long)]
        result_file: Option<String>,
    },
}

fn main() -> Result<()> {
    let cli = Cli::parse();

    match cli.command {
        Commands::Install => commands::install::run(),
        Commands::Init => commands::init::run(),
        Commands::Spawn { task_id } => commands::spawn::run(&task_id),
        Commands::Respawn { task_id } => commands::respawn::run(&task_id),
        Commands::Audit { task_id } => commands::audit::run(&task_id),
        Commands::Amend {
            task_id,
            brief,
            message,
        } => {
            let cwd = std::env::current_dir().expect("cannot determine current directory");
            commands::amend::run_in(&cwd, &task_id, brief.as_deref(), message.as_deref())
        }
        Commands::Checkpoint { command } => match command {
            CheckpointCommands::Save { message } => commands::checkpoint::save(message.as_deref()),
            CheckpointCommands::List => commands::checkpoint::list(),
            CheckpointCommands::Restore { id, respawn } => {
                commands::checkpoint::restore(id.as_deref(), respawn)
            }
        },
        Commands::Status { json } => commands::status::run(json),
        Commands::Teardown {
            task_id,
            all,
            force,
        } => commands::teardown::run(task_id.as_deref(), all, force),
        Commands::Dashboard => commands::dashboard::run(),
        Commands::Integrate { dry_run } => commands::integrate::run(dry_run),
        Commands::Layout { mode } => {
            let mode_str = match mode {
                LayoutMode::Tile => "tile",
                LayoutMode::Collate => "collate",
            };
            commands::layout::run(mode_str)
        }
        Commands::Resume => commands::resume::run(),
        Commands::Watch => commands::watch::run(),
        Commands::Events { tail } => commands::events::run(tail),
        Commands::Plan { command } => match command {
            PlanCommands::Validate => commands::plan::run(),
        },
        Commands::Run { command } => match command {
            RunCommands::Create { slug } => commands::run::create(&slug),
            RunCommands::List => commands::run::list(),
            RunCommands::Archive => commands::run::archive(),
        },
        Commands::Worker { command } => match command {
            WorkerCommands::Status {
                task,
                state,
                phase,
                message,
                tokens,
            } => commands::worker::status::run(
                &task,
                &state,
                phase.as_deref(),
                message.as_deref(),
                tokens,
            ),
            WorkerCommands::Heartbeat { task, interval } => {
                commands::worker::heartbeat::run(&task, interval)
            }
            WorkerCommands::Note { task, message } => commands::worker::note::run(&task, &message),
            WorkerCommands::Result { task, file, stdin } => {
                commands::worker::result::run(&task, file.as_deref(), stdin)
            }
            WorkerCommands::Done { task, result_file } => {
                commands::worker::done::run(&task, result_file.as_deref())
            }
        },
    }
}
