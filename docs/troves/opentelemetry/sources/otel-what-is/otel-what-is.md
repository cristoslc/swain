---
source-id: "otel-what-is"
title: "What is OpenTelemetry?"
type: web
url: "https://opentelemetry.io/docs/what-is-opentelemetry/"
fetched: 2026-03-27T00:00:00Z
hash: "c7b71b5a09f34ae95a942b25d522dc4208f37965750ddf0446a00b9340ead28a"
---

# What is OpenTelemetry?

A brief explanation of what OpenTelemetry is and isn't.

OpenTelemetry is:

* An **observability framework and toolkit** designed to facilitate the

  + Generation
  + Export
  + Collection

  of telemetry data such as traces, metrics, and logs.
* **Open source**, as well as **vendor- and tool-agnostic**, meaning that it can
  be used with a broad variety of observability backends, including open source
  tools like [Jaeger](https://www.jaegertracing.io/) and [Prometheus](https://prometheus.io/), as well as commercial offerings.
  OpenTelemetry is **not** an observability backend itself.

A major goal of OpenTelemetry is to enable easy instrumentation of your
applications and systems, regardless of the programming language,
infrastructure, and runtime environments used.

The backend (storage) and the frontend (visualization) of telemetry data are
intentionally left to other tools.

## What is observability?

Observability is the ability to understand the internal state of a system by
examining its outputs. In the context of software, this means being able to
understand the internal state of a system by examining its telemetry data, which
includes traces, metrics, and logs.

To make a system observable, it must be instrumented. That is, the code
must emit traces, metrics, or logs. The instrumented data must then
be sent to an observability backend.

## Why OpenTelemetry?

With the rise of cloud computing, microservices architectures, and increasingly
complex business requirements, the need for software and infrastructure
observability is greater than ever.

OpenTelemetry satisfies the need for observability while following two key
principles:

1. You own the data that you generate. There's no vendor lock-in.
2. You only have to learn a single set of APIs and conventions.

Both principles combined grant teams and organizations the flexibility they need
in today's modern computing world.

If you want to learn more, take a look at OpenTelemetry's
[mission, vision, and values](https://opentelemetry.io/community/mission/).

## Main OpenTelemetry components

OpenTelemetry consists of the following major components:

* A specification for all components
* A standard protocol that defines the shape of telemetry data
* Semantic conventions that define a standard naming scheme for common telemetry data types
* APIs that define how to generate telemetry data
* Language SDKs that implement the specification, APIs, and export of telemetry data
* A library ecosystem that implements instrumentation for common libraries and frameworks
* Automatic instrumentation components that generate telemetry data without requiring code changes
* The OpenTelemetry Collector, a proxy that receives, processes, and exports telemetry data
* Various other tools, such as the OpenTelemetry Operator for Kubernetes, OpenTelemetry Helm Charts, and community assets for FaaS

OpenTelemetry is used by a wide variety of libraries, services and apps that have OpenTelemetry
integrated to provide observability by default.

OpenTelemetry is supported by numerous vendors, many of whom provide commercial support for OpenTelemetry and contribute to the project directly.

## Extensibility

OpenTelemetry is designed to be extensible. Some examples of how it can be
extended include:

* Adding a receiver to the OpenTelemetry Collector to support telemetry data
  from a custom source
* Loading custom instrumentation libraries into an SDK
* Creating a distribution of an SDK or the Collector tailored to a specific use case
* Creating a new exporter for a custom backend that doesn't yet support the
  OpenTelemetry protocol (OTLP)
* Creating a custom propagator for a nonstandard context propagation format

Although most users might not need to extend OpenTelemetry, the project is
designed to make it possible at nearly every level.

## History

OpenTelemetry is a [Cloud Native Computing Foundation](https://www.cncf.io) (CNCF) project that is
the result of a [merger](https://www.cncf.io/blog/2019/05/21/a-brief-history-of-opentelemetry-so-far/) between two prior projects,
[OpenTracing](https://opentracing.io) and [OpenCensus](https://opencensus.io).
Both of these projects were created to solve the same problem: the lack of a
standard for how to instrument code and send telemetry data to an Observability
backend. As neither project was fully able to solve the problem independently,
they merged to form OpenTelemetry and combine their strengths while offering a
single solution.

## What next?

* [Getting started](https://opentelemetry.io/docs/getting-started/) -- jump right in!
* Learn about [OpenTelemetry concepts](https://opentelemetry.io/docs/concepts/).
* [Watch videos](https://www.youtube.com/@otel-official) from the OTel for beginners or other playlists.
* Sign up for [training](https://opentelemetry.io/training/), including the free course Getting started with OpenTelemetry.
