---
source-id: powell-design-dev-drift
type: web
url: https://www.sebastienpowell.com/blog/solving-the-design-development-drift
fetched: 2026-03-19
---

# Solving the Design-Development Drift

Source: Sebastien Powell (2025)

## Core Problem

Two sources of truth: a Figma design library and a component library in code. These need to be kept aligned, or consistency breaks down.

## Key Question

Should components be code-first or design-first?

- Converting design to code is manual and lengthy (edge cases, accessibility, composability, architecture integration)
- Converting code to design is increasingly automated (story.to.design, Anima pull components from Storybook into Figma)

## Recommended Approach: Code-First

1. **Design tokens** — centralized definition, consumed by both Figma and code (via Tokens Studio or Specify)
2. **Components** — code is canonical source of truth; Storybook stories sync to Figma via plugins
3. **Workflow** — designers can experiment in Figma, but production truth lives in code
4. **Enforcement** — linters (eslint-plugin-tailwind), CODEOWNERS for system-critical components, Chromatic for visual regression testing

## Preventing Regressions

- No two-way sync from Figma to code (designers can override but can't push)
- CODEOWNERS protects core component files
- Chromatic in CI pipeline for visual regression detection

## Relevance to Swain

This is the "application project" case — when there's actual running code. The approach suggests: make code the source of truth, and treat design docs as intent/vision documents that inform code but don't claim to represent current state unless actively verified.
