---
source-id: "otel-collector"
title: "OpenTelemetry Collector"
type: web
url: "https://opentelemetry.io/docs/collector/"
fetched: 2026-03-27T00:00:00Z
hash: "814f15e46657e5b89804fc1a17ad429f51b41e5093beed607580ad30799b0cad"
---

# Collector

Vendor-agnostic way to receive, process and export telemetry data.

## Introduction

The OpenTelemetry Collector offers a vendor-agnostic implementation of how to
receive, process and export telemetry data. It removes the need to run, operate,
and maintain multiple agents/collectors. This works with improved scalability
and supports open source observability data formats (e.g. Jaeger, Prometheus,
Fluent Bit, etc.) sending to one or more open source or commercial backends.

## Objectives

* *Usability*: Reasonable default configuration, supports popular protocols,
  runs and collects out of the box.
* *Performance*: Highly stable and performant under varying loads and
  configurations.
* *Observability*: An exemplar of an observable service.
* *Extensibility*: Customizable without touching the core code.
* *Unification*: Single codebase, deployable as an agent or collector with
  support for traces, metrics, and logs.

## When to use a collector

For most language specific instrumentation libraries you have exporters for
popular backends and OTLP. You might wonder,

> under what circumstances does one use a collector to send data, as opposed to
> having each service send directly to the backend?

For trying out and getting started with OpenTelemetry, sending your data
directly to a backend is a great way to get value quickly. Also, in a
development or small-scale environment you can get decent results without a
collector.

However, in general we recommend using a collector alongside your service, since
it allows your service to offload data quickly and the collector can take care
of additional handling like retries, batching, encryption or even sensitive data
filtering.

It is also easier to set up a collector than you might think: the
default OTLP exporters in each language assume a local collector endpoint, so if
you launch a collector it will automatically start receiving telemetry.

## Collector security

Follow best practices to make sure your collectors are hosted and configured securely.

## Status

The **Collector** status is: mixed, since core Collector components
currently have mixed stability levels.

**Collector components** differ in their maturity levels. Each component has its
stability documented in its README. You can find a list of all available
Collector components in the [registry](https://opentelemetry.io/ecosystem/registry/?language=collector).

Support is guaranteed for Collector software artifacts for a certain time period
based on the artifact's intended audience. This support includes, at minimum,
fixes for critical bugs and security issues.

## Distributions and releases

For information about Collector distributions and releases, including the
latest release, see [Distributions](https://opentelemetry.io/docs/collector/distributions/).

## Sub-topics

- **[Quick start](https://opentelemetry.io/docs/collector/quick-start/)** -- Setup and collect telemetry in minutes!
- **[Install the Collector](https://opentelemetry.io/docs/collector/install/)**
- **[Deploy the Collector](https://opentelemetry.io/docs/collector/deploy/)** -- Patterns you can apply to deploy the OpenTelemetry Collector.
- **[Configuration](https://opentelemetry.io/docs/collector/configuration/)** -- Learn how to configure the Collector to suit your needs.
- **[Components](https://opentelemetry.io/docs/collector/components/)** -- Receivers, processors, exporters, connectors, and extensions.
- **[Management](https://opentelemetry.io/docs/collector/management/)** -- How to manage your OpenTelemetry Collector deployment at scale.
- **[Distributions](https://opentelemetry.io/docs/collector/distributions/)**
- **[Internal telemetry](https://opentelemetry.io/docs/collector/internal-telemetry/)**
- **[Troubleshooting](https://opentelemetry.io/docs/collector/troubleshooting/)** -- Recommendations for troubleshooting the Collector.
- **[Scaling the Collector](https://opentelemetry.io/docs/collector/scaling/)**
- **[Transforming telemetry](https://opentelemetry.io/docs/collector/transforming-telemetry/)**
- **[Architecture](https://opentelemetry.io/docs/collector/architecture/)**
- **[Extend the Collector](https://opentelemetry.io/docs/collector/extend/)** -- Learn how to extend the OpenTelemetry Collector with custom components.
- **[Benchmarks](https://opentelemetry.io/docs/collector/benchmarks/)**
- **[Registry](https://opentelemetry.io/docs/collector/registry/)** -- Exporters, processors, receivers and other useful components.
- **[Resiliency](https://opentelemetry.io/docs/collector/resiliency/)** -- How to configure a resilient OTel Collector pipeline.
