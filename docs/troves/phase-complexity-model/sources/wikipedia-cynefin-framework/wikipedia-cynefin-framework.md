---
source-id: "wikipedia-cynefin-framework"
title: "Cynefin framework — Wikipedia"
type: web
url: "https://en.wikipedia.org/wiki/Cynefin_framework"
fetched: 2026-03-23T12:00:00Z
hash: "2f10740035d0cc20df241b5ff6e1f3ed353a7a800cb73e57240a2a38670887b4"
---

# Cynefin Framework — Wikipedia

The Cynefin framework is a conceptual framework used to aid decision-making. Created in 1999 by Dave Snowden when he worked for IBM Global Services. It has been described as a "sense-making device."

## Five Domains

### Clear (Simple)
The relationship between cause and effect is obvious. The approach is to Sense–Categorize–Respond. Apply best practices. Fixed constraints — actions in set order.

### Complicated
The relationship between cause and effect requires analysis or investigation. The approach is Sense–Analyze–Respond. Apply good practices (not "best" — multiple valid approaches exist). Governing constraints — rules and policies guide but don't dictate.

### Complex
The relationship between cause and effect can only be perceived in retrospect. The approach is Probe–Sense–Respond. Emergent practices. Enabling constraints — allow function without controlling. Experiments, safe-to-fail probes.

### Chaotic
No relationship between cause and effect at systems level. The approach is Act–Sense–Respond. Novel practices. No effective constraints. Must act first to stabilize, then sense where you are.

### Confusion/Disorder
The state of not knowing which domain you are in. The primary danger is that people interpret the situation through their preferred domain. Must break down the situation and assign each element to one of the other four domains.

## Key Distinctions for Automation

The constraint types per domain are critical for determining what kind of automation is appropriate:

- **Fixed constraints** (Clear): Fully automatable — known steps, known order
- **Governing constraints** (Complicated): Partially automatable — rules can be encoded, expert judgment needed at decision points
- **Enabling constraints** (Complex): Automate scaffolding (experiments, feedback loops) but not decisions
- **No constraints** (Chaotic): Automation limited to alerting and stabilization

## Software Development Applications

A 2015 ACM paper ("Exploring the Use of the Cynefin Framework to Inform Software Development Approach Decisions") validates using Cynefin to select software development methodologies based on situational context.

A 2018 paper (Ilieva, Anguelov, Nikolov) applied Cynefin specifically to AI bot decision-making, examining how agents should adapt their behavior based on the complexity domain they're operating in.

Source: Snowden, D. J., & Boone, M. E. 2007. "A Leader's Framework for Decision Making." Harvard Business Review.
