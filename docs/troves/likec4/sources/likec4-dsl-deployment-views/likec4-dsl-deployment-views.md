---
source-id: "likec4-dsl-deployment-views"
title: "LikeC4 Deployment Views"
type: documentation-site
url: "https://likec4.dev/dsl/deployment/views/"
fetched: 2026-03-23T00:00:00Z
hash: "--"
---

# LikeC4 Deployment Views

## Overview

Deployment views enable visualization of deployment models using the same predicate-based approach as standard model views.

## View Definition

```likec4
views {
  deployment view index {
    title 'Production Deployment'
    link https://likec4.dev
    include prod.**
  }
}
```

## Supported Syntax

```likec4
deployment view prod {
  include *                                    // works
  include * where tag is #next                 // works
  include * -> *                               // works
  include * -> * where tag is #next            // works
  include * -> * where source.tag is #next     // works
}
```

### Limitations

Currently unsupported:
- `with` expressions for styling
- Shared styles and predicates
- Relationship browser and element details popups (operates only on logical model)

## Filtering Rules

**Tag Resolution:**
- Deployment instance tags combine model tags and deployment model tags
- Child element tags come from model definitions only
- Deployment node tags come from deployment model only
- Tags do not inherit from parent nodes

**Kind Resolution:**
- Deployment instance kind references the model element's kind
- Child element kind comes from the child definition
- Deployment node kind comes from the node definition
