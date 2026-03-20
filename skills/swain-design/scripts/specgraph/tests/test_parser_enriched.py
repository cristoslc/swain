"""Tests for enriched linked-artifacts parsing in specgraph parser."""
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
