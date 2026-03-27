# OpenTelemetry Trove Synthesis

Thematic distillation across 11 sources covering the OpenTelemetry project — its architecture, specification, signals, collector, governance, and community structure.

## Key Findings

### What OpenTelemetry Is

OpenTelemetry (OTel) is a **vendor-neutral observability framework** under the CNCF (incubating status). It provides APIs, SDKs, and tools to **instrument, generate, collect, and export** telemetry data. Critically, it is *not* a backend — it handles the production and transport of telemetry, leaving storage and visualization to other tools (Jaeger, Prometheus, Grafana, commercial APMs). [otel-what-is, otel-org-overview]

Formed from a 2019 merger of OpenTracing and OpenCensus, it unifies two previously competing standards. The project spans **97 repositories** across Go, Python, TypeScript, Java, Rust, C#, C++, Ruby, Swift, Erlang/Elixir, and PHP. [otel-org-overview]

### The Three (Plus Two) Signals

OTel defines **four primary signal types**, with a fifth emerging:

1. **Traces** — Distributed traces tracking request paths across services. Built from Spans (units of work) organized into a trace tree via trace_id/span_id/parent_id. Spans carry attributes, events, links, and status. Key concepts: SpanKind (Client/Server/Internal/Producer/Consumer), Span Context (propagated across process boundaries), and sampling. [otel-signals-traces, otel-specification-repo/trace-api]

2. **Metrics** — Numerical measurements captured at runtime. Three primary instrument types: Counter (monotonic sum), Histogram (statistical distribution), Gauge (point-in-time value). Also UpDownCounter and observable (async callback) variants. Metrics use Views to customize aggregation and Metric Readers to export. [otel-signals-metrics, otel-specification-repo/metrics-api]

3. **Logs** — Timestamped text records with optional structured metadata. OTel's approach is notably different from traces/metrics: rather than replacing existing logging libraries, it bridges them. The Logs Bridge API connects existing log frameworks (log4j, SLF4J, Python logging) to OTel's export pipeline. Log records include body, timestamp, severity, trace context, and attributes. [otel-signals-logs, otel-specification-repo/logs-api]

4. **Baggage** — Key-value pairs propagated across process boundaries alongside trace context. Not exported to backends directly — used for cross-cutting concerns like feature flags or tenant IDs.

5. **Profiles** — Continuous profiling data (newer, less mature signal). [otel-spec-overview]

### Architecture: The Collector

The **OpenTelemetry Collector** is a vendor-agnostic proxy for telemetry data. It receives, processes, and exports data through a pipeline architecture:

- **Receivers** — Accept data (OTLP, Jaeger, Prometheus, and custom formats)
- **Processors** — Transform data (batching, sampling, attribute manipulation, filtering)
- **Exporters** — Send data to backends (OTLP, Jaeger, Prometheus, logging, and many vendor-specific)
- **Connectors** — Bridge between pipelines (one signal type to another)
- **Extensions** — Add capabilities (health checks, performance profiling, z-pages)

Two distributions: `otelcol` (core) and `otelcol-contrib` (community-contributed components). Can be deployed as agent (sidecar/host), gateway (centralized), or both. [otel-collector]

### The Specification

Version **1.55.0** at time of collection. Organized into three tiers:

- **API Specification** — Context, Baggage, Tracing, Metrics, Logs APIs. Defines the contracts that application code instruments against.
- **SDK Specification** — Implementation requirements for processors, exporters, samplers, views, and configuration. This is what language SDK authors implement.
- **Data Specification** — OTLP protocol (gRPC, HTTP/protobuf, HTTP/JSON), semantic conventions, and compatibility with OpenCensus/OpenTracing/Prometheus.

Uses RFC 2119 keyword semantics (MUST, SHOULD, MAY). The API/SDK separation is fundamental: applications depend only on the API; the SDK is a runtime dependency that can be swapped. [otel-spec-overview, otel-specification-repo]

### Context Propagation

Context propagation is the mechanism that ties signals together across process boundaries. It defines:

- **Context** — An immutable key-value store carried through execution
- **Propagators** — Inject/extract context into carriers (HTTP headers, gRPC metadata, environment variables)
- **W3C TraceContext** — The default propagation format (traceparent + tracestate headers)

The specification details TextMapPropagator interface, composite propagators, and the newer Environment Variable Carrier for batch/script scenarios. [otel-specification-repo/context-propagation]

### Resource Model

Resources represent the entity producing telemetry — typically a service instance. Key attributes include `service.name`, `service.version`, `service.instance.id`, `host.name`, and cloud/container metadata. Resources are attached at SDK initialization and propagated with all telemetry. Resource detection can be automatic (cloud metadata APIs) or manual. [otel-specification-repo/resource]

### Governance and Community

**Dual-committee model** under the CNCF:

- **Governance Committee (GC)** — 9 elected members, 2-year staggered terms. Owns non-technical governance: CoC, membership, scope, CNCF relations, roadmap.
- **Technical Committee (TC)** — No term limits, min 4 members. Owns all technical decisions: releases, quality, specification changes.

Work is organized into **SIGs** (Special Interest Groups):

- **Specification SIGs** — General spec, Sampling, Logs, Semantic Conventions (General, System Metrics, K8s, GenAI, CI/CD, RPC, Security, Service/Deployment), Entities
- **Implementation SIGs** — Language SDKs (Collector, .NET, Go, Java, JavaScript, Python, Ruby, Rust, Swift, PHP, Erlang/Elixir, C++, Zig), plus OpAMP, Demo, Helm, Operator
- **Cross-cutting SIGs** — Documentation (opentelemetry.io), Communications, End User, OTEP (enhancement proposals), Community, Configuration

Contributor ladder: Member -> Triager -> Approver -> Maintainer (+ Emeritus). SIGs have significant autonomy over their implementations. [otel-community-repo]

## Points of Agreement

All sources consistently emphasize:

- **Vendor neutrality** as a core principle — you own your data, no lock-in
- **API/SDK separation** as an architectural fundamental
- **The Collector as the recommended deployment pattern** (rather than direct SDK-to-backend export)
- **Semantic conventions** as essential for interoperability across languages and vendors
- **OTLP** as the canonical wire protocol

## Points of Disagreement / Tension

- **Logs maturity** — The Logs signal takes a notably different approach (bridge existing logging rather than replace it), and the spec acknowledges this is less mature than traces/metrics
- **Profiles** — Still in early development, not yet at the same maturity level as the other signals
- **Collector complexity** — The pipeline model is powerful but the configuration surface area is large (hundreds of community-contributed receivers/processors/exporters)

## Gaps

- **Cost management** — Sources don't deeply cover strategies for controlling telemetry volume/cost at scale
- **Practical deployment patterns** — Getting started docs are language-specific but don't cover production architecture decisions (sampling strategies, collector topology, multi-cluster)
- **Performance benchmarks** — The spec references a performance benchmark document but concrete numbers across languages are sparse
- **Entity model** — The Entities spec is new and still evolving; implications for resource modeling are unclear
- **Migration from proprietary agents** — Limited guidance on transitioning from vendor-specific APM agents to OTel
