---
source-id: "langmem-conceptual-guide"
title: "Long-term Memory in LLM Applications — LangMem Conceptual Guide"
type: web
url: "https://langchain-ai.github.io/langmem/concepts/conceptual_guide/#memory-types"
fetched: 2026-03-23T00:00:00Z
hash: "08408b2f822ae6635b0cb954e9c8204d2614c5d52bc18ed32b4a4dc2852e387d"
---

# Long-term Memory in LLM Applications

Long-term memory allows agents to remember important information across conversations. LangMem provides ways to extract meaningful details from chats, store them, and use them to improve future interactions. At its core, each memory operation in LangMem follows the same pattern:

1. Accept conversation(s) and current memory state
2. Prompt an LLM to determine how to expand or consolidate the memory state
3. Respond with the updated memory state

The best memory systems are often application-specific. In designing yours, the following questions can serve as a useful guide:

1. **What** type of content should your agent learn: facts/knowledge? summary of past events? Rules and style?
2. **When** should the memories be formed (and **who** should form the memories)
3. **Where** should memories be stored? (in the prompt? Semantic store?). This largely determines how they will be recalled.

## Types of Memory

Memory in LLM applications can reflect some of the structure of human memory, with each type serving a distinct purpose in building adaptive, context-aware systems:

| Memory Type | Purpose | Agent Example | Human Example | Typical Storage Pattern |
| --- | --- | --- | --- | --- |
| Semantic | Facts & Knowledge | User preferences; knowledge triplets | Knowing Python is a programming language | Profile or Collection |
| Episodic | Past Experiences | Few-shot examples; Summaries of past conversations | Remembering your first day at work | Collection |
| Procedural | System Behavior | Core personality and response patterns | Knowing how to ride a bicycle | Prompt rules or Collection |

### Semantic Memory: Facts and Knowledge

[Semantic memory](https://en.wikipedia.org/wiki/Semantic_memory) stores the essential facts and other information that ground an agent's responses. Two common representations of semantic memory are collections (to record an unbounded amount of knowledge to be searched at runtime) and profiles (to record task-specific information that follows a strict schema that is easily looked up by user or agent).

#### Collection

Collections are what most people think of when they imagine agent long-term memory. In this type, memories are stored as individual documents or records. For each new conversation, the memory system can decide to insert new memories to the store.

Using a collection-type memory adds some complexity to the process of updating your memory state. The system must reconcile new information with previous beliefs, either *deleting*/*invalidating* or *updating*/*consolidating* existing memories. If the system over-extracts, this could lead to reduced precision of memories when your agent needs to search the store. If it under-extracts, this could lead to low recall. LangMem uses a memory enrichment process that strives to balance memory creation and consolidation, while letting you, the developer, customize the instructions to further shift the strength of each.

Finally, memory relevance is more than just semantic similarity. Recall should combine similarity with "importance" of the memory, as well as the memory's "strength", which is a function of how recently/frequently it was used.

*API: [create_memory_manager](https://langchain-ai.github.io/langmem/reference/memory/#langmem.create_memory_manager)*

```python
from langmem import create_memory_manager

manager = create_memory_manager(
    "anthropic:claude-3-5-sonnet-latest",
    instructions="Extract all noteworthy facts, events, and relationships. Indicate their importance.",
    enable_inserts=True,
)

# Process a conversation to extract semantic memories
conversation = [
    {"role": "user", "content": "I work at Acme Corp in the ML team"},
    {"role": "assistant", "content": "I'll remember that. What kind of ML work do you do?"},
    {"role": "user", "content": "Mostly NLP and large language models"}
]

memories = manager.invoke({"messages": conversation})
```

#### Profiles

**Profiles** are well-scoped for a particular task. Profiles are a single document that represents the current state, like a user's main goals with using an app, their preferred name and response style, etc. When new information arrives, it updates the existing document rather than creating a new one. This approach is ideal when you only care about the latest state and want to avoid remembering extraneous information.

*API: [create_memory_manager](https://langchain-ai.github.io/langmem/reference/memory/#langmem.create_memory_manager)*

```python
from langmem import create_memory_manager
from pydantic import BaseModel

class UserProfile(BaseModel):
    """Save the user's preferences."""
    name: str
    preferred_name: str
    response_style_preference: str
    special_skills: list[str]
    other_preferences: list[str]

manager = create_memory_manager(
    "anthropic:claude-3-5-sonnet-latest",
    schemas=[UserProfile],
    instructions="Extract user preferences and settings",
    enable_inserts=False,
)

conversation = [
    {"role": "user", "content": "Hi! I'm Alex but please call me Lex. I'm a wizard at Python and love making AI systems that don't sound like boring corporate robots 🤖"},
    {"role": "assistant", "content": "Nice to meet you, Lex! Love the anti-corporate-robot stance. How would you like me to communicate with you?"},
    {"role": "user", "content": "Keep it casual and witty - and maybe throw in some relevant emojis when it feels right ✨ Also, besides AI, I do competitive speedcubing!"},
]

profile = manager.invoke({"messages": conversation})[0]
```

Choose between profiles and collections based on how you'll use the data: profiles excel when you need quick access to current state and when you have data requirements about what type of information you can store. They are also easy to present to a user for manual editing. Collections are useful when you want to track knowledge across many interactions without loss of information, and when you want to recall certain information contextually rather than every time.

### Episodic Memory: Past Experiences

Episodic memory preserves successful interactions as learning examples that guide future behavior. Unlike semantic memory which stores facts, episodic memory captures the full context of an interaction — the situation, the thought process that led to success, and why that approach worked. These memories help the agent learn from experience, adapting its responses based on what has worked before.

*API: [create_memory_manager](https://langchain-ai.github.io/langmem/reference/memory/#langmem.create_memory_manager)*

```python
from pydantic import BaseModel, Field
from langmem import create_memory_manager

class Episode(BaseModel):
    """An episode captures how to handle a specific situation, including the reasoning process
    and what made it successful."""

    observation: str = Field(
        ...,
        description="The situation and relevant context"
    )
    thoughts: str = Field(
        ...,
        description="Key considerations and reasoning process"
    )
    action: str = Field(
        ...,
        description="What was done in response"
    )
    result: str = Field(
        ...,
        description="What happened and why it worked"
    )

manager = create_memory_manager(
    "anthropic:claude-3-5-sonnet-latest",
    schemas=[Episode],
    instructions="Extract examples of successful interactions. Include the context, thought process, and why the approach worked.",
    enable_inserts=True,
)
```

### Procedural Memory: System Instructions

Procedural memory encodes how an agent should behave and respond. It starts with system prompts that define core behavior, then evolves through feedback and experience. As the agent interacts with users, it refines these instructions, learning which approaches work best for different situations.

*API: [create_prompt_optimizer](https://langchain-ai.github.io/langmem/reference/prompt_optimization/#langmem.create_prompt_optimizer)*

```python
from langmem import create_prompt_optimizer

optimizer = create_prompt_optimizer(
    "anthropic:claude-3-5-sonnet-latest",
    kind="metaprompt",
    config={"max_reflection_steps": 3}
)

prompt = "You are a helpful assistant."
trajectory = [
    {"role": "user", "content": "Explain inheritance in Python"},
    {"role": "assistant", "content": "Here's a detailed theoretical explanation..."},
    {"role": "user", "content": "Show me a practical example instead"},
]
optimized = optimizer.invoke({
    "trajectories": [(trajectory, {"user_score": 0})],
    "prompt": prompt
})
```

## Writing Memories

Memories can form in two ways, each suited for different needs. Active formation happens during conversations, enabling immediate updates when critical context emerges. Background formation occurs between interactions, allowing deeper pattern analysis without impacting response time.

| Formation Type | Latency Impact | Update Speed | Processing Load | Use Case |
| --- | --- | --- | --- | --- |
| Active | Higher | Immediate | During Response | Critical Context Updates |
| Background | None | Delayed | Between/After Calls | Pattern Analysis, Summaries |

### Conscious Formation

Active memory formation happens during the conversation, enabling immediate updates when critical context emerges. This approach is easy to implement and lets the agent itself choose how to store and update its memory. However, it adds perceptible latency to user interactions, and it adds one more obstacle to the agent's ability to satisfy the user's needs.

### Subconscious Formation

"Subconscious" memory formation refers to the technique of prompting an LLM to reflect on a conversation after it occurs (or after it has been inactive for some period), finding patterns and extracting insights without slowing down the immediate interaction or adding complexity to the agent's tool choice decisions. This approach is perfect for ensuring higher recall of extracted information.

## Integration Patterns

LangMem's memory utilities are organized in two layers of integration patterns:

### 1. Core API

At its heart, LangMem provides functions that transform memory state without side effects. These primitives are the building blocks for memory operations:

* **Memory Managers**: Extract new memories, update or remove outdated memories, and consolidate and generalize from existing memories based on new conversation information
* **Prompt Optimizers**: Update prompt rules and core behavior based on conversation information (with optional feedback)

These core functions do not depend on any particular database or storage system. You can use them in any application.

### 2. Stateful Integration

The next layer up depends on LangGraph's long-term memory store. These components use the core API above to transform memories that exist in the store and upsert/delete them as needed when new conversation information comes in:

* **Store Managers**: Automatically persist extracted memories
* **Memory Management Tools**: Give agents direct access to memory operations

## Storage System

When using LangMem's stateful operators or platform services, the storage system is built on LangGraph's storage primitives.

### Memory Namespaces

Memories are organized into namespaces that allow for natural segmentation of data:

* **Multi-Level Namespaces**: Group memories by organization, user, application, or any other hierarchical structure
* **Contextual Keys**: Identify memories uniquely within their namespace
* **Structured Content**: Store rich, structured data with metadata for better organization

```python
# Organize memories by organization -> configurable user -> context
namespace = ("acme_corp", "{user_id}", "code_assistant")
```

Namespaces can include template variables (such as `"{user_id}"`) to be populated at runtime from `configurable` fields in the `RunnableConfig`.

### Flexible Retrieval

LangMem integrates directly with LangGraph's BaseStore interface for memory storage and retrieval. The storage system supports multiple ways to retrieve memories:

* **Direct Access**: Get a specific memory by key
* **Semantic Search**: Find memories by semantic similarity
* **Metadata Filtering**: Filter memories by their attributes
