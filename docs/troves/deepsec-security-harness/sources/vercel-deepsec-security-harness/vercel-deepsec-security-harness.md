---
source-id: "vercel-deepsec-security-harness"
title: "Introducing deepsec: The Security Harness for Finding Vulnerabilities in Your Codebase"
type: web
url: "https://vercel.com/blog/introducing-deepsec-find-and-fix-vulnerabilities-in-your-code-base"
fetched: 2026-05-05T02:39:07Z
---

# Introducing deepsec: The Security Harness for Finding Vulnerabilities in Your Codebase

**Published:** May 4, 2026 | **Author:** Malte Ubl
**Links:** [GitHub repo](https://github.com/vercel-labs/deepsec/) | [Documentation](https://github.com/vercel-labs/deepsec/#docs)

## Overview

`deepsec` is an open-source security harness powered by coding agents. It runs on your own infrastructure and surfaces hard-to-find issues in large codebases. You can run `deepsec` on your laptop without setting up a cloud service for privileged source code access. For inference, you can use your existing Claude or Codex subscription without any additional setup.

Scanning large repos can take multiple days on a single machine. To run research jobs in parallel, `deepsec` supports optional fanout to Vercel Sandboxes for remote execution. Scans on Vercel's codebases routinely scale up to 1,000+ concurrent sandboxes.

## Architecture

At its core, `deepsec` uses `claude` and `codex` to perform tailored investigation of a codebase using Opus 4.7 at max effort and GPT 5.5 at xhigh reasoning.

Scans start with static analysis to identify security-sensitive files, then coding agents investigate each candidate, tracing data flows, checking for mitigations, and producing actionable findings with severity ratings.

### Workflow stages

- **Scan**: Performs a regex-only scan of all files for security-sensitive areas that subsequent steps will focus on.
- **Investigate**: Agents investigate each file identified in the scan.
- **Revalidate**: A second agent run validates investigation findings to remove false positives and reclassify severity.
- **Enrich**: Once investigation is complete, an agent uses git metadata and other optional services to identify the contributors responsible for fixing each issue.
- **Export**: The `export` command formats the findings as instructions so that they can be turned into tickets for humans and coding agents.

## Running `deepsec` on Production Code

`deepsec` has been highly useful on Vercel's own monorepos and for their customers' codebases. During development, Vercel ran `deepsec` on several open source repositories of Vercel customers and partners.

> We've been on a lookout for a tool to do security scans on our open source repositories. deepsec's scan have been the most thorough, with most findings, and good true-positive rate.
> — James Perkins, Co-founder and CEO @ [Unkey](https://www.unkey.com/)

In a scan of the [open source version](https://github.com/dubinc/dub) of [dub.co](http://dub.co) — a marketing attribution platform for affiliate programs and short links with authenticated access, database interaction, and multiple backend services — deepsec surfaced issues that Steven Tey called actionable:

> We get a lot of automated security reports, but most of them aren't actionable. deepsec is the first tool that's surfaced the kind of issues we'd actually want a security engineer to flag, and it runs on infrastructure we control.
> — Steven Tey, Founder and CEO @ [dub.co](https://dub.co/)

Running against Vercel's own monorepos, `deepsec` identified subtle edge cases in auth conditions, leading to the development of a [custom scanner plugin](https://github.com/vercel-labs/deepsec/blob/main/docs/writing-matchers.md) that covers every authentication path in the code.

### False positives and best uses

Some of `deepsec`'s findings will be false positives. The false positive rate is roughly 10-20%. Given the impact of true positive findings, Vercel considers this acceptable, and the `revalidate` step is designed to further reduce false positives.

`deepsec` works best for applications and services. It may be usable for libraries and frameworks, but those would likely require custom prompts and scanners.

## Customization and plugins

`deepsec` ships with a plugin system for adapting it to your codebase. The most common plugins are custom scanners: regex matchers tuned to your auth model, data layer, or team conventions. Vercel recommends using `deepsec` with your coding agent and asking it to write those matchers based on findings from an initial scan:

```
Inspect previous runs against ./my-app.
Are there custom deepsec matchers we should
add to find more candidates for vulnerabilities?
```

## "Cyber" model compatibility

Both Anthropic and OpenAI offer "cyber" versions of their most capable models, fine-tuned to accept security tasks the base models won't. `deepsec` works with these, but is also fully functional with off-the-shelf models.

`deepsec` ships with a classifier that checks whether the task was refused after each research step. For the prompts `deepsec` uses, refusals are a non-issue for both Opus 4.7 and GPT 5.5.

## Getting started

Run `npx deepsec init` at the root of your repository. This creates a `.deepsec` directory used to configure the system and store a catalog of investigations. Follow the output of the command.
