---
source-id: "algocademy-longest-path-dag"
title: "Longest Path in a DAG: Mastering Graph Algorithms - AlgoCademy"
type: web
url: "https://algocademy.com/blog/longest-path-in-a-dag-mastering-graph-algorithms-for-technical-interviews/"
fetched: 2026-03-22T00:00:00Z
hash: "aec47520ec7b14de1bcea1d35064e02927076040bfd3e71e74ccfc5805fe2812"
---

# Longest Path in a DAG

## Problem definition

Given a Directed Acyclic Graph (DAG), find the longest path from any starting vertex to any ending vertex. Length is defined as the number of edges (or sum of edge weights if weighted).

**Key distinction**: while shortest path in graphs with cycles can be solved efficiently (Dijkstra's), longest path in graphs with cycles is **NP-hard**. The acyclic nature of DAGs allows efficient O(V+E) solution.

## Algorithm

The solution combines two concepts:

### 1. Topological Sorting

Order vertices so that for every directed edge (u, v), u comes before v. This ensures when we process a vertex, all its predecessors have already been processed.

```python
def topological_sort(graph):
    def dfs(v):
        visited.add(v)
        for neighbor in graph[v]:
            if neighbor not in visited:
                dfs(neighbor)
        stack.append(v)

    visited = set()
    stack = []
    for vertex in graph:
        if vertex not in visited:
            dfs(vertex)
    return stack[::-1]
```

### 2. Dynamic Programming

Process vertices in topological order, maintaining longest path ending at each vertex:

1. Perform topological sort
2. Initialize `dist[v] = 0` for all vertices
3. For each vertex `u` in topological order:
   - For each neighbor `v` of `u`:
     - `dist[v] = max(dist[v], dist[u] + weight(u, v))`
4. Maximum value in `dist` is the longest path length

### Complexity

- **Time**: O(V + E) — topological sort O(V+E) then process each edge once O(E)
- **Space**: O(V) — visited set, stack, dist dictionary

## Real-world applications

1. **Project scheduling (Critical Path Method)**: Tasks as vertices, dependencies as edges. Longest path = critical path = minimum project duration.
2. **Build systems**: DAG of module dependencies. Longest path optimizes build process.
3. **Course scheduling**: Courses and prerequisites form a DAG. Longest path = minimum semesters.
4. **Pipeline processing**: Instruction pipelines as DAGs. Longest path = clock cycle time.

## Relevance to swain

Swain's dependency model already forms DAGs at two levels:
- **Task-level**: `tk dep` creates edges between tasks within a plan
- **Artifact-level**: `depends-on-artifacts` creates edges between artifacts

The longest-path algorithm is directly applicable to both. The key implementation question is whether to compute on the task DAG, the artifact DAG, or both — and how to handle the absence of fixed duration estimates (agent work has variable duration).

## Variations

- **Shortest path in DAG**: Same approach, change max to min
- **All paths in DAG**: DFS or DP
- **Longest path with constraints**: Pass through specific vertices
- **Parallel task scheduling**: Given DAG and multiple processors, minimize total time (critical path determines minimum)
