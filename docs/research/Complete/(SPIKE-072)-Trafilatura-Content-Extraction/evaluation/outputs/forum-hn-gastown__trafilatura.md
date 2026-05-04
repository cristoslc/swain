---
title: Hacker News
url: https://news.ycombinator.com/item?id=46463757
hostname: ycombinator.com
sitename: This is clearly going to develop the same problem Beads has. I've used it. I'm i...
date: 2026-01-02
---
This is clearly going to develop the same problem Beads has. I've used it. I'm in stage 7. Beads is a good idea with a bad implementation. It's not a designed product in the sense we are used to, it's more like a stream of consciousness converted directly into code. There are many features that overlap significantly, strange bugs, and the docs are also AI generated so have fun reading them. It's a program that isn't only vibe coded, it was vibe designed too.

Gas Town is clearly the same thing multiplied by ten thousand. The number of overlapping and adhoc concepts in this design is overwhelming. Steve is ahead of his time but we aren't going to end up using this stuff. Instead a few of the core insights will get incorporated into other agents in a simpler but no less effective way.

And anyway the big problem is accountability. The reason everyone makes a face when Steve preaches agent orchestration is that he must be in an unusual social situation. Gas Town sounds fun if you are accountable to nobody: not for code quality, design coherence or inferencing costs. The rest of us are accountable for at least the first two and even in corporate scenarios where there is a blank check for tokens, that can't last. So the bottleneck is going to be how fast humans can review code and agree to take responsibility for it. Meaning, if it's crap code with embarrassing bugs then that goes on your EOY perf review. Lots of parallel agents can't solve that fundamental bottleneck.

>This is clearly going to develop the same problem Beads has. I've used it. I'm in stage 7. Beads is a good idea with a bad implementation. It's not a designed product in the sense we are used to, it's more like a stream of consciousness converted directly into code. There are many features that overlap significantly, strange bugs, and the docs are also AI generated so have fun reading them. It's a program that isn't only vibe coded, it was vibe designed too.

Yeah this describes my feeling on beads too. I actually really like the idea - a lightweight task/issue tracker integrated with a coding agent does seem more useful than a pile of markdown todos/plans/etc. But it just doesnt work that well. Its really buggy and the bugs seem to confuse the agent since it was given instructions to do things a certain way that dont work consistently.

I tried using beads. There kept being merge conflicts and the agent just kept one or the other changes instead of merging it intelligently, killing any work I did on making tasks or resolving others. Still haven't seen how beads solves this problem... and it's also an unnecessary one. This should be a separate piece of it that doesn't rely on agent not funging up the merge.

How long until Atlassian makes "JIRA for Agents" where all your tasks and updates and memory aren't stored in Git (so no merge conflicts) but are still centralized and shareable between all your agents/devs/teams..

> Course, I’ve never looked at Beads either, and it’s 225k lines of Go code that tens of thousands of people are using every day. I just created it in October. If that makes you uncomfortable, get out now.

You might like linear-beads[1] better. It's a simpler and less invasive version of beads I made to solve some of the unusual design choices. It can also (optionally) use linear as the storage backend for the agent's tasks, which has the excellent side effect that you as a human can actually see what the agent is working on and direct the agent from within linear.

Despite it's quirks I think beads is going to go down as one of the first pieces of software that got some adoption where the end user is an agent

Linear is great, it's what JIRA should've been. Basically task management for people who don't want to deal with task management. It's also full featured, fast (they were famously one of the earlier apps to use a local-first sync-engine style architecture), and keyboard-centric.

Definitely suitable for hobby projects, but can also scale to large teams and massive codebases.

It unlocks a (still) hidden multiagent orchestration function in Claude code. The person making it unminified the code and figured out how to unlock it.

I find it quite well done - I started a orchestrator project a few days ago and scrapped it because it'll be fully integrated soon it seems.

Why can't you use an issue tracker that is built into the git control, like forgejo? It feels like it would be easy to use this with an API key, out or direct database access (I'm doing both with agents). If you self host, you've got a very standard and reliable issue tracker. Why does beads need to exist? What can't an agent do with that setup I've described above?

I believe the idea is that it's for managing many fine-grained todo's to keep the agents on track. When multiple code agents are working at the same time and when there's a merge conflict, the code agents can do the merges, too.

But yeah, I'm only running one code agent at a time, so that's not a problem I have. I should probably start with just a todo list as plain text.

I am wondering if it would be a viable strategy to vibe code almost "in reverse" - take a giant ball of slop such as beads, and use agents to strip away feature after feature until you are left with only exactly what you need, streamlined to your exact workflow. Maybe it'd be faster to just start from scratch, but it might be an interesting experiment. Most of my struggles with using beads so far have come from being off the #1 use case of too many of its features, and having to slog through too much documentation to know what to actually use.