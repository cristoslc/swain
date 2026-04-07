---
source-id: "opencode-github-readme"
title: "anomalyco/opencode — GitHub README"
type: web
url: "https://github.com/anomalyco/opencode"
fetched: 2026-04-07T01:57:51Z
hash: "a4d946e37663be856955c52d501c8cde6aa155f499508361f4eba992d01d6917"
---

# anomalyco/opencode — The open source AI coding agent

**Stars:** 138k | **Forks:** 15.3k | **Contributors:** 844 | **Latest:** v1.3.17 (Apr 6, 2026)

## Installation

```bash
# curl installer
curl -fsSL https://opencode.ai/install | bash

# Package managers
npm i -g opencode-ai@latest
brew install anomalyco/tap/opencode   # macOS/Linux (recommended)
brew install opencode                  # official brew formula (less frequent updates)
scoop install opencode                 # Windows
choco install opencode                 # Windows
sudo pacman -S opencode               # Arch Linux (Stable)
paru -S opencode-bin                  # Arch Linux (AUR, Latest)
mise use -g opencode                  # Any OS
nix run nixpkgs#opencode              # or github:anomalyco/opencode for dev branch
```

## Desktop App (BETA)

Available as a desktop application for macOS (Apple Silicon / Intel), Windows, and Linux (deb/rpm/AppImage).

```bash
brew install --cask opencode-desktop  # macOS
```

## Built-in agents

Switch between agents with the `Tab` key:

- **build** — Default, full-access agent for development work.
- **plan** — Read-only agent for analysis and code exploration. Denies file edits, asks permission before bash commands. Ideal for exploring unfamiliar codebases or planning changes.
- **general** — Subagent for complex searches and multistep tasks. Used internally; can be invoked with `@general` in messages.

## FAQ: How is this different from Claude Code?

Very similar in capability. Key differences:

- **100% open source.**
- **Not coupled to any provider.** Supports Claude, OpenAI, Google, local models, and more via OpenCode Zen (curated model list).
- **Out-of-the-box LSP support.**
- **Focus on TUI.** Built by neovim users and the creators of terminal.shop, pushing the limits of what's possible in the terminal.
- **Client/server architecture.** The TUI frontend is one of many possible clients. OpenCode can run on your computer while you drive it remotely from a mobile app.

## Architecture notes

- **Client/server split:** Running `opencode` starts a TUI (client) and a background HTTP server. The two are decoupled.
- **Config split:** `opencode.json` configures server/runtime behavior. `tui.json` configures the TUI client separately.
- **Language:** Primary code is TypeScript (57.9%) + MDX (38.3%), with Rust (0.5%) for performance-sensitive parts.
- **SDK:** A generated JS/TS SDK from the OpenAPI spec is available (`packages/sdk/js`).
