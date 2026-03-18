---
source-id: "docker-agent-tutorial-coding-agent"
title: "Building a coding agent | Docker Agent Docs"
type: web
url: "https://docs.docker.com/ai/docker-agent/tutorial/"
fetched: 2026-03-17T00:00:00Z
hash: "632df0c3aaea7a0b1a73eb003ba05bdea55b5a8f8ad4682b3715e55abbc5761f"
---

# Building a Coding Agent — Docker Agent Tutorial

This tutorial teaches you how to build a coding agent that can help with software development tasks. You'll start with a basic agent and progressively add capabilities until you have a production-ready assistant that can read code, make changes, run tests, and even look up documentation.

## What you'll build

A coding agent that can:
- Read and modify files in your project
- Run commands like tests and linters
- Follow a structured development workflow
- Look up documentation when needed
- Track progress through multi-step tasks

## Prerequisites

- Docker Agent installed
- API key configured — set `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` in your environment
- A project to work with — any codebase where you want agent assistance

## Creating your first agent

An agent is defined in a YAML configuration file. The minimal agent needs just a model and instructions.

Create a file named `agents.yml`:

```yaml
agents:
  root:
    model: openai/gpt-5
    description: A basic coding assistant
    instruction: |
      You are a helpful coding assistant. Help me write and understand code.
```

Run your agent:

```bash
$ docker agent run agents.yml
```

The agent can answer coding questions, but it can't see your files or run commands yet.

## Adding tools

A coding agent needs to interact with your project files and run commands. Enable these capabilities by adding toolsets.

```yaml
agents:
  root:
    model: openai/gpt-5
    description: A coding assistant with filesystem access
    instruction: |
      You are a helpful coding assistant. You can read and write files to help me
      develop software. Always check if code works before finishing a task.
    toolsets:
      - type: filesystem
      - type: shell
```

Your agent can now:
- Read and write files in the current directory
- Execute shell commands
- Explore your project structure

> **Note:** The agent operates in the current directory by default and will request permission if it needs to access other directories.

## Structuring agent instructions

Generic instructions produce generic results. For production use, you want your agent to follow a specific workflow and understand your project's conventions.

This example shows a Go development agent, but you can adapt the pattern for any language:

```yaml
agents:
  root:
    model: anthropic/claude-sonnet-4-5
    description: Expert Go developer
    instruction: |
      Your goal is to help with code-related tasks by examining, modifying, and validating code changes.

      <TASK>
      # Workflow:
      # 1. Analyze: Understand requirements and identify relevant code.
      # 2. Examine: Search for files, analyze structure and dependencies.
      # 3. Modify: Make changes following best practices.
      # 4. Validate: Run linters/tests. If issues found, return to Modify.
      </TASK>

      Constraints:
      - Be thorough in examination before making changes
      - Always validate changes before considering the task complete
      - Write code to files, don't show it in chat

      ## Development Workflow
      - `go build ./...` - Build the application
      - `go test ./...` - Run tests
      - `golangci-lint run` - Check code quality
    add_date: true
    add_environment_info: true
    toolsets:
      - type: filesystem
      - type: shell
      - type: todo
```

The structured instructions give your agent:
- A clear workflow to follow (analyze, examine, modify, validate)
- Project-specific commands to run
- Constraints that prevent common mistakes
- Context about the environment (`add_date` and `add_environment_info`)

The `todo` toolset helps the agent track progress through multi-step tasks.

## Composing multiple agents

Complex tasks often benefit from specialized agents. Add a librarian agent that can search for documentation while your main agent stays focused on coding:

```yaml
agents:
  root:
    model: anthropic/claude-sonnet-4-5
    description: Expert Go developer
    instruction: |
      Your goal is to help with code-related tasks by examining, modifying, and validating code changes.
      When you need to look up documentation or research how something works, ask the librarian agent.
      (rest of instructions from previous section...)
    toolsets:
      - type: filesystem
      - type: shell
      - type: todo
    sub_agents:
      - librarian

  librarian:
    model: anthropic/claude-haiku-4-5
    description: Documentation researcher
    instruction: |
      You are the librarian. Your job is to find relevant documentation, articles, or resources
      to help the developer agent. Search the internet and fetch web pages as needed.
    toolsets:
      - type: mcp
        ref: docker:duckduckgo
      - type: fetch
```

Your main agent will delegate the research to the librarian, then use that information to modify your code. This keeps the main agent's context focused on the coding task while still having access to up-to-date documentation.

Using a smaller, faster model (Haiku) for the librarian saves costs since documentation lookup doesn't need the same reasoning depth as code changes.

## Adapting for your project

**Update the development commands** — replace the Go commands with your project's workflow:

```yaml
## Development Workflow
- `npm test` - Run tests
- `npm run lint` - Check code quality
- `npm run build` - Build the application
```

**Add project-specific constraints** — if your agent keeps making the same mistakes, add explicit constraints:

```yaml
Constraints:
- Always run tests before considering a task complete
- Follow the existing code style in src/ directories
- Never modify files in the generated/ directory
- Use TypeScript strict mode for new files
```

**Choose the right models:**

For coding tasks, use reasoning-focused models:
- `anthropic/claude-sonnet-4-5` — Strong reasoning, good for complex code
- `openai/gpt-5` — Fast, good general coding ability

For auxiliary tasks like documentation lookup, smaller models work well:
- `anthropic/claude-haiku-4-5` — Fast and cost-effective
- `openai/gpt-5-mini` — Good for simple tasks

**Iterate based on usage** — when you notice issues:
1. Add specific instructions to prevent the problem
2. Update constraints to guide behavior
3. Add relevant commands to the development workflow
4. Consider adding specialized sub-agents for complex areas

## What you learned

- Create a basic Docker Agent configuration
- Add tools to enable agent capabilities
- Write structured instructions for consistent behavior
- Compose multiple agents for specialized tasks
- Adapt agents for different programming languages and workflows
