---
source-id: "010"
title: "Raw Source — inspect.py + preview_amendify.py + amendify.py (self-improvement loop)"
type: local
path: "cognee/cognee_skills/inspect.py + preview_amendify.py + amendify.py"
url: "https://github.com/topoteretes/cognee/tree/demo/graphskill_COG-4178/cognee/cognee_skills"
fetched: 2026-03-15T21:10:00Z
hash: "sha256:placeholder"
---

# inspect.py

```python
"""Inspect why a skill fails by analyzing failed SkillRun records."""

from __future__ import annotations

import logging
import time
from typing import Optional
from uuid import uuid5, UUID

from cognee.infrastructure.databases.graph import get_graph_engine
from cognee.infrastructure.llm.LLMGateway import LLMGateway
from cognee.infrastructure.llm import get_llm_config
from cognee.modules.engine.models.node_set import NodeSet
from cognee.modules.engine.utils.generate_node_id import generate_node_id
from cognee.tasks.storage import add_data_points

from cognee.cognee_skills.models.skill_inspection import InspectionResult, SkillInspection

logger = logging.getLogger(__name__)

INSPECTION_NAMESPACE = UUID("e5f6a7b8-c9d0-1234-ef01-23456789abcd")

SYSTEM_PROMPT = """\
You are an expert at diagnosing why agentic skills fail. Given a skill's instructions \
and one or more failed execution records, identify the root cause and propose a \
hypothesis for improvement. Be precise and actionable."""

USER_PROMPT_TEMPLATE = """\
Skill name: {skill_name}

Skill instructions:
---
{instructions}
---

Failed execution records ({run_count} runs, avg success score: {avg_score:.2f}):

{formatted_runs}

Analyze these failures and determine:
- failure_category: one of "instruction_gap", "ambiguity", "wrong_scope", \
"tooling", "context_missing", "other"
- root_cause: concise description of the root cause
- severity: "low", "medium", "high", or "critical"
- improvement_hypothesis: actionable hypothesis for improving the skill
- confidence: your confidence from 0.0 to 1.0"""


def _format_run(run_props: dict, index: int) -> str:
    """Format a single failed run for the LLM prompt."""
    parts = [f"Run {index + 1}:"]
    if run_props.get("task_text"):
        parts.append(f"  Task: {run_props['task_text'][:500]}")
    if run_props.get("error_type"):
        parts.append(f"  Error type: {run_props['error_type']}")
    if run_props.get("error_message"):
        parts.append(f"  Error message: {run_props['error_message'][:500]}")
    if run_props.get("result_summary"):
        parts.append(f"  Result summary: {run_props['result_summary'][:500]}")
    score = run_props.get("success_score", 0.0)
    parts.append(f"  Success score: {score}")
    if run_props.get("tool_trace"):
        trace = str(run_props["tool_trace"])[:1000]
        parts.append(f"  Tool trace (truncated): {trace}")
    return "\n".join(parts)


async def inspect_skill(
    skill_id: str,
    min_runs: int = 1,
    score_threshold: float = 0.5,
    node_set: str = "skills",
) -> Optional[SkillInspection]:
    """Analyze failed SkillRuns for a skill and produce an inspection.

    Args:
        skill_id: The skill to inspect.
        min_runs: Minimum number of failed runs required before inspecting.
        score_threshold: Runs with success_score below this are considered failures.
        node_set: Graph node set to search.

    Returns:
        A persisted SkillInspection DataPoint, or None if insufficient failures.
    """
    engine = await get_graph_engine()
    raw_nodes, _ = await engine.get_nodeset_subgraph(node_type=NodeSet, node_name=[node_set])

    # Find the skill
    skill_node = None
    for _, props in raw_nodes:
        if props.get("type") == "Skill" and props.get("skill_id") == skill_id:
            skill_node = props
            break

    if skill_node is None:
        logger.warning("Skill '%s' not found in graph", skill_id)
        return None

    # Find failed runs
    failed_runs = []
    for _, props in raw_nodes:
        if (
            props.get("type") == "SkillRun"
            and props.get("selected_skill_id") == skill_id
            and float(props.get("success_score", 1.0)) < score_threshold
        ):
            failed_runs.append(props)

    if len(failed_runs) < min_runs:
        logger.info(
            "Skill '%s' has %d failed runs (need %d), skipping inspection",
            skill_id,
            len(failed_runs),
            min_runs,
        )
        return None

    # Compute stats
    scores = [float(r.get("success_score", 0.0)) for r in failed_runs]
    avg_score = sum(scores) / len(scores) if scores else 0.0
    run_ids = [r.get("run_id", str(i)) for i, r in enumerate(failed_runs)]

    # Format runs for prompt (limit to 10 most recent)
    runs_to_show = failed_runs[:10]
    formatted_runs = "\n\n".join(_format_run(r, i) for i, r in enumerate(runs_to_show))

    instructions = skill_node.get("instructions", "")[:8000]
    skill_name = skill_node.get("name", skill_id)

    user_prompt = USER_PROMPT_TEMPLATE.format(
        skill_name=skill_name,
        instructions=instructions,
        run_count=len(failed_runs),
        avg_score=avg_score,
        formatted_runs=formatted_runs,
    )

    try:
        result: InspectionResult = await LLMGateway.acreate_structured_output(
            text_input=user_prompt,
            system_prompt=SYSTEM_PROMPT,
            response_model=InspectionResult,
        )
    except Exception as exc:
        logger.warning("LLM inspection failed for skill '%s': %s", skill_id, exc)
        return None

    llm_config = get_llm_config()
    inspection_id = str(
        uuid5(INSPECTION_NAMESPACE, f"{skill_id}:{len(failed_runs)}:{avg_score}:{time.time()}")
    )

    inspection = SkillInspection(
        id=uuid5(INSPECTION_NAMESPACE, inspection_id),
        name=f"inspection: {skill_name}",
        description=f"Inspection for skill '{skill_name}': {result.root_cause[:200]}",
        inspection_id=inspection_id,
        skill_id=skill_id,
        skill_name=skill_name,
        failure_category=result.failure_category,
        root_cause=result.root_cause,
        severity=result.severity,
        improvement_hypothesis=result.improvement_hypothesis,
        analyzed_run_ids=run_ids,
        analyzed_run_count=len(failed_runs),
        avg_success_score=avg_score,
        inspection_model=llm_config.llm_model or "unknown",
        inspection_confidence=result.confidence,
    )

    ns = NodeSet(id=generate_node_id("NodeSet:skills"), name="skills")
    inspection.belongs_to_set = [ns]

    await add_data_points([inspection])
    logger.info(
        "Inspected skill '%s': category=%s, severity=%s, confidence=%.2f",
        skill_name,
        result.failure_category,
        result.severity,
        result.confidence,
    )

    return inspection
```

---

# preview_amendify.py

```python
"""Propose an amendment to a skill's instructions based on an inspection."""

from __future__ import annotations

import logging
from typing import Optional
from uuid import uuid5, UUID

from cognee.infrastructure.llm.LLMGateway import LLMGateway
from cognee.infrastructure.llm import get_llm_config
from cognee.modules.engine.models.node_set import NodeSet
from cognee.modules.engine.utils.generate_node_id import generate_node_id
from cognee.tasks.storage import add_data_points

from cognee.cognee_skills.models.skill_inspection import SkillInspection
from cognee.cognee_skills.models.skill_amendment import AmendmentProposal, SkillAmendment

logger = logging.getLogger(__name__)

AMENDMENT_NAMESPACE = UUID("f6a7b8c9-d0e1-2345-f012-3456789abcde")

SYSTEM_PROMPT = """\
You are an expert at improving agentic skill instructions. Given an inspection of what's \
wrong and the current instructions, produce improved instructions that fix the issue. \
Preserve overall structure and style. Only change what needs to change. Output the \
COMPLETE amended instructions (not a diff)."""

USER_PROMPT_TEMPLATE = """\
Skill name: {skill_name}

Inspection:
- Failure category: {failure_category}
- Root cause: {root_cause}
- Severity: {severity}
- Improvement hypothesis: {improvement_hypothesis}
- Analyzed {run_count} failed runs (avg success score: {avg_score:.2f})

Current instructions:
---
{instructions}
---

Produce:
- amended_instructions: The COMPLETE improved instructions
- change_explanation: What was changed and why
- expected_improvement: What improvement is expected
- confidence: Your confidence from 0.0 to 1.0"""


async def preview_skill_amendify(
    inspection: SkillInspection,
    skill: dict,
) -> Optional[SkillAmendment]:
    """Generate a proposed amendment for a skill based on its inspection.

    Args:
        inspection: The SkillInspection describing what's wrong.
        skill: The skill dict (from client.load()) with current instructions.

    Returns:
        A persisted SkillAmendment DataPoint with status="proposed".
    """
    instructions = skill.get("instructions", "")
    skill_name = skill.get("name", inspection.skill_name)

    user_prompt = USER_PROMPT_TEMPLATE.format(
        skill_name=skill_name,
        failure_category=inspection.failure_category,
        root_cause=inspection.root_cause,
        severity=inspection.severity,
        improvement_hypothesis=inspection.improvement_hypothesis,
        run_count=inspection.analyzed_run_count,
        avg_score=inspection.avg_success_score,
        instructions=instructions[:8000],
    )

    try:
        result: AmendmentProposal = await LLMGateway.acreate_structured_output(
            text_input=user_prompt,
            system_prompt=SYSTEM_PROMPT,
            response_model=AmendmentProposal,
        )
    except Exception as exc:
        logger.warning("LLM amendment generation failed for skill '%s': %s", skill_name, exc)
        return None

    llm_config = get_llm_config()
    amendment_id = str(
        uuid5(AMENDMENT_NAMESPACE, f"{inspection.inspection_id}:{inspection.skill_id}")
    )

    amendment = SkillAmendment(
        id=uuid5(AMENDMENT_NAMESPACE, amendment_id),
        name=f"amendment: {skill_name}",
        description=f"Proposed amendment for skill '{skill_name}': {result.change_explanation[:200]}",
        amendment_id=amendment_id,
        skill_id=inspection.skill_id,
        skill_name=skill_name,
        inspection_id=inspection.inspection_id,
        original_instructions=instructions,
        amended_instructions=result.amended_instructions,
        change_explanation=result.change_explanation,
        expected_improvement=result.expected_improvement,
        status="proposed",
        amendment_model=llm_config.llm_model or "unknown",
        amendment_confidence=result.confidence,
        pre_amendment_avg_score=inspection.avg_success_score,
    )

    ns = NodeSet(id=generate_node_id("NodeSet:skills"), name="skills")
    amendment.belongs_to_set = [ns]

    await add_data_points([amendment])
    logger.info(
        "Proposed amendment for skill '%s' (confidence=%.2f): %s",
        skill_name,
        result.confidence,
        result.change_explanation[:100],
    )

    return amendment
```

---

# amendify.py

```python
"""Apply, rollback, and evaluate skill amendments."""

from __future__ import annotations

import hashlib
import logging
import re
import time
import uuid
from pathlib import Path
from typing import Optional

from cognee.infrastructure.databases.graph import get_graph_engine
from cognee.modules.engine.models.node_set import NodeSet
from cognee.modules.engine.utils.generate_node_id import generate_node_id
from cognee.tasks.storage import add_data_points

from cognee.cognee_skills.utils import _make_change_event

logger = logging.getLogger(__name__)


def _tag_with_nodeset(items, node_set: str = "skills"):
    """Tag DataPoints with belongs_to_set so they appear in nodeset subgraph queries."""
    ns = NodeSet(id=generate_node_id(f"NodeSet:{node_set}"), name=node_set)
    for item in items:
        if hasattr(item, "belongs_to_set"):
            item.belongs_to_set = [ns]
    return items


def _content_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def _replace_skill_md_body(file_content: str, new_body: str) -> str:
    """Replace the body of a SKILL.md file (below frontmatter) with new content."""
    pattern = re.compile(r"^(---\s*\n.*?\n---\s*\n)", re.DOTALL)
    match = pattern.match(file_content)
    if match:
        return match.group(1) + new_body
    return new_body


async def _load_amendment_from_graph(amendment_id: str, node_set: str) -> Optional[dict]:
    """Load a SkillAmendment node from graph by amendment_id."""
    engine = await get_graph_engine()
    raw_nodes, _ = await engine.get_nodeset_subgraph(node_type=NodeSet, node_name=[node_set])
    for nid, props in raw_nodes:
        if props.get("type") == "SkillAmendment" and props.get("amendment_id") == amendment_id:
            return {"nid": str(nid), **props}
    return None


async def _load_skill_from_graph(skill_id: str, node_set: str) -> Optional[tuple]:
    """Load a Skill node from graph, returning (nid, props)."""
    engine = await get_graph_engine()
    raw_nodes, _ = await engine.get_nodeset_subgraph(node_type=NodeSet, node_name=[node_set])
    for nid, props in raw_nodes:
        if props.get("type") == "Skill" and props.get("skill_id") == skill_id:
            return (str(nid), props)
    return None


def _reconstruct_amendment(node_dict: dict):
    """Reconstruct a SkillAmendment DataPoint from a raw graph node dict."""
    from cognee.cognee_skills.models.skill_amendment import SkillAmendment

    node_id = node_dict.get("id", node_dict.get("nid", ""))
    return SkillAmendment(
        id=uuid.UUID(str(node_id)) if node_id else uuid.uuid4(),
        amendment_id=node_dict.get("amendment_id", ""),
        skill_id=node_dict.get("skill_id", ""),
        skill_name=node_dict.get("skill_name", ""),
        inspection_id=node_dict.get("inspection_id", ""),
        original_instructions=node_dict.get("original_instructions", ""),
        amended_instructions=node_dict.get("amended_instructions", ""),
        change_explanation=node_dict.get("change_explanation", ""),
        expected_improvement=node_dict.get("expected_improvement", ""),
        status=node_dict.get("status", "proposed"),
        amendment_model=node_dict.get("amendment_model", ""),
        amendment_confidence=float(node_dict.get("amendment_confidence", 0.0)),
        pre_amendment_avg_score=float(node_dict.get("pre_amendment_avg_score", 0.0)),
        applied_at_ms=int(node_dict.get("applied_at_ms", 0)),
        post_amendment_avg_score=float(node_dict.get("post_amendment_avg_score", 0.0)),
        post_amendment_run_count=int(node_dict.get("post_amendment_run_count", 0)),
    )


async def amendify(
    amendment_id: str,
    write_to_disk: bool = False,
    validate: bool = False,
    validation_task_text: str = "",
    node_set: str = "skills",
) -> dict:
    """Apply a proposed amendment to a skill.

    1. Load SkillAmendment from graph
    2. Load Skill from graph
    3. Optionally write amended instructions to SKILL.md on disk
    4. Update Skill node in graph with amended instructions
    5. Re-run enrichment pipeline on the updated skill
    6. Emit a SkillChangeEvent
    7. Update amendment status to "applied"
    8. Optionally validate by executing the skill

    Args:
        amendment_id: The amendment to apply.
        write_to_disk: If True, also update the SKILL.md file on disk.
        validate: If True, run execute_skill with validation_task_text after applying.
        validation_task_text: Task text for validation execution.
        node_set: Graph node set.

    Returns:
        Summary dict with applied amendment details and optional validation result.
    """
    amendment_node = await _load_amendment_from_graph(amendment_id, node_set)
    if amendment_node is None:
        return {"success": False, "error": f"Amendment '{amendment_id}' not found"}

    amendment_status = amendment_node.get("status", "")
    if amendment_status != "proposed":
        return {
            "success": False,
            "error": f"Amendment '{amendment_id}' has status '{amendment_status}', expected 'proposed'",
        }

    skill_id = amendment_node.get("skill_id", "")
    skill_result = await _load_skill_from_graph(skill_id, node_set)
    if skill_result is None:
        return {"success": False, "error": f"Skill '{skill_id}' not found"}

    skill_nid, skill_props = skill_result
    old_hash = skill_props.get("content_hash", "")
    amended_instructions = amendment_node.get("amended_instructions", "")
    skill_name = skill_props.get("name", skill_id)

    # Write to disk if requested
    if write_to_disk:
        source_path = skill_props.get("source_path", "")
        if source_path and Path(source_path).exists():
            file_content = Path(source_path).read_text(encoding="utf-8")
            new_content = _replace_skill_md_body(file_content, amended_instructions)
            Path(source_path).write_text(new_content, encoding="utf-8")
            logger.info("Wrote amended instructions to %s", source_path)

    # Update skill in graph + re-enrich
    new_hash = _content_hash(amended_instructions)
    try:
        from cognee.cognee_skills.tasks.enrich_skills import enrich_skills
        from cognee.cognee_skills.tasks.materialize_task_patterns import materialize_task_patterns
        from cognee.cognee_skills.models.skill import Skill

        skill_obj = Skill(
            id=uuid.UUID(str(skill_props.get("id", skill_nid))),
            skill_id=skill_id,
            name=skill_name,
            description=skill_props.get("description", ""),
            instructions=amended_instructions,
            content_hash=new_hash,
        )

        enriched = await enrich_skills([skill_obj])
        if enriched:
            materialized = await materialize_task_patterns(enriched)
            _tag_with_nodeset(materialized, node_set)
            await add_data_points(materialized)
            logger.info("Re-enriched skill '%s' after amendment", skill_name)
        else:
            _tag_with_nodeset([skill_obj], node_set)
            await add_data_points([skill_obj])
    except Exception as exc:
        logger.warning("Re-enrichment after amendment failed, persisting basic update: %s", exc)
        from cognee.cognee_skills.models.skill import Skill

        skill_obj = Skill(
            id=uuid.UUID(str(skill_props.get("id", skill_nid))),
            skill_id=skill_id,
            name=skill_name,
            description=skill_props.get("description", ""),
            instructions=amended_instructions,
            content_hash=new_hash,
        )
        _tag_with_nodeset([skill_obj], node_set)
        await add_data_points([skill_obj])

    # Emit change event
    event = _make_change_event(
        skill_id, skill_name, "amended", old_hash=old_hash, new_hash=new_hash
    )
    _tag_with_nodeset([event], node_set)
    await add_data_points([event])

    # Update amendment status via DataPoint upsert
    applied_at_ms = int(time.time() * 1000)
    amendment_node["status"] = "applied"
    amendment_node["applied_at_ms"] = applied_at_ms
    amendment_dp = _reconstruct_amendment(amendment_node)
    _tag_with_nodeset([amendment_dp], node_set)
    await add_data_points([amendment_dp])

    result = {
        "success": True,
        "amendment_id": amendment_id,
        "skill_id": skill_id,
        "skill_name": skill_name,
        "status": "applied",
        "old_hash": old_hash,
        "new_hash": new_hash,
    }

    # Optional validation
    if validate and validation_task_text:
        try:
            from cognee.cognee_skills.execute import execute_skill

            skill_dict = {
                "skill_id": skill_id,
                "name": skill_name,
                "instructions": amended_instructions,
                "instruction_summary": skill_props.get("instruction_summary", ""),
                "description": skill_props.get("description", ""),
                "tags": skill_props.get("tags", []),
                "complexity": skill_props.get("complexity", ""),
                "source_path": skill_props.get("source_path", ""),
                "task_patterns": [],
            }
            validation_result = await execute_skill(
                skill=skill_dict, task_text=validation_task_text
            )
            result["validation"] = validation_result
        except Exception as exc:
            result["validation"] = {"success": False, "error": str(exc)}

    return result


async def rollback_amendify(
    amendment_id: str,
    write_to_disk: bool = False,
    node_set: str = "skills",
) -> bool:
    """Rollback an applied amendment, restoring original instructions.

    Args:
        amendment_id: The amendment to rollback.
        write_to_disk: If True, also restore the original SKILL.md on disk.
        node_set: Graph node set.

    Returns:
        True if rollback succeeded, False otherwise.
    """
    amendment_node = await _load_amendment_from_graph(amendment_id, node_set)
    if amendment_node is None:
        logger.warning("Amendment '%s' not found", amendment_id)
        return False

    if amendment_node.get("status") != "applied":
        logger.warning(
            "Amendment '%s' status is '%s', not 'applied'",
            amendment_id,
            amendment_node.get("status"),
        )
        return False

    skill_id = amendment_node.get("skill_id", "")
    skill_result = await _load_skill_from_graph(skill_id, node_set)
    if skill_result is None:
        logger.warning("Skill '%s' not found for rollback", skill_id)
        return False

    skill_nid, skill_props = skill_result
    old_hash = skill_props.get("content_hash", "")
    original_instructions = amendment_node.get("original_instructions", "")
    skill_name = skill_props.get("name", skill_id)

    # Restore on disk if requested
    if write_to_disk:
        source_path = skill_props.get("source_path", "")
        if source_path and Path(source_path).exists():
            file_content = Path(source_path).read_text(encoding="utf-8")
            new_content = _replace_skill_md_body(file_content, original_instructions)
            Path(source_path).write_text(new_content, encoding="utf-8")
            logger.info("Restored original instructions to %s", source_path)

    # Restore original instructions + re-enrich
    new_hash = _content_hash(original_instructions)
    try:
        from cognee.cognee_skills.tasks.enrich_skills import enrich_skills
        from cognee.cognee_skills.tasks.materialize_task_patterns import materialize_task_patterns
        from cognee.cognee_skills.models.skill import Skill

        skill_obj = Skill(
            id=uuid.UUID(str(skill_props.get("id", skill_nid))),
            skill_id=skill_id,
            name=skill_name,
            description=skill_props.get("description", ""),
            instructions=original_instructions,
            content_hash=new_hash,
        )
        enriched = await enrich_skills([skill_obj])
        if enriched:
            materialized = await materialize_task_patterns(enriched)
            _tag_with_nodeset(materialized, node_set)
            await add_data_points(materialized)
        else:
            _tag_with_nodeset([skill_obj], node_set)
            await add_data_points([skill_obj])
    except Exception as exc:
        logger.warning("Re-enrichment after rollback failed, persisting basic update: %s", exc)
        from cognee.cognee_skills.models.skill import Skill

        skill_obj = Skill(
            id=uuid.UUID(str(skill_props.get("id", skill_nid))),
            skill_id=skill_id,
            name=skill_name,
            description=skill_props.get("description", ""),
            instructions=original_instructions,
            content_hash=new_hash,
        )
        _tag_with_nodeset([skill_obj], node_set)
        await add_data_points([skill_obj])

    # Emit change event
    event = _make_change_event(
        skill_id, skill_name, "rolled_back", old_hash=old_hash, new_hash=new_hash
    )
    _tag_with_nodeset([event], node_set)
    await add_data_points([event])

    # Update amendment status via DataPoint upsert
    amendment_node["status"] = "rolled_back"
    amendment_dp = _reconstruct_amendment(amendment_node)
    _tag_with_nodeset([amendment_dp], node_set)
    await add_data_points([amendment_dp])

    logger.info("Rolled back amendment '%s' for skill '%s'", amendment_id, skill_name)
    return True


async def evaluate_amendify(
    amendment_id: str,
    node_set: str = "skills",
) -> dict:
    """Evaluate an amendment by comparing pre- and post-amendment success scores.

    Args:
        amendment_id: The amendment to evaluate.
        node_set: Graph node set.

    Returns:
        Dict with pre_avg, post_avg, improvement, run_count, recommendation.
    """
    amendment_node = await _load_amendment_from_graph(amendment_id, node_set)
    if amendment_node is None:
        return {"error": f"Amendment '{amendment_id}' not found"}

    skill_id = amendment_node.get("skill_id", "")
    pre_avg = float(amendment_node.get("pre_amendment_avg_score", 0.0))
    applied_at_ms = int(amendment_node.get("applied_at_ms", 0))

    # Load all SkillRun nodes for this skill
    engine = await get_graph_engine()
    raw_nodes, _ = await engine.get_nodeset_subgraph(node_type=NodeSet, node_name=[node_set])

    # Find post-amendment runs (created after the amendment was applied)
    post_scores = []
    for _, props in raw_nodes:
        if props.get("type") == "SkillRun" and props.get("selected_skill_id") == skill_id:
            started = int(props.get("started_at_ms", 0))
            if applied_at_ms == 0 or started > applied_at_ms:
                score = float(props.get("success_score", 0.0))
                post_scores.append(score)

    post_avg = sum(post_scores) / len(post_scores) if post_scores else 0.0
    improvement = post_avg - pre_avg
    recommendation = "keep" if improvement >= 0 else "rollback"

    # Update the amendment node with post-amendment stats via DataPoint upsert
    amendment_node["post_amendment_avg_score"] = post_avg
    amendment_node["post_amendment_run_count"] = len(post_scores)
    amendment_dp = _reconstruct_amendment(amendment_node)
    _tag_with_nodeset([amendment_dp], node_set)
    await add_data_points([amendment_dp])

    return {
        "amendment_id": amendment_id,
        "skill_id": skill_id,
        "pre_avg": pre_avg,
        "post_avg": post_avg,
        "improvement": improvement,
        "run_count": len(post_scores),
        "recommendation": recommendation,
    }
```
