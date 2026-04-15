use anyhow::Result;

use crate::events;

pub fn run(tail: usize) -> Result<()> {
    let cwd = std::env::current_dir()?;
    let events = events::tail(&cwd, tail)?;

    if events.is_empty() {
        println!("No events.");
        return Ok(());
    }

    for event in &events {
        let ts = event.timestamp.format("%H:%M:%S");
        let task = event.task_id.as_deref().unwrap_or("-");
        let severity = format!("{:?}", event.severity).to_uppercase();
        let etype = serde_json::to_string(&event.event_type)
            .unwrap_or_default()
            .trim_matches('"')
            .to_string();
        println!(
            "{ts}  {severity:<5}  {task:<6}  {etype:<20}  {}",
            event.message
        );
    }

    Ok(())
}
