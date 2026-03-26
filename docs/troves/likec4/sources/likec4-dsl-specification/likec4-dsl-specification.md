---
source-id: "likec4-dsl-specification"
title: "LikeC4 DSL Specification Guide"
type: documentation-site
url: "https://likec4.dev/dsl/specification/"
fetched: 2026-03-23T00:00:00Z
hash: "--"
---

# LikeC4 DSL Specification Guide

## Overview

The `specification` block defines the notation system for your architecture model, establishing element kinds, relationships, tags, and custom colors.

## Element Kind

Element kinds represent different types of components in your architecture:

```likec4
specification {
  element user
  element cloud
  element system
  element application
  element component
  element controller
  element microservice
  element queue
  element restapi
  element graphqlMutation
  element repository
  element database
  element pgTable
}
```

Element kinds can include properties, descriptions, and styling:

```likec4
specification {
  element queue {
    title 'Kafka'
    description 'Kafka queue'
    technology 'kafka topic'
    notation 'Kafka Topic'
    style {
      shape queue
    }
  }
}
```

## Relationship

Define relationship types to describe connections between elements:

```likec4
specification {
  relationship async
  relationship subscribes
  relationship is-downstream-of
}
```

## Tag

Tags enable marking, grouping, filtering, and adding semantics to elements, relationships, and views:

```likec4
specification {
  tag deprecated
  tag epic-123
  tag team2
}
```

### Tag Colors

Assign colors to tags:

```likec4
specification {
  tag deprecated {
    color #FF0000
  }
}
```

### Default Tags on Elements

Apply tags directly to element kinds:

```likec4
specification {
  element kafka-topic {
    #infra #data-lake
  }
  tag infra
  tag data-lake
}
```

## Color

Define custom colors extending built-in themes:

```likec4
specification {
  color custom-color1 #F00
  color custom-color2 #AABBCC
  color custom-color3 rgb(255, 0, 0)
  color custom-color4 rgb(100 150 200)
  color custom-color5 rgba(44, 8, 128, 0.9)
  color custom-color6 rgba(255, 200, 100, 50%)

  element person {
    style {
      color custom-color1
    }
  }
}
```

### Color Format Support

Supports 3, 6, or 8-character hex codes, and `rgb()`/`rgba()` formats. The system generates complementary colors (border, text, label backgrounds) using the Mantine library color palette generator.
