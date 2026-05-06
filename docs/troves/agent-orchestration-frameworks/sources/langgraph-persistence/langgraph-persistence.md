---
title: LangGraph Persistence - Checkpoints, Threads, and State Management
url: https://docs.langchain.com/oss/python/langgraph/persistence
source-type: web-page
fetched: 2026-05-05
transcript-source: web-page
---

# LangGraph Persistence

## Overview

LangGraph has a built-in persistence layer using checkpointers to save graph state. Every super-step in the graph can be saved automatically.

## Checkpoints

### What Are Checkpoints?

Checkpointers in LangGraph:
- Save snapshots of graph state at each execution step
- Enable memory between interactions
- Support human-in-the-loop workflows
- Provide fault tolerance
- Stored in "threads"

### Key Capabilities

1. **Memory persistence**: Conversations survive crashes, restarts, and long breaks
2. **Time travel**: Fork graph state at arbitrary checkpoints to explore alternative trajectories
3. **Fault tolerance**: Restart from last successful step if nodes fail
4. **Pending writes**: Store writes from successful nodes even if others fail in the same super-step

## Thread-Based State Management

- Checkpoints are stored in threads
- Must specify a `thread_id` when invoking a graph with a checkpointer
- Thread's current and historical state can be retrieved
- Supports multiple concurrent threads

### Implementation Example

```python
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

# Define state
class State(TypedDict):
    foo: str
    bar: Annotated[list[str], add]

# Build graph
builder = StateGraph(State)
builder.add_node("node_a", node_a)
builder.add_edge(START, "node_a")

# Compile with checkpointer
memory = InMemorySaver()
graph = builder.compile(checkpointer=memory)

# Invoke with thread_id
config = {"configurable": {"thread_id": "thread-1"}}
result = graph.invoke({"foo": "hello"}, config)
```

## Checkpointer Implementations

### Built-in Options
- `InMemorySaver`: For development/testing
- `SqliteSaver`: Local persistence
- `PostgresSaver`: Production database persistence
- `RedisSaver`: Fast, TTL-based expiration
- `CouchbaseSaver`: Enterprise NoSQL
- `BedrockSessionSaver`: AWS Bedrock integration

### Production Usage
- 92% of production LangGraph deployments use checkpointing for conversation continuity
- Redis recommended for short-lived conversational agents
- PostgreSQL for durable long-term storage

## State Schema

LangGraph uses explicit, reducer-driven state schemas:
- Python's TypedDict for type safety
- Annotated types with reducer functions
- Prevents data loss in multi-agent systems

## Session Management

### Loading State
```python
# Load checkpoint from Redis and rehydrate
saved_state = checkpointer.get(thread_id)
result = graph.invoke(saved_state, config)
```

### Scaling Multiple Sessions
- Partition Redis keys by session
- Ensure atomic writes to avoid collisions
- Wrap in session manager class for transparency

## Best Practices

1. **Always use checkpointing in production**
2. **Choose storage backend based on TTL needs**
3. **Partition by session for multi-user apps**
4. **Implement atomic writes**
5. **Consider conversation history limits**

## Challenges

- `langgraph dev` command may ignore persistent checkpointer config
- Custom checkpointer implementations needed for some databases (e.g., MySQL)
- State management overhead for complex graphs

---

Sources:
- https://docs.langchain.com/oss/python/langgraph/persistence
- https://langgraphjs.guide/persistence/
- https://machinelearningplus.com/gen-ai/langgraph-persistence-checkpointing-save-resume/
