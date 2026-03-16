---
source-id: "013"
title: "Raw Source — models/ (all DataPoint definitions)"
type: local
path: "cognee/cognee_skills/models/"
url: "https://github.com/topoteretes/cognee/tree/demo/graphskill_COG-4178/cognee/cognee_skills/models"
fetched: 2026-03-15T21:10:00Z
hash: "sha256:placeholder"
---

# models/__init__.py

```python
from .skill import Skill, SkillResource
from .task_pattern import TaskPattern
from .skill_run import SkillRun, ToolCall, CandidateSkill
from .skill_change_event import SkillChangeEvent
from .skill_inspection import InspectionResult, SkillInspection
from .skill_amendment import AmendmentProposal, SkillAmendment
```

---

# models/skill.py

```python
from typing import Any, Dict, List, Optional
from cognee.low_level import DataPoint
from cognee.infrastructure.engine import Edge


class SkillResource(DataPoint):
    """A bundled file within a skill folder (reference doc, script, asset)."""

    name: str
    path: str
    resource_type: str  # "reference", "script", "asset", "other"
    content: Optional[str] = None
    content_hash: str = ""
    metadata: dict = {"index_fields": ["name"]}


class Skill(DataPoint):
    """An agentic skill parsed from a SKILL.md folder."""

    skill_id: str
    name: str
    description: str
    instructions: str  # full markdown body — stored but NOT indexed

    # Parser-derived originals (never overwritten by LLM)
    description_raw: str = ""
    triggers_raw: List[str] = []
    tags_raw: List[str] = []

    # LLM-enriched fields (filled by enrich_skills task)
    instruction_summary: str = ""
    triggers: List[str] = []
    tags: List[str] = []
    complexity: str = ""  # "simple", "workflow", "agent"
    task_pattern_candidates: List[str] = []

    # Parser-only fields (deterministic, never LLM-filled)
    tools: List[str] = []
    source_path: str = ""
    source_repo: str = ""
    content_hash: str = ""
    is_active: bool = True
    extra_metadata: Optional[Dict[str, Any]] = None

    # Enrichment provenance
    enrichment_model: str = ""
    enrichment_confidence: float = 0.0

    resources: List[SkillResource] = []
    related_skills: List["Skill"] = []
    solves: List[tuple[Edge, "TaskPattern"]] = []

    metadata: dict = {"index_fields": ["name", "instruction_summary", "description"]}


from .task_pattern import TaskPattern  # noqa: E402

Skill.model_rebuild()
```

---

# models/task_pattern.py

```python
from typing import List
from cognee.low_level import DataPoint
from cognee.infrastructure.engine import Edge


class TaskPattern(DataPoint):
    """A normalized intent/task category that skills can solve."""

    pattern_id: str
    name: str = ""
    pattern_key: str = ""
    text: str  # LLM-generated intent description
    category: str = ""

    # Evidence / provenance
    source_skill_ids: List[str] = []  # which skills proposed this pattern
    examples: List[str] = []  # trigger phrases that led to this pattern
    enrichment_model: str = ""
    enrichment_confidence: float = 0.0

    prefers: List[tuple[Edge, "Skill"]] = []
    metadata: dict = {"index_fields": ["text"]}


from .skill import Skill  # noqa: E402

TaskPattern.model_rebuild()
```

---

# models/skill_run.py

```python
from typing import Any, Dict, List, Optional
from cognee.low_level import DataPoint


class ToolCall(DataPoint):
    """A single tool invocation within a skill run."""

    tool_name: str
    tool_input: Optional[Dict[str, Any]] = None
    tool_output: Optional[str] = None
    success: bool = True
    duration_ms: int = 0
    metadata: dict = {"index_fields": []}


class CandidateSkill(DataPoint):
    """A skill considered during routing, with its retrieval score and signals."""

    skill_id: str
    score: float = 0.0
    signals: Optional[Dict[str, Any]] = None
    metadata: dict = {"index_fields": []}


class SkillRun(DataPoint):
    """Record of a skill execution within a session."""

    run_id: str
    session_id: str
    cognee_session_id: str = ""
    task_text: str
    result_summary: str = ""
    success_score: float = 0.0  # 0.0 to 1.0

    # Routing decision
    candidate_skills: List[CandidateSkill] = []
    selected_skill: Optional["Skill"] = None
    selected_skill_id: str = ""
    task_pattern_id: str = ""
    router_version: str = ""

    tool_trace: List[ToolCall] = []

    error_type: str = ""
    error_message: str = ""

    started_at_ms: int = 0
    latency_ms: int = 0
    feedback: float = 0.0  # -1.0 to 1.0, 0 = no feedback

    previous_run: Optional["SkillRun"] = None

    metadata: dict = {"index_fields": ["task_text", "result_summary"]}


from .skill import Skill  # noqa: E402

SkillRun.model_rebuild()
```

---

# models/skill_amendment.py

```python
"""Amendment models for skill instruction improvements."""

from pydantic import BaseModel, Field

from cognee.low_level import DataPoint


class AmendmentProposal(BaseModel):
    """LLM response model for a proposed amendment (not persisted)."""

    amended_instructions: str = Field(description="Complete amended instructions (not a diff)")
    change_explanation: str = Field(description="What was changed and why")
    expected_improvement: str = Field(
        description="What improvement is expected from this amendment"
    )
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)


class SkillAmendment(DataPoint):
    """Persisted amendment node in graph."""

    amendment_id: str
    skill_id: str
    skill_name: str
    inspection_id: str
    original_instructions: str
    amended_instructions: str
    change_explanation: str
    expected_improvement: str
    status: str = "proposed"  # "proposed" | "applied" | "rolled_back" | "rejected"
    amendment_model: str = ""
    amendment_confidence: float = 0.0
    pre_amendment_avg_score: float = 0.0
    applied_at_ms: int = 0  # epoch ms when amendment was applied (for evaluate filtering)
    post_amendment_avg_score: float = 0.0
    post_amendment_run_count: int = 0

    metadata: dict = {"index_fields": ["change_explanation"]}
```

---

# models/skill_inspection.py

```python
"""Inspection models for analyzing skill failures."""

from typing import List, Literal

from pydantic import BaseModel, Field

from cognee.low_level import DataPoint


class InspectionResult(BaseModel):
    """LLM response model for skill failure inspection (not persisted)."""

    failure_category: Literal[
        "instruction_gap",
        "ambiguity",
        "wrong_scope",
        "tooling",
        "context_missing",
        "other",
    ] = Field(description="Category of the root failure")
    root_cause: str = Field(description="Concise description of the root cause")
    severity: Literal["low", "medium", "high", "critical"] = Field(
        description="How severe the failure is"
    )
    improvement_hypothesis: str = Field(description="Actionable hypothesis for improving the skill")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)


class SkillInspection(DataPoint):
    """Persisted inspection node in graph."""

    inspection_id: str
    skill_id: str
    skill_name: str
    failure_category: str
    root_cause: str
    severity: str
    improvement_hypothesis: str
    analyzed_run_ids: List[str] = []
    analyzed_run_count: int = 0
    avg_success_score: float = 0.0
    inspection_model: str = ""
    inspection_confidence: float = 0.0

    metadata: dict = {"index_fields": ["root_cause", "improvement_hypothesis"]}
```

---

# models/skill_change_event.py

```python
"""Temporal event for tracking skill lifecycle changes."""

from typing import Optional
from cognee.modules.engine.models.Event import Event
from cognee.modules.engine.models.Timestamp import Timestamp


class SkillChangeEvent(Event):
    """Records a skill add/update/remove for temporal queries.

    Extends Cognee's Event DataPoint so the TemporalRetriever can find it.
    """

    skill_id: str
    change_type: str = ""  # "added", "updated", "removed"
    old_content_hash: str = ""
    new_content_hash: str = ""
    skill_name: str = ""

    metadata: dict = {"index_fields": ["name", "description"]}
```
