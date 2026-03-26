---
source-id: "likec4-react"
title: "LikeC4 React Components Documentation"
type: documentation-site
url: "https://likec4.dev/tooling/react/"
fetched: 2026-03-23T00:00:00Z
hash: "--"
---

# LikeC4 React Components

## Installation

```bash
npm i @likec4/core @likec4/diagram
```

## Core Components

### LikeC4ModelProvider

Wraps diagram components and provides the layouted model instance.

**Model preparation methods:**

1. **CLI code generation:** `likec4 codegen model --outfile ./likec4-model.ts`
2. **From source files:** `LikeC4.fromWorkspace('/path')`
3. **Model Builder:** `Builder.specification({...}).model(...).views(...).toLikeC4Model()`

### LikeC4View

Foundational component for rendering diagrams:

```jsx
<LikeC4ModelProvider model={likec4model}>
  <LikeC4View
    viewId="index1"
    onNodeClick={(nodeId) => console.log(nodeId)}
  />
</LikeC4ModelProvider>
```

### ReactLikeC4

Advanced component with greater control:

```jsx
<ReactLikeC4
  viewId={viewId}
  pannable
  zoomable={false}
  keepAspectRatio
  showNavigationButtons
  enableDynamicViewWalkthrough={false}
  enableElementDetails
  enableRelationshipDetails
  showDiagramTitle={false}
  onNavigateTo={setViewId}
  onNodeClick={(nodeId) => console.log(nodeId)}
/>
```

## Available Hooks

- `useLikeC4Model` — access the full model
- `useLikeC4Specification` — access specification data
- `useLikeC4ViewModel` — access a specific view's model
- `useEnabledFeatures`, `useCurrentViewId`, `useXYFlow`, `useDiagram`, `useDiagramContext`

## Custom Node Renderers

Override default rendering with primitive components:

```jsx
import {
  ElementActions, elementNode, ElementNodeContainer,
  ElementShape, ElementTitle
} from '@likec4/diagram/custom'
```

## Styling

- Bundled: `@import '@likec4/diagram/styles.css'`
- With Mantine: `@import "@likec4/diagram/styles-min.css"`
- PandaCSS integration via `@likec4/styles/preset`
