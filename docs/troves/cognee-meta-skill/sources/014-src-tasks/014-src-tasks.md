---
source-id: "014"
title: "Raw Source — tasks/ (pipeline stages: parse, enrich, materialize, apply_node_set)"
type: local
path: "cognee/cognee_skills/tasks/"
url: "https://github.com/topoteretes/cognee/tree/demo/graphskill_COG-4178/cognee/cognee_skills/tasks"
fetched: 2026-03-15T21:10:00Z
hash: "sha256:placeholder"
---

# tasks/parse_skills.py

```python
"""Pipeline task that parses a skills folder into Skill DataPoints."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from cognee.cognee_skills.models.skill import Skill
from cognee.cognee_skills.parser.skill_parser import parse_skills_folder


def parse_skills_task(
    data: Any,
    context: Optional[Dict[str, Any]] = None,
    source_repo: str = "",
) -> List[Skill]:
    """Parse a skills folder path into Skill DataPoints.

    Accepts either a string path or a list whose first element is a string path.
    Returns a flat list of Skill DataPoints ready for add_data_points.
    """
    if isinstance(data, (list, tuple)):
        skills_path = data[0] if data else None
    else:
        skills_path = data

    if not skills_path or not isinstance(skills_path, str):
        raise ValueError(f"Expected a skills folder path, got: {skills_path!r}")

    return parse_skills_folder(skills_path, source_repo=source_repo)
```

---

# tasks/enrich_skills.py

```python
"""LLM enrichment task: fills derived Skill fields from raw content."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

from cognee.infrastructure.llm.LLMGateway import LLMGateway
from cognee.infrastructure.llm import get_llm_config

from cognee.cognee_skills.models.skill import Skill

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are an expert at analyzing agentic skill documentation.
Given the raw content of a skill document, extract structured metadata.
Be concise and precise. Only include information that is clearly supported by the text.
If a field cannot be determined, use a sensible default rather than guessing."""

USER_PROMPT_TEMPLATE = """\
Skill name: {name}
Skill description (may be empty): {description}

Full skill document:
---
{instructions}
---

Analyze this skill and fill in the following fields:
- description: A concise, normalized 1-2 sentence description of what this skill is. \
Improve on the raw description if present, or generate one if empty.
- instruction_summary: A concise 2-3 sentence summary of what this skill does and when to use it.
- triggers: A list of short phrases describing when this skill should be activated \
(e.g. "user asks to summarize a document", "code review requested").
- tags: A list of category tags from this vocabulary: \
context-management, evaluation, code, memory, multi-agent, tool-design, data-processing, \
web, filesystem, planning, debugging, testing, documentation, security, performance, other. \
Pick 1-5 that apply.
- complexity: Classify as "simple" (single-step, no orchestration), \
"workflow" (multi-step with defined sequence), or "agent" (requires autonomous decision-making).
- task_pattern_candidates: 3-8 short slug-style patterns this skill can solve \
(e.g. "llm_evaluation", "context_compression", "tool_api_design"). Use snake_case.
- confidence: Your confidence in the extraction from 0.0 to 1.0."""


class SkillEnrichment(BaseModel):
    """LLM response model for skill enrichment — only the derived fields."""

    description: str = Field(
        description="Concise, normalized 1-2 sentence description of the skill"
    )
    instruction_summary: str = Field(description="2-3 sentence summary of the skill")
    triggers: List[str] = Field(default_factory=list, description="When to activate this skill")
    tags: List[str] = Field(default_factory=list, description="Category tags")
    complexity: Literal["simple", "workflow", "agent"] = Field(default="simple")
    task_pattern_candidates: List[str] = Field(
        default_factory=list, description="Canonical task patterns this skill solves"
    )
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)


async def _enrich_one(skill: Skill, llm_model_name: str) -> Skill:
    """Call the LLM to enrich a single Skill's derived fields."""
    user_prompt = USER_PROMPT_TEMPLATE.format(
        name=skill.name,
        description=skill.description,
        instructions=skill.instructions[:8000],
    )

    try:
        result: SkillEnrichment = await LLMGateway.acreate_structured_output(
            text_input=user_prompt,
            system_prompt=SYSTEM_PROMPT,
            response_model=SkillEnrichment,
        )

        skill.description = result.description
        skill.instruction_summary = result.instruction_summary
        skill.triggers = result.triggers
        skill.tags = result.tags
        skill.complexity = result.complexity
        skill.task_pattern_candidates = result.task_pattern_candidates
        skill.enrichment_model = llm_model_name
        skill.enrichment_confidence = result.confidence

        logger.info("Enriched skill '%s' (confidence=%.2f)", skill.name, result.confidence)

    except Exception as exc:
        logger.warning("Failed to enrich skill '%s': %s", skill.name, exc)

    return skill


async def enrich_skills(
    skills: List[Skill],
    context: Optional[Dict[str, Any]] = None,
) -> List[Skill]:
    """Enrich a batch of Skills using LLM structured extraction.

    Fills: description, instruction_summary, triggers, tags, complexity,
           task_pattern_candidates, enrichment_model, enrichment_confidence.
    Raw parser values preserved in: description_raw, triggers_raw, tags_raw.
    Never modifies: skill_id, instructions, source_path, source_repo,
                    content_hash, resources, tools.
    """
    llm_config = get_llm_config()
    llm_model_name = llm_config.llm_model or "unknown"

    enriched = await asyncio.gather(*[_enrich_one(s, llm_model_name) for s in skills])

    logger.info(
        "Enriched %d/%d skills", len([s for s in enriched if s.instruction_summary]), len(skills)
    )
    return list(enriched)
```

---

# tasks/materialize_task_patterns.py

```python
"""Materialize TaskPattern nodes from Skill.task_pattern_candidates + LLM enrich."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID, uuid5

from pydantic import BaseModel, Field

from cognee.infrastructure.engine import Edge
from cognee.infrastructure.llm.LLMGateway import LLMGateway
from cognee.infrastructure.llm import get_llm_config

from cognee.cognee_skills.models.skill import Skill
from cognee.cognee_skills.models.task_pattern import TaskPattern

logger = logging.getLogger(__name__)

NAMESPACE = UUID("b2c3d4e5-f6a7-8901-bcde-f12345678901")

CATEGORIES = [
    "context-management",
    "evaluation",
    "code",
    "memory",
    "multi-agent",
    "tool-design",
    "data-processing",
    "web",
    "filesystem",
    "planning",
    "debugging",
    "testing",
    "documentation",
    "security",
    "performance",
    "other",
]

SYSTEM_PROMPT = """\
You are an expert at categorizing agentic task patterns.
Given a task pattern slug and the names of skills that solve it,
produce a short human-readable description and a category."""

USER_PROMPT_TEMPLATE = """\
Task pattern slug: {slug}
Skills that solve this pattern: {skill_names}

Fill in:
- text: A concise 1-2 sentence description of what this task pattern represents.
- category: Pick exactly one from: {categories}"""


class TaskPatternEnrichment(BaseModel):
    """LLM response model for task pattern enrichment."""

    text: str = Field(description="1-2 sentence description of the task pattern")
    category: str = Field(default="other", description="Category from controlled vocabulary")


def _make_pattern_id(slug: str) -> UUID:
    return uuid5(NAMESPACE, slug)


async def _enrich_one_pattern(
    slug: str,
    skill_names: List[str],
    llm_model: str,
) -> TaskPatternEnrichment:
    """LLM call to produce text + category for one TaskPattern."""
    user_prompt = USER_PROMPT_TEMPLATE.format(
        slug=slug,
        skill_names=", ".join(skill_names),
        categories=", ".join(CATEGORIES),
    )
    try:
        return await LLMGateway.acreate_structured_output(
            text_input=user_prompt,
            system_prompt=SYSTEM_PROMPT,
            response_model=TaskPatternEnrichment,
        )
    except Exception as exc:
        logger.warning("Failed to enrich pattern '%s': %s", slug, exc)
        return TaskPatternEnrichment(
            text=slug.replace("_", " "),
            category="other",
        )


async def materialize_task_patterns(
    skills: List[Skill],
    context: Optional[Dict[str, Any]] = None,
) -> List[Skill]:
    """Create TaskPattern nodes from candidates and wire solves edges.

    1. Collect all task_pattern_candidates across skills, deduplicate.
    2. LLM-enrich each unique pattern (text + category).
    3. Create TaskPattern DataPoints with deterministic IDs.
    4. Populate Skill.solves with (Edge, TaskPattern) tuples.
    """
    slug_to_skill_ids: Dict[str, List[str]] = {}
    slug_to_skill_names: Dict[str, List[str]] = {}
    slug_to_examples: Dict[str, List[str]] = {}

    for skill in skills:
        for slug in skill.task_pattern_candidates:
            slug_to_skill_ids.setdefault(slug, []).append(skill.skill_id)
            slug_to_skill_names.setdefault(slug, []).append(skill.name)
            for trigger in skill.triggers[:3]:
                slug_to_examples.setdefault(slug, []).append(trigger)

    if not slug_to_skill_ids:
        logger.info("No task_pattern_candidates found; skipping materialization.")
        return skills

    llm_config = get_llm_config()
    llm_model = llm_config.llm_model or "unknown"

    enrichments = await asyncio.gather(
        *[
            _enrich_one_pattern(slug, names, llm_model)
            for slug, names in slug_to_skill_names.items()
        ]
    )

    patterns: Dict[str, TaskPattern] = {}
    for (slug, _), enrichment in zip(slug_to_skill_ids.items(), enrichments):
        examples = list(dict.fromkeys(slug_to_examples.get(slug, [])))[:10]
        patterns[slug] = TaskPattern(
            id=_make_pattern_id(slug),
            pattern_id=slug,
            name=slug,
            pattern_key=slug,
            text=enrichment.text,
            category=enrichment.category,
            source_skill_ids=slug_to_skill_ids[slug],
            examples=examples,
            enrichment_model=llm_model,
            enrichment_confidence=0.9,
        )

    for skill in skills:
        skill.solves = [
            (Edge(relationship_type="solves"), patterns[slug])
            for slug in skill.task_pattern_candidates
            if slug in patterns
        ]

    logger.info(
        "Materialized %d TaskPatterns from %d skills",
        len(patterns),
        len(skills),
    )
    return skills
```

---

# tasks/apply_node_set.py

```python
"""Pipeline task that sets belongs_to_set on Skill DataPoints using Cognee's NodeSet."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from cognee.low_level import DataPoint
from cognee.modules.engine.models.node_set import NodeSet
from cognee.modules.engine.utils.generate_node_id import generate_node_id

from cognee.cognee_skills.models.skill import Skill


def _tag(dp: DataPoint, ns: NodeSet, node_set: str) -> None:
    """Add the NodeSet to a DataPoint's belongs_to_set if not already present."""
    existing = dp.belongs_to_set or []
    existing_names = {s.name if hasattr(s, "name") else s for s in existing}
    if node_set not in existing_names:
        dp.belongs_to_set = list(existing) + [ns]


async def apply_node_set(
    skills: List[Skill],
    context: Optional[Dict[str, Any]] = None,
    node_set: str = "skills",
) -> List[Skill]:
    """Tag all skills and their children with belongs_to_set."""
    ns = NodeSet(id=generate_node_id(f"NodeSet:{node_set}"), name=node_set)

    for skill in skills:
        _tag(skill, ns, node_set)
        for resource in skill.resources or []:
            _tag(resource, ns, node_set)
        for _edge, pattern in skill.solves or []:
            _tag(pattern, ns, node_set)

    return skills
```
