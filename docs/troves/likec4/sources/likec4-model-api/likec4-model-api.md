---
source-id: "likec4-model-api"
title: "LikeC4 Model API Documentation"
type: documentation-site
url: "https://likec4.dev/tooling/model-api/"
fetched: 2026-03-23T00:00:00Z
hash: "--"
---

# LikeC4 Model API

## Overview

Programmatic access to query and traverse your architecture model. The API allows querying and traversal of the model from DSL, but not modification or creation.

## Installation

```bash
npm i likec4
```

## Initialization

### From Workspace

```javascript
import { LikeC4 } from 'likec4'
const likec4 = await LikeC4.fromWorkspace('/path/to/workspace')
```

Options: `printErrors`, `throwIfInvalid`, `logger`, `graphviz` (wasm/binary), `watch`, `mcp` (false/stdio/{port}).

### From Source String

```javascript
const likec4 = await LikeC4.fromSource(`
  specification { element system }
  model { cloud = system 'System' }
  views { view index { include * } }
`)
```

## Model Types

- **LikeC4Model.Computed** — computed views, synchronous, fast for traversal
- **LikeC4Model.Layouted** — extends computed with layout data (dimensions, positions)

## Core API

```typescript
interface LikeC4Model {
  roots(): Element[]
  elements(): Element[]
  element(id: Fqn): Element
  relationships(): Relationship[]
  relationship(id: RelationID): Relationship
  views(): ReadonlyArray<LikeC4ViewModel>
  view(viewId: ViewID): LikeC4ViewModel
  parent(element): Element | null
  children(element): Element[]
  siblings(element): Element[]
  ancestors(element): Element[]
  descendants(element): Element[]
  incoming(element, filter?): Relationship[]
  incomers(element, filter?): Element[]
  outgoing(element, filter?): Relationship[]
  outgoers(element, filter?): Element[]
}
```

## Querying

```javascript
const model = likec4.computedModel()

// Elements by kind
model.elementsOfKind('microservice')

// Complex filtering
model.elementsWhere({
  and: [
    { kind: 'kind1' },
    { or: [{ tag: 'tag2' }, { tag: { neq: 'tag3' } }] }
  ]
})

// Traverse relationships
model.element('cloud.backend.api')
  .incoming()
  .filter(r => r.isTagged('http'))
  .map(r => r.source)

// Views containing an element
model.element('cloud.backend.api').views()
```

## Model Builder

Type-safe builder from `@likec4/core/builder`:

```javascript
import { Builder } from "@likec4/core/builder"

const m = Builder
  .specification({
    elements: {
      actor: { style: { shape: 'person' } },
      system: {},
      component: {}
    },
    relationships: { likes: {} },
    tags: ['tag1', 'tag2']
  })
  .model(({ actor, system, component, rel }, _) =>
    _(
      actor('alice'),
      system('cloud').with(
        component('backend').with(component('api'), component('db'))
      )
    )
  )
  .views(({ view, $include }, _) =>
    _(view('index', 'Index').with($include('cloud.*')))
  )
  .toLikeC4Model()
```

Supports both chain style and composition style. Can be mixed based on preference.

## Deployment Model API

```javascript
const model = likec4.computedModel()
const deployment = model.deployment

for (const instance of deployment.instancesOf('cloud.backend.api')) {
  // Process instance
}
```
