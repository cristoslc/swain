---
source-id: "otel-specification-repo"
title: "OpenTelemetry Specification Repository"
type: repository
url: "https://github.com/open-telemetry/opentelemetry-specification"
fetched: 2026-03-27T00:00:00Z
hash: "411aadc2e31ed98bcadad8df2150056459bc72e46f42721f03f8ccf8e86e9bb2"
selective: true
highlights:
  - "overview.md"
  - "trace-api.md"
  - "metrics-api.md"
  - "logs-api.md"
  - "resource.md"
  - "context-propagation.md"
---

# OpenTelemetry Specification Repository

Selective extraction from the OpenTelemetry specification repository. Contains
the core specification documents covering the API surface for traces, metrics,
logs, resource semantics, and context propagation.

## Source Files Extracted

| Highlight File | Source Path(s) | Description |
|---|---|---|
| overview.md | specification/overview.md | Architecture overview, signal descriptions, library design |
| trace-api.md | specification/trace/api.md | Tracing API: TracerProvider, Tracer, Span, SpanContext |
| metrics-api.md | specification/metrics/api.md | Metrics API: MeterProvider, Meter, Instruments |
| logs-api.md | specification/logs/api.md | Logs Bridge API: LoggerProvider, Logger, LogRecord |
| resource.md | specification/resource/data-model.md + specification/resource/sdk.md | Resource data model and SDK |
| context-propagation.md | specification/context/README.md + specification/context/api-propagators.md | Context API and Propagators API |

## Repository Structure (specification/ only)

```
specification/
  baggage/          - Baggage API
  common/           - Shared attribute naming, types, instrumentation scope
  compatibility/    - OpenTracing, OpenCensus, Prometheus compatibility
  configuration/    - File-based configuration API and SDK
  context/          - Context and Propagators API
  entities/         - Entity data model (development)
  logs/             - Logs Bridge API, SDK, data model
  metrics/          - Metrics API, SDK, data model, exporters
  profiles/         - Profiling signal (development)
  protocol/         - OTLP protocol specification
  resource/         - Resource data model and SDK
  schemas/          - Telemetry schema file format
  trace/            - Tracing API, SDK, exporters
  overview.md       - Architecture overview
  glossary.md       - Term definitions
  versioning-and-stability.md - Stability guarantees
```
