"""Tests for enriched linked-artifacts and artifact-refs parsing in specgraph parser."""
import sys
from pathlib import Path

# Add parent to path so we can import parser
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from parser import parse_frontmatter, extract_list_ids


def test_plain_string_linked_artifacts_unchanged():
    """Plain string entries continue to work as before."""
    content = """---
title: "Test"
artifact: SPEC-001
linked-artifacts:
  - SPEC-002
  - DESIGN-003
---
# Body
"""
    fields = parse_frontmatter(content)
    assert fields is not None
    ids = extract_list_ids(fields, "linked-artifacts")
    assert "SPEC-002" in ids
    assert "DESIGN-003" in ids


def test_enriched_entry_parsed_as_dict():
    """Enriched entries with artifact/rel/commit become dicts in the list."""
    content = """---
title: "Test TRAIN"
artifact: TRAIN-001
linked-artifacts:
  - artifact: SPEC-067
    rel: [documents]
    commit: abc1234
    verified: 2026-03-19
---
# Body
"""
    fields = parse_frontmatter(content)
    assert fields is not None
    la = fields["linked-artifacts"]
    assert len(la) == 1
    assert isinstance(la[0], dict)
    assert la[0]["artifact"] == "SPEC-067"
    assert la[0]["rel"] == ["documents"]
    assert la[0]["commit"] == "abc1234"
    assert la[0]["verified"] == "2026-03-19"


def test_enriched_entry_extract_list_ids():
    """extract_list_ids returns artifact IDs from enriched dict entries."""
    content = """---
title: "Test TRAIN"
artifact: TRAIN-001
linked-artifacts:
  - artifact: SPEC-067
    rel: [documents]
    commit: abc1234
    verified: 2026-03-19
  - DESIGN-003
---
# Body
"""
    fields = parse_frontmatter(content)
    ids = extract_list_ids(fields, "linked-artifacts")
    assert "SPEC-067" in ids
    assert "DESIGN-003" in ids


def test_mixed_plain_and_enriched():
    """Lists can contain both plain strings and enriched dicts."""
    content = """---
title: "Test TRAIN"
artifact: TRAIN-001
linked-artifacts:
  - artifact: SPEC-067
    rel: [documents]
    commit: abc1234
    verified: 2026-03-19
  - artifact: RUNBOOK-002
    rel: [documents, depends-on]
    commit: def5678
    verified: 2026-03-19
  - DESIGN-003
---
# Body
"""
    fields = parse_frontmatter(content)
    la = fields["linked-artifacts"]
    assert len(la) == 3
    assert isinstance(la[0], dict)
    assert isinstance(la[1], dict)
    assert isinstance(la[2], str)
    assert la[1]["rel"] == ["documents", "depends-on"]


def test_enriched_multiple_rels():
    """rel field parsed as a list even with multiple values."""
    content = """---
title: "Test"
artifact: TRAIN-001
linked-artifacts:
  - artifact: SPEC-042
    rel: [documents, depends-on]
---
# Body
"""
    fields = parse_frontmatter(content)
    la = fields["linked-artifacts"]
    assert la[0]["rel"] == ["documents", "depends-on"]


def test_enriched_no_commit_pin():
    """Enriched entry without commit pin is valid (just rel, no staleness tracking)."""
    content = """---
title: "Test"
artifact: TRAIN-001
linked-artifacts:
  - artifact: SPEC-042
    rel: [documents]
---
# Body
"""
    fields = parse_frontmatter(content)
    la = fields["linked-artifacts"]
    assert isinstance(la[0], dict)
    assert la[0]["artifact"] == "SPEC-042"
    assert "commit" not in la[0]


# --- artifact-refs tests ---


def test_artifact_refs_parsed_as_dict():
    """artifact-refs entries with artifact/rel/commit become dicts in the list."""
    content = """---
title: "Test TRAIN"
artifact: TRAIN-001
artifact-refs:
  - artifact: SPEC-067
    rel: [documents]
    commit: abc1234
    verified: 2026-03-19
---
# Body
"""
    fields = parse_frontmatter(content)
    assert fields is not None
    ar = fields["artifact-refs"]
    assert len(ar) == 1
    assert isinstance(ar[0], dict)
    assert ar[0]["artifact"] == "SPEC-067"
    assert ar[0]["rel"] == ["documents"]
    assert ar[0]["commit"] == "abc1234"
    assert ar[0]["verified"] == "2026-03-19"


def test_artifact_refs_extract_list_ids():
    """extract_list_ids returns artifact IDs from artifact-refs dict entries."""
    content = """---
title: "Test TRAIN"
artifact: TRAIN-001
artifact-refs:
  - artifact: SPEC-067
    rel: [documents]
    commit: abc1234
    verified: 2026-03-19
---
# Body
"""
    fields = parse_frontmatter(content)
    ids = extract_list_ids(fields, "artifact-refs")
    assert "SPEC-067" in ids


def test_artifact_refs_multiple_entries():
    """Multiple artifact-refs entries are all parsed."""
    content = """---
title: "Test DESIGN"
artifact: DESIGN-001
artifact-refs:
  - artifact: SPEC-067
    rel: [aligned]
    commit: abc1234
    verified: 2026-03-19
  - artifact: EPIC-005
    rel: [aligned]
    commit: def5678
    verified: 2026-03-19
---
# Body
"""
    fields = parse_frontmatter(content)
    ar = fields["artifact-refs"]
    assert len(ar) == 2
    ids = extract_list_ids(fields, "artifact-refs")
    assert "SPEC-067" in ids
    assert "EPIC-005" in ids


def test_artifact_refs_coexists_with_linked_artifacts():
    """artifact-refs and linked-artifacts can coexist in the same frontmatter."""
    content = """---
title: "Test TRAIN"
artifact: TRAIN-001
linked-artifacts:
  - DESIGN-003
artifact-refs:
  - artifact: SPEC-067
    rel: [documents]
    commit: abc1234
    verified: 2026-03-19
---
# Body
"""
    fields = parse_frontmatter(content)
    la_ids = extract_list_ids(fields, "linked-artifacts")
    ar_ids = extract_list_ids(fields, "artifact-refs")
    assert "DESIGN-003" in la_ids
    assert "SPEC-067" in ar_ids


def test_sourcecode_refs_parsed():
    """sourcecode-refs entries are parsed as dicts with path/blob/commit/verified."""
    content = """---
title: "Test DESIGN"
artifact: DESIGN-001
sourcecode-refs:
  - path: src/components/Button/Button.tsx
    blob: a1b2c3d
    commit: def5678
    verified: 2026-03-19
---
# Body
"""
    fields = parse_frontmatter(content)
    assert fields is not None
    sr = fields["sourcecode-refs"]
    assert len(sr) == 1
    assert isinstance(sr[0], dict)
    assert sr[0]["path"] == "src/components/Button/Button.tsx"
    assert sr[0]["blob"] == "a1b2c3d"
    assert sr[0]["commit"] == "def5678"
    assert sr[0]["verified"] == "2026-03-19"
