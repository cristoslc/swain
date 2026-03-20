---
source-id: cwe-367-toctou
type: documentation
title: "CWE-367: Time-of-check Time-of-use (TOCTOU) Race Condition"
url: "https://cwe.mitre.org/data/definitions/367.html"
fetched: 2026-03-20
content-hash: "--"
---

# CWE-367: Time-of-check Time-of-use (TOCTOU) Race Condition

## Description

The weakness occurs when a product checks a resource's state before using it, but the resource can change between the check and use, invalidating the check results. A gap exists between verifying that a resource meets certain conditions and actually using that resource.

## Common Consequences

- **Integrity violations**: unauthorized read/write access to resources
- **Execution logic alteration**: application performs unexpected actions
- **Activity hiding**: malicious modifications bypass logging
- **Unexpected states**: product operates with invalid resource conditions

## Key Relationships

- Parent weakness: CWE-362 (Race Condition in shared resource synchronization)
- Related to: CWE-363 (Race Condition Enabling Link Following), CWE-386 (Symbolic Name mapping issues)
- Member of: CWE-557 (Concurrency Issues)

## Observed Real-World Examples

- CVE-2015-1743: sandbox bypass via file replacement after verification
- CVE-2008-2958: TOCTOU enabling symlink attack prevention bypass
- CVE-2003-0813: multi-threaded race causing use-after-free vulnerabilities

## Potential Mitigations

- Eliminate the check-before-use pattern where possible
- Employ atomic operations combining check and use
- Use environmental locking mechanisms before checking
- Recheck resources after operations to confirm success
- Limit time between check and use operations

## Detection Methods

Static analysis tools can identify potential instances by modeling data and control flow patterns, seeking vulnerable connections between input sources and resource interactions.

## Relevance to CI/CD

The TOCTOU pattern extends beyond security to any system with non-atomic check-then-act sequences on shared state. In CI/CD, the "check" is running tests on an isolated branch and the "use" is merging into the shared main branch. The state (main branch contents) can change between check and use, invalidating the test results.
