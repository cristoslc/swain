# LikeC4 Trove Synthesis

## What LikeC4 Is

LikeC4 is an open-source (MIT), TypeScript-based architecture-as-code tool that provides a custom DSL for modeling software architecture and generating interactive diagrams. It draws from the C4 Model and Structurizr DSL but is more flexible — teams define their own element kinds, relationship types, and visual notation rather than being locked to the standard C4 hierarchy (Person/System/Container/Component).

The tool spans the full pipeline: DSL authoring (with LSP/VSCode support) -> model computation -> Graphviz layout -> interactive React rendering -> static site export.

## Key Architectural Concepts

### DSL Structure

Four top-level blocks:
- **specification** — defines the vocabulary: element kinds, relationship kinds, tags, custom colors
- **model** — declares elements, hierarchy, and relationships using the specified vocabulary
- **views** — creates visual projections of the model using predicate-based include/exclude/where rules
- **global** — shared styles and predicate groups reusable across views

### Three View Types

1. **Static views** — predicate-driven projections of the model (the primary view type)
2. **Dynamic views** — scenario/sequence descriptions with steps, parallel blocks, and notes
3. **Deployment views** — infrastructure-layer visualizations mapping logical elements to deployment nodes via `instanceOf`

### Predicate System

Views are not hand-drawn — they're computed from predicates. The predicate system supports:
- Wildcard expansion (`*`, `.*`, `.**`, `._`)
- Relationship direction (`->`, `<->`, `<-`)
- `where` clauses filtering by kind, tag, and metadata
- `with` overrides for per-view element/relationship customization
- Groups with visual boundaries
- Global predicate groups for reuse
- Rank constraints for layout control

### Extensibility

The `extend` keyword allows splitting models across files with metadata merging rules (duplicates become arrays, arrays merge, single-value arrays simplify to strings). This enables collaborative architecture documentation where different teams own different parts of the model.

## Tooling Ecosystem

### MCP Server (High relevance to swain)

LikeC4 ships an MCP server (`@likec4/mcp`) with 17+ tools for programmatic model querying:
- Element search, read, diff, and batch operations
- Graph traversal (ancestors, descendants, incomers, outgoers)
- Relationship path finding (bounded BFS)
- Tag and metadata querying with boolean logic
- Subgraph summarization

This means an agent can query an architecture model via MCP without parsing the DSL directly.

### Model API (Programmatic)

The `likec4` npm package provides:
- `LikeC4.fromWorkspace()` / `LikeC4.fromSource()` for model loading
- Full traversal API: `elements()`, `relationships()`, `incoming()`, `outgoing()`, `ancestors()`, `descendants()`
- `elementsWhere()` with composable filter predicates
- `Builder` API for programmatic model construction (type-safe, two composition styles)

### CLI

Dev server, static site build, PNG/JSON/DrawIO export, Mermaid/PlantUML/D2/DOT generation, validation, formatting, LSP server.

### React Components

Embeddable diagram components (`LikeC4View`, `ReactLikeC4`) with customizable node renderers, hooks for model access, and PandaCSS integration.

## Relevance to Swain

### Direct applicability: Component Catalog

The architecture conversation summary proposed a component catalog with human-declared intent and source-derived evidence. LikeC4 could serve as the **intent declaration layer**:
- Element kinds map to component types (service, database, queue, etc.)
- Tags map to status markers (#deprecated, #experimental)
- Metadata maps to ownership, SLA, governance
- Relationships map to dependency/data flow declarations
- The `governs` / `touches` relationships from the architecture doc could be modeled as relationship kinds

### Direct applicability: ADR Graph

The proposed ADR relationship model (`governs`, `supersedes`, `conflicts_with`, `instantiated_by`, `touches`) could be expressed as LikeC4 relationship kinds, with ADRs and components as element kinds. The MCP server would then provide the graph query capability the architecture doc called for — without building a custom graph layer.

### Direct applicability: Reconciliation

LikeC4's `validate` command detects layout drift. A similar pattern could detect model drift — where the declared architecture (LikeC4 model) diverges from the actual codebase. This maps directly to the intent/evidence reconciliation concept.

### MCP integration path

Since LikeC4 ships an MCP server, swain could integrate via:
1. Maintain a `.c4` model alongside the artifact tree
2. Configure `@likec4/mcp` as an MCP server for the agent
3. Use MCP tools at planning time to query "what components does this spec touch?" and "what ADRs govern those components?"

This avoids building a custom graph layer — the MCP server IS the graph query API.

## Points of Agreement Across Sources

- Architecture-as-code with a custom DSL is the right abstraction level (not UML, not freeform diagrams)
- Predicate-based view generation (compute views from model, don't hand-draw them) keeps views in sync with model
- The C4 Model's rigid hierarchy should be relaxable — teams need custom element kinds
- MCP is the right integration surface for agent-model interaction

## Gaps

- **No built-in ADR/decision tracking** — LikeC4 models architecture, not decisions. ADRs would need to be modeled as elements or tracked separately.
- **No source code analysis** — LikeC4 is pure declaration. The evidence/derivation layer (scanning source code to detect drift) would need to be built separately.
- **No diff/change tracking over time** — The model is a point-in-time snapshot. Version comparison would rely on git history of `.c4` files.
- **Dynamic view limitations** — Sequence variant only supports leaf elements; nested parallel blocks not supported.
- **Deployment view limitations** — No `with` expressions, no shared styles, no relationship browser.
