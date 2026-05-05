---
title: "OpenHands Agent Architecture"
url: https://docs.openhands.dev/sdk/arch/agent
hostname: docs.openhands.dev
description: "High-level architecture of the reasoning-action loop"
date: 2025-01-13
sitename: OpenHands Documentation
type: web-page
---

# Agent

> High-level architecture of the reasoning-action loop

The **Agent** component implements the core reasoning-action loop that drives autonomous task execution.

## Core Responsibilities

The Agent system has four primary responsibilities:

1. **Reasoning-Action Loop** - Query LLM to generate next actions based on conversation history
2. **Tool Orchestration** - Select and execute tools, handle results and errors
3. **Context Management** - Apply skills, manage conversation history via condensers
4. **Security Validation** - Analyze proposed actions for safety before execution

## Key Components

| Component | Purpose | Design |
|-----------|---------|--------|
| `Agent` | Main implementation | Stateless reasoning-action loop executor |
| `AgentBase` | Abstract base class | Defines agent interface and initialization |
| `AgentContext` | Context container | Manages skills, prompts, and metadata |
| `Condenser` | History compression | Reduces context when token limits approached |
| `SecurityAnalyzer` | Safety validation | Evaluates action risk before execution |

## Reasoning-Action Loop

The agent operates through a **single-step execution model**:

1. **Pending Actions**: If actions awaiting confirmation exist, execute them
2. **Condensation**: Compress history if condenser exists
3. **LLM Query**: Query LLM with messages from event history
4. **Response Parsing**: Parse LLM response into events (ActionEvent or MessageEvent)
5. **Confirmation Check**: If actions need user approval, set waiting status
6. **Action Execution**: Execute tools and create ObservationEvents

**Key Characteristics:**
- **Stateless**: Agent holds no mutable state between steps
- **Event-Driven**: Reads from event history, writes new events
- **Interruptible**: Each step is atomic and can be paused/resumed

## Agent Context

The agent applies `AgentContext` which includes **skills** and **prompts**:

| Skill Type | Activation | Use Case |
|------------|------------|----------|
| **repo** | Always included | Project-specific context, conventions |
| **knowledge** | Trigger words/patterns | Domain knowledge, special behaviors |

## Tool Execution

Tools follow a **strict action-observation pattern**:

**Execution Modes:**

| Mode | Behavior | Use Case |
|------|----------|----------|
| **Direct** | Execute immediately | Development, trusted environments |
| **Confirmation** | Store as pending, wait for approval | High-risk actions, production |

**Security Integration:**
- Low Risk: Execute immediately
- Medium Risk: Log warning, execute with monitoring
- High Risk: Block execution, request confirmation

## Component Relationships

- **Conversation → Agent**: Orchestrates step execution, provides event history
- **Agent → LLM**: Queries for next actions, receives tool calls or messages
- **Agent → Tools**: Executes actions, receives observations
- **AgentContext → Agent**: Injects skills and prompts into LLM queries
