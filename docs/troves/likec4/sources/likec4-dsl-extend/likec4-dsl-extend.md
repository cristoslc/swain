---
source-id: "likec4-dsl-extend"
title: "LikeC4 Extend Syntax Guide"
type: documentation-site
url: "https://likec4.dev/dsl/extend/"
fetched: 2026-03-23T00:00:00Z
hash: "--"
---

# LikeC4 Extend Syntax Guide

## Overview

LikeC4 allows enriching your architecture model by extending existing elements and relationships across multiple files. This modular approach keeps landscape files clean while organizing complex internals separately.

## Extending Elements

```likec4
model {
  extend cloud {
    service1 = service 'Service 1'
  }
}
```

**Fully Qualified Names Required:**
```likec4
extend cloud.service2  // correct
extend service2        // error
```

**Scope Inheritance:** Extended elements inherit their parent's scope, allowing references to siblings.

### Adding Properties

```likec4
model {
  extend cloud {
    #additional-tag, #another-tag
    metadata {
      prop1 'value1'
    }
    link ../src/index.ts#L1-L10
  }
}
```

## Metadata Merging Rules

- Identical duplicate values stored as single strings
- Different values for the same key become arrays
- Multiple extensions across files merge properly
- Duplicates are de-duplicated
- Single-value arrays convert back to strings

## Extending Relationships

Relationships identified by source, target, kind (optional), and title (optional):

```likec4
extend frontend -> api "Makes requests" {
  metadata {
    latency_p95 '150ms'
    rate_limit '1000req/s'
  }
}
```

Different relationship kinds are treated as separate relations. Relations without a title and with empty string title are treated identically.

**Limitation:** Extending relationships currently works only for logical models, not deployment model relationships.

## Workspace Organization Example

```
cloud/
  service1.c4
  service2.c4
externals/
  amazon.c4
landscape.c4
specs.c4
```
