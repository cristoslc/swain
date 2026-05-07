---
title: AutoGen - A Framework for Building AI Agents and Applications
url: https://microsoft.github.io/autogen/stable/
source-type: web-page
fetched: 2026-05-05
transcript-source: web-page
---

# AutoGen - A Framework for Building AI Agents and Applications

## Overview

AutoGen is a Microsoft framework for building AI agents and applications with multiple abstraction layers.

## Architecture Layers

### AgentChat
- Programming framework for building conversational single and multi-agent applications
- Built on Core
- Requires Python 3.10+
- Quick prototyping with agents using Python

```python
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

agent = AssistantAgent("assistant", OpenAIChatCompletionClient(model="gpt-4o"))
```

### Core
- Event-driven programming framework
- Building scalable multi-agent AI systems
- Use cases:
  - Deterministic and dynamic agentic workflows for business processes
  - Research on multi-agent collaboration
  - Distributed agents for multi-language applications

### Extensions (autogen-ext)
- Implementations of Core and AgentChat components
- Interface with external services or other libraries

Built-in extensions:
- `McpWorkbench` for using Model-Context Protocol (MCP) servers
- `OpenAIAssistantAgent` for using Assistant API
- `DockerCommandLineCodeExecutor` for running code in Docker
- `GrpcWorkerAgentRuntime` for distributed agents

### Studio (AutoGen Studio)
- Web-based UI for prototyping with agents without writing code
- Built on AgentChat
- Quick start for new AutoGen users

```bash
pip install -U autogenstudio
autogenstudio ui --port 8080 --appdir ./myapp
```

## Key Features

### Conversational Agents
- Multi-turn conversation support
- Group chat patterns
- Human-in-the-loop scenarios
- Natural language interaction focus

### Multi-Agent Support
- Single and multi-agent applications
- Agent-to-agent communication
- Collaborative problem solving

### MCP Integration
- Native MCP server support via McpWorkbench
- Connect to external tools and data sources

### Distributed Agents
- GrpcWorkerAgentRuntime for distributed scenarios
- Multi-language application support

## Version History

- Current: 0.2+ with AgentChat, Core, Extensions layers
- Legacy: 0.2 Docs available for migration

## Microsoft Ecosystem

- Developed by Microsoft
- Integrates with Azure OpenAI
- .NET support available

---

Source: https://microsoft.github.io/autogen/stable/
