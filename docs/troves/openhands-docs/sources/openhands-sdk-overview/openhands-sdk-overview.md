---
title: "OpenHands Software Agent SDK Overview"
url: https://docs.openhands.dev/sdk
hostname: docs.openhands.dev
description: "Build AI agents that write software. A clean, modular SDK with production-ready tools."
date: 2025-01-13
sitename: OpenHands Documentation
type: web-page
---

# Software Agent SDK

> Build AI agents that write software. A clean, modular SDK with production-ready tools.

The OpenHands Software Agent SDK is a set of Python and REST APIs for building **agents that work with code**.

You can use the OpenHands Software Agent SDK for:

* One-off tasks, like building a README for your repo
* Routine maintenance tasks, like updating dependencies
* Major tasks that involve multiple agents, like refactors and rewrites

You can even use the SDK to build new developer experiences—it's the engine behind the [OpenHands CLI](/openhands/usage/cli/quick-start) and [OpenHands Cloud](/openhands/usage/cloud/openhands-cloud).

## Features

- **Single Python API**: A unified Python API that enables you to run agents locally or in the cloud, define custom agent behaviors, and create custom tools.
- **Pre-defined Tools**: Ready-to-use tools for executing Bash commands, editing files, browsing the web, integrating with MCP, and more.
- **REST-based Agent Server**: A production-ready server that runs agents anywhere, including Docker and Kubernetes, while connecting seamlessly to the Python API.

## Why OpenHands Software Agent SDK?

### Emphasis on coding

While other agent SDKs (e.g. [LangChain](https://python.langchain.com/docs/tutorials/agents/)) are focused on more general use cases, like delivering chat-based support or automating back-office tasks, OpenHands is purpose-built for software engineering.

### State-of-the-Art Performance

OpenHands is a top performer across a wide variety of benchmarks, including SWE-bench, SWT-bench, and multi-SWE-bench. The SDK includes a number of state-of-the-art agentic features developed by our research team, including:

* Task planning and decomposition
* Automatic context compression
* Security analysis
* Strong agent-computer interfaces

OpenHands has attracted researchers from a wide variety of academic institutions, and is [becoming the preferred harness](https://x.com/Alibaba_Qwen/status/1947766835023335516) for evaluating LLMs on coding tasks.

### Free and Open Source

OpenHands is also the leading open source framework for coding agents. It's MIT-licensed, and can work with any LLM—including big proprietary LLMs like Claude and OpenAI, as well as open source LLMs like Qwen and Devstral.

Other SDKs (e.g. [Claude Code](https://github.com/anthropics/claude-agent-sdk-python)) are proprietary and lock you into a particular model. Given how quickly models are evolving, it's best to stay model-agnostic!

## Get Started

- [Getting Started Guide](/sdk/getting-started): Install the SDK, run your first agent, and explore the guides.

## Learn the SDK

- [Core Concepts](/sdk/arch/overview): Understand the SDK's architecture: agents, tools, workspaces, and more.
- [API Reference](https://github.com/OpenHands/software-agent-sdk/tree/main/openhands-sdk/openhands/sdk): Explore the complete SDK API and source code.

## Build with Examples

- [Standalone SDK](/sdk/guides/hello-world): Build local agents with custom tools and capabilities.
- [Remote Execution](/sdk/guides/agent-server/local-server): Run agents on remote servers with Docker sandboxing.
- [GitHub Workflows](/sdk/guides/github-workflows/todo-management): Automate repository tasks with agent-powered workflows.

## Community

- [Join Slack](https://openhands.dev/joinslack): Connect with the OpenHands community on Slack.
- [GitHub Repository](https://github.com/OpenHands/software-agent-sdk): Contribute to the SDK or report issues on GitHub.
