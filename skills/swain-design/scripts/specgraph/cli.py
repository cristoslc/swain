"""CLI dispatch for specgraph."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from . import graph


def _get_repo_root() -> Path:
    """Find the git repository root."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        return Path(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: not inside a git repository", file=sys.stderr)
        sys.exit(1)


def _ensure_cache(repo_root: Path, force: bool = False) -> dict:
    """Ensure the graph cache is fresh and return its data."""
    cf = graph.cache_path(str(repo_root))
    docs_dir = repo_root / "docs"

    if force or graph.needs_rebuild(cf, docs_dir):
        data = graph.build_graph(repo_root)
        graph.write_cache(data, cf)
        return data

    cached = graph.read_cache(cf)
    if cached is None:
        data = graph.build_graph(repo_root)
        graph.write_cache(data, cf)
        return data
    return cached


def cmd_build(args: argparse.Namespace, repo_root: Path) -> None:
    """Force-rebuild the dependency graph from frontmatter."""
    data = _ensure_cache(repo_root, force=True)
    cf = graph.cache_path(str(repo_root))
    print(f"Graph built: {cf}")
    print(f"  Nodes: {len(data['nodes'])}")
    print(f"  Edges: {len(data['edges'])}")


def cmd_xref(args: argparse.Namespace, repo_root: Path) -> None:
    """Show cross-reference validation results."""
    data = _ensure_cache(repo_root)

    if "xref" not in data:
        print("Warning: cache has no xref data — run 'specgraph build' to refresh", file=sys.stderr)
        return

    xref = data.get("xref") or []

    if getattr(args, "json", False):
        print(json.dumps(xref, indent=2))
        return

    # === Cross-Reference Gaps ===
    print("=== Cross-Reference Gaps ===")
    print()
    gaps_found = False
    for entry in xref:
        if entry.get("body_not_in_frontmatter"):
            if not gaps_found:
                gaps_found = True
            print(f"{entry['artifact']} ({entry.get('file', '')}):")
            for ref_id in sorted(entry["body_not_in_frontmatter"]):
                print(f"  -> {ref_id} (mentioned in body, not in frontmatter)")
            print()
    if not gaps_found:
        print("(none)")
        print()

    # === Missing Reciprocal Edges ===
    print("=== Missing Reciprocal Edges ===")
    print()
    reciprocal_found = False
    for entry in xref:
        for gap in entry.get("missing_reciprocal", []):
            reciprocal_found = True
            print(
                f"{entry['artifact']}: should list {gap['from']} in"
                f" {gap['expected_field']} ({gap['from']} {gap['edge_type']} {entry['artifact']})"
            )
    if not reciprocal_found:
        print("(none)")
    print()

    # === Stale References ===
    print("=== Stale References ===")
    print()
    stale_found = False
    for entry in xref:
        if entry.get("frontmatter_not_in_body"):
            if not stale_found:
                stale_found = True
            print(f"{entry['artifact']} ({entry.get('file', '')}):")
            for ref_id in sorted(entry["frontmatter_not_in_body"]):
                print(f"  -> {ref_id} (declared in frontmatter, not in body)")
            print()
    if not stale_found:
        print("(none)")


def main(argv: list[str] | None = None) -> None:
    """Main entry point for the specgraph CLI."""
    parser = argparse.ArgumentParser(
        prog="specgraph",
        description="Build and query the spec artifact dependency graph",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Include finished artifacts (resolved/terminal states)",
    )
    parser.add_argument(
        "--all-edges",
        action="store_true",
        help="Show all edge types in mermaid output",
    )

    subparsers = parser.add_subparsers(dest="command")

    # build
    subparsers.add_parser("build", help="Force-rebuild the dependency graph")

    # xref
    xref_parser = subparsers.add_parser("xref", help="Show cross-reference validation results")
    xref_parser.add_argument("--json", action="store_true", help="Output raw JSON")

    # Placeholder subcommands — will be implemented in SPEC-031
    for cmd in (
        "blocks",
        "blocked-by",
        "tree",
        "neighbors",
        "scope",
        "impact",
        "edges",
    ):
        sp = subparsers.add_parser(cmd)
        sp.add_argument("id", nargs="?", default=None)

    for cmd in ("ready", "next", "mermaid", "status", "overview"):
        subparsers.add_parser(cmd)

    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        sys.exit(1)

    repo_root = _get_repo_root()

    if args.command == "build":
        cmd_build(args, repo_root)
    elif args.command == "xref":
        cmd_xref(args, repo_root)
    else:
        # Ensure cache is fresh for all commands
        _ensure_cache(repo_root)
        print(
            f"Command '{args.command}' not yet implemented — see SPEC-031",
            file=sys.stderr,
        )
        sys.exit(1)
