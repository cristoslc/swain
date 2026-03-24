---
source-id: "likec4-dsl-model"
title: "LikeC4 Model Syntax Guide"
type: documentation-site
url: "https://likec4.dev/dsl/model/"
fetched: 2026-03-23T00:00:00Z
hash: "--"
---

# LikeC4 Model Syntax Guide

## Element Basics

Elements form the foundation of LikeC4 architecture models. Each requires a `kind` and `name` (identifier):

```likec4
specification {
  element actor
  element service
}

model {
  actor customer
  service cloud
  cloud = service
}
```

**Valid Name Rules:**
- Letters, digits, hyphens, underscores allowed
- Cannot start with digits or contain periods
- Examples: `api`, `Api2`, `_api` (valid); `1api`, `a.pi` (invalid)

## Element Properties

### Title

```likec4
model {
  saas = softwareSystem 'SaaS'

  saas = softwareSystem {
    title 'SaaS'
    title: 'SaaS'  // colon optional
  }
}
```

### Description & Summary

```likec4
model {
  saas = softwareSystem 'SaaS' 'Provides services to customers'

  saas = softwareSystem {
    title 'SaaS'
    summary 'Provides services to customers'
    description 'Detailed description...'
  }
}
```

Summary displays on diagrams; description appears in detail dialogs. If only one is provided, it serves both purposes.

### Technology

```likec4
model {
  api = service {
    technology 'REST'
  }

  saas = softwareSystem 'SaaS' 'Summary' 'Technology'
}
```

Auto-derived: If an element uses bundled icons (`aws:`, `azure:`, `gcp:`, `tech:`) without explicit technology, LikeC4 automatically generates labels (e.g., `tech:apache-flink` -> "Apache Flink").

### Tags

Tags must precede other properties:

```likec4
model {
  appV1 = application 'App v1' {
    #deprecated
    description 'Old version'
  }

  appV2 = application {
    #next, #serverless
    #team2
    title 'App v2'
  }
}
```

### Links

Elements support multiple links with optional labels:

```likec4
model {
  bastion = application 'Bastion' {
    link https://any-external-link.com
    link https://github.com/likec4/likec4 'Repository'
    link ssh://bastion.internal 'SSH'
    link ../src/index.ts#L1-L10
  }
}
```

### Metadata

Key-value pairs supporting strings, JSON, and YAML:

```likec4
model {
  app = application 'App' {
    metadata {
      prop1 'value1'
      prop2 'yaml: content'
      prop3 '{"json": "content"}'
    }
  }
}
```

Array literals supported:

```likec4
model {
  api = service 'API Gateway' {
    metadata {
      version '3.2.1'
      maintainer 'Platform Team'
      tags ['backend', 'gateway', 'microservice']
      regions ['us-east-1', 'eu-west-1']
      critical true
    }
  }
}
```

Duplicate property names collect values into arrays, preserving definition order.

## Markdown Support

Descriptions and summaries support markdown using triple quotes:

```likec4
model {
  mobile = application {
    title 'Mobile Application'
    description '''
      ### Multi-platform application
      [React Native](https://reactnative.dev)
    '''
  }
}
```

## Hierarchical Structure

Elements function as containers for nested elements:

```likec4
model {
  service service1 {
    component backend {
      component api
    }
    component frontend
  }
}
```

Fully Qualified Names (namespace with parent prefixes):
- `service1`, `service1.backend`, `service1.backend.api`, `service1.frontend`

Constraint: Duplicate names cannot exist within same parent container but can exist in different containers.
