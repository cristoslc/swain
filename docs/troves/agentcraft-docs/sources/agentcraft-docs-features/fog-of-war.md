---
title: Fog of War
url: https://www.getagentcraft.com/docs/features/fog-of-war
fetched: 2026-05-04
type: documentation
---

# Fog of War

Visualize where your agents are actively working.

Fog of War dims areas of the map without active heroes, giving you a visual sense of where work is happening.

## Toggle

Press V to toggle fog of war on and off.

## How It Works

When fog of war is enabled, areas of the 3D map that don't have active heroes are darkened using a post-processing shader. Areas near active heroes remain fully visible, creating a natural focus on where work is in progress.

The fog effect simply darkens pixels — it doesn't change colors or apply tone mapping distortion. Toggling fog on or off produces consistent colors.

## Territory Heatmap

Press H (with no hero selected) to toggle the territory heatmap. This visualization shows which areas of the map have the most hero activity.

## Technical Details

The fog of war uses a Three.js post-processing pipeline:

- Fog OFF: RenderPass → OutputPass
- Fog ON: RenderPass → FogPass → OutputPass

The fog pass is color-neutral — it darkens pixels without color space conversion. The renderer uses NoToneMapping to avoid ACES color compression, ensuring terrain and building colors remain consistent whether fog is on or off.