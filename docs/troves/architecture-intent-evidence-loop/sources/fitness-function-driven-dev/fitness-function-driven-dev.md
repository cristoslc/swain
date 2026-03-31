---
source-id: "fitness-function-driven-dev"
title: "Fitness Function-Driven Development"
type: web
url: "https://www.thoughtworks.com/en-us/insights/articles/fitness-function-driven-development"
fetched: 2026-03-29T00:00:00Z
hash: "bba8c6ce5be7c2579f9283a6d8d0fe51fa66ba9a40bdbb30404a1d930d01d795"
---

# Fitness Function-Driven Development

**Authors:** Paula Paul and Rosemary Wang
**Published:** January 11, 2019
**Source:** ThoughtWorks Insights
**Capability:** Cap 3 -- Pressure-Test (Go Deeper)

## Content

TDD involves writing tests first then developing minimal code to pass. Fitness Function-Driven Development extends this idea to architectural quality attributes: scalability, reliability, observability, and other "-ilities."

### What Are Fitness Functions?

Architectural goals and constraints may change independently of functional expectations. Fitness functions describe how close an architecture is to achieving an architectural aim. Just as TDD tests verify business outcomes, fitness functions measure alignment to architectural goals.

### Where to Start

Think of architecture as a product having user journeys. Gather input from stakeholders in business, compliance, operations, security, infrastructure, and development. Group top attributes into common themes (resilience, operability, stability). Examine conflicts and trade-offs -- e.g., goals for agility may conflict with goals for stability.

### Fitness Functions in Delivery Pipelines

Create fitness functions and include them in appropriate delivery pipelines. This communicates metrics as an important aspect of enterprise architecture. Regular fitness function reviews focus architectural efforts on meaningful, quantifiable outcomes.

### Categories with Code Examples

**Code Quality** (Modifiability, Manageability, Adaptability):
```
describe "Code Quality" do
  it "has test coverage above 90%"
  it "has maintainability rating of .1 or higher (B)"
end
```

**Resiliency** (Availability, Fault Tolerance):
```
describe "Resiliency" do
  it "has less than 1% error rate for new deployment"
  it "has less than 5% error rate with network latency"
  it "completes a transaction under 10 seconds with network latency"
end
```

**Observability** (Monitoring, Debugging):
```
describe "Observability" do
  it "streams metrics"
  it "has parseable logs"
end
```

**Performance** (Scalability, Throughput):
```
describe "Performance" do
  it "completes a transaction under 10 seconds"
  it "has less than 10% error rate for 10000 transactions"
end
```

**Compliance** (Regulatory, Legal, Corporate):
```
describe "Compliance Standards" do
  it "should not have PII in the logs"
  it "should report types of personal information processed"
  it "should have been audited in the past year"
end
```

**Security** (Code Analysis, CVE Analysis):
```
describe "Security" do
  it "should use corporate-approved libraries only"
  it "should not have any of the OWASP Top 10"
  it "should not have plaintext secrets in codebase"
  it "should not use libraries with known vulnerabilities"
end
```

**Operability** (Runbooks, Alerts, Documentation):
```
describe "Operability Standards" do
  it "should have a service runbook"
  it "should have a README"
  it "should have alerts"
  it "should have tracing IDs"
end
```

### Key Benefits

1. Objectively measures technical debt and drives code quality
2. Informs coding choices for interfaces, events, and APIs
3. Communicates architectural standards as code
4. Empowers development teams to deliver features aligned with architectural goals
5. Helps organizations avoid organic architectural drift

## Relevance to Intent-Evidence Loop

This article provides the **practical implementation guide** for encoding architectural intent as executable specifications. The fitness function categories map directly to the kinds of evidence the loop needs to collect:

- **Code Quality** fitness functions = evidence about internal quality (connects to Fowler's quality-worth-cost argument)
- **Observability** fitness functions = meta-evidence about whether evidence collection itself is working
- **Compliance/Security** fitness functions = evidence about constraint conformance

For swain, the operability fitness functions are particularly relevant -- they check for the presence of exactly the kind of architectural documentation (runbooks, READMEs) that the trove identifies as "amortized derivation."
