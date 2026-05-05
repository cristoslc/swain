---
title: Skill Scrolls
url: https://www.getagentcraft.com/docs/features/skill-scrolls
fetched: 2026-05-04
type: documentation
---

# Skill Scrolls

Collectible scrolls that install real agent skills.

Skill Scrolls are collectible items scattered across the RTS map. When a hero walks to a scroll, a card shows a skill from skills.sh with an install button. This makes map exploration rewarding and helps you discover agent skills organically.

## How It Works

1. Find a scroll — Gold glowing scrolls appear at random positions on the map (5 at a time)
2. Walk to it — Click or right-click the scroll with a hero selected. The hero walks to the scroll's position
3. Pick it up — When the hero arrives, a skill card modal appears showing the skill name, description, and install count
4. Install or dismiss — Click Install Skill to add it to your Claude Code skills, or Dismiss to skip it

### Installation

Skills are installed via the skills.sh CLI:

```
npx skills add <source> --skill <skillId> -a claude-code -y
```

After installation, the skill appears in ~/.claude/skills/ and extends your agent's capabilities.

## Respawn

When all 5 scrolls are collected (installed or dismissed), a new batch of 5 scrolls spawns after a random delay (10-20 minutes). The new batch draws from skills you haven't already installed.

## Scroll Catalog

AgentCraft ships with a curated catalog of ~20 skills from skills.sh. The catalog is pre-built and committed to the repository — no runtime scraping needed. Skills you've already installed are automatically filtered out.

## Map Appearance

- Scrolls float and rotate on the map with a gold ground ring
- Gold dots appear on the minimap for each uncollected scroll
- Scrolls have an invisible hit area for click detection

## Error Handling

If installation fails, the skill card shows a user-friendly error message:

| Error | Message |
| --- | --- |
| Network issue | "Network error: Could not reach npm registry" |
| Skill not found | "Skill not found in registry" |
| Permission denied | "Permission denied: Check npm permissions" |
| Timeout | "Installation timed out: Check network connection" |