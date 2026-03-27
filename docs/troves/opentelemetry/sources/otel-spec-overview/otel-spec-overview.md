---
source-id: "otel-spec-overview"
title: "OpenTelemetry Specification 1.55.0 - Overview"
type: web
url: "https://opentelemetry.io/docs/specs/otel/"
fetched: 2026-03-27T00:00:00Z
hash: "adfd55564af2a92d2bee59656064208f17f77300a3e7271a7b1eafe57b1c387a"
---

# OpenTelemetry Specification 1.55.0

## Contents

- Overview
- Glossary
- Principles and Guidelines
  - Core Principles
  - Versioning and stability for OpenTelemetry clients
  - Library Guidelines
    - Package/Library Layout
    - General error handling guidelines
  - Performance
- API Specification
  - Context
    - Propagators
    - Environment Variable Carriers
  - Baggage
  - Tracing
  - Metrics
  - Logs
    - API
- SDK Specification
  - Tracing
  - Metrics
  - Logs
  - Resource
  - Configuration
- Data Specification
  - Semantic Conventions
  - Protocol (OTLP)
    - Metrics Data Model
    - Logs Data Model
    - Profiles Mappings
  - Compatibility
    - OpenCensus
    - OpenTracing
    - Prometheus and OpenMetrics
    - Trace Context in non-OTLP Log Formats

## Specification Structure

The specification is organized into:

### API Specification
Defines the cross-cutting concerns and signal-specific APIs:
- **Context** — cross-cutting concerns including propagators and environment variable carriers
- **Baggage** — key-value pairs propagated across process boundaries
- **Tracing API** — creating and managing spans
- **Metrics API** — recording measurements
- **Logs API** — emitting log records

### SDK Specification
Defines the implementation requirements:
- **Tracing SDK** — span processors, exporters, samplers
- **Metrics SDK** — metric readers, exporters, views
- **Logs SDK** — log record processors, exporters
- **Resource SDK** — resource detection and merging
- **Configuration** — file-based and environment-variable configuration

### Data Specification
Defines the data model and wire protocol:
- **Semantic Conventions** — standardized attribute names and values
- **OTLP (OpenTelemetry Protocol)** — the wire protocol for exporting telemetry
- **Compatibility** — interop with OpenCensus, OpenTracing, Prometheus

## Notation Conventions and Compliance

The keywords "MUST", "MUST NOT", "REQUIRED", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in the specification are to be interpreted as described in BCP 14 (RFC2119, RFC8174) when they appear in all capitals.

An implementation of the specification is not compliant if it fails to satisfy one or more of the "MUST", "MUST NOT", "REQUIRED" requirements.

## Project Naming

- The official project name is "OpenTelemetry" (no space between "Open" and "Telemetry")
- The official acronym is "OTel". "OT" MAY be used only as part of a longer acronym (e.g., OTCA)
- Sub-projects follow the pattern "OpenTelemetry {language/runtime/component}" (e.g., "OpenTelemetry Python", "OpenTelemetry .NET", "OpenTelemetry Collector")

## Key Specification Areas

### Signals
OpenTelemetry defines four primary signal types:
1. **Traces** — distributed traces tracking requests across services
2. **Metrics** — numerical measurements of system behavior
3. **Logs** — timestamped text records with structured metadata
4. **Profiles** — continuous profiling data (newer addition)

### Protocol (OTLP)
- OTLP Specification 1.10.0
- Supports gRPC, HTTP/protobuf, and HTTP/JSON transports
- Design goals, requirements, and exporter specifications

### Entities
- Entity Data Model — representing resources as entities
- Entity Propagation — propagating entity information

### Configuration
- API, SDK, and Data Model for configuration
- Environment variable specification
- Common configuration patterns

### Compatibility
- OpenCensus migration path
- OpenTracing bridge
- Prometheus and OpenMetrics interop
- Trace context in non-OTLP log formats
