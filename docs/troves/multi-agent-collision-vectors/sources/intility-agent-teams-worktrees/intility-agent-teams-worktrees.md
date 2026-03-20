---
source-id: intility-agent-teams-worktrees
type: web-page
title: "Agent Teams or: How I Learned to Stop Worrying About Merge Conflicts and Love Git Worktrees"
url: "https://engineering.intility.com/article/agent-teams-or-how-i-learned-to-stop-worrying-about-merge-conflicts-and-love-git-worktrees"
fetched: 2026-03-20
content-hash: "--"
---

# Agent Teams or: How I Learned to Stop Worrying About Merge Conflicts and Love Git Worktrees

## Merge Conflict Philosophy

The author embraces conflicts as inevitable rather than preventable: "You might be thinking that this is bound to result in merge conflicts. It does. Thankfully Claude is quite good at handling them so no need to worry."

Resolution approach: feed Claude a fresh session with PR details and ask it to inspect branches, identify merge order, and resolve conflicts automatically using the `gh` CLI tool.

## Coordination Between Agents

For team-based workflows:
- Designate one "team lead" session that coordinates
- Assign individual teammates to specific features with worktrees
- Instruct the lead to coordinate merging after features complete
- Use model specification (Opus vs Sonnet) for different complexity levels

## Practical Lessons Learned

Key gotchas:
- Claude sandboxing conflicts with worktree creation
- Context compaction can be buggy in teams (requires canceling all tasks first)
- Auto-accepting file edits sometimes does not persist across teammates

Best practices:
- Add `.worktrees/` to `.gitignore` explicitly
- Create a `CLAUDE.md` with clear worktree instructions
- Use session managers (tmux, terminal tabs) for parallel monitoring
- Consider parallel code review patterns for complex merge scenarios

## Key Insight

The strategy prioritizes continuous parallel work over conflict avoidance, leveraging AI capabilities to resolve integration issues post-development. This is an explicit trade-off: accept merge conflicts as a cost of parallelism, and use AI to resolve them rather than preventing them.

## Limitation

This approach works for textual merge conflicts but does not address semantic conflicts — changes that merge cleanly but are logically incompatible. The author does not discuss post-merge testing or verification.
