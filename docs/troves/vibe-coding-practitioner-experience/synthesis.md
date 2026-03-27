# Synthesis: Vibe Coding Practitioner Experience

## Key findings

### The 80/20 illusion

Karpathy's local prototype came together quickly using Cursor + Claude 3.7 -- a beautiful React frontend with animations and responsive design materialized in short order. He felt 80% done, but the local demo represented closer to 20% of the total effort. The remaining 80% was production deployment: wiring up APIs, authentication, payments, environment configuration, and dev-to-prod promotion across multiple services.

### The friction is in the browser, not the editor

The most striking observation is where the time actually went. Karpathy spent most of his effort not in the code editor but in browser tabs -- navigating Vercel settings, Clerk dashboards, Stripe configuration, Google Cloud Console OAuth setup, and DNS records. This configuration work is not accessible to LLMs: it lives in browser-based UIs, behind logins, across fragmented service dashboards. The code itself was the easy part.

### LLM knowledge decay

Every external service integration hit the same pattern: Claude hallucinated deprecated APIs, model names, and code patterns. OpenAI's API conventions had changed. Replicate's API had shifted to streaming responses that neither Karpathy nor Claude understood. Clerk authentication code was ~1000 lines of deprecated API calls. Stripe docs served JavaScript when the project used TypeScript. Each required manual doc copy-pasting to get unstuck, undermining the "vibe coding" flow.

### Service ecosystem designed for teams, not solo/LLM-assisted devs

The entire infrastructure stack -- Vercel, Clerk, Stripe, Google OAuth -- was designed for teams of professional web developers in a pre-LLM world. This manifests as: convoluted permission menus, mandatory dev-to-prod promotion ceremonies, domain ownership requirements for auth, rate limiting that blocks new legitimate accounts, and environment variable management that silently breaks deploys. Karpathy nearly quit during the Clerk configuration phase.

### Forward-looking solutions

Karpathy identifies four directions that could reduce friction:

1. **Batteries-included platforms** -- opinionated, preconfigured with domain, hosting, auth, payments, database, and server functions out of the box
2. **LLM-friendly service APIs** -- CLI tools, curl-configurable backends, markdown docs; talk to the LLM, not the developer
3. **Simpler tech stacks** -- plain HTML/CSS/JS + Python backend (FastAPI + Fly.io) instead of the serverless multiverse
4. **Apps as prompts** -- many simple apps could be reduced to a prompt + structured output, akin to custom GPTs or Artifacts

## Gaps

- **No comparative data**: this is a single practitioner's account. Other vibe coders may hit different friction points or use different mitigation strategies. Additional sources from other practitioners would strengthen the findings.
- **Platform response not covered**: Karpathy describes the problems but does not cover how platforms are adapting. For Stripe's specific response to LLM-assisted development (Agent Toolkit, MCP server, docs-as-context), see the related trove [`agent-service-provisioning`](../agent-service-provisioning/).
- **No longitudinal tracking**: the post is a snapshot from April 2025. Whether these friction points improve over subsequent months is not addressed.
- **Database/queue layer unexplored**: Karpathy abandoned the persistence layer (Supabase, Upstash) as "too much bear," so the friction of that integration remains unmeasured.
