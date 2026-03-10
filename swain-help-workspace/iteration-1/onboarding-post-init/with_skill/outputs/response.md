**Welcome to swain.** Here's how it works:

**The big picture:** Swain manages your project's documentation artifacts (specs, stories, ADRs, etc.) and tracks implementation work -- so nothing falls through the cracks between sessions.

**Three things to know:**

1. **`/swain` is your entry point.** It routes to the right sub-skill automatically. You can also call skills directly (`/swain-design`, `/swain-do`, etc.).

2. **Design before you build.** When you want to implement something, start with `/swain` to create a spec or story. Swain enforces a "plan before code" workflow -- it creates tracked tasks before implementation begins.

3. **Governance is automatic.** `/swain-config` runs at session start to ensure routing rules are in place. You don't need to think about it.

**Common starting points:**
- "I want to plan a new feature" -- creates an Epic or Story
- "Write a spec for X" -- creates an Agent Spec
- "What should I work on next?" -- checks your task backlog
- "File a bug" -- creates a Bug artifact
- "Let's release" -- version bump + changelog

**Need more?** Ask me anything about swain, or say `/swain help reference` for a full cheat sheet.
