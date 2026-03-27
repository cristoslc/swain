---
source-id: "collison-stripe-projects-announcement"
title: "Stripe Projects announcement"
type: web
url: "https://x.com/patrickc/status/2037190688950161709"
fetched: 2026-03-27T00:00:00Z
hash: "e1e7075cfb1c551d9cdcc3ac89f269098c15c325c4f1337b30ec903d3a913c53"
---

# Stripe Projects Announcement

**Author:** Patrick Collison (@patrickc), Stripe CEO
**Posted:** 2026-03-27
**Platform:** X (Twitter)
**URL:** https://x.com/patrickc/status/2037190688950161709

## Full Text

When @karpathy built MenuGen (https://karpathy.bearblog.dev/vibe-coding-menugen/), he said:

> "Vibe coding menugen was exhilarating and fun escapade as a local demo, but a bit of a painful slog as a deployed, real app. Building a modern app is a bit like assembling IKEA future. There are all these services, docs, API keys, configurations, dev/prod deployments, team and security features, rate limits, pricing tiers."

We've all run into this issue when building with agents: you have to scurry off to establish accounts, clicking things in the browser as though it's the antediluvian days of 2023, in order to unblock its superintelligent progress.

So we decided to build Stripe Projects to help agents instantly provision services from the CLI. For example, simply run:

```
$ stripe projects add posthog/analytics
```

And it'll create a PostHog account, get an API key, and (as needed) set up billing.

Projects is launching today as a developer preview. You can register for access (we'll make it available to everyone soon) at http://projects.dev. We're also rolling out support for many new providers over the coming weeks. (Get in touch if you'd like to make your service available.)

https://projects.dev
