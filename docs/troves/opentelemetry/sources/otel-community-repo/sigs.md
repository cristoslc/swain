---
source-id: "otel-community-repo"
extract: "sigs"
files:
  - "sigs.yml"
  - "project-management.md"
---

# OpenTelemetry Special Interest Groups (SIGs)

SIGs are the primary organizational unit for work in OpenTelemetry. Each SIG owns specific repositories, holds regular meetings, and has its own maintainers. SIG definitions live in `sigs.yml` (machine-readable YAML consumed by automation to generate README tables).

## SIG Categories

### Specification SIGs

Define standards, protocols, and semantic conventions.

| SIG | Meeting | Key Repos |
|-----|---------|-----------|
| Specification: General + OTel Maintainers Sync | Tuesday 08:00 PT | opentelemetry-specification, opentelemetry-proto, build-tools |
| Specification: Sampling | Thursday 08:00 PT | |
| Specification: Logs | Tuesday 10:00 PT | |
| Semantic Conventions: General | Monday 08:00 PT | |
| Semantic Conventions: System Metrics | | |
| Semantic Conventions: K8s | | |
| Semantic Conventions and Instrumentation: GenAI | | |
| Semantic Conventions: CI/CD | | |
| Semantic Conventions: RPC | | |
| Semantic Conventions: Security | | |
| Semantic Conventions: Service and Deployment | | |
| Specification: Entities | | |

### Implementation SIGs

Build language SDKs, collectors, and instrumentation.

| SIG | Notes |
|-----|-------|
| OpAMP | Open Agent Management Protocol |
| Prometheus Interoperability | |
| Functions as a Service (FAAS) | |
| Profiling | |
| OpenTelemetry on Mainframes | |
| Client Instrumentation | |
| Android: SDK + Automatic Instrumentation | |
| Arrow | OTel Arrow protocol |
| Browser | |
| Collector | Core collector component |
| C++: SDK | |
| .NET: Automatic Instrumentation | |
| .NET: SDK | |
| Erlang/Elixir: SDK | |
| GoLang: SDK | |
| GoLang: Automatic Instrumentation | |
| GoLang: Compile-Time Instrumentation | |
| Injector | |
| Java: SDK + Instrumentation | |
| JavaScript: SDK | |
| Kotlin: SDK | |
| PHP: SDK | |
| Python: SDK | |
| Ruby: SDK | |
| Rust: SDK | |
| Swift: SDK | |
| Network | |
| eBPF Instrumentation | |
| Kubernetes Operator | |
| Kubernetes Helm Charts | |
| Community Demo Application | |
| Semantic Conventions: Tooling | |

### Cross-Cutting SIGs

Horizontal concerns spanning multiple implementation SIGs.

| SIG | Notes |
|-----|-------|
| Communications (Website, Documentation) | Manages opentelemetry.io |
| End-User SIG | End-user feedback and adoption |
| Security | Security practices and vulnerability management |
| Project Infrastructure | Build/test/release infrastructure |
| Contributor Experience | Contributor onboarding and tooling |
| Developer Experience | SDK usability and ergonomics |

### Localization Teams (part of SIG Communications)

Bengali, Chinese (zh-CN), French (fr-FR), Japanese (ja-JA), Polish (pl-PL), Portuguese (pt-BR), Romanian (ro-RO), Spanish (es-ES), Ukrainian (uk-UA).

## SIG Structure in sigs.yml

Each SIG entry in `sigs.yml` contains:

```yaml
- name: 'SIG Name'
  meeting: 'Day at HH:MM PT'
  notes:
    type: gDoc
    value: <google-doc-id>
  chat:
    - type: slack
      name: '#channel-name'
      id: <slack-channel-id>
  invites: calendar-invite-key
  sponsors:            # TC sponsors
    - name: Person Name
      github: handle
  gcLiaison:           # GC liaison for check-ins
    - name: Person Name
      github: handle
  repositories:        # GitHub repos owned by this SIG
    - https://github.com/open-telemetry/repo-name
  roadmapProjectIDs:   # GitHub project board IDs
    - 123
```

## Project Lifecycle

Large cross-cutting efforts are formalized as "projects" (tracked in `projects/` directory). Projects:

- Require a TC sponsor and GC approval
- Have clear goals, staffing, and deadlines
- May result in new SIG formation
- Follow a lifecycle from proposal through completion

### Completed Projects (examples)

CI/CD, Client Instrumentation, Database Client SemConv, Event API, FaaS, Feature Flag, HTTP, Logging Bridge (one per language), Project Infrastructure.

### Active Projects (examples)

Agentic Workflow, Browser Phase 1, CI/CD Phase 2, Collector v1, Config, Contributor Experience, Developer Experience, Gen AI, Go Compile Instrumentation, K8s SemConv, Mainframe, OTel Blueprints, OTelArrow, Resources and Entities, RPC SemConv, Sampling, Security SemConv, System SemConv, Zig SIG Bootstrap.
