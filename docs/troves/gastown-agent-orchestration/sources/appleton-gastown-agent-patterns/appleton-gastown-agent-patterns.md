---
source-id: "appleton-gastown-agent-patterns"
title: "Gas Town's Agent Patterns, Design Bottlenecks, and Vibecoding at Scale"
type: web
url: "https://maggieappleton.com/gastown"
fetched: 2026-04-11T23:32:00Z
hash: "204b78278a4638a2af5fd62e57eee5c2330582d1adefff8ee15714e8ac0392ad"
---

# Gas Town's Agent Patterns, Design Bottlenecks, and Vibecoding at Scale

*By Maggie Appleton — maggieappleton.com*

On agent orchestration patterns, why design and critical thinking are the new bottlenecks, and whether we should let go of looking at code.

**Topics:** Artificial Intelligence, Critical Thinking, Design, Language Models, Web Development

**Planted:** January 2026

---

A few weeks ago [Steve Yegge](https://en.wikipedia.org/wiki/Steve_Yegge) published an elaborate [manifesto and guide](https://steve-yegge.medium.com/welcome-to-gas-town-4f25ee16dd04) to Gas Town, his Mad-Max-Slow-Horses-Waterworld-etc-themed agent orchestrator that runs dozens of coding agents simultaneously in a metaphorical town of automated activity. Gas Town is entirely vibecoded, hastily designed with off-the-cuff solutions, and inefficiently burning through thousands of dollars a month in API costs.

This doesn't sound promising, but it's lit divisive debates and sparks of change across the software engineering community. A small hype machine has formed around it. There's somehow already a [$GAS](https://bags.fm/7pskt3A1Zsjhngazam7vHWjWHnfgiRump916Xj7ABAGS) [meme coin](https://en.wikipedia.org/wiki/Meme_coin) doing over $400k in earnings.

We should take Yegge's creation seriously not because it's a serious, working tool for today's developers (it isn't). But because it's a good piece of speculative design fiction that asks provocative questions and reveals the shape of constraints we'll face as agentic coding systems mature and grow.

> "Design fiction" or "speculative design" is a branch of design where you create things (objects, prototypes, sketches) from a plausible near future. Not to predict what's going to happen, but to provoke questions and start conversations about what *could* happen.

Yegge deserves praise for exercising agency and taking a swing at a system like this, despite the inefficiencies and chaos of this iteration. And then running a public tour of his shitty, quarter-built plane while it's mid-flight.

## 1. Design and planning becomes the bottleneck when agents write all the code

When you have a fat stack of agents churning through code tasks, development time is no longer the bottleneck. Yegge says "Gas Town churns through implementation plans so quickly that you have to do a LOT of design and planning to keep the engine fed." Design becomes the limiting factor: imagining what you want to create and then figuring out all the gnarly [little details](http://johnsalvatier.org/blog/2017/reality-has-a-surprising-amount-of-detail) required to make your imagination into reality.

The friction is always the design: how should we architect this? What should this feel like? How should this look? Is that transition subtle enough? How composable should this be? Is this the right metaphor?

When it's not the design, it's the product strategy and planning: What are the highest priority features to tackle? Which piece of this should we build first? When do we need to make that decision? What's the next logical, incremental step we need to make progress here?

These are the kind of decisions that agents cannot make for you. They require your human context, taste, preferences, and vision.

Gas Town seems to be halfway into this pitfall. The biggest flaw in Yegge's creation is that it is poorly designed — he absolutely did not design the shape of this system ahead of time, thoughtfully considering which metaphors and primitives would make this effective, efficient, easy to use, and comprehensible.

This Hacker News [comment from qcnguy](https://news.ycombinator.com/item?id=46463757) describes the problem well:

> "Beads is a good idea with a bad implementation. It's not a designed product in the sense we are used to, it's more like **a stream of consciousness converted directly into code. It's a program that isn't only vibe coded, it was vibe designed too.**"
>
> "Gas Town is clearly the same thing multiplied by ten thousand. **The number of overlapping and ad hoc concepts in this design is overwhelming.** Steve is ahead of his time but we aren't going to end up using this stuff. Instead a few of the core insights will get incorporated into other agents in a simpler but no less effective way."

This feels like one of the most critical, emerging footguns of liberally hands-off agentic development. You can move so fast you never stop to think. It is so easy to prompt, you don't fully consider what you're building at each step of the process. It is only once you are hip-deep in poor architectural decisions, inscrutable bugs, and a fuzzy memory of what you set out to do, do you realise you have burned a billion tokens in exchange for a pile of hot trash.

## 2. Buried in the chaos are sketches of future agent orchestration patterns

While the current amalgamation of polecats, convoys, deacons, molecules, protomolecules, mayors, seances, hooks, beads, witnesses, wisps, rigs, refineries, and dogs is a bunch of undercooked spaghetti, Yegge's patterns *roughly* sketch out some useful conceptual shapes for future agentic systems.

### Agents have specialised roles with hierarchical supervision

Every agent in Gas Town has a permanent, specialised role. When an agent spins up a new session, it knows who it is and what job it needs to do:

- **The Mayor** is the human concierge: the main agent you talk to. It talks to all the other agents for you, kicking off work, receiving notifications when things finish, and managing the flow of production.
- **Polecats** are temporary grunt workers. They complete single, isolated tasks, then disappear after submitting their work to be merged.
- **The Witness** supervises the Polecats and helps them get unstuck. Its job is to solve problems and nudge the proletariat workers along.
- **The Refinery** manages the merge queue into the main branch. It evaluates each piece of work waiting to be merged, resolving conflicts in the process. It can creatively "re-imagine" implementations if merge conflicts get too hairy.

Giving each agent a single job means you can prompt them more precisely, limit what they're allowed to touch, and run lots of them at once without them stepping on each other's toes.

There's also a clear chain of command between these agents. You talk to the Mayor, who coordinates work across the system. The Mayor never writes code. It talks to you, then creates work tasks and assigns them to workers. A set of system supervisors called the Witness, the Deacon, and "Boot the Dog" intermittently nudge the grunt workers and each other to check everyone is doing their work.

Gas Town's hierarchical approach solves both a coordination and attention problem. Without it, you are the one assigning tasks to dozens of individual agents, checking who's stuck, who's idle, and who's waiting on work from someone else. With the Mayor as your single interface, that overhead disappears.

There's a lot of opportunity to diversify the cast of characters and make more use of [specialist subagents](https://code.claude.com/docs/en/sub-agents). The agents in Gas Town are all generalist workers in the software development pipeline. But we could add in any kind of specialist: a dev ops expert, a product manager, a front-end debugger, an accessibility checker, a documentation writer.

### Agent roles and tasks persist, sessions are ephemeral

One of the major limitations of current coding agents is running out of context. Before you even hit the limits of a context window, [context rot](https://research.trychroma.com/context-rot) degrades the output enough that it's not worth keeping. We constantly have to compact or start fresh sessions.

Gas Town's solution: make each agent session disposable by design. It stores the important information — agent identities and tasks — in Git, then liberally kills off sessions and spins up fresh ones when needed. New sessions are told their identity and currently assigned work, and continue on where the last one left off. Gas Town also lets new sessions ask their predecessors what happened through "seancing": resuming the last session as a separate instance in order to let the new agent ask questions about unfinished work.

This saving and recalling is all done through Gas Town's "Beads" system. Beads are tiny, trackable units of work — like issues in an issue tracker — stored as JSON in Git alongside your code. Each bead has an ID, description, status, and assignee. Agent identities are also stored as beads, giving each worker a persistent address that survives session crashes.

Yegge didn't invent this pattern of tracking atomic tasks outside agent memory in something structured like JSON. Anthropic described the same approach in their research on [effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents), just published in November 2025.

### Feeding agents continuous streams of work

The whole promise of an orchestration system like Gas Town is it's a perpetual motion machine. You give high-level orders to the mayor, and then a zoo of agents kicks off to break it down into tasks, assign them, execute them, check for bugs, fix the bugs, review the code, and merge it in.

Each worker agent has its own queue of assigned work and a "hook" pointing to the current thing they should be doing. The minute they finish a task, the next one jumps to the front of the queue. The mayor fills up these queues — breaking down large features into atomic tasks and assigning them to available workers. In theory, the workers are never idle or lacking tasks.

This principle of "workers always do their work" is better in theory than practice. It turns out to be slightly difficult because current models are trained as helpful assistants who wait politely for human instructions. They're not used to checking a task queue and independently getting on with things.

Gas Town's patchwork solution is aggressive prompting and constant nudging. Supervisor agents spend their time poking workers to see if anyone's stalled out or run dry on work. These periodic nudges move through the agent hierarchy like a heartbeat keeping everything moving. A decent band-aid for v1, but more serious efforts at agent orchestration will need reliable ways to keep agents on task.

### Merge queues and agent-managed conflicts

When you have a bunch of agents all working in parallel, you're going to run into merge conflicts. Each agent is off on its own branch, and by the time it finishes its task, the main branch might look completely different.

Gas Town has a dedicated merge agent — the Refinery — that works through the merge queue one change at a time. It resolves conflicts and gets changes into main. When things get really tangled, it can creatively "re-imagine" the changes: re-doing the work to fit the new codebase. Or escalate to a human if needed.

But there's another way to sidestep merge conflict nightmares that Gas Town doesn't have: ditch PRs for [stacked diffs](https://newsletter.pragmaticengineer.com/p/stacked-diffs). The traditional git workflow puts each feature on its own branch for days or weeks, accumulating commits, then getting merged back as one chunky PR.

Stacked diffs break work into small, atomic changes that each get reviewed and merged on their own. This fits how agents naturally work. They're already producing tiny, focused changes rather than sprawling multi-day branches. [Cursor](https://cursor.com/)'s recent acquisition of [Graphite](https://graphite.com/), a tool built specifically for stacked diff workflows, suggests others see this opportunity.

## 3. The price is extremely high, but so is the (potential) value

Yegge describes Gas Town as "expensive as hell… you won't like Gas Town if you ever have to think, even for a moment, about where money comes from." He's on his second Claude account to get around Anthropic's spending limits.

Conservatively assuming $2,000-$5,000 USD per month. The current cost is almost certainly artificially inflated by system inefficiency — work gets lost, bugs get fixed numerous times, designs go missing and need redoing. As models improve and orchestration patterns mature, cost should drop while output quality rises.

Even at $1-3k/month for a mature version, that's reasonable against an average US senior developer salary of $120,000 USD. If Gas Town could speed up a senior developer's work by 2-3x or more, it would easily be worth 10-30% of their salary.

## 4. Yegge never looks at code. When should we stop looking too?

Yegge is leaning into the true definition of [vibecoding](https://x.com/karpathy/status/1886192184808149383?lang=en): "It is 100% vibecoded. I've never seen the code, and I never care to." Not looking at code *at all* is a very bold proposition.

"Should developers still look at code?" will become one of the most divisive and heated debates over the coming years. Both the purist AI-sceptic camp and the agentic maximalist camp mistake a contextual judgement for a personality trait and firm moral position.

A more productive debate: how *close* should the code be in agentic software development tools? How easy should it be to access? How often do we expect developers to edit it by hand?

Interfaces like [Claude Code](https://code.claude.com/docs/en/overview), [Cursor](https://cursor.com/), and [Conductor](https://docs.conductor.build/) do not put code front and centre. The agent is your first and primary interface. This design choice assumes it is easier to ask an agent to make the change for you, than it is to type the syntax yourself.

The right distance depends on what you're building, who you're building with, and what happens when things go wrong:

### Domain and programming language

Front-end versus backend makes a huge difference. Language is a poor medium for describing aesthetic feelings — you always need to touch the CSS. Model competence also varies wildly by language; prompting React and Tailwind gives much better results than Rust or Haskell, where models still regularly choke on borrow checkers and type systems.

### Access to feedback loops and definitions of success

The more agents can validate their own work, the better the results. If agents can run tests, open browsers, take screenshots, and click around, they can spot their mistakes. Tools like the [Ralph Wiggum plugin](https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum) lean into this — it loops until tests pass or some specific condition is validated. This doesn't work for less clearly defined work though.

### Risk tolerance for shit going wrong

Stakes matter. If an agent breaks images on your personal blog, you'll recover. But healthcare systems, banking apps — consequences scale up fast. Corporate software has compliance and regulatory sign-off people who need to see, understand, and verify the code.

> "Gas Town sounds fun if you are accountable to nobody: not for code quality, design coherence or inferencing costs. The rest of us are accountable for at least the first two and even in corporate scenarios where there is a blank check for tokens, that can't last. So the bottleneck is going to be how fast humans can review code and agree to take responsibility for it." — qcnguy, Hacker News

### Greenfield vs. brownfield projects

Starting fresh (greenfield), you can let agents make architectural decisions — the cost of mistakes is low. But in an existing codebase (brownfield) with years of accumulated conventions, implicit patterns, and code that exists for reasons nobody remembers, agents need much tighter supervision.

### Number of collaborators

Solo, you can YOLO. With more than a handful of people, you need to agree on coding standards and agent rules. The pace of change when everyone's using agents can be overwhelming. Team coordination can fall apart when everyone's agents start moving too fast.

### Your experience level

More senior developers can prompt better, debug better, and set up more stringent preferences earned through decades of seeing what can go wrong. Newer developers don't have that catalogue of failures yet and are much more likely to prompt their own personal house of cards.

---

Appleton is currently in the code-must-be-close camp for most serious professional work. She expects to shift to code-at-a-distance over the next year or two as harnesses and tools mature. The infrastructure matters far more than model improvements: validation loops, tests, and specialised subagents focused on security, debugging, and code quality are what will make code-at-a-distance feasible.

Gas Town itself is not "it." It's not going to evolve into the thing everyone uses in 2027. It's a provocative piece of speculative design, not a system many people will use in earnest. But the problems it's wrestling with and the patterns it has sketched out will unquestionably show up in the next generation of development tools.

As the pace of software development speeds up, we'll feel the pressure intensify in other parts of the pipeline: thoughtful design, critical thinking, user research, planning and coordination within teams, deciding what to build, and whether it's been built well. The most valuable tools in this new world won't be the ones that generate the most code fastest. They'll be the ones that help us think more clearly, plan more carefully, and keep the quality bar high while everything accelerates.
