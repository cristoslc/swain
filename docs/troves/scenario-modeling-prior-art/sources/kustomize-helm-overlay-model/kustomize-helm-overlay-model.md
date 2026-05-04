---
title: "Kustomize / Helm — Base + Overlay as Config Variant Modeling"
source-url: https://spacelift.io/blog/kustomize-vs-helm
source-type: web-page
fetched: 2026-04-28
transcript-source: web-search-synthesis
---

# Kustomize / Helm — Config Variant Modeling

**Sources:** spacelift.io, ibm.com, harness.io, justinpolidori.com

## Summary

Kustomize and Helm are the two dominant Kubernetes config management tools. Their variant-modeling approaches are the closest analogs in software infrastructure to "same artifact, different assumptions." Each defines a distinct primitive for variant modeling.

## Kustomize: Base + Overlay

The Kustomize primitive is the **overlay**. A base defines the canonical configuration. Overlays patch specific fields for a named variant (dev, staging, prod):

```
base/
  deployment.yaml        ← canonical resource
  kustomization.yaml     ← base manifest

overlays/
  dev/
    kustomization.yaml   ← patches: replicas=1, image=:dev
  prod/
    kustomization.yaml   ← patches: replicas=10, image=:stable
```

Operator invocation: `kubectl apply -k overlays/prod/`. The tool computes `base + patch = rendered output` at apply time. You never edit the rendered output directly — only the patch.

**Key properties:**
- Single source of truth (base). Overlays express *delta from base*, not full copies.
- Overlays are composable — stack multiple patches.
- No side-by-side comparison tooling built in. You `diff <(kubectl kustomize overlays/dev) <(kubectl kustomize overlays/prod)` manually.
- No "what if I apply this overlay to staging instead of prod?" tooling.

## Helm: Values Files as Scenario Parameters

The Helm primitive is the **values file**. A chart defines templates with `{{ .Values.foo }}` placeholders. A values file fills them in for a named context:

```
helm install my-app ./chart -f values-prod.yaml
```

Multiple values files can be layered: `-f values-base.yaml -f values-prod.yaml`. Later files override earlier ones.

**Key properties:**
- Values are parameters, not structural patches. The template structure is fixed.
- Side-by-side comparison: `helm template . -f values-dev.yaml > /tmp/dev.yaml && helm template . -f values-prod.yaml > /tmp/prod.yaml && diff /tmp/dev.yaml /tmp/prod.yaml`.
- No native "compare scenarios" command. Diff is manual.

## Combined Pattern (Mature Platform Teams)

Helm for packaging and versioning; Kustomize for environment-specific patching of Helm output. The combination models "upstream chart + local org defaults + environment-specific overrides" as a three-layer variant tree.

## Relevance to swain Scenario Modeling

Kustomize's base+overlay pattern directly maps to swain's use case:
- **Base** = the canonical artifact graph (all ADRs in their actual state).
- **Overlay** = a named scenario file that pins specific ADRs to alternative states (`adr-046: active` instead of `superseded`).
- **Rendered output** = swain chart computed with the overlay applied.

The key Kustomize lesson for swain: overlays should express *delta from base*, not full copies. A scenario should say "ADR-046 = active, everything else unchanged" — not duplicate the entire graph.

**Key lesson:** The overlay-as-delta pattern is the right mental model for swain scenarios. Helm's values-file pattern (parameter substitution) also applies for priority-weight overrides.
