# Synthesis: Agent Service Provisioning

## Key Findings

Stripe has launched **Stripe Projects**, a CLI-first service provisioning layer that targets agent and vibe-coding workflows. The announcement (from Stripe CEO Patrick Collison) directly responds to a well-documented pain point: when agents or vibe-coders build deployed applications, they hit a wall of manual, browser-based service configuration -- account creation, API key retrieval, billing setup, and provider onboarding.

The core interface is a single CLI command:

```
$ stripe projects add posthog/analytics
```

This provisions a PostHog account, generates an API key, and configures billing -- all without leaving the terminal. The product launched 2026-03-27 as a developer preview at [projects.dev](https://projects.dev), with broader access and additional providers planned.

**What this signals:**

- **Service provisioning is becoming a CLI/agent-automatable primitive.** Stripe is betting that the `provider/service` namespace pattern (similar to package managers) will become the standard interface for service onboarding.
- **The "last mile" of agent development is infrastructure, not code.** Collison explicitly frames the problem as agents being blocked by human-in-the-loop browser workflows. This positions Projects as infrastructure for agentic autonomy.
- **Stripe is extending its platform beyond payments** into a general developer services marketplace, using billing integration as the wedge.

*Source: collison-stripe-projects-announcement*

## Points of Agreement

The friction Collison quotes from Karpathy's MenuGen experience -- "all these services, docs, API keys, configurations, dev/prod deployments, team and security features, rate limits, pricing tiers" -- aligns with practitioner reports across the vibe-coding space. Browser-based service configuration is consistently identified as the primary bottleneck that breaks flow state during agent-assisted development.

This trove should be cross-referenced with the `vibe-coding-practitioner-experience` trove if/when it is created, as it would document the same friction pattern from the practitioner side.

*Source: collison-stripe-projects-announcement (quoting Karpathy's MenuGen writeup)*

## Gaps and Open Questions

- **No technical architecture disclosed.** How does Projects work under the hood? Is it OAuth delegation, direct account creation via provider APIs, or something else? The security implications differ significantly by approach.
- **No pricing model.** Does Stripe take a cut? Is it free as a developer acquisition channel? Usage-based? This matters for evaluating sustainability.
- **Provider ecosystem scope unclear.** Only one provider (PostHog) is shown as an example. The breadth and depth of the provider catalog at launch is unknown.
- **Security model unspecified.** Who owns the provisioned accounts? How are credentials stored and rotated? Can an agent provision resources that outlive the session?
- **No detail on teardown or lifecycle management.** Can you `stripe projects remove posthog/analytics`? What happens to the provisioned account and data?

*These gaps may close as the developer preview matures and documentation is published.*
