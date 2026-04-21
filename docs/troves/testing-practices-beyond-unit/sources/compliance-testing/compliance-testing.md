---
source-id: compliance-testing
trove: testing-practices-beyond-unit
type: methodology-definition
title: "Compliance Testing: Turning Governance into Executable Specifications"
author: "Michael Nygard; ThoughtWorks Technology Radar; Open Policy Agent contributors"
fetched: 2026-04-20
freshness-ttl: 365
url: "https://openpolicyagent.org"
tags: [compliance, policy-as-code, OPA, ADR, architecture-decisions, governance, compliance-as-code, executable-specifications]
---

# Compliance Testing: Turning Governance into Executable Specifications

## What Compliance Testing Is

Compliance testing verifies that a system adheres to policies, standards, and architectural decisions. It answers the question: "Are we actually doing what we said we would do?" This is distinct from functional testing (does it work?), performance testing (is it fast?), and security testing (is it safe?). Compliance testing checks whether the system conforms to declared constraints — architectural, regulatory, organizational, or operational.

The shift from document-based compliance to code-based compliance is the key trend. Instead of a governance document that says "all services must use TLS 1.3," a compliance test asserts the same thing programmatically. The document rots. The test breaks when violated.

## ADR Compliance as Executable Specifications

Michael Nygard's "Documenting Architecture Decisions" (2011) introduced the Architecture Decision Record (ADR), a short document capturing a decision's context, decision, and consequences. ADRs are the canonical form of architectural governance: they say what was decided, why, and what constraints follow.

ADRs are documents. Documents cannot enforce themselves. A decision that says "all new services will be written in Go" is only as strong as the next developer's willingness to read it and comply. This is the gap that compliance testing closes.

An ADR becomes an executable specification when each constraint it declares has a corresponding automated check:

- ADR-015 says "all API endpoints must require authentication." A compliance test scans route definitions and fails if any are missing auth middleware.
- ADR-019 says "all scripts follow the bash scripting conventions in CLAUDE.md." A compliance test lints scripts against the conventions.
- ADR-021 says "no service may store PII in logs." A compliance test scans log statements and fails if any contain email addresses, social security numbers, or other PII patterns.

The ADR is still valuable as context. It explains why the constraint exists. The compliance test is the enforcement mechanism. Together, they form a closed loop: the decision states intent, the test verifies compliance, and violations produce actionable feedback immediately rather than at audit time.

## Open Policy Agent

Open Policy Agent (OPA, openpolicyagent.org) is a general-purpose policy engine that decouples policy decision-making from policy enforcement. OPA uses the Rego language to define policies as code, evaluates those policies against input data, and returns allow/deny decisions.

OPA's relevance to compliance testing:

- **Policy as data.** Rego policies are version-controlled, reviewed, and tested like any other code. This makes compliance auditable, repeatable, and changeable through the same processes that govern application code.
- **Unified policy enforcement.** OPA can evaluate policies across Kubernetes admission control, API authorization, data filtering, and infrastructure provisioning. The same policy language covers different domains.
- **Built-in testing.** Rego has a test framework. You write a policy, write a test for the policy, and run `opa test`. This is compliance testing: the policy is the specification, the Rego test is the compliance check, and CI enforcement is the gate.

Example: a Rego policy that denies Kubernetes deployments without resource limits:

```rego
deny[msg] {
    input.request.kind.kind == "Deployment"
    container := input.request.object.spec.template.spec.containers[_]
    not container.resources.limits
    msg := sprintf("container <%v> has no resource limits", [container.name])
}
```

The corresponding Rego test:

```rego
test_deployment_without_limits_denied {
    deny[msg] with input as {"request": {"kind": {"kind": "Deployment"}, "object": {"spec": {"template": {"spec": {"containers": [{"name": "app"}]}}}}}}
    msg == "container <app> has no resource limits"
}
```

This cycle — write policy, write test, enforce in CI — is compliance-as-code.

## Compliance-as-Code

The ThoughtWorks Technology Radar has tracked "Compliance as Code" as a theme across multiple editions. The core idea: regulatory and organizational compliance requirements should be encoded as automated tests and policy checks, not assessed manually through periodic audits.

Compliance-as-code has several dimensions:

- **Infrastructure compliance.** Policies that check Terraform, CloudFormation, or Kubernetes manifests against security baselines, tagging requirements, and architectural standards. Tools: OPA Conftest, Checkov, tfsec, Bridgecrew.
- **Application compliance.** Policies that check application code against ADRs, coding standards, and security requirements. Tools: Semgrep, custom linters, ArchUnit (for Java).
- **Data compliance.** Policies that check data handling against GDPR, HIPAA, SOC 2, and other regulatory frameworks. Tools: data lineage scanners, PII detection tools, GitGuardian.
- **Process compliance.** Policies that check git history, CI configuration, and deployment pipelines against organizational requirements (e.g., "all production deploys require a review approval"). Tools: GitHub branch protection rules, OPA gatekeeper, custom CI checks.

The ThoughtWorks Radar emphasizes that compliance-as-code is not just for regulated industries. Any team that writes ADRs, defines coding standards, or maintains architectural guidelines benefits from encoding those constraints as tests. Manual compliance review is slow, inconsistent, and easy to skip under time pressure. Automated compliance review is fast, consistent, and impossible to skip once wired into CI.

## GitGuardian and Bridgecrew

GitGuardian scans repositories for secrets,credentials, and sensitive data. It is a compliance testing tool: it checks whether a codebase violates the policy "no secrets in source control." The policy is simple, the enforcement is automated, and violations are flagged immediately rather than discovered at audit time.

Bridgecrew (now part of Palo Alto Networks) scans Infrastructure as Code (Terraform, CloudFormation, Kubernetes) against security and compliance benchmarks (CIS, PCI-DSS, HIPAA). It is compliance testing for infrastructure: the policy is defined by a benchmark, the check is automated, and the feedback is immediate.

Both tools illustrate the pattern: define a policy, automate the check, enforce in CI. Whether the policy comes from a regulatory framework or an ADR, the mechanism is the same.

## Relationship to Other Practices

- **Dogfooding** (see companion source) validates that the product works for real users. Compliance testing validates that the product is built the way the team said it would be built. They address different quality attributes — usage and conformance, respectively.
- **Observability-driven testing** (see companion source) uses production data to decide what to test. Compliance testing uses declared policies to decide what to check. ODT is data-driven. Compliance testing is policy-driven. Both are automated, both run in CI, and both produce evidence.
- **Testing quadrants** (see companion source) place compliance testing in Q4 (technology-facing, critiquing team). It is a critique of the implementation against declared constraints, not a test of business behavior.
- **Swain's verification landscape** (see companion source) includes ADR compliance as a specific verification dimension. DESIGN-027's "Artifact alignment agent" iterates over active ADRs and checks whether implementation code conforms to them. This is compliance testing applied to ADRs.

## Practical Takeaways

1. **Start with ADRs that have clear, testable constraints.** An ADR that says "use Go for new services" is testable (check file extensions, build files, or import statements). An ADR that says "favor simplicity" is not directly testable but may imply testable constraints (e.g., "no dependency may add more than 5KB to the bundle").
2. **Write the compliance test alongside the ADR.** If the ADR is worth writing, the test is worth writing. An ADR without a compliance test is a suggestion, not a constraint.
3. **Wire compliance tests into CI.** A test that runs manually is a test that will be skipped. Wire ADR compliance checks into the same pipeline that runs unit and integration tests.
4. **Use OPA for cross-domain policies.** Rego policies can be shared across infrastructure, application, and data compliance. This reduces duplication and keeps policies consistent.
5. **Track compliance test failures as drift signals.** A failing compliance test is not just a bug. It is a signal that the system has drifted from the declared architecture. Each failure should prompt a question: is the ADR wrong, or is the implementation wrong? Either answer is valuable.