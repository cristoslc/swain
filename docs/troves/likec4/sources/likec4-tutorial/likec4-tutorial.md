---
source-id: "likec4-tutorial"
title: "LikeC4 Getting Started Tutorial"
type: documentation-site
url: "https://likec4.dev/tutorial/"
fetched: 2026-03-23T00:00:00Z
hash: "--"
---

# LikeC4 Getting Started Tutorial

## Overview

This tutorial teaches architecture modeling using LikeC4, a domain-specific language for creating architecture diagrams. You can follow along using either the online playground or by installing the VSCode extension.

## Step-by-Step Instructions

### 1. Prepare the Specification

Begin by defining element types in your architecture:

```likec4
specification {
  element actor
  element system
}
```

### 2. Create the Model

Add top-level architectural entities:

```likec4
specification {
  element actor
  element system
}

model {
  customer = actor 'Customer'
  saas = system 'Our SaaS'
}
```

### 3. Add a Hierarchy

Introduce nested components within systems:

```likec4
specification {
  element actor
  element system
  element component
}

model {
  customer = actor 'Customer'
  saas = system 'Our SaaS' {
    component ui
    component backend
  }
}
```

### 4. Add Relationships

Create connections between elements using arrows:

```likec4
model {
  customer = actor 'Customer'
  saas = system 'Our SaaS' {
    component ui
    component backend

    ui -> backend
    customer -> ui 'opens in browser'
  }
}
```

### 5. Create First Diagram

Define views using predicates to visualize the model:

```likec4
views {
  view index {
    include *
  }
}
```

The `include *` predicate shows top-level elements and infers relationships from nested structures.

### 6. Add More Views

Create multiple perspectives of your architecture:

```likec4
views {
  view index {
    include *
  }

  view of saas {
    include *
  }
}
```

### 7. Enrich the Model

Add descriptions, styling, and visual properties:

```likec4
model {
  customer = actor 'Customer' {
    description 'The regular customer of the system'
  }

  saas = system 'Our SaaS' {
    component ui 'Frontend' {
      description 'Nextjs application, hosted on Vercel'
      style {
        icon tech:nextjs
        shape browser
      }
    }
    component backend 'Backend Services' {
      description 'Implements business logic and exposes REST API'
    }

    ui -> backend 'fetches via HTTPS'
  }

  customer -> ui 'opens in browser'
}
```

### 8. Handle Model Changes

Modify existing elements by updating properties:

```likec4
model {
  customer = actor 'Customer' {
    description 'Our dear customer'
  }

  customer -> saas 'enjoys our product'
}
```

Changes automatically propagate to all views.

## Key Concepts

**Views as Projections:** Views are filtered representations of your model determined by predicates controlling what to include or exclude.

**Relationship Inference:** Relationships between parent elements are derived from connections between their children.

**Model-Driven Updates:** Modifying the model automatically refreshes all dependent views.

## Resources

- [Interactive playground](https://playground.likec4.dev/w/tutorial/)
- [Complete specification documentation](https://likec4.dev/dsl/specification/)
- [Styling options](https://likec4.dev/dsl/styling/)
