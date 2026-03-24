---
source-id: "likec4-dsl-views-predicates"
title: "LikeC4 View Predicates Reference"
type: documentation-site
url: "https://likec4.dev/dsl/views/predicates/"
fetched: 2026-03-23T00:00:00Z
hash: "--"
---

# LikeC4 View Predicates - Complete Reference

## Overview

Views are not static — they are generated from the model. Changes in the model immediately update views. Two predicate types control visibility: element and relationship predicates.

Views contain elements and connections (relationships). Connections represent merged relationships — both direct between elements and those derived from nested elements.

## Element Predicates

### Basic Syntax

```likec4
view {
  include backend
  include frontend
  include authService
  include messageBroker.*
  include messageBroker.**
  exclude messageBroker.emailsQueue
}
```

**Order is significant:** predicates are applied as defined within the view. Excludes apply only to elements/relationships included earlier.

### Wildcard Patterns

**Children `.*`** — direct children:
```likec4
include cloud.*
// Same as: include cloud.backend, cloud.ui
```

**Descendants `.**`** — descendants with relationships to visible elements:
```likec4
include cloud.**
```

**Expand `._`** — children with relationships only:
```likec4
include cloud._
```

### Element Overrides

```likec4
include cloud.backend with {
  title 'Backend components'
  description '...'
  technology 'Java, Spring'
  icon tech:java
  color amber
  shape browser
  multiple true
}
```

### Custom Navigation

```likec4
view view2 {
  include *
  include cloud.backend with {
    navigateTo view3
  }
}
```

### Filter by Kind or Tag

```likec4
include element.kind != system
exclude element.kind = container
include element.tag != #V2
exclude element.tag = #next
```

## Relationship Predicates

### Directed Relationships

```likec4
include customer -> cloud
include customer -> cloud.*
```

### Any Relationship

```likec4
include customer <-> cloud
```

### Incoming/Outgoing

```likec4
include -> backend     // incoming
include customer ->    // outgoing
include -> cloud.* ->  // in/out
```

### Relationship Customization

```likec4
include
  cloud.* <-> amazon.* with {
    color red
    line solid
  },
  customer -> cloud.* with {
    title 'Customer uses cloud'
    navigateTo dynamicview1
  }
```

## Filter with `where`

```likec4
include cloud.* where kind is microservice

include cloud.*
  where
    kind == microservice and
    tag != #deprecated

include cloud.*
  where
    not (kind is microservice or kind is webapp)
    and tag is not #legacy
    and (tag is #v1 or tag is #v2)
```

### Metadata Filter

```likec4
include cloud.* where metadata.environment is "production"
exclude * where not metadata.version
include * where metadata.critical is true
include * where metadata.regions is "us-east-1"  // array containment
```

## Global Predicate Groups

```likec4
global {
  predicateGroup microservices {
    include cloud.* where kind is microservice
    exclude * where tag is #deprecated
  }
}

views {
  view of newServices {
    include cloud.new.*
    global predicate microservices
  }
}
```

## Groups

```likec4
view {
  group 'Service Bus' {
    color amber
    opacity 20%
    border solid
    include messageBroker.*
  }
}
```

Nested groups supported. For element predicates, first group wins. For relationship predicates, last group wins.

## Style Predicates

```likec4
view apiApp of internetBankingSystem.apiApplication {
  include *

  style * {
    color muted
    opacity 10%
  }

  style element.tag = #deprecated {
    color muted
  }
}
```

## Auto-Layout

```likec4
view {
  include *
  autoLayout LeftRight 120 110
}
```

Directions: `TopBottom` (default), `BottomTop`, `LeftRight`, `RightLeft`.

## Rank Constraints

```likec4
view checkoutFlow {
  include *

  rank same {
    cloud.backend.api,
    cloud.backend.billingApi
  }

  rank source {
    customer
  }

  rank sink {
    analytics,
    dataWarehouse
  }
}
```

Allowed values: `same` (default), `min`, `max`, `source`, `sink`.
