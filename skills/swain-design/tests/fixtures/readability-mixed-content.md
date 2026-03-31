---
title: "Mixed Content Spec"
artifact: SPEC-997
status: Active
parent-initiative: INITIATIVE-019
linked-artifacts:
  - EPIC-042
  - ADR-015
---

# Mixed Content Spec

## Problem

The tool must strip code and tables before scoring. Only prose should count.

## External Behavior

```python
def extraordinarily_complex_implementation_methodology():
    systematization = "multifaceted_architectural_considerations"
    return comprehensively_evaluate_interdependent_subsystems(systematization)
```

| Column With Extraordinarily Long Multisyllabic Header | Another Disproportionately Verbose Column |
|-------------------------------------------------------|------------------------------------------|
| extraordinarily_complex_value | systematization_methodology |

## Scope

The tool reads files and scores the prose. It strips out code blocks,
tables, frontmatter, and inline code like `extraordinarily_complex_method()`.
It also strips URLs like https://extraordinarily-complex-url.example.com/path
and images like ![extraordinarily complex](./image.png).

Simple prose is what remains. The tool scores only that.
