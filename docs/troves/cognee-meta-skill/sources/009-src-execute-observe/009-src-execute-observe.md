---
source-id: "009"
title: "Raw Source — execute.py + observe.py (execution and observation)"
type: local
path: "cognee/cognee_skills/execute.py + cognee/cognee_skills/observe.py"
url: "https://github.com/topoteretes/cognee/tree/demo/graphskill_COG-4178/cognee/cognee_skills"
fetched: 2026-03-15T21:10:00Z
hash: "sha256:placeholder"
---

# execute.py

```python
"""Execute a skill: load instructions, call LLM, return result with timing."""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, Optional

import litellm

from cognee.infrastructure.llm import get_llm_config

logger = logging.getLogger(__name__)

SYSTEM_PROMPT_TEMPLATE = """\
You are executing the skill "{skill_name}".

{instructions}

Follow the instructions above to complete the user's task. \
Be thorough but concise. If the instructions reference tools or external actions \
you cannot perform, describe what should be done instead."""

EVALUATE_PROMPT = """\
You are a quality evaluator. Score how useful the output is for the user's task.

The skill's instructions may be flawed — that's exactly what we're trying to detect. \
Do NOT score based on whether the output follows the instructions. \
Score based on whether a human reading this output would find it helpful for their task.

Task: {task_text}
Output to evaluate:
{output}

Respond with ONLY a JSON object: {{"score": <float 0.0 to 1.0>, "reason": "<one sentence>"}}

Scoring guide:
- 1.0: Output is exactly what someone would want for this task
- 0.7-0.9: Mostly useful, minor gaps
- 0.4-0.6: Partially useful, significant gaps
- 0.1-0.3: Mostly unhelpful or off-topic
- 0.0: Completely useless or empty"""


async def execute_skill(
    skill: Dict[str, Any],
    task_text: str,
    context: Optional[str] = None,
) -> Dict[str, Any]:
    """Execute a loaded skill against a task using the configured LLM.

    Args:
        skill: Skill dict as returned by Skills.load() (must have 'instructions' and 'name').
        task_text: The user's task description.
        context: Optional additional context to include in the user message.

    Returns:
        Dict with keys: output, model, latency_ms, success, error.
    """
    llm_config = get_llm_config()
    model = llm_config.llm_model
    api_key = llm_config.llm_api_key

    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        skill_name=skill.get("name", "unknown"),
        instructions=skill.get("instructions", ""),
    )

    user_message = task_text
    if context:
        user_message = f"{task_text}\n\nAdditional context:\n{context}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]

    start_ms = int(time.time() * 1000)

    try:
        response = await litellm.acompletion(
            model=model,
            messages=messages,
            api_key=api_key,
        )
        output = response.choices[0].message.content or ""
        latency_ms = int(time.time() * 1000) - start_ms

        logger.info(
            "Executed skill '%s' in %dms",
            skill.get("skill_id", ""),
            latency_ms,
        )

        return {
            "output": output,
            "skill_id": skill.get("skill_id", ""),
            "model": model,
            "latency_ms": latency_ms,
            "success": True,
            "error": None,
        }

    except Exception as exc:
        latency_ms = int(time.time() * 1000) - start_ms
        logger.warning(
            "Skill execution failed for '%s': %s",
            skill.get("skill_id", ""),
            exc,
        )
        return {
            "output": "",
            "skill_id": skill.get("skill_id", ""),
            "model": model,
            "latency_ms": latency_ms,
            "success": False,
            "error": str(exc),
        }


async def evaluate_output(
    skill: Dict[str, Any],
    task_text: str,
    output: str,
) -> Dict[str, Any]:
    """Score output quality with a second LLM call.

    Returns:
        Dict with keys: score (float 0.0-1.0), reason (str).
    """
    import json as _json

    llm_config = get_llm_config()

    prompt = EVALUATE_PROMPT.format(
        task_text=task_text,
        output=output[:2000],
    )

    try:
        response = await litellm.acompletion(
            model=llm_config.llm_model,
            messages=[{"role": "user", "content": prompt}],
            api_key=llm_config.llm_api_key,
        )
        raw = response.choices[0].message.content or ""
        # Strip markdown fences if present
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
        parsed = _json.loads(cleaned)
        score = max(0.0, min(1.0, float(parsed.get("score", 0.0))))
        reason = str(parsed.get("reason", ""))
        logger.info(
            "Evaluated skill '%s' output: score=%.2f reason=%s",
            skill.get("skill_id", ""),
            score,
            reason,
        )
        return {"score": score, "reason": reason}
    except Exception as exc:
        logger.warning("Output evaluation failed for '%s': %s", skill.get("skill_id", ""), exc)
        return {"score": 1.0, "reason": f"Evaluation failed: {exc}"}
```

---

# observe.py

```python
"""Observe layer: record SkillRun executions directly to graph.

Runs are persisted as SkillRun DataPoints and prefers edge weights
are updated immediately — no intermediate cache.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional
from uuid import uuid5, UUID

from cognee.low_level import setup
from cognee.infrastructure.databases.graph import get_graph_engine
from cognee.modules.engine.models.node_set import NodeSet
from cognee.tasks.storage import add_data_points
from cognee.tasks.storage.index_graph_edges import index_graph_edges

from cognee.cognee_skills.models.skill_run import SkillRun, ToolCall, CandidateSkill
from cognee.modules.engine.utils.generate_node_id import generate_node_id

logger = logging.getLogger(__name__)

NAMESPACE = UUID("c3d4e5f6-a7b8-9012-cdef-123456789012")


async def record_skill_run(
    session_id: str,
    task_text: str,
    selected_skill_id: str,
    task_pattern_id: str = "",
    result_summary: str = "",
    success_score: float = 0.0,
    candidate_skills: Optional[List[Dict[str, Any]]] = None,
    router_version: str = "",
    tool_trace: Optional[List[Dict[str, Any]]] = None,
    feedback: float = 0.0,
    error_type: str = "",
    error_message: str = "",
    cognee_session_id: str = "",
    latency_ms: int = 0,
) -> dict:
    """Record a skill execution directly to the graph.

    Builds a SkillRun DataPoint, persists it via add_data_points,
    and updates the TaskPattern → Skill prefers edge weight immediately.

    Returns a summary dict with key fields.
    """
    await setup()

    started_at_ms = int(time.time() * 1000)
    run_id = f"{session_id}:{task_text}:{started_at_ms}"

    candidates = []
    for cs in candidate_skills or []:
        candidates.append(
            CandidateSkill(
                id=uuid5(NAMESPACE, f"{run_id}:candidate:{cs.get('skill_id', '')}"),
                skill_id=cs.get("skill_id", ""),
                score=cs.get("score", 0.0),
                signals=cs.get("signals"),
            )
        )

    tool_calls = []
    for i, tc in enumerate(tool_trace or []):
        tool_calls.append(
            ToolCall(
                id=uuid5(NAMESPACE, f"{run_id}:{tc.get('tool_name', '')}:{i}"),
                tool_name=tc.get("tool_name", ""),
                tool_input=tc.get("tool_input"),
                tool_output=tc.get("tool_output"),
                success=tc.get("success", True),
                duration_ms=tc.get("duration_ms", 0),
            )
        )

    skill_run = SkillRun(
        id=uuid5(NAMESPACE, run_id),
        run_id=run_id,
        session_id=session_id,
        cognee_session_id=cognee_session_id,
        task_text=task_text,
        result_summary=result_summary,
        success_score=success_score,
        candidate_skills=candidates,
        selected_skill_id=selected_skill_id,
        task_pattern_id=task_pattern_id,
        router_version=router_version,
        tool_trace=tool_calls,
        error_type=error_type,
        error_message=error_message,
        started_at_ms=started_at_ms,
        latency_ms=latency_ms,
        feedback=feedback,
    )

    # Tag the SkillRun with the node set so it's visible to inspect/amendify
    ns = NodeSet(id=generate_node_id("NodeSet:skills"), name="skills")
    skill_run.belongs_to_set = [ns]

    await add_data_points([skill_run])
    await index_graph_edges()

    if task_pattern_id and selected_skill_id:
        await _update_prefers_weight(task_pattern_id, selected_skill_id, success_score)

    logger.info(
        "Recorded SkillRun: session=%s skill=%s score=%.2f",
        session_id,
        selected_skill_id,
        success_score,
    )

    return {
        "run_id": run_id,
        "session_id": session_id,
        "task_text": task_text,
        "selected_skill_id": selected_skill_id,
        "task_pattern_id": task_pattern_id,
        "result_summary": result_summary,
        "success_score": success_score,
        "started_at_ms": started_at_ms,
        "latency_ms": latency_ms,
    }


async def _update_prefers_weight(
    task_pattern_id: str,
    skill_id: str,
    score: float,
) -> None:
    """Update a single TaskPattern → Skill prefers edge weight incrementally."""
    engine = await get_graph_engine()
    raw_nodes, raw_edges = await engine.get_nodeset_subgraph(
        node_type=NodeSet, node_name=["skills"]
    )

    tp_nid = None
    sk_nid = None
    for nid, props in raw_nodes:
        ntype = props.get("type", "")
        if ntype == "TaskPattern" and props.get("pattern_key") == task_pattern_id:
            tp_nid = str(nid)
        elif ntype == "Skill" and props.get("skill_id") == skill_id:
            sk_nid = str(nid)
        if tp_nid and sk_nid:
            break

    if not tp_nid or not sk_nid:
        logger.debug(
            "Skipping prefers update: tp=%s sk=%s (node not found)",
            task_pattern_id,
            skill_id,
        )
        return

    prior_sum = 0.0
    prior_count = 0
    for src_id, tgt_id, rel_name, edge_props in raw_edges:
        if rel_name == "prefers" and str(src_id) == tp_nid and str(tgt_id) == sk_nid:
            prior_sum = float((edge_props or {}).get("weight_sum", 0.0))
            prior_count = int((edge_props or {}).get("run_count", 0))
            break

    new_sum = prior_sum + score
    new_count = prior_count + 1
    new_weight = new_sum / new_count

    await engine.add_edges(
        [
            (
                tp_nid,
                sk_nid,
                "prefers",
                {
                    "weight": round(new_weight, 4),
                    "weight_sum": round(new_sum, 4),
                    "run_count": new_count,
                },
            )
        ]
    )
```
