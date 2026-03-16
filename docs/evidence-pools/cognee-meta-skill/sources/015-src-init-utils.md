---
source-id: "015"
title: "Raw Source — __init__.py + utils.py + example.py (API surface, helpers, demo)"
type: local
path: "cognee/cognee_skills/__init__.py + utils.py + example.py"
url: "https://github.com/topoteretes/cognee/tree/demo/graphskill_COG-4178/cognee/cognee_skills"
fetched: 2026-03-15T21:10:00Z
hash: "sha256:placeholder"
---

# __init__.py

```python
"""cognee.cognee_skills — skill routing with learned preferences.

Primary API (via ``from cognee import skills``):
    skills.ingest()              — parse SKILL.md files, enrich via LLM, store in graph + vector
    skills.ingest_meta_skill()   — ingest the cognee-skills meta-skill (self-improvement loop guide)
    skills.upsert()              — re-ingest, skipping unchanged, updating changed, removing deleted
    skills.remove()              — remove a single skill by id
    skills.get_context()         — ranked skill recommendations for a task
    skills.load()                — full details (including full instructions) for a skill by id
    skills.run()                 — find the best skill and execute it (one call does everything)
    skills.execute()             — load a skill and execute it against a task via LLM
    skills.list()                — list all ingested skills with summaries
    skills.observe()             — record a skill execution (persists to graph immediately)
    skills.inspect()             — inspect why a skill fails
    skills.preview_amendify()    — preview a proposed amendment to fix a failing skill
    skills.amendify()            — apply a proposed amendment
    skills.rollback_amendify()   — rollback an applied amendment
    skills.evaluate_amendify()   — compare pre/post amendment success scores
    skills.auto_amendify()       — fully automatic: inspect → preview → apply in one call
    skills.execute(auto_amendify=True) — execute with automatic amendment on failure

Lower-level API:
    ingest_skills()              — parse SKILL.md files, enrich via LLM, store in graph + vector
    upsert_skills()              — diff-based re-ingestion of a skills folder
    remove_skill()               — remove a single skill by id from graph + vector
    recommend_skills()           — semantic retrieval ranked by vector similarity + prefers weights
    execute_skill()              — execute a loaded skill dict against a task via LLM
    record_skill_run()           — record a skill execution to graph and update prefers weights
    inspect_skill()              — analyze failed runs and produce an inspection
    preview_skill_amendify()     — generate amended instructions from an inspection
    amendify()                   — apply an amendment to a skill in the graph
    rollback_amendify()          — rollback an applied amendment
    evaluate_amendify()          — compare pre/post amendment success scores

Models:
    Skill, SkillRun, TaskPattern, ToolCall, CandidateSkill, SkillChangeEvent,
    SkillResource, SkillInspection, SkillAmendment
"""

from cognee.cognee_skills.client import Skills, skills
from cognee.cognee_skills.execute import evaluate_output, execute_skill
from cognee.cognee_skills.pipeline import ingest_skills, upsert_skills, remove_skill
from cognee.cognee_skills.retrieve import recommend_skills
from cognee.cognee_skills.observe import record_skill_run
from cognee.cognee_skills.inspect import inspect_skill
from cognee.cognee_skills.preview_amendify import preview_skill_amendify
from cognee.cognee_skills.amendify import amendify, rollback_amendify, evaluate_amendify

from cognee.cognee_skills.models import (
    CandidateSkill,
    Skill,
    SkillAmendment,
    SkillChangeEvent,
    SkillInspection,
    SkillResource,
    SkillRun,
    TaskPattern,
    ToolCall,
)

__all__ = [
    "Skills",
    "skills",
    "ingest_skills",
    "upsert_skills",
    "remove_skill",
    "recommend_skills",
    "evaluate_output",
    "execute_skill",
    "record_skill_run",
    "inspect_skill",
    "preview_skill_amendify",
    "amendify",
    "rollback_amendify",
    "evaluate_amendify",
    "CandidateSkill",
    "Skill",
    "SkillAmendment",
    "SkillChangeEvent",
    "SkillInspection",
    "SkillResource",
    "SkillRun",
    "TaskPattern",
    "ToolCall",
]
```

---

# utils.py

```python
"""Shared helpers for the skills package."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid5, UUID

from cognee.modules.engine.utils.generate_timestamp_datapoint import generate_timestamp_datapoint
from cognee.modules.engine.models.Timestamp import Timestamp

from cognee.cognee_skills.models.skill_change_event import SkillChangeEvent

EVENT_NAMESPACE = UUID("d4e5f6a7-b8c9-0123-def0-123456789abc")


def _now_timestamp() -> Timestamp:
    """Create a Cognee Timestamp DataPoint for the current UTC time."""
    now = datetime.now(timezone.utc)
    raw = Timestamp(
        id=UUID(int=0),
        time_at=0,
        year=now.year,
        month=now.month,
        day=now.day,
        hour=now.hour,
        minute=now.minute,
        second=now.second,
        timestamp_str="",
    )
    return generate_timestamp_datapoint(raw)


def _make_change_event(
    skill_id: str,
    skill_name: str,
    change_type: str,
    old_hash: str = "",
    new_hash: str = "",
) -> SkillChangeEvent:
    ts = _now_timestamp()
    return SkillChangeEvent(
        id=uuid5(EVENT_NAMESPACE, f"{skill_id}:{change_type}:{ts.time_at}"),
        name=f"skill_{change_type}: {skill_name}",
        description=f"Skill '{skill_name}' ({skill_id}) was {change_type}.",
        skill_id=skill_id,
        change_type=change_type,
        old_content_hash=old_hash,
        new_content_hash=new_hash,
        skill_name=skill_name,
        at=ts,
    )
```

---

# example.py

```python
"""End-to-end demo: closed feedback loop.

Ingest skills -> recommend -> pick top -> simulate execution -> record ->
recommend again (prefers weights shift).

Usage:
    python -m cognee.cognee_skills.example                           # uses built-in example_skills/
    python -m cognee.cognee_skills.example /path/to/skills           # uses external folder
    python -m cognee.cognee_skills.example /path/to/skills my-repo   # with source_repo label
"""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

import cognee

from cognee.infrastructure.databases.graph import get_graph_engine
from cognee.infrastructure.databases.vector import get_vector_engine
from cognee.modules.engine.models.node_set import NodeSet
from cognee.cognee_skills.pipeline import ingest_skills
from cognee.cognee_skills.observe import record_skill_run
from cognee.cognee_skills.retrieve import recommend_skills

COGNEE_SYSTEM_DIR = Path(__file__).parent / ".cognee_system"
DEFAULT_SKILLS_DIR = Path(__file__).parent / "example_skills"

SESSION_ID = "demo-session-001"

SIMULATED_EXECUTIONS: Dict[str, Dict[str, Any]] = {
    "Compress my conversation history to fit in 8k tokens": {
        "result_summary": "Compressed 32k tokens to 7.5k using anchored iterative summarization.",
        "success_score": 0.92,
        "feedback": 0.8,
        "latency_ms": 3520,
    },
    "Reduce my prompt to under 4k tokens": {
        "result_summary": "Compressed 16k tokens to 3.8k using hierarchical summarization.",
        "success_score": 0.85,
        "feedback": 0.6,
        "latency_ms": 2100,
    },
}


async def _resolve_task_pattern(task_text: str, top_rec: Dict[str, Any]) -> str:
    """Pick the best task_pattern_id for a query.

    First tries a vector search on TaskPattern_text (same collection that
    retrieval uses) so the promoted prefers edge lands on a pattern that
    retrieval's matched-patterns-only logic will find.  Falls back to the
    first TaskPattern on the selected skill, or "".
    """
    try:
        vector_engine = get_vector_engine()
        hits = await vector_engine.search(
            collection_name="TaskPattern_text",
            query_text=task_text,
            limit=1,
            include_payload=True,
        )
        if hits:
            hit_id = str(hits[0].id)
            engine = await get_graph_engine()
            raw_nodes, _ = await engine.get_nodeset_subgraph(
                node_type=NodeSet, node_name=["skills"]
            )
            for nid, props in raw_nodes:
                if str(nid) == hit_id and props.get("type") == "TaskPattern":
                    pk = props.get("pattern_key", "")
                    if pk:
                        return pk
    except Exception:
        pass

    patterns = top_rec.get("task_patterns", [])
    return patterns[0]["pattern_key"] if patterns else ""


def _build_candidate_list(recs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert recommendation list to the candidate_skills format for observe."""
    return [
        {
            "skill_id": r["skill_id"],
            "score": r["score"],
            "signals": {"vector": r["vector_score"], "prefers": r["prefers_score"]},
        }
        for r in recs
    ]


def _print_recs(recs: List[Dict[str, Any]]) -> None:
    for i, rec in enumerate(recs):
        print(
            f"    {i + 1}. {rec['name']}  "
            f"vector={rec['vector_score']}  prefers={rec['prefers_score']}  "
            f"final={rec['score']}"
        )
        if rec["prior_runs"]:
            best = max(r["success_score"] for r in rec["prior_runs"])
            print(f"       prior_runs={len(rec['prior_runs'])}  best_score={best}")


async def _recommend_and_record(
    task_text: str,
    step_label: str,
) -> List[Dict[str, Any]]:
    """Full closed-loop iteration: recommend -> pick top -> record."""
    print(f"\n{'=' * 60}")
    print(f"{step_label}")
    print("=" * 60)

    # Recommend
    recs = await recommend_skills(task_text, top_k=3, node_set="skills")
    print(f"  Query: {task_text}")
    print("  Recommendations:")
    _print_recs(recs)

    if not recs:
        print("  (no skills found, skipping record/promote)")
        return recs

    top = recs[0]

    # Resolve pattern via vector search
    pattern_id = await _resolve_task_pattern(task_text, top)
    print(f"  Selected: {top['name']}  |  pattern: {pattern_id}")

    # Simulate execution
    sim = SIMULATED_EXECUTIONS.get(
        task_text,
        {
            "result_summary": f"Executed {top['name']} successfully.",
            "success_score": 0.80,
            "feedback": 0.5,
            "latency_ms": 1500,
        },
    )

    # Record to cache
    await record_skill_run(
        session_id=SESSION_ID,
        task_text=task_text,
        selected_skill_id=top["skill_id"],
        task_pattern_id=pattern_id,
        result_summary=sim["result_summary"],
        success_score=sim["success_score"],
        candidate_skills=_build_candidate_list(recs),
        router_version="v1.0-closed-loop",
        feedback=sim["feedback"],
        latency_ms=sim["latency_ms"],
    )
    print(
        f"  Recorded run: skill={top['skill_id']}  "
        f"score={sim['success_score']}  pattern={pattern_id}"
    )

    return recs


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    skills_folder = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SKILLS_DIR
    source_repo = sys.argv[2] if len(sys.argv) > 2 else ""

    if not skills_folder.is_dir():
        print(f"Error: {skills_folder} is not a directory.")
        sys.exit(1)

    skill_count = sum(
        1 for d in skills_folder.iterdir() if d.is_dir() and (d / "SKILL.md").exists()
    )
    print(f"Found {skill_count} skills in {skills_folder}")

    cognee.config.system_root_directory(str(COGNEE_SYSTEM_DIR))
    await cognee.prune.prune_system(metadata=True)

    # ── Step 1: Ingest skills ──
    print("\n" + "=" * 60)
    print("STEP 1: Ingesting skills")
    print("=" * 60)
    await ingest_skills(
        skills_folder=skills_folder,
        dataset_name="skills",
        source_repo=source_repo,
        node_set="skills",
    )

    # ── Step 2: First recommend + record + promote (prefers all zero) ──
    query1 = "Compress my conversation history to fit in 8k tokens"
    baseline_recs = await _recommend_and_record(
        query1,
        "STEP 2: First query (no prefers data yet)",
    )

    # ── Step 3: Second task + recommend + record + promote ──
    query2 = "Reduce my prompt to under 4k tokens"
    await _recommend_and_record(
        query2,
        "STEP 3: Second query (reinforces prefers stats)",
    )

    # ── Step 4: Re-run first query — show prefers boost ──
    print(f"\n{'=' * 60}")
    print("STEP 4: Re-run first query (should show prefers boost)")
    print("=" * 60)
    final_recs = await recommend_skills(query1, top_k=3, node_set="skills")
    print(f"  Query: {query1}")
    print("  Recommendations:")
    _print_recs(final_recs)

    # ── Before/after comparison ──
    if baseline_recs and final_recs:
        b = baseline_recs[0]
        f = final_recs[0]
        print(f"\n  Before/After for top skill ({f['name']}):")
        print(f"    vector_score:  {b['vector_score']}  ->  {f['vector_score']}")
        print(f"    prefers_score: {b['prefers_score']}  ->  {f['prefers_score']}")
        print(f"    final_score:   {b['score']}  ->  {f['score']}")

    # ── Step 5: Visualize the graph ──
    print(f"\n{'=' * 60}")
    print("STEP 5: Visualizing the skills graph")
    print("=" * 60)
    graph_path = COGNEE_SYSTEM_DIR.parent / "graph.html"
    await cognee.visualize_graph(str(graph_path))
    print(f"  Graph saved to: {graph_path}")
    print(f"  Open in browser: file://{graph_path}")
    print("\nDone.")


if __name__ == "__main__":
    asyncio.run(main())
```
