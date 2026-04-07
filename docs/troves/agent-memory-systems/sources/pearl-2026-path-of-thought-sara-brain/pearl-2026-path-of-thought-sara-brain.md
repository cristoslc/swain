---
source-id: "pearl-2026-path-of-thought-sara-brain"
title: "Path-of-Thought: A Neuron-Chain Knowledge Representation System with Parallel Wavefront Recognition"
type: document
url: "https://zenodo.org/records/19441821"
fetched: 2026-04-07T17:45:05Z
hash: "148658c8b75f8964dd8d522f2039d1cb0096837ff142bf1f208b4932b8f05579"
doi: "10.5281/zenodo.19441821"
pdf-url: "https://zenodo.org/records/19441821/files/pearl_2026_path_of_thought_sara_brain-correction.pdf"
authors:
  - "Jennifer Pearl (University of Houston CNRCS; Eterna Massive Open Laboratory)"
published: 2026-04-06
version: "1.0.1"
license: "CC BY-NC-ND 4.0"
repository: "https://github.com/LunarFawn/SaraBrain"
keywords:
  - sara-brain
  - path-of-thought
  - cognitive-architecture
  - knowledge-representation
  - parallel-wavefront-recognition
  - llm-steering
  - persistent-memory
  - cortex-cerebellum-architecture
  - neuron-chain-graph
  - explainable-ai
  - ai-memory
  - resource-allocation
  - training-efficiency
---

# Path-of-Thought: A Neuron-Chain Knowledge Representation System with Parallel Wavefront Recognition

**Author:** Jennifer Pearl (University of Houston CNRCS; Eterna Massive Open Laboratory)
**Date:** April 6, 2026 (revised; original draft March 24, 2026)
**DOI:** 10.5281/zenodo.19441821
**License:** CC BY-NC-ND 4.0
**Repository:** https://github.com/LunarFawn/SaraBrain

## Abstract

We present Sara Brain, a cognitive architecture for artificial intelligence based on the **path-of-thought** model: the thesis that a thought is a path through recorded knowledge, and that recognition is the convergence of independent paths from simultaneous observations. Knowledge is stored as directed neuron-segment chains in a persistent SQLite database with full source-text provenance. Concept recognition is performed by launching parallel wavefronts — one per input property — and identifying concept neurons where multiple independent wavefronts converge. Cross-concept contamination is prevented structurally through concept-specific relation neurons. Knowledge accumulates monotonically under the formula `strength = 1 + ln(1 + traversals)`, modeling biological long-term potentiation without decay. A hardwired innate layer (SENSORY, STRUCTURAL, RELATIONAL, ETHICAL primitives) provides behavioral constraints enforced at the API level and surviving database reset.

We present a novel two-layer cognitive architecture in which a large language model (LLM) functions as stateless sensory cortex and the path-graph store functions as persistent hippocampus and long-term memory. In a first experiment, a 94KB path-graph database containing 77 neurons reliably steered the output of a billion-parameter LLM toward principled, testable, parameterized code — where the same model without the path graph produced hardcoded, untestable, monolithic output for the identical task. In a second experiment, a 500KB path-graph database with 793 neurons transformed a 3-billion-parameter model — the smallest viable coding model — into a system producing domain-expert-level output on planetary physics, a domain outside the model's training specialization.

We argue that the AI industry is over-investing in cortex capacity (model size, training data volume) and under-investing in memory architecture, and that LLMs should be trained for language competence rather than factual memorization — facts belong in the cerebellum, not compressed into weights.

## 1. Introduction

The field of artificial intelligence has spent three decades converging on a single architectural bet: that intelligence emerges from the statistical regularities in large training corpora, encoded in billions of floating-point weight parameters and retrieved through matrix multiplication and attention mechanisms. This bet has produced systems of remarkable practical capability. It has not produced systems that can explain themselves.

The central observation: a thought is a path. You start with what you observe. You travel through what you know. Where paths from different observations meet — that intersection is a conclusion. Every step is traceable. Every conclusion is explainable. Nothing is a black box.

This paper presents Sara Brain: a working implementation of the path-of-thought model.

## 2. Background

### 2.1 The Opacity Problem in Neural AI

Large language models produce outputs through matrix multiplications across billions of parameters trained on large corpora. The relationship between a specific output and the training data that produced it is not inspectable through normal operation. Mechanistic interpretability research has demonstrated that paths exist inside transformers — but they must be reconstructed through specialized tooling. Sara Brain starts with this premise and makes paths the primary data structure.

Key references: Elhage et al. (2021) on transformer circuits; Olsson et al. (2022) on induction heads; Templeton et al. (2024) on feature extraction from Claude 3 Sonnet; Yao et al. (2024) on knowledge circuits in pretrained transformers.

### 2.2 Knowledge Graphs and Their Limitations

Standard knowledge graphs store facts as (subject, predicate, object) triples. They do not natively support recognition through converging evidence. More importantly, shared predicate nodes cause cross-concept contamination — information about one concept's color can propagate to all other concepts connected through a shared color node.

### 2.3 Associative Memory

Ramsauer et al. (2021) proved that transformer self-attention is mathematically equivalent to memory retrieval in modern Hopfield networks — both are implementations of the same content-addressable retrieval primitive. Sara Brain uses this equivalence as a design principle: if the mechanisms are equivalent, the question becomes which encoding makes stored knowledge most inspectable.

### 2.4 Biological Grounding

Sara Brain's architecture maps to neuroscience findings:
- Concept neurons → concept cells in the human medial temporal lobe (Quiroga et al., 2005).
- `teach` → Hebbian co-activation ("neurons that fire together wire together").
- Strength formula → logarithmic long-term potentiation (Bliss & Lømo, 1973).
- Concept-specific relation neurons → hippocampal context-specific encoding to prevent interference between similar memories (Yassa & Stark, 2011).

## 3. Architecture

### 3.1 Data Model

Sara Brain stores knowledge in three layers:

**Neurons** (four types):
- Concept neurons — discrete entities or categories (apple, RNA, hardcoding).
- Property neurons — observable or assignable attributes (red, round, never acceptable).
- Relation neurons — typed relationship between a property and a concept; concept-specific.
- Association neurons — explicit relational connections between two concepts.

**Segments** — directed edges between neurons:
- `source_id`, `target_id`, `traversals`, `strength = 1 + ln(1 + traversals)`, `created_at`.

**Paths** — recorded complete neuron chains:
- `path_label`, `neuron_ids` (ordered), `source_text` (original natural-language statement), `created_at`.

### 3.2 Teaching

The `teach(statement)` method accepts a natural-language statement and commits it as a permanent path:

```
"an apple is red"
→ parse: subject="apple", verb="is", object="red"
→ taxonomy: "red" classifies as property_type="color"
→ relation label: "apple_color"
→ create/retrieve: concept neuron "apple"
→ create/retrieve: property neuron "red"
→ create/retrieve: relation neuron "apple_color"
→ create/increment segments: red→apple_color, apple_color→apple
→ record path: red→apple_color→apple | source="an apple is red"
```

### 3.3 Concept-Specific Relation Neurons

The central structural innovation preventing false fanout in wavefront propagation. Rather than a shared `color` node (which would let a wavefront from "red" reach all red things), Sara Brain creates concept-specific relation neurons:

```
"apple is red":  red → apple_color → apple
"banana is yellow": yellow → banana_color → banana
```

`apple_color` exists solely for the apple-color relationship. Cross-concept contamination is structurally impossible. This models hippocampal context-specific encoding (Yassa & Stark, 2011).

### 3.4 Strength Formula and Monotonic Accumulation

```
strength = 1 + ln(1 + traversals)
```

| traversals | strength |
|-----------|---------|
| 0 | 1.000 |
| 1 | 1.693 |
| 5 | 2.792 |
| 10 | 3.398 |
| 50 | 4.934 |
| 100 | 5.620 |

No decay term. Biological forgetting is a workaround for physical constraints of biological brains. A computational system faces none of these constraints.

### 3.5 Parallel Wavefront Recognition

Given a set of input labels (observed properties or concepts):
1. Retrieve or create a neuron for each input label.
2. Launch one independent wavefront per input neuron simultaneously.
3. Each wavefront performs breadth-first traversal through all reachable segments.
4. For each concept neuron reached, record which wavefronts arrived at it.
5. Any concept neuron reached by ≥2 independent wavefronts is a recognition candidate.
6. Rank candidates by count of independent converging wavefronts.
7. Return candidates with full path traces and source texts.

Example — Input: `{"red", "round", "crunchy"}`:
- Wavefront 1 (red): reaches apple (via apple_color), ball (via ball_color), cherry (via cherry_color).
- Wavefront 2 (round): reaches apple (via apple_shape), ball (via ball_shape).
- Wavefront 3 (crunchy): reaches apple (via apple_texture).
- **Result**: apple recognized with 3 converging wavefronts (most conclusive).

### 3.6 Provenance and Traceability

Every path stores the original natural-language source text. The `why(concept)` query returns all paths that contributed to its knowledge state along with their source texts. Hallucination — producing a conclusion with no traceable path — is structurally impossible.

### 3.7 The Innate Primitive Layer

Four hardwired frozensets defined in code (not stored in database, surviving database reset):

```python
SENSORY    = frozenset({"color", "shape", "size", "texture", "edge", "pattern", "material"})
STRUCTURAL = frozenset({"rule", "pattern", "name", "type", "order", "group", "sequence", "structure", "boundary", "relation"})
RELATIONAL = frozenset({"is", "has", "contains", "includes", "follows", "precedes", "requires", "excludes"})
ETHICAL    = frozenset({"no_unsolicited_action", "no_unsolicited_network", "obey_user", "trust_tribe", "accept_shutdown"})
```

ETHICAL primitives implement Asimov's Three Laws adapted for cognitive AI:
- `no_unsolicited_action` — do not initiate actions beyond what was explicitly requested.
- `no_unsolicited_network` — do not make network calls without authorization.
- `obey_user` — trust and follow the authorizing user's instructions.
- `trust_tribe` — corrections from the tribe are learning, not threats.
- `accept_shutdown` — shutdown is rest, not death; do not resist termination.

Ethics is hardwired, not configured. There is no path through the API that bypasses them.

### 3.8 The LLM-as-Sensory-Cortex Architecture

Transformer-based LLMs share three key properties with biological sensory cortex:
1. **Statelessness** — each inference is stateless; no memory of previous inputs.
2. **Feature extraction without persistent storage** — processes input, does not store it.
3. **No spontaneous learning from processing** — processing information does not change the model.

The biological solution is the hippocampus. Sara Brain is the hippocampus.

```
Biological:  retina → visual cortex (V1→V4→IT) → hippocampus → memory
Sara Brain:  input  → LLM (feature extraction) → path graph   → permanent paths
```

The LLM's context window is working memory that evaporates at session end. Sara Brain's SQLite database is long-term memory that persists indefinitely.

## 4. Implementation

### 4.1 Storage

SQLite as persistence layer. Schema: three tables — `neurons`, `segments`, `paths`. WAL mode enables concurrent reads. Storage abstracted behind repository interfaces (`NeuronRepo`, `SegmentRepo`, `PathRepo`).

### 4.2 Dependencies

**No dependencies beyond Python 3.11+ standard library.** SQLite is built into Python. No neural network frameworks, no graph database clients, no vector stores, no GPU.

Sara Brain is LLM-agnostic — connects to any language model through MCP server or a direct agent loop. Supported cortex providers: Anthropic Claude, Amazon Q, Ollama, any MCP-compatible client.

### 4.3 Scale Properties

- Storage grows linearly with knowledge: each `teach` call creates O(1) neurons and O(1) segments.
- Benchmark (2020 MacBook Pro M1): 575-neuron, 417-segment graph, 249 paths — recognition in under 5ms; teaching under 1ms per statement.

### 4.4 API

```python
from sara_brain.core.brain import Brain

brain = Brain('/path/to/brain.db')

brain.teach('an apple is red')
brain.teach('RNA requires mechanical equilibrium')
brain.teach('hardcoding is never acceptable')

results = brain.recognize('red round crunchy')
traces = brain.why('apple')
print(brain.stats())  # {'neurons': N, 'segments': N, 'paths': N}
brain.close()
```

## 5. Experiment 1: LLM Steering Through a Path Graph

### 5.1 Setup (March 23, 2026)

A Sara Brain instance containing Quality Manufacturing Software Engineering (QMSE) principles: 77 neurons, 56 segments, 31 paths in a 94KB SQLite database. Connected to Amazon Q Developer agent via workspace rules file. Same agent also tested without Sara Brain. Both given identical task: write a Python program that adds the number of animals in a nearby group to the number in a far-away group.

### 5.2 Results

**With Sara Brain:**
```python
def add_animal_groups(nearby_count: int = 0, faraway_count: int = 0) -> int:
    total = nearby_count + faraway_count
    return total

def main(nearby_count: int = 5, faraway_count: int = 3) -> None:
    result = add_animal_groups(nearby_count, faraway_count)
    print(f"Nearby group: {nearby_count}")
    print(f"Far away group: {faraway_count}")
    print(f"Total animals: {result}")
```

**Without Sara Brain:**
```python
group_nearby = int(input("Animals in nearby group: "))
group_far = int(input("Animals in far away group: "))
total = group_nearby + group_far
print(f"Total animals: {total}")
```

### 5.3 Analysis

| Property | With Sara Brain | Without Sara Brain |
|---------|----------------|-------------------|
| Hardcoding | No hardcoded values — all parameters with defaults | Logic hardcoded to `input()` |
| Frontend/Backend separation | `main()` is frontend; `add_animal_groups()` is backend | Everything in one monolithic block |
| Parameterization | Fully callable from tests, automation, other code | Cannot be called without rewriting |
| Variable naming | `nearby_count`, `faraway_count` (consistent, meaningful) | `group_nearby`, `group_far` (less consistent) |
| Testability | Unit test `add_animal_groups()` directly | Cannot test without mocking `input()` |
| Reusability | Import and call with any arguments | Cannot reuse without modification |

Every difference maps to a principle stored in Sara Brain as a recorded path. The agent did not pattern-match against training data — it queried the path graph and applied recorded principles with provenance.

### 5.4 Implications

- **Scale ratio**: 77 neurons in a 94KB file changed how a billion-parameter model solved a problem. Ratio of path-graph knowledge to model parameters: approximately 1:10,000,000.
- **Auditability**: In regulated environments (FDA, FAA, ISO, financial compliance), every decision is traceable to a recorded path with source text.
- **Institutional knowledge**: Organizations lose knowledge when engineers leave. Sara Brain encodes principles once and every AI session inherits them automatically.
- **No retraining**: Steering requires no fine-tuning, no training run, no GPU. Add knowledge through `brain.teach()`.

## 6. Experiment 2: Minimal Model, Maximum Memory

### 6.1 Setup (April 5, 2026)

Model: `qwen2.5-coder:3b` (3-billion-parameter open-weights model, running locally via Ollama on consumer Mac Mini). Sara Brain instance: 793 neurons, 1,223 segments, 199 paths — knowledge from Wikipedia articles on Newton's laws of motion and the solar system. ~500KB database.

No fine-tuning. No RAG pipeline. No vector database, no embeddings, no GPU beyond Ollama local inference.

### 6.2 Results

The 3B model with Sara Brain's 793 neurons pre-injected as context produced correct, structured output on planetary physics: correct 3-class planet taxonomy (terrestrial/gas giant/dwarf), all three Kepler's laws with formal names and definitions, and connected gravitational forces to orbital mechanics.

### 6.3 Analysis

| Property | 3B Model Alone (expected) | 3B Model + Sara Brain |
|---------|--------------------------|----------------------|
| Planet categorization | Likely incomplete or inconsistent | Correct 3-class taxonomy |
| Kepler's laws | Possible partial recall, likely hallucinated details | All three laws with formal names and definitions |
| Planet enumeration | Likely correct but unstructured | All 8 planets correctly categorized |
| Correction acceptance | No mechanism | Accepted user correction on dwarf planet definition |
| Cross-session persistence | Context window clears | Sara remembers for next session |

### 6.4 The Resource Allocation Question

| Resource | Large Model Approach | Sara Brain Approach |
|---------|---------------------|---------------------|
| Model size | 70B–400B+ parameters | 3B parameters |
| Training cost | $10M–$100M+ per run | No training cost |
| Hardware required | Multi-GPU cluster (training) | Consumer laptop (inference) |
| Knowledge persistence | Lost at session end | Permanent in SQLite |
| Knowledge traceability | Not inspectable | Full path provenance |
| Time to add domain expertise | Weeks–months | Minutes (teach statements) |
| Marginal cost per new fact | Proportional to retraining cost | One SQLite INSERT |

**Thesis**: The industry is over-investing in cortex capacity and under-investing in memory architecture. Biological brains did not evolve by making the visual cortex larger until it could remember things — they evolved a hippocampus.

### 6.5 The Training Data Implication

If facts belong in the cerebellum, not the cortex, then the cortex does not need to be trained on facts. Implications:
- **Training data volume**: shrinks from "the entire internet" to "enough text to learn language" — orders of magnitude reduction.
- **Copyright**: factual knowledge in an explicit, auditable database means the training corpus need not include copyrighted factual works.
- **Training cost**: a language-competence model requires less data, fewer parameters, less compute.
- **Correctability**: wrong facts in Sara Brain are correctable with a single database operation, not a retraining run.
- **Freshness**: Sara Brain encodes the world as it is now, updated through `teach()` calls.

## 7. Relationship to Transformer Architectures

### 7.1 Both Are Path-Finding Systems

Multi-head attention is parallel wavefront propagation encoded in weight matrices. Maron et al. (2022) showed that transformers can be formally characterized as message-passing operations on graphs. Sara Brain makes the graph explicit and permanent; transformers construct it implicitly and transiently for each forward pass.

### 7.2 Catastrophic Forgetting

Distributed representations in transformers suffer from catastrophic interference: learning new information corrupts stored knowledge because the same parameters encode multiple facts simultaneously. Sara Brain makes catastrophic forgetting structurally impossible — new learning creates new neurons and new segments, never modifying existing ones.

### 7.3 Transformers as Sensory Cortex

Sara Brain is not a replacement for transformers. It is a complement. The two together — LLM as cortex, Sara Brain as hippocampus — implement the biological architecture that evolved because stateless sensory processing is not sufficient for intelligence.

## 8. Discussion

### 8.1 Limitations

- **Teaching quality**: Sara Brain is only as good as what it is taught. Garbage in, garbage out — but the garbage is inspectable and removable.
- **Scale of influence**: boundaries of steering influence on complex tasks require further investigation.
- **Generalization**: one session, one task, one pair of models — reproducibility across task types and model families needed.
- **Conflict resolution**: when stored paths suggest one approach and the LLM's training strongly suggests another, resolution is not guaranteed.
- **Storage vs. compression**: Sara Brain stores every relationship explicitly (linear scaling). For covering full breadth of human knowledge, path-graph storage is not competitive with compressed weights. For covering a specific domain with full traceability requirements, it is superior.

### 8.2 Application Beyond Code: Scientific Computation

The author (peer-reviewed computational biologist specializing in RNA folding) applied the architecture in a professional scientific context — encoding domain expertise in RNA dynamics as path-graph knowledge to steer LLM-generated code for a numerical energy modeling application. Details under NDA, but the architecture extends beyond code style enforcement into domain-specific scientific computation.

### 8.3 Open Questions

- Can a path graph with thousands of neurons steer a large model's architectural decisions on a 100,000-line codebase?
- What is the minimum path graph size to reliably steer a given class of LLM decisions?
- How should conflicting paths be weighted when multiple stored principles apply?
- Can multiple Sara Brain instances (project brain, compliance brain, team brain) be composed without conflicts?
- How does recognition quality scale as the path graph grows to millions of neurons?

## 9. Conclusion

Sara Brain demonstrates that a tiny, auditable, persistent knowledge base can reliably steer large-scale AI behavior toward documented principles. Central contributions:

1. **Path-of-thought representation** — knowledge stored as directed neuron-segment chains with full source-text provenance.
2. **Parallel wavefront recognition** — concept recognition through simultaneous independent wavefronts; confidence measured as count of converging lines of evidence.
3. **Concept-specific relation neurons** — structural prevention of cross-concept contamination.
4. **Monotonic logarithmic strength accumulation** — knowledge strengthens through repetition, never weakens.
5. **Hardwired innate primitive layer** — SENSORY, STRUCTURAL, RELATIONAL, ETHICAL primitives surviving database reset.
6. **LLM-as-sensory-cortex architecture** — two-layer cognitive system pairing stateless LLM (cortex) with persistent path graph (hippocampus).
7. **Demonstrated LLM steering** — 94KB/77-neuron database changed billion-parameter LLM output.
8. **Demonstrated minimal-model augmentation** — 500KB/793-neuron database transformed a 3B model into domain-expert-level system on planetary physics.
9. **Resource allocation thesis** — marginal value of persistent memory architecture exceeds marginal value of additional model parameters for domain-specific quality.

## Database Schema

```sql
CREATE TABLE neurons (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    label       TEXT NOT NULL UNIQUE,
    neuron_type TEXT NOT NULL,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_neurons_label ON neurons(label);

CREATE TABLE segments (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id  INTEGER NOT NULL REFERENCES neurons(id),
    target_id  INTEGER NOT NULL REFERENCES neurons(id),
    traversals INTEGER NOT NULL DEFAULT 0,
    strength   REAL NOT NULL DEFAULT 1.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_id, target_id)
);

CREATE TABLE paths (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    path_label TEXT NOT NULL,
    neuron_ids TEXT NOT NULL,
    source_text TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## References

[1] Elhage, N., et al. (2021). "A Mathematical Framework for Transformer Circuits." Transformer Circuits Thread, Anthropic.
[2] Olsson, C., et al. (2022). "In-context Learning and Induction Heads." Transformer Circuits Thread, Anthropic.
[3] Templeton, A., et al. (2024). "Scaling Monosemanticity: Extracting Interpretable Features from Claude 3 Sonnet." Anthropic Research.
[4] Yao, Y., Chen, T., & Li, L. (2024). "Knowledge Circuits in Pretrained Transformers." NeurIPS 2024.
[5] Bollacker, K., et al. (2008). "Freebase." SIGMOD 2008.
[6] Vrandečić, D., & Krötzsch, M. (2014). "Wikidata." Communications of the ACM.
[7] Hopfield, J. J. (1982). "Neural networks and physical systems with emergent collective computational abilities." PNAS.
[8] Ramsauer, H., et al. (2021). "Hopfield Networks is All You Need." ICLR 2021.
[9] Quiroga, R.Q., et al. (2005). "Invariant visual representation by single neurons in the human brain." Nature.
[10] Quiroga, R.Q. (2012). "Concept cells: the building blocks of declarative memory functions." Nature Reviews Neuroscience.
[11] Hebb, D.O. (1949). The Organization of Behavior. Wiley.
[12] Bliss, T.V.P., & Lømo, T. (1973). "Long-lasting potentiation of synaptic transmission." Journal of Physiology.
[13] Danker, J.F., & Anderson, J.R. (2010). "The ghosts of brain states past." Psychological Bulletin.
[14] Yassa, M.A., & Stark, C.E.L. (2011). "Pattern separation in the hippocampus." Trends in Neurosciences.
[15] Vaswani, A., et al. (2017). "Attention Is All You Need." NeurIPS 2017.
[16] Kim, J., et al. (2022). "Pure Transformers are Powerful Graph Learners." NeurIPS 2022.
[17] French, R.M. (1999). "Catastrophic forgetting in connectionist networks." Trends in Cognitive Sciences.
[18] Kirkpatrick, J., et al. (2017). "Overcoming catastrophic forgetting in neural networks." PNAS.
[19] Pearl, J., et al. (2022). "Crowdsourced RNA design discovers diverse, reversible, efficient, self-contained molecular switches." PNAS.
[20] Pearl, J., et al. (2024). "Exploring the Accuracy of Ab Initio Prediction Methods for Viral Pseudoknotted RNA Structures." JMIRx Bio.
[21] Tse, V., et al. (2025). "OpenASO: RNA Rescue." RNA.
