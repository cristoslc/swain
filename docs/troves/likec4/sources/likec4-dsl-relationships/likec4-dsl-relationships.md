---
source-id: "likec4-dsl-relationships"
title: "LikeC4 Relationships Guide"
type: documentation-site
url: "https://likec4.dev/dsl/relationships/"
fetched: 2026-03-23T00:00:00Z
hash: "--"
---

# LikeC4 Relationships Guide

## Overview

Relationships describe the connections, data flows and interactions within your model.

## Defining Relationships

Relationships use the `->` operator to connect elements:

```likec4
model {
  customer = actor 'Customer'
  cloud = service 'Cloud'
  customer -> cloud
}
```

### Nested Relationships

Relationships can be nested within parent elements:

```likec4
model {
  service cloud {
    component backend
    component frontend
    frontend -> backend
    customer -> frontend
  }
}
```

### Sourceless Relationships

Nested relationships can omit their source, automatically using the parent element:

```likec4
model {
  actor customer {
    -> frontend  // same as customer -> frontend
  }
  service cloud {
    component frontend {
      -> backend  // same as frontend -> backend
    }
  }
}
```

Sourceless relationships must be nested; they cannot exist at the model level.

## Relationship Kinds

Define semantic relationship types in the specification section:

```likec4
specification {
  element system
  relationship async
  relationship uses
}

model {
  system1 -[async]-> system2
  system1 .uses system2
}
```

Kinds enable richer semantics (REST, gRPC, GraphQL, Sync/Async) and customized styling.

## Properties

### Title

```likec4
model {
  customer -> frontend 'opens in browser'
}
```

### Description (supports markdown)

```likec4
model {
  customer -> frontend 'opens in browser' {
    description '''
      **Customer** opens the frontend in browser
    '''
  }
}
```

### Technology

```likec4
model {
  customer -> frontend 'opens in browser' {
    technology 'HTTPS'
  }
}
```

### Tags

```likec4
model {
  frontend -> backend 'requests data' #graphql #team1
}
```

### Links

```likec4
model {
  customer -> frontend 'opens in browser' {
    link https://any-external-link.com
    link https://github.com/likec4/likec4 'Repository'
  }
}
```

### Navigate To

Links to dynamic views for zoomed detail:

```likec4
model {
  webApp -> backend.api {
    title 'requests data for the dashboard'
    navigateTo dashboard-request-flow
  }
}
```

## Metadata

Relationships support metadata:

```likec4
model {
  customer -> frontend 'opens in browser' {
    metadata {
      prop1 'value1'
      prop2 '{...json...}'
    }
  }
}
```
