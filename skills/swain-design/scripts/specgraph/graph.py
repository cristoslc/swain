"""Graph building and cache I/O for specgraph."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from .parser import (
    extract_list_ids,
    extract_scalar_id,
    get_body,
    parse_artifact,
)
from .xref import compute_xref, _XREF_LIST_FIELDS


def _is_valid_ref(val: str) -> bool:
    """Check if a value is a valid reference (not a YAML null/empty placeholder)."""
    return val not in ("", "~", "null", "[]", "--", '""', "''")


def repo_hash(repo_root: str) -> str:
    """Compute the cache filename hash from the repo root path.

    Matches bash: printf '%s' "$REPO_ROOT" | shasum -a 256 | cut -c1-12
    """
    return hashlib.sha256(repo_root.encode()).hexdigest()[:12]


def cache_path(repo_root: str) -> Path:
    """Return the cache file path for a given repo root."""
    h = repo_hash(repo_root)
    return Path(f"/tmp/agents-specgraph-{h}.json")


def _find_artifact_files(docs_dir: Path) -> list[Path]:
    """Find all markdown files in docs/ that could be artifacts."""
    files = []
    for md in sorted(docs_dir.rglob("*.md")):
        if md.name in ("README.md",) or md.name.startswith("list-"):
            continue
        files.append(md)
    return files


def build_graph(
    repo_root: Path,
) -> dict[str, Any]:
    """Build the artifact dependency graph from frontmatter.

    Returns a dict with keys: generated, repo, nodes, edges.
    """
    docs_dir = repo_root / "docs"
    nodes: dict[str, dict] = {}
    edges: list[dict] = []

    def add_edge(from_id: str, to_val: str, edge_type: str) -> None:
        if not _is_valid_ref(to_val):
            return
        edges.append({"from": from_id, "to": to_val, "type": edge_type})

    artifact_dicts: list[dict] = []

    for filepath in _find_artifact_files(docs_dir):
        artifact = parse_artifact(filepath, repo_root)
        if artifact is None:
            continue

        aid = artifact.artifact
        fields = artifact.raw_fields
        track = fields.get("track", "")
        priority_weight = fields.get("priority-weight", "")
        sort_order = fields.get("sort-order", 0)
        try:
            sort_order = int(sort_order) if sort_order else 0
        except (ValueError, TypeError):
            sort_order = 0
        nodes[aid] = {
            "title": artifact.title,
            "status": artifact.status,
            "type": artifact.type,
            "track": track,
            "file": artifact.file,
            "description": artifact.description,
            "priority_weight": priority_weight,
            "sort_order": sort_order,
            "brief_description": fields.get("brief-description", ""),
        }

        # depends-on edges
        for dep in extract_list_ids(fields, "depends-on-artifacts"):
            add_edge(aid, dep, "depends-on")

        # parent-vision (scalar or list)
        pv = extract_scalar_id(fields, "parent-vision")
        if pv is None:
            pvs = extract_list_ids(fields, "parent-vision")
            pv = pvs[0] if pvs else None
        if pv:
            add_edge(aid, pv, "parent-vision")

        # parent-epic (scalar or list)
        pe = extract_scalar_id(fields, "parent-epic")
        if pe is None:
            pes = extract_list_ids(fields, "parent-epic")
            pe = pes[0] if pes else None
        if pe:
            add_edge(aid, pe, "parent-epic")

        # parent-initiative (scalar or list)
        pi = extract_scalar_id(fields, "parent-initiative")
        if pi is None:
            pis = extract_list_ids(fields, "parent-initiative")
            pi = pis[0] if pis else None
        if pi:
            add_edge(aid, pi, "parent-initiative")

        # Track dual-parent warning
        has_parent_epic = pe is not None
        has_parent_initiative = pi is not None
        if has_parent_epic and has_parent_initiative:
            nodes[aid]["_dual_parent_warning"] = True

        # List-type relationship edges (all typed xref fields except depends-on-artifacts,
        # which is handled above with its own "depends-on" edge type)
        for list_field in _XREF_LIST_FIELDS:
            if list_field == "depends-on-artifacts":
                continue
            for ref in extract_list_ids(fields, list_field):
                add_edge(aid, ref, list_field)

        # addresses (preserves full format like JOURNEY-NNN.PP-NN)
        addresses = fields.get("addresses", [])
        if isinstance(addresses, list):
            for addr in addresses:
                addr_str = str(addr).strip()
                if addr_str and _is_valid_ref(addr_str):
                    add_edge(aid, addr_str, "addresses")

        # Scalar relationship edges
        for scalar_field in ("superseded-by", "evidence-pool", "source-issue"):
            val = fields.get(scalar_field, "")
            if isinstance(val, str) and val and _is_valid_ref(val):
                add_edge(aid, val, scalar_field)

        # Collect artifact dict for xref computation
        content = filepath.read_text(encoding="utf-8")
        body = get_body(content)
        artifact_dicts.append({
            "id": aid,
            "file": artifact.file,
            "body": body,
            "frontmatter": fields,
        })

    xref = compute_xref(artifact_dicts, edges)

    # Append dual-parent warnings to xref
    for aid, node in nodes.items():
        if node.pop("_dual_parent_warning", False):
            xref.append({
                "artifact": aid,
                "file": node.get("file", ""),
                "body_not_in_frontmatter": [],
                "frontmatter_not_in_body": [],
                "missing_reciprocal": [],
                "dual_parent": True,
                "dual_parent_message": f"{aid} has both parent-epic and parent-initiative — use exactly one",
            })

    generated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "generated": generated,
        "repo": str(repo_root),
        "nodes": nodes,
        "edges": edges,
        "xref": xref,
    }


def needs_rebuild(cache_file: Path, docs_dir: Path) -> bool:
    """Check if the cache needs rebuilding (any docs/*.md newer than cache)."""
    if not cache_file.exists():
        return True
    cache_mtime = cache_file.stat().st_mtime
    for md in docs_dir.rglob("*.md"):
        if md.stat().st_mtime > cache_mtime:
            return True
    return False


def write_cache(data: dict, cache_file: Path) -> None:
    """Write graph data to the cache file atomically."""
    fd, tmp_name = tempfile.mkstemp(
        dir=str(cache_file.parent),
        prefix=f"{cache_file.stem}.",
        suffix=".tmp",
    )
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
        tmp.rename(cache_file)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise


def read_cache(cache_file: Path) -> Optional[dict]:
    """Read graph data from the cache file."""
    if not cache_file.exists():
        return None
    with open(cache_file, encoding="utf-8") as f:
        return json.load(f)
