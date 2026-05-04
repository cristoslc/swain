use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RunMetadata {
    pub id: String,
    pub slug: String,
    pub created_at: DateTime<Utc>,
    #[serde(default)]
    pub archived: bool,
}

impl RunMetadata {
    pub fn new(slug: &str) -> Self {
        let now = Utc::now();
        let timestamp = now.format("%Y%m%dT%H%M%S").to_string();
        let sanitized: String = slug
            .chars()
            .map(|c| match c {
                'a'..='z' | 'A'..='Z' | '0'..='9' | '-' | '_' | '.' => c,
                _ => '-',
            })
            .collect();
        let id = format!("{}-{}", timestamp, sanitized);
        Self {
            id,
            slug: slug.to_string(),
            created_at: now,
            archived: false,
        }
    }
}
