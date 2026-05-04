use anyhow::{anyhow, Result};
use serde::de::DeserializeOwned;

/// Split a markdown string at its `---` frontmatter delimiters.
///
/// Returns `(yaml_str, rest)` where `yaml_str` is the YAML content between
/// the opening and closing `---` lines and `rest` is everything after the
/// closing delimiter (including its leading newline, if any).
fn split_frontmatter(content: &str) -> Result<(&str, &str)> {
    let trimmed = content.trim_start();

    if !trimmed.starts_with("---") {
        return Err(anyhow!("missing opening frontmatter delimiter '---'"));
    }

    // Skip past the opening "---" line
    let after_open = &trimmed[3..];
    let after_open = after_open.strip_prefix('\n').unwrap_or(after_open);

    let close_pos = after_open
        .find("\n---")
        .ok_or_else(|| anyhow!("missing closing frontmatter delimiter '---'"))?;

    let yaml_str = &after_open[..close_pos];
    let body_start = close_pos + 4; // skip "\n---"
    let rest = &after_open[body_start..];

    Ok((yaml_str, rest))
}

/// Parse YAML frontmatter delimited by `---` from a markdown string.
///
/// Returns the deserialized frontmatter and the body text after the closing delimiter.
pub fn parse<T: DeserializeOwned>(content: &str) -> Result<(T, String)> {
    let (yaml_str, rest) = split_frontmatter(content)?;

    let body = if rest.is_empty() {
        String::new()
    } else {
        // Strip the newline right after the closing ---
        rest.strip_prefix('\n').unwrap_or(rest).to_string()
    };

    let frontmatter: T = serde_yaml::from_str(yaml_str)
        .map_err(|e| anyhow!("failed to parse frontmatter YAML: {e}"))?;

    Ok((frontmatter, body))
}

/// Update a single key's value in the YAML frontmatter of a markdown string.
///
/// Finds the line starting with `<key>:` and replaces it with `<key>: <new_value>`.
/// Values containing YAML-special characters are automatically quoted.
/// Returns the reassembled document, or an error if the key is not found.
pub fn update_field(content: &str, key: &str, new_value: &str) -> Result<String> {
    let (yaml_str, body) = split_frontmatter(content)?;

    let safe_value = yaml_safe_value(new_value);

    let mut found = false;
    let updated_lines: Vec<String> = yaml_str
        .lines()
        .map(|line| {
            let stripped = line.trim_start();
            if stripped.starts_with(&format!("{key}:")) || stripped.starts_with(&format!("{key} :"))
            {
                found = true;
                format!("{key}: {safe_value}")
            } else {
                line.to_string()
            }
        })
        .collect();

    if !found {
        return Err(anyhow!("key '{key}' not found in frontmatter"));
    }

    let updated_yaml = updated_lines.join("\n");
    Ok(format!("---\n{updated_yaml}\n---{body}"))
}

/// Quote a YAML value if it contains characters that need escaping.
fn yaml_safe_value(value: &str) -> String {
    if value == "null" || value == "true" || value == "false" || value.is_empty() {
        return format!("\"{value}\"");
    }
    if value.contains('%')
        || value.contains(':')
        || value.contains('#')
        || value.contains('{')
        || value.contains('}')
        || value.contains('[')
        || value.contains(']')
        || value.contains(',')
        || value.contains('&')
        || value.contains('*')
        || value.contains('!')
        || value.contains('|')
        || value.contains('>')
        || value.contains('\'')
        || value.contains('"')
        || value.contains('`')
        || value.contains('@')
        || value.starts_with(' ')
        || value.ends_with(' ')
    {
        let escaped = value.replace('"', "\\\"");
        return format!("\"{escaped}\"");
    }
    value.to_string()
}

/// Update a key's value in frontmatter, or append it if the key doesn't exist.
pub fn upsert_field(content: &str, key: &str, new_value: &str) -> Result<String> {
    let (yaml_str, body) = split_frontmatter(content)?;

    let safe_value = yaml_safe_value(new_value);

    let mut found = false;
    let updated_lines: Vec<String> = yaml_str
        .lines()
        .map(|line| {
            let stripped = line.trim_start();
            if stripped.starts_with(&format!("{key}:")) || stripped.starts_with(&format!("{key} :"))
            {
                found = true;
                format!("{key}: {safe_value}")
            } else {
                line.to_string()
            }
        })
        .collect();

    let updated_yaml = if found {
        updated_lines.join("\n")
    } else {
        let mut lines = updated_lines;
        lines.push(format!("{key}: {safe_value}"));
        lines.join("\n")
    };

    Ok(format!("---\n{updated_yaml}\n---{body}"))
}

/// Extract a raw string value for a key from frontmatter YAML lines.
pub fn get_field(content: &str, key: &str) -> Result<Option<String>> {
    let (yaml_str, _body) = split_frontmatter(content)?;

    for line in yaml_str.lines() {
        let stripped = line.trim_start();
        if stripped.starts_with(&format!("{key}:")) || stripped.starts_with(&format!("{key} :")) {
            let value = if let Some(rest) = stripped.strip_prefix(&format!("{key}:")) {
                rest.trim()
            } else if let Some(rest) = stripped.strip_prefix(&format!("{key} :")) {
                rest.trim()
            } else {
                ""
            };
            return Ok(Some(value.to_string()));
        }
    }
    Ok(None)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashMap;

    #[test]
    fn parse_simple_frontmatter() {
        let content = "---\ntitle: Hello\n---\nBody text";
        let (fm, body): (HashMap<String, String>, String) = parse(content).unwrap();
        assert_eq!(fm["title"], "Hello");
        assert_eq!(body, "Body text");
    }

    #[test]
    fn parse_no_delimiters_fails() {
        let content = "No frontmatter here";
        let result = parse::<HashMap<String, String>>(content);
        assert!(result.is_err());
    }

    #[test]
    fn update_field_replaces_value() {
        let content = "---\nfoo: bar\nbaz: qux\n---\nBody";
        let updated = update_field(content, "foo", "new_val").unwrap();
        assert!(updated.contains("foo: new_val"));
        assert!(updated.contains("baz: qux"));
        assert!(updated.contains("Body"));
    }

    #[test]
    fn update_field_missing_key_fails() {
        let content = "---\nfoo: bar\n---\nBody";
        let result = update_field(content, "nonexistent", "val");
        assert!(result.is_err());
    }
}
