---
source-id: "likec4-dsl-dynamic-views"
title: "LikeC4 Dynamic Views Guide"
type: documentation-site
url: "https://likec4.dev/dsl/views/dynamic/"
fetched: 2026-03-23T00:00:00Z
hash: "--"
---

# LikeC4 Dynamic Views: Complete Guide

## Overview

Dynamic views describe specific use-cases or scenarios with particular elements and interactions defined exclusively within the view, without extending the core model.

## Dynamic View Definition

```likec4
dynamic view example {
  title 'Dynamic View Example'
  customer -> web 'opens in browser'
  web -> auth 'updates bearer token if needed'
  web -> api 'POST request'
  api -> auth // title is derived from the model
  api -> api 'process request' // allow self-call

  // reverse direction, as a response
  web <- api 'returns JSON'

  // Include elements not participating in steps
  include cloud, ui, backend
  style cloud {
    color muted
    opacity 0%
  }
}
```

### Continuous Steps

Steps can be chained: `A -> B -> C`, which automatically identifies backward directions. `A -> B -> A` is equivalent to `A -> B; A <- B`.

### Parallel Steps

```likec4
dynamic view parallelexample {
  title 'Dynamic View Parallel Example'
  ui -> api
  parallel {
    api -> cache
    api -> db
  }
  // or using shorthand
  par {
    api -> cache
    api -> db
  }
}
```

Nested parallel blocks are not supported.

### Navigation

Steps can link to other dynamic views:

```likec4
dynamic view level1 {
  title 'Highlevel'
  ui -> api {
    navigateTo moreDetails
  }
}

dynamic view moreDetails {
  title 'Some details'
}
```

### Notes

Markdown-formatted notes add context to steps:

```likec4
dynamic view stepnotes {
  ui -> api {
    notes '''
      **What it does**:
      - requests data using predefined GraphQL queries
      - queries regression on CI
    '''
  }
}
```

## Variants

### Diagram (default)

Displays interactions as a diagram format showing the flow between components.

### Sequence

Classic sequence diagram with vertical actor timelines and horizontal interaction arrows.

**Limitation:** Only supports leaf elements (elements without child elements).

## Actor Ordering

### Custom Ordering

The `include` predicate enforces strict ordering:

```likec4
dynamic view order2 {
  customer -> web -> auth -> web -> api

  // Enforce specific order
  include auth, web, api
}
```

Partially-specified `include` predicates derive remaining order from step definitions.
