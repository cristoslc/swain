# Gabe Pereyra on X: Building Spectre

**URL:** https://x.com/gabepereyra/status/2041568552256197074
**Date:** April 7, 2026
**Author:** Gabe Pereyra (@gabepereyra)

## Summary
Spectre is Harvey's internal collaborative cloud agent platform designed to move the "local coding agent loop" into the cloud to solve organizational boundary issues (isolation, security, sharing, and integration).

## Key Architectural Primitives

### 1. Durable Runs vs. Ephemeral Workers
- **Durable Run:** The primary object of collaboration. It carries ownership, sharing, history, artifacts, and session references.
- **Ephemeral Workers:** Short-lived processes that execute a slice of work and then terminate.
- **Benefit:** Simplifies failure recovery and allows follow-up work to resume from archived state without needing to "reanimate" a live process.

### 2. Sandboxes as Execution Boundaries
- Workers operate in isolated environments with scoped repository access, specific tool bundles, and constrained credentials.
- They cannot mutate core system state directly; all durable changes go through the control plane.
- **Security:** Prevents the "ambient access" problem of desktop-first agents where an agent inherits the engineer's entire machine state.

### 3. The Harness
- The harness is the "system" that wraps the model-tool loop.
- Responsible for: context assembly, provider adaptation, progress representation, cost accounting, and state terminal conditions.
- **Insight:** The harness is the actual product when durability, observability, and safety are required in an enterprise setting.

### 4. Collaboration Surfaces
- The prompt box is not the primary interface; surfaces include Slack, web run pages, and PRs.
- All surfaces point to the same durable run, ensuring a single source of truth and avoiding fragmented private sessions.

### 5. Scheduled Runs
- Automation (cleanup, test gen, dependency checks) uses the same runtime as interactive work, making background tasks visible and reviewable.

## Organizational Impact
- **From Desktop to Cloud:** Shifts the center of gravity to ensure reproducible permissions, constrained egress, and durable audits.
- **Cross-functional Collaboration:** Allows PMs and designers to participate in agent runs without needing a terminal.
- **Application to Legal:** The analogies from Spectre (repos $\rightarrow$ matters, PRs $\rightarrow$ review workflows, sandboxes $\rightarrow$ ethical walls) inform Harvey's core product design for the legal industry.
