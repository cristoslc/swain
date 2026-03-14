"""Cross-reference scanning and validation for specgraph artifacts."""

from __future__ import annotations

import re

from .parser import extract_list_ids, extract_scalar_id, _ARTIFACT_ID_RE


def scan_body(body_text: str, known_ids: set[str], self_id: str) -> set[str]:
    """Find artifact IDs mentioned in body text that are in the known graph."""
    found = set(_ARTIFACT_ID_RE.findall(body_text))
    return (found & known_ids) - {self_id}


def collect_frontmatter_ids(frontmatter: dict) -> set[str]:
    """Collect all artifact IDs referenced in frontmatter fields.

    Extracts from:
    - List fields: depends-on-artifacts, linked-artifacts, validates
    - addresses list: strips sub-path (e.g. JOURNEY-001.PP-03 -> JOURNEY-001)
    - Scalar fields: parent-epic, parent-vision, superseded-by

    Excludes: source-issue, evidence-pool
    """
    ids: set[str] = set()

    # List fields — extract artifact IDs from each item
    for key in ("depends-on-artifacts", "linked-artifacts", "validates"):
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
    for key in ("parent-epic", "parent-vision", "superseded-by"):
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

        # Two expected node shapes: flat dict {field: value} from tests, or
        # {raw_fields: {field: value}} from parse_artifact() output via graph.py.
        if "linked-artifacts" in node:
            linked = node["linked-artifacts"]
        elif "raw_fields" in node:
            linked = node["raw_fields"].get("linked-artifacts", [])
        else:
            linked = []

        if not isinstance(linked, list):
            linked = [linked] if linked else []

        if from_id not in linked:
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

    # Build known_ids set and nodes dict for reciprocal check
    known_ids = {a["id"] for a in artifacts}
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

        # Intentional broad sweep: scan for ALL TYPE-NNN patterns in the body,
        # not just those in the loaded graph. This catches dangling references to
        # IDs that are not yet in the graph (e.g. missing artifacts, typos). The
        # known-ID filter in scan_body() serves a different purpose — it is used
        # when the caller only wants to identify in-graph references (e.g. for
        # scope/impact queries). Self-reference is still excluded.
        body_ids = set(_ARTIFACT_ID_RE.findall(body)) - {artifact_id}
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
