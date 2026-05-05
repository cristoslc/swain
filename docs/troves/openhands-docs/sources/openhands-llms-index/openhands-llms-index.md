---
title: "OpenHands Documentation Index (llms.txt)"
url: https://docs.openhands.dev/llms.txt
hostname: docs.openhands.dev
description: "LLM-friendly index of OpenHands documentation (V1)"
date: 2025-01-13
sitename: OpenHands Documentation
type: web-page
---

# OpenHands Docs

> LLM-friendly index of OpenHands documentation (V1). Legacy V0 docs pages are intentionally excluded.

The sections below intentionally separate OpenHands product documentation (Web App Server / Cloud / CLI) from the OpenHands Software Agent SDK.

## OpenHands Software Agent SDK

- ACP Agent: Delegate to an ACP-compatible server (Claude Code, Gemini CLI, etc.) instead of calling an LLM directly.
- Agent: High-level architecture of the reasoning-action loop
- Agent Server Package: HTTP API server for remote agent execution with workspace isolation, container orchestration, and multi-user support.
- Agent Settings: Configure, serialize, and recreate agents from structured settings.
- Agent Skills & Context: Skills add specialized behaviors, domain knowledge, and context-aware triggers to your agent through structured prompts.
- API-based Sandbox: Connect to hosted API-based agent server for fully managed infrastructure.
- Apptainer Sandbox: Run agent server in rootless Apptainer containers for HPC and shared computing environments.
- Ask Agent Questions: Get sidebar replies from the agent during conversation execution without interrupting the main flow.
- Assign Reviews: Automate PR management with intelligent reviewer assignment and workflow notifications using OpenHands Agent
- Browser Session Recording: Record and replay your agent's browser sessions using rrweb.
- Browser Use: Enable web browsing and interaction capabilities for your agent.
- Condenser: High-level architecture of the conversation history compression system
- Context Condenser: Manage agent memory by condensing conversation history to save tokens.
- Conversation: High-level architecture of the conversation orchestration system
- Conversation with Async: Use async/await for concurrent agent operations and non-blocking execution.
- Creating Custom Agent: Learn how to design specialized agents with custom tool sets
- Critic (Experimental): Real-time evaluation of agent actions using an LLM-based critic model, with built-in iterative refinement.
- Custom Tools: Tools define what agents can do. The SDK includes built-in tools for common operations and supports creating custom tools for specialized needs.
- Custom Tools with Remote Agent Server: Learn how to use custom tools with a remote agent server by building a custom base image that includes your tool implementations.
- Custom Visualizer: Customize conversation visualization by creating custom visualizers or configuring the default visualizer.
- Design Principles: Core architectural principles guiding the OpenHands Software Agent SDK's development.
- Docker Sandbox: Run agent server in isolated Docker containers for security and reproducibility.
- Events: High-level architecture of the typed event framework
- Exception Handling: Provider-agnostic exceptions raised by the SDK and recommended patterns for handling them.
- FAQ: Frequently asked questions about the OpenHands SDK
- File-Based Agents: Define specialized sub-agents as simple Markdown files with YAML frontmatter — no Python code required.
- Fork a Conversation: Branch off an existing conversation for follow-up exploration without contaminating the original.
- Getting Started: Install the OpenHands SDK and build AI agents that write software.
- GPT-5 Preset (ApplyPatchTool): Use the GPT-5 preset to build an agent that swaps the standard FileEditorTool for ApplyPatchTool.
- Hello World: The simplest possible OpenHands agent - configure an LLM, create an agent, and complete a task.
- Hooks: Use lifecycle hooks to observe, log, and customize agent execution.
- Image Input: Send images to multimodal agents for vision-based tasks and analysis.
- Interactive Terminal: Enable agents to interact with terminal applications like ipython, python REPL, and other interactive CLI tools.
- Iterative Refinement: Implement iterative refinement workflows where agents refine their work based on critique feedback until quality thresholds are met.
- LLM: High-level architecture of the provider-agnostic language model interface
- LLM Fallback Strategy: Automatically try alternate LLMs when the primary model fails with a transient error.
- LLM Profile Store: Save, load, and manage reusable LLM configurations so you never repeat setup code again.
- LLM Registry: Dynamically select and configure language models using the LLM registry.
- LLM Streaming: Stream LLM responses token-by-token for real-time display and interactive user experiences.
- LLM Subscriptions: Use your ChatGPT Plus/Pro subscription to access Codex models without consuming API credits.
- Local Agent Server: Run agents through a local HTTP server with RemoteConversation for client-server architecture.
- MCP Integration: High-level architecture of Model Context Protocol support
- Metrics Tracking: Track token usage, costs, and latency metrics for your agents.
- Model Context Protocol: Model Context Protocol (MCP) enables dynamic tool integration from external servers. Agents can discover and use MCP-provided tools automatically.
- Model Routing: Route agent's LLM requests to different models.
- Observability & Tracing: Enable OpenTelemetry tracing to monitor and debug your agent's execution with tools like Laminar, MLflow, Honeycomb, or any OTLP-compatible backend.
- OpenHands Cloud Workspace: Connect to OpenHands Cloud for fully managed sandbox environments with optional SaaS credential inheritance.
- Overview: Understanding the OpenHands Software Agent SDK's package structure, component interactions, and execution models.
- Overview: Run agents on remote servers with isolated workspaces for production deployments.
- Parallel Tool Execution: Execute multiple tools concurrently within a single LLM response to improve throughput for independent operations.
- Pause and Resume: Pause agent execution, perform operations, and resume without losing state.
- Persistence: Save and restore conversation state for multi-session workflows.
- Plugins: Plugins bundle skills, hooks, MCP servers, agents, and commands into reusable packages that extend agent capabilities.
- PR Review: Use OpenHands Agent to generate meaningful pull request review
- Reasoning: Access model reasoning traces from Anthropic extended thinking and OpenAI responses API.
- SDK Package: Core framework components for building agents - the reasoning loop, state management, and extensibility system.
- Secret Registry: Provide environment variables and secrets to agent workspace securely.
- Security: High-level architecture of action security analysis and validation
- Security & Action Confirmation: Control agent action execution through confirmation policy and security analyzer.
- Send Message While Running: Interrupt running agents to provide additional context or corrections.
- Skill: High-level architecture of the reusable prompt system
- Software Agent SDK: Build AI agents that write software. A clean, modular SDK with production-ready tools.
- Stuck Detector: Detect and handle stuck agents automatically with timeout mechanisms.
- Sub-Agent Delegation: Enable parallel task execution by delegating work to multiple sub-agents that run independently and return consolidated results.
- Task Tool Set: Delegate complex work to specialized sub-agents that run synchronously and return results to the parent agent.
- Theory of Mind (TOM) Agent: Enable your agent to understand user intent and preferences through Theory of Mind capabilities, providing personalized guidance based on user modeling.
- TODO Management: Implement TODOs using OpenHands Agent
- Tool System & MCP: High-level architecture of the action-observation tool framework
- Workspace: High-level architecture of the execution environment abstraction

## OpenHands CLI

- Command Reference: Complete reference for all OpenHands CLI commands and options
- Critic (Experimental): Automatic task success prediction and iterative refinement for OpenHands LLM Provider users
- GUI Server: Launch the full OpenHands web GUI using Docker
- Headless Mode: Run OpenHands without UI for scripting, automation, and CI/CD pipelines
- IDE Integration Overview: Use OpenHands directly in your favorite code editor through the Agent Client Protocol
- Installation: Install the OpenHands CLI on your system
- JetBrains IDEs: Configure OpenHands with IntelliJ IDEA, PyCharm, WebStorm, and other JetBrains IDEs
- MCP Servers: Manage Model Context Protocol servers to extend OpenHands capabilities
- OpenHands Cloud: Create and manage OpenHands Cloud conversations from the CLI
- Quick Start: Get started with OpenHands CLI in minutes
- Resume Conversations: How to resume previous conversations in the OpenHands CLI
- Terminal (CLI): Use OpenHands interactively in your terminal with the command-line interface
- Toad Terminal: Use OpenHands with the Toad universal terminal interface for AI agents
- VS Code: Use OpenHands in Visual Studio Code with the VSCode ACP community extension
- Web Interface: Access the OpenHands CLI through your web browser
- Zed IDE: Configure OpenHands with the Zed code editor through the Agent Client Protocol

## OpenHands Web App Server

- About OpenHands
- API Keys Settings: View your OpenHands LLM key and create API keys to work with OpenHands programmatically.
- Application Settings: Configure application-level settings for OpenHands.
- Automated Code Review: Set up automated PR reviews using OpenHands and the Software Agent SDK
- Automations Overview: Create scheduled tasks that run automatically in OpenHands Cloud and Enterprise.
- AWS Bedrock: OpenHands uses LiteLLM to make calls to AWS Bedrock models.
- Azure: OpenHands uses LiteLLM to make calls to Azure's chat models.
- Backend Architecture
- COBOL Modernization: Modernizing legacy COBOL systems with OpenHands
- Configuration Options: How to configure OpenHands V1 (Web UI, env vars, and sandbox settings).
- Configure: High level overview of configuring the OpenHands Web interface.
- Creating Automations: Learn how to create scheduled automations using the Automation Skill.
- Custom LLM Configurations: OpenHands supports defining multiple named LLM configurations in your config.toml file.
- Custom Sandbox: This guide is for users that would like to use their own custom Docker image for the runtime.
- Debugging
- Dependency Upgrades: Automating dependency updates and upgrades with OpenHands
- Development Overview: This guide provides an overview of the key documentation resources available in the OpenHands repository.
- Docker Sandbox: The recommended sandbox provider for running OpenHands locally.
- Environment Variables Reference: Complete reference of all environment variables supported by OpenHands
- Evaluation Harness
- Event-Based Automations: Trigger automations from GitHub events or custom webhooks instead of cron schedules.
- Good vs. Bad Instructions: Learn how to write effective instructions for OpenHands
- Google Gemini/Vertex: OpenHands uses LiteLLM to make calls to Google's chat models.
- Groq: OpenHands uses LiteLLM to make calls to chat models on Groq.
- Hooks: Use lifecycle hooks to control agent behavior - block dangerous commands, enforce quality checks before stopping, inject context, and more.
- Incident Triage: Using OpenHands to investigate and resolve production incidents
- Integrations Settings: How to setup and modify the various integrations in OpenHands.
- Key Features
- Language Model (LLM) Settings: This page goes over how to set the LLM to use in OpenHands.
- LiteLLM Proxy: OpenHands supports using the LiteLLM proxy to access various LLM providers.
- Local LLMs: When using a Local LLM, OpenHands may have limited functionality.
- Main Agent and Capabilities
- Managing Automations: List, update, enable, disable, and delete your automations.
- Model Context Protocol (MCP): This page outlines how to configure and use the Model Context Protocol (MCP) in OpenHands.
- Moonshot AI: How to use Moonshot AI models with OpenHands
- OpenAI: OpenHands uses LiteLLM to make calls to OpenAI's chat models.
- OpenHands: OpenHands LLM provider with access to state-of-the-art (SOTA) agentic coding models.
- OpenHands GitHub Action: This guide explains how to use the OpenHands GitHub Action in your own projects.
- OpenHands in Your SDLC: How OpenHands fits into your software development lifecycle
- OpenRouter: OpenHands uses LiteLLM to make calls to chat models on OpenRouter.
- Overview: OpenHands can connect to any LLM supported by LiteLLM.
- Overview: Where OpenHands runs code in V1: Docker sandbox, Process, or Remote.
- Process Sandbox: Run the agent server as a local process without container isolation.
- Prompting Best Practices: When working with OpenHands AI software developer, providing clear and effective prompts is key to getting accurate and useful responses.
- Remote Sandbox: Run conversations in a remote sandbox environment.
- Repository Customization: You can customize how OpenHands interacts with your repository by creating a `.openhands` directory at the root level.
- REST API (V1): Overview of the current V1 REST endpoints used by the Web app.
- Runtime Architecture
- Search Engine Setup: Configure OpenHands to use Tavily as a search engine.
- Secrets Management: How to manage secrets in OpenHands.
- Setup: Getting started with running OpenHands on your own.
- Spark Migrations: Migrating Apache Spark applications with OpenHands
- Troubleshooting
- Tutorial Library: Centralized hub for OpenHands tutorials and examples
- Use Cases Overview: Explore how OpenHands can help with common software development challenges
- Vulnerability Remediation: Using OpenHands to identify and fix security vulnerabilities in your codebase
- WebSocket Connection
- When to Use OpenHands: Guidance on when OpenHands is the right tool for your task

## OpenHands Cloud

- Bitbucket Integration: This guide walks you through the process of installing OpenHands Cloud for your Bitbucket repositories.
- Cloud API: OpenHands Cloud provides a REST API that allows you to programmatically interact with OpenHands.
- Cloud UI: The Cloud UI provides a web interface for interacting with OpenHands.
- Getting Started: Getting started with OpenHands Cloud.
- GitHub Integration: This guide walks you through the process of installing OpenHands Cloud for your GitHub repositories.
- GitLab Integration
- Jira Cloud Integration: Complete guide for setting up Jira Cloud integration with OpenHands Cloud.
- Jira Data Center Integration (Coming soon...): Complete guide for setting up Jira Data Center integration with OpenHands Cloud.
- Linear Integration (Coming soon...): Complete guide for setting up Linear integration with OpenHands Cloud.
- Plugin Launcher: Use the OpenHands Cloud `/launch` route to open a conversation with plugins or skills pre-configured from a Git repository.
- Project Management Tool Integrations (Coming soon...): Overview of OpenHands Cloud integrations with project management platforms.
- Slack Integration: This guide walks you through installing the OpenHands Slack app.

## OpenHands Overview

- Community: Learn about the OpenHands community, mission, and values
- Contributing: Join us in building OpenHands and the future of AI.
- FAQs: Frequently asked questions about OpenHands.
- First Projects: So you've run OpenHands. Now what?
- General Skills: General guidelines for OpenHands to work more effectively with the repository.
- Global Skills: Global skills are keyword-triggered skills that apply to all OpenHands users.
- Introduction: Welcome to OpenHands, a community focused on AI-driven development
- Keyword-Triggered Skills: Keyword-triggered skills provide OpenHands with specific instructions that are activated when certain keywords appear in the prompt.
- Model Context Protocol (MCP): Model Context Protocol support across OpenHands platforms
- Organization and User Skills: Organizations and users can define skills that apply to all repositories belonging to the organization or user.
- Overview: Skills are specialized prompts that enhance OpenHands with domain-specific knowledge, expert guidance, and automated task handling.
- Quick Start: Choose how you want to run OpenHands

## Other

- Enterprise vs. Open Source: Compare OpenHands Enterprise and Open Source offerings to choose the right option for your team
- Kubernetes Installation: Deploy OpenHands Enterprise into your own Kubernetes cluster using Helm
- OpenHands Enterprise: Run AI coding agents on your own infrastructure with complete control
- Quick Start: Get started with a 30-day trial of OpenHands Enterprise.
- Resource Limits: Configure memory, CPU, and storage for OpenHands Enterprise components
