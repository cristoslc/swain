---
source-id: "likec4-dsl-deployment-model"
title: "LikeC4 Deployment Models"
type: documentation-site
url: "https://likec4.dev/dsl/deployment/model/"
fetched: 2026-03-23T00:00:00Z
hash: "--"
---

# LikeC4 Deployment Models

## Overview

The deployment model represents a physical infrastructure layer distinct from the logical model. It features its own hierarchical structure of deployment nodes while maintaining references to logical model elements.

## Specification

Deployment node types must be defined within the specification section:

```likec4
specification {
  deploymentNode environment
  deploymentNode zone
  deploymentNode kubernetes {
    style {
      color blue
      icon tech:kubernetes
      multiple true
    }
  }
  deploymentNode vm {
    notation 'Virtual Machine'
    technology 'VMware'
  }
}
```

## Deployment Nodes

Nodes organize hierarchically within a deployment block:

```likec4
deployment {
  environment prod {
    zone eu {
      zone zone1 {
        vm vm1
        vm vm2
      }
      zone2 = zone {
        vm1 = vm
        vm2 = vm
      }
    }
  }
}
```

### Node Properties

```likec4
deployment {
  environment prod 'Production' {
    #live #sla-customer
    technology 'OpenTofu'
    summary 'Production environment'
    description '''
      ## Detailed description
      With **Markdown** support
    '''
    link https://likec4.dev
    zone eu {
      title 'EU Region'
    }
  }
}
```

### Extending Nodes

```likec4
// File: 'deployments/prod.c4'
deployment {
  environment prod
}

// File: 'deployments/prod/zone-eu.c4'
deployment {
  extend prod {
    zone eu
  }
}
```

## Deployed Instances

The `instanceOf` operator maps logical model elements to deployment nodes:

```likec4
deployment {
  environment prod {
    zone eu {
      zone zone1 {
        instanceOf frontend.ui
        instanceOf backend.api
      }
      zone zone2 {
        ui = instanceOf frontend.ui
        api1 = instanceOf backend.api
        api2 = instanceOf backend.api
      }
      db = instanceOf database
    }
  }
}
```

### Overriding Instance Properties

```likec4
deployment {
  environment prod {
    zone eu {
      db = instanceOf database {
        title 'Primary DB'
        technology 'PostgreSQL with streaming replication'
        icon tech:postgresql
        style {
          color red
        }
      }
    }
  }
}
```

## Deployment Relationships

The deployment model inherits relationships from the logical model and permits deployment-specific connections:

```likec4
deployment {
  environment prod {
    vm vm1 {
      db = instanceOf database 'Primary DB'
    }
    vm vm2 {
      db = instanceOf database 'Standby DB'
    }
    vm2.db -> vm1.db 'replicates'
  }
}
```

### Typed Relationships

```likec4
deployment {
  environment prod {
    vm2.db -[streaming]-> vm1.db {
      #next, #live
      title 'replicates'
      description 'Streaming replication'
    }
  }
}
```
