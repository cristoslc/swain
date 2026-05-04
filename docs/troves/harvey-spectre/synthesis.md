# Synthesis: Harvey Spectre

## Key Findings
Harvey's Spectre platform shifts the agentic loop from the local desktop to a cloud-native runtime. This transition is driven by the need for organizational legibility, security, and collaboration in an enterprise setting.

## Core Architectural Themes

### 1. State Management: Durable Runs vs. Ephemeral Workers
The system decouples the *record of work* (the durable run) from the *execution agent* (the ephemeral worker). 
- **Result:** High availability, resumability, and consistent collaboration surfaces across different interfaces (Slack, Web, PRs).

### 2. Security: Explicit Boundaries
By utilizing sandboxes as the execution boundary, Spectre avoids the "ambient access" patterns of local agents.
- **Result:** Reproducible permissions and constrained egress, which are critical for enterprise audit and compliance.

### 3. The "Harness" as the Product
The "harness" transforms a raw model-tool loop into a production system. It manages context engineering, state terminal conditions, and cost accounting.
- **Result:** The infrastructure surrounding the model becomes the primary value driver for enterprise reliability.

### 4. Expansion of Collaboration
Moving the agent runtime to the cloud enables non-engineering personas (PMs, Designers) to interact with agent work via shared surfaces, removing the terminal as a bottleneck.

## Gaps & Open Questions
- The specific technical implementation of "provider adapters" is not detailed.
- The exact mechanism for "archived session state" restoration is mentioned but not explained.
