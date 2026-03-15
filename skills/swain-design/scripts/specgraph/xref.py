"""Cross-reference scanning and validation for specgraph artifacts."""

from __future__ import annotations

from .parser import extract_list_ids, extract_scalar_id, _ARTIFACT_ID_RE


# Known artifact type prefixes — used to filter body-scanned IDs and avoid
# false positives from CVE identifiers, SPDX license tags, model names, etc.
_KNOWN_ARTIFACT_PREFIXES = frozenset({
    "VISION", "EPIC", "SPEC", "SPIKE", "ADR", "JOURNEY",
    "PERSONA", "DESIGN", "RUNBOOK", "STORY", "BUG", "INITIATIVE",
})

# All list-type frontmatter fields that carry artifact cross-references.
# Shared with graph.py to keep the two files in sync.
_XREF_LIST_FIELDS = (
    "depends-on-artifacts",
    "linked-artifacts",
    "validates",
    "linked-research",
    "linked-adrs",
    "linked-epics",
    "linked-specs",
    "affected-artifacts",
    "linked-personas",
    "linked-journeys",
    "linked-stories",
)


def scan_body(body_text: str, known_ids: set[str], self_id: str) -> set[str]:
    """Find artifact IDs mentioned in body text that are in the known graph."""
    found = set(_ARTIFACT_ID_RE.findall(body_text))
    return (found & known_ids) - {self_id}


def collect_frontmatter_ids(frontmatter: dict) -> set[str]:
    """Collect all artifact IDs referenced in frontmatter fields.

    Extracts from:
    - List fields: all fields in _XREF_LIST_FIELDS
    - addresses list: strips sub-path (e.g. JOURNEY-001.PP-03 -> JOURNEY-001)
    - Scalar fields: parent-epic, parent-vision, superseded-by

    Excludes: source-issue, evidence-pool
    """
    ids: set[str] = set()

    # List fields — extract artifact IDs from each item
    for key in _XREF_LIST_FIELDS:
        ids.update(extract_list_ids(frontmatter, key))

    # addresses — strip sub-path suffix, keep only the base artifact ID
    addresses = frontmatter.get("addresses", [])
    if isinstance(addresses, list):
        for item in addresses:
            if isinstance(item, str):
                # Strip sub-path like ".PP-03" — take only the first ARTIFACT_ID_RE match
                match = _ARTIFACT_ID_RE.match(item)
                if match:
                    ids.add(match.group(0))

    # Scalar fields
    for key in ("parent-epic", "parent-vision", "parent-initiative", "superseded-by"):
        val = extract_scalar_id(frontmatter, key)
        if val:
            ids.add(val)

    return ids


def check_reciprocal_edges(nodes: dict, edges: list[dict]) -> list[dict]:
    """Check that depends-on edges have a corresponding linked-artifacts entry.

    For each edge with type == "depends-on" from A to B:
    - If B is missing from nodes, flag as a gap.
    - If B's linked-artifacts does not contain A, flag as a gap.

    Returns a list of gap dicts with keys: from, to, edge_type, expected_field.
    """
    gaps: list[dict] = []

    for edge in edges:
        if edge.get("type") != "depends-on":
            continue

        from_id = edge["from"]
        to_id = edge["to"]

        node = nodes.get(to_id)
        if node is None:
            # Target node is missing from graph — flag as gap
            gaps.append({
                "from": from_id,
                "to": to_id,
                "edge_type": "depends-on",
                "expected_field": "linked-artifacts",
            })
            continue

        # Check all xref list fields for a back-link — artifacts may use any
        # typed field (linked-research, linked-adrs, etc.) not just linked-artifacts.
        back_linked: set[str] = set()
        raw = node.get("raw_fields", node)  # support both node shapes
        for field in _XREF_LIST_FIELDS:
            vals = raw.get(field, [])
            if not isinstance(vals, list):
                vals = [vals] if vals else []
            back_linked.update(vals)

        if from_id not in back_linked:
            gaps.append({
                "from": from_id,
                "to": to_id,
                "edge_type": "depends-on",
                "expected_field": "linked-artifacts",
            })

    return gaps


def compute_discrepancies(body_ids: set[str], frontmatter_ids: set[str]) -> dict:
    """Compute set differences between body-mentioned and frontmatter-declared IDs.

    Returns a dict with:
    - body_not_in_frontmatter: IDs found in body but not declared in frontmatter
    - frontmatter_not_in_body: IDs declared in frontmatter but not found in body
    """
    return {
        "body_not_in_frontmatter": body_ids - frontmatter_ids,
        "frontmatter_not_in_body": frontmatter_ids - body_ids,
    }


def compute_xref(artifacts: list[dict], edges: list[dict]) -> list[dict]:
    """Run full cross-reference pipeline over a list of artifact dicts.

    Each artifact dict must have: id, file, body, frontmatter.

    Returns a list of entries (one per artifact) that have at least one
    discrepancy. Each entry has:
    - artifact: str
    - file: str
    - body_not_in_frontmatter: list
    - frontmatter_not_in_body: list
    - missing_reciprocal: list of gap dicts
    """
    if not artifacts:
        return []

    # Build nodes dict for reciprocal check
    nodes: dict = {}
    for a in artifacts:
        fm = a.get("frontmatter", {})
        nodes[a["id"]] = fm

    # Check reciprocal edges across all nodes
    reciprocal_gaps = check_reciprocal_edges(nodes, edges)
    # Group reciprocal gaps by the "to" node (the one missing the back-link)
    reciprocal_by_artifact: dict[str, list[dict]] = {}
    for gap in reciprocal_gaps:
        reciprocal_by_artifact.setdefault(gap["to"], []).append({
            "from": gap["from"],
            "edge_type": gap["edge_type"],
            "expected_field": gap["expected_field"],
        })

    results = []
    for artifact in artifacts:
        artifact_id = artifact["id"]
        body = artifact.get("body", "")
        frontmatter = artifact.get("frontmatter", {})

        # Broad sweep for TYPE-NNN patterns, filtered to known artifact prefixes.
        # This catches dangling references not yet in the graph while suppressing
        # false positives from CVE identifiers (CVE-2024), SPDX tags (GPL-2),
        # model names (GPT-4), pain-point IDs (PP-01), and other non-artifact
        # patterns that match the general [A-Z]+-\d+ shape.
        body_ids = {
            ref for ref in _ARTIFACT_ID_RE.findall(body)
            if ref.split("-")[0] in _KNOWN_ARTIFACT_PREFIXES
        } - {artifact_id}
        fm_ids = collect_frontmatter_ids(frontmatter)
        discrepancies = compute_discrepancies(body_ids, fm_ids)
        missing_reciprocal = reciprocal_by_artifact.get(artifact_id, [])

        has_discrepancy = (
            discrepancies["body_not_in_frontmatter"]
            or discrepancies["frontmatter_not_in_body"]
            or missing_reciprocal
        )

        if has_discrepancy:
            results.append({
                "artifact": artifact_id,
                "file": artifact.get("file", ""),
                "body_not_in_frontmatter": sorted(discrepancies["body_not_in_frontmatter"]),
                "frontmatter_not_in_body": sorted(discrepancies["frontmatter_not_in_body"]),
                "missing_reciprocal": missing_reciprocal,
            })

    return results
