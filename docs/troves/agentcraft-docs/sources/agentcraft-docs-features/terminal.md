---
title: Integrated Terminal
url: https://www.getagentcraft.com/docs/features/terminal
fetched: 2026-05-04
type: documentation
---

# Integrated Terminal

Run shell commands without leaving AgentCraft.

AgentCraft includes a full PTY terminal in the bottom HUD. Run shell commands without leaving the game interface.

## Opening the Terminal

- Press F in the command grid to open the terminal
- Press Ctrl+T from anywhere

The first press creates a new terminal tab. Subsequent presses toggle the panel visibility.

## Multi-Tab Support

The terminal supports multiple tabs, similar to VS Code:

| Action | Effect |
| --- | --- |
| Click + button | Open a new terminal tab |
| Click a tab | Switch to that terminal (session preserved) |
| Click x on a tab | Close that terminal and kill the PTY |
| Close last tab | Panel hides, all state resets |

### Session Preservation

- Switching tabs is CSS-only — the PTY session stays alive in the background
- Toggling the panel closed preserves all running sessions — reopen to continue
- Closing a tab (x button) kills that PTY process
- Closing the browser kills all PTYs automatically

## Shell Environment

The terminal uses your configured login shell ($SHELL, defaulting to /bin/zsh) with the -l flag, so your PATH, nvm, pyenv, and other shell profile settings are available. The working directory is set to your project directory.

## Session Restart

If you type exit or the shell process exits, the terminal shows "Session ended. Press any key to restart." Pressing any key restarts the shell in the same tab.

## Layout

The terminal occupies the content area of the center HUD module. If a hero is selected when the terminal opens, the hero portrait remains visible on the left. If nothing is selected, the terminal fills the full center module.

## Keyboard Shortcuts

| Key | Action |
| --- | --- |
| F | Toggle terminal (command grid) |
| Ctrl+T | Toggle terminal (global) |

Note: Ctrl+T is intercepted to prevent the browser's "new tab" shortcut. Global hotkeys (Q/W/E/R/F, etc.) are not intercepted while the terminal has focus.