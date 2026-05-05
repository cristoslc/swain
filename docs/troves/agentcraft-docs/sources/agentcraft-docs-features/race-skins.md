---
title: Race Skins
url: https://www.getagentcraft.com/docs/features/race-skins
fetched: 2026-05-04
type: documentation
---

# Race Skins

Transform the entire game world with faction themes.

Race Skins let you choose a faction that transforms the entire game world — buildings, hero characters, worker models, terrain textures, and animated portraits.

## Available Races

| Race | Description |
| --- | --- |
| Orc (default) | Savage & brutal |
| Human | Noble & steadfast |
| Elf | Ancient & mystical |
| Undead | Dark & relentless |

More races are planned for future releases.

## Selecting a Skin

1. Open Settings (gear icon in the top bar)
2. Go to the Visual tab
3. Click a race card under Race Skin
4. The page reloads to apply the new skin

A page reload is required because the 3D models, textures, and terrain need to be re-initialized.

## What Changes

Each race affects every visual layer of the game:

- Buildings — All 8 structures (throne, banner, mine, engineering, archives, recon, analysis, settings) use race-specific 3D models
- Heroes — 5 unique character models per race, deterministically assigned by session ID
- Workers — Race-themed worker units
- Portraits — Animated WebP avatars with idle, casting, and thinking states
- Terrain — Grass/dirt textures, tree palettes, and water colors change per race

## Hero Models

Each race has 5 hero slots. Heroes are deterministically mapped to a slot based on session ID, so the same session always gets the same character.

| Slot | Orc | Human | Elf | Undead |
| --- | --- | --- | --- | --- |
| 0 | Chieftain | Paladin | Queen | King |
| 1 | Shaman | Knight | Priestess | Warrior |
| 2 | Archer | Mage | Warrior | Mage |
| 3 | Grunt | Archer | Archer | Archer |
| 4 | Warrior | Soldier | Assassin | Assassin |

## Persistence

Your race skin selection is saved in three places for reliability:

- Browser localStorage
- Server settings file (~/.claude-rts/settings.json)
- In-memory for hero spawning