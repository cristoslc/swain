---
source-id: "mountain-goat-agile-critical-path"
title: "The Critical Path on Agile Projects - Mountain Goat Software"
type: web
url: "https://www.mountaingoatsoftware.com/blog/the-critical-path-on-agile-projects"
fetched: 2026-03-22T00:00:00Z
hash: "c3f5d27648a824b5c508a789b69da9289f6582b2f2a86543d71f6a8324504d8f"
---

# The Critical Path on Agile Projects

**Author:** Mike Cohn (founding member of Agile Alliance and Scrum Alliance)

On a traditional, sequential process an important part of the project manager's job is identifying the project's critical path. The critical path is the sequence of activities that will take the longest to complete and that, therefore, determines the overall length of the project.

Because agile projects are split into a sequence of iterations this question must be answered two ways:

1. What is the critical path within an iteration?
2. What is the critical path within a project?

## Within an iteration

When Cohn first started doing Scrum projects, he worried about the critical path — it was part of his job as a manager. He feared the team wouldn't see the critical path without his guidance.

After two years of worrying, he came to the realization that **the team would always be smarter than him**. In those years (and the nine since), he has yet to work on an iteration where they neared the end and realized they mathematically had capacity but couldn't finish because of sequential dependencies.

**Conclusion on iteration critical path:**
- It is easy to see because iterations are so short (typically 2-4 weeks)
- It does need to be considered but informally — it happens naturally during iteration planning and daily standups
- Don't worry about it. Team members will naturally figure it out.

## Across the project

For the project-level critical path, Cohn recommends **rolling lookahead planning**: teams conclude their iteration planning by taking a five-minute look ahead at the next 1-3 iterations. This high-level forecast helps identify dependencies between teams and avoids being surprised by a long critical path.

On very complex projects, Cohn wouldn't oppose drawing a network diagram to see relationships among 3-6 months of features (ideally user stories). However, **before spending time on that, he would try to write mostly independent product backlog items**. If a project's backlog items are independent and can be developed in any sequence, then critical path issues disappear.

## Key insight for agent-native contexts

The core takeaway: **short iterations make critical path analysis within iterations unnecessary** because teams naturally see and manage dependencies. The project-level critical path matters more but can be mitigated by writing independent work items and doing lightweight lookahead planning.

This maps directly to swain's context: within a SPEC's implementation plan (short, focused work), critical path analysis is likely overkill. Across SPECs within an EPIC or across artifacts, it could add value — especially for stakeholder communication about what gates overall progress.
