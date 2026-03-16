"""CLI dispatch for specgraph."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from . import graph
from . import queries


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

    # Commands requiring a mandatory ID
    for cmd in ("blocks", "blocked-by", "tree", "deps", "neighbors", "scope", "impact"):
        sp = subparsers.add_parser(cmd)
        sp.add_argument("id", help="Artifact ID (e.g. SPEC-001)")

    # edges: optional ID
    sp = subparsers.add_parser("edges")
    sp.add_argument("id", nargs="?", default=None, help="Filter by artifact ID (optional)")

    # Commands with no ID argument
    for cmd in ("ready", "next", "mermaid", "status", "overview"):
        subparsers.add_parser(cmd)

    # Priority commands
    subparsers.add_parser("decision-debt", help="Show decision debt per vision")
    rec_parser = subparsers.add_parser("recommend", help="Show ranked recommendation")
    rec_parser.add_argument("--focus", default=None, help="Focus vision ID (e.g. VISION-001)")
    rec_parser.add_argument("--json", action="store_true", help="Output raw JSON")


    # attention: drift detection
    att_parser = subparsers.add_parser("attention", help="Show attention distribution by vision")
    att_parser.add_argument("--days", type=int, default=30, help="Lookback window in days")
    att_parser.add_argument("--json", action="store_true", help="Output raw JSON")

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
        data = _ensure_cache(repo_root)
        nodes = data.get("nodes", {})
        edges = data.get("edges", [])
        show_links = sys.stdout.isatty()
        repo_root_str = str(repo_root)
        show_all = args.all

        if args.command == "blocks":
            print(queries.blocks(args.id, nodes, edges, repo_root_str, show_links))
        elif args.command == "blocked-by":
            print(queries.blocked_by(args.id, nodes, edges, repo_root_str, show_links))
        elif args.command in ("tree", "deps"):
            print(queries.tree(args.id, nodes, edges, repo_root_str, show_links))
        elif args.command == "neighbors":
            print(queries.neighbors(args.id, nodes, edges, repo_root_str, show_links))
        elif args.command == "scope":
            print(queries.scope(args.id, nodes, edges, repo_root_str, show_links))
        elif args.command == "impact":
            print(queries.impact(args.id, nodes, edges, repo_root_str, show_links))
        elif args.command == "edges":
            print(queries.edges_cmd(args.id, nodes, edges))
        elif args.command == "ready":
            print(queries.ready(nodes, edges, repo_root_str, show_links))
        elif args.command == "next":
            print(queries.next_cmd(nodes, edges, repo_root_str, show_links))
        elif args.command == "mermaid":
            print(queries.mermaid_cmd(nodes, edges, show_all, args.all_edges))
        elif args.command == "status":
            print(queries.status_cmd(nodes, edges, show_all))
        elif args.command == "overview":
            print(queries.overview(nodes, edges, show_all, repo_root_str, show_links))
        elif args.command == "decision-debt":
            from .priority import compute_decision_debt
            import json as _json
            debt = compute_decision_debt(nodes, edges)
            print(_json.dumps(debt, indent=2))
        elif args.command == "recommend":
            from .priority import rank_recommendations
            import json as _json
            focus = getattr(args, "focus", None)
            ranked = rank_recommendations(nodes, edges, focus_vision=focus)
            if getattr(args, "json", False):
                print(_json.dumps(ranked, indent=2))
            else:
                for i, item in enumerate(ranked[:10]):
                    marker = "→ " if i == 0 else "  "
                    print(f"{marker}{item['id']}  score={item['score']}  unblocks={item['unblock_count']}  weight={item['vision_weight']}  vision={item['vision_id'] or 'none (orphan)'}")
        elif args.command == "attention":
            from .attention import scan_git_log, compute_attention, compute_drift
            import json as _json
            # Read settings for drift thresholds
            settings_path = repo_root / "swain.settings.json"
            drift_thresholds = None
            att_days = getattr(args, "days", 30)
            if settings_path.exists():
                try:
                    settings = _json.loads(settings_path.read_text())
                    p = settings.get("prioritization", {})
                    drift_thresholds = p.get("driftThresholds")
                    att_days = p.get("attentionWindowDays", att_days)
                except (ValueError, KeyError):
                    pass
            log_entries = scan_git_log(repo_root, days=att_days)
            attention = compute_attention(log_entries, nodes, edges)
            drift = compute_drift(attention, nodes, drift_thresholds=drift_thresholds)
            if getattr(args, "json", False):
                print(_json.dumps({"attention": attention, "drift": drift}, indent=2))
            else:
                print("=== Attention Distribution ===")
                for vid, data in sorted(attention.items()):
                    vnode = nodes.get(vid, {})
                    label = vnode.get("title", vid)
                    weight = vnode.get("priority_weight", "medium") or "medium"
                    print(f"  {vid} ({label}) [weight: {weight}] — {data['transitions']} transitions, last: {data['last_activity'] or 'never'}")
                if drift:
                    print()
                    print("=== Attention Drift ===")
                    for d in drift:
                        print(f"  {d['vision_id']} (weight: {d['weight']}) — {d['days_since_activity']} days since last activity (threshold: {d['threshold']})")
        else:
            print(f"Unknown command: {args.command}", file=sys.stderr)
            sys.exit(1)
