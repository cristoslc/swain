#!/usr/bin/env python3
"""swain chart — vision-rooted hierarchy display.

Subsumes specgraph. Uses lenses to filter/annotate the vision-rooted tree.
Falls through to specgraph CLI for low-level commands.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)

from specgraph.graph import cache_path, read_cache, build_graph, needs_rebuild, write_cache
from specgraph.tree_renderer import render_vision_tree
from specgraph.lenses import LENSES, RecommendLens, AttentionLens
from specgraph import cli as specgraph_cli


def _get_repo_root() -> str:
    """Find the git repository root."""
    import subprocess
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL,
        ).decode().strip()
    except subprocess.CalledProcessError:
        return os.getcwd()


def _ensure_cache(repo_root: str) -> dict:
    """Ensure graph cache is fresh, rebuild if needed."""
    from pathlib import Path
    cp = cache_path(repo_root)
    docs_dir = Path(repo_root) / "docs"
    if needs_rebuild(cp, docs_dir):
        data = build_graph(Path(repo_root))
        write_cache(data, cp)
    else:
        data = read_cache(cp)
    return data


def _read_focus_lane(repo_root: str) -> str | None:
    """Read focus lane from session.json if it exists."""
    session_file = os.path.join(repo_root, ".agents", "session.json")
    if os.path.isfile(session_file):
        try:
            with open(session_file) as f:
                session = json.load(f)
            return session.get("focus_lane")
        except (json.JSONDecodeError, IOError):
            pass
    return None


def _resolve_depth(args, lens, repo_root: str) -> int:
    """Resolve effective depth: explicit > focus lane > lens default."""
    if args.depth is not None:
        return args.depth
    focus = _read_focus_lane(repo_root)
    if focus:
        return 4  # execution depth when focused
    return lens.default_depth


def _resolve_phase_filter(args) -> set[str] | None:
    """Resolve phase filter from args."""
    if args.phase:
        return set(args.phase.split(","))
    if args.hide_terminal:
        return None  # handled by lens selection (which excludes terminal)
    return None


# Lens commands that produce vision-rooted tree output
_LENS_COMMANDS = {"default", "ready", "recommend", "attention", "debt",
                  "unanchored", "status"}

# Commands that pass through to specgraph CLI
_PASSTHROUGH_COMMANDS = {"build", "xref", "blocks", "blocked-by", "tree",
                         "deps", "neighbors", "scope", "impact", "edges",
                         "mermaid", "next", "decision-debt"}


def main():
    parser = argparse.ArgumentParser(
        prog="swain-chart",
        description="Vision-rooted hierarchy display",
    )
    sub = parser.add_subparsers(dest="command")

    # Lens-based tree commands
    for lens_name in _LENS_COMMANDS:
        if lens_name == "default":
            continue  # default is the no-subcommand behavior
        p = sub.add_parser(lens_name, help=f"{lens_name} lens")
        _add_tree_args(p)
        if lens_name == "recommend":
            p.add_argument("--focus", type=str, default=None,
                           help="Focus on a specific Vision ID")
        if lens_name == "attention":
            p.add_argument("--days", type=int, default=30,
                           help="Days of git history to scan")

    # Passthrough commands (delegate to specgraph CLI)
    for cmd in _PASSTHROUGH_COMMANDS:
        p = sub.add_parser(cmd, help=f"(specgraph) {cmd}")
        p.add_argument("id", nargs="?", default=None, help="Artifact ID")
        p.add_argument("--all", action="store_true", dest="show_all")
        p.add_argument("--all-edges", action="store_true")
        p.add_argument("--json", action="store_true", dest="json_output")
        p.add_argument("--focus", type=str, default=None)
        p.add_argument("--days", type=int, default=30)

    # Add tree args to the main parser for default (no subcommand) usage
    _add_tree_args(parser)

    args = parser.parse_args()
    command = args.command

    # If no command, use default lens
    if command is None or command == "default":
        command = "default"

    # Passthrough to specgraph CLI
    if command in _PASSTHROUGH_COMMANDS:
        # Delegate to specgraph's main() with the same argv
        specgraph_cli.main()
        return

    # Lens-based tree rendering
    repo_root = _get_repo_root()
    data = _ensure_cache(repo_root)
    nodes = data["nodes"]
    edges = data["edges"]

    # Instantiate the lens
    if command == "recommend":
        focus = getattr(args, "focus", None) or _read_focus_lane(repo_root)
        lens = RecommendLens(focus_vision=focus)
    elif command == "attention":
        days = getattr(args, "days", 30)
        lens = AttentionLens(days=days)
    elif command in LENSES:
        lens = LENSES[command]()
    else:
        lens = LENSES["default"]()

    # Select and annotate
    selected = lens.select(nodes, edges)
    annotations = lens.annotate(nodes, edges)

    # Resolve depth and phase filter
    depth = _resolve_depth(args, lens, repo_root)
    phase_filter = _resolve_phase_filter(args)
    show_ids = getattr(args, "ids", False)
    flat_output = getattr(args, "flat", False)
    json_output = getattr(args, "json_output", False)

    # Render
    lines = render_vision_tree(
        nodes=selected,
        all_nodes=nodes,
        edges=edges,
        depth=depth,
        phase_filter=phase_filter,
        annotations=annotations,
        sort_key=lens.sort_key,
        show_ids=show_ids,
    )

    if json_output:
        # Structured JSON output
        result = {
            "lens": command,
            "depth": depth,
            "selected_count": len(selected),
            "selected": sorted(selected),
            "annotations": annotations,
            "tree": lines,
        }
        print(json.dumps(result, indent=2))
    elif flat_output:
        # Flat list — just selected artifact IDs with titles
        for aid in sorted(selected):
            node = nodes.get(aid, {})
            title = node.get("title", aid)
            status = node.get("status", "")
            ann = annotations.get(aid, "")
            parts = [aid, title, status]
            if ann:
                parts.append(ann)
            print("  ".join(parts))
    else:
        # Tree output
        print("\n".join(lines))


def _add_tree_args(parser):
    """Add common tree display arguments."""
    parser.add_argument("--depth", type=int, default=None,
                        help="Tree depth (2=strategic, 4=execution)")
    parser.add_argument("--detail", action="store_const", const=4,
                        dest="depth",
                        help="Alias for --depth 4")
    parser.add_argument("--phase", type=str, default=None,
                        help="Comma-separated phases to include")
    parser.add_argument("--hide-terminal", action="store_true",
                        help="Exclude terminal-phase artifacts")
    parser.add_argument("--flat", action="store_true",
                        help="Flat list output (no tree)")
    parser.add_argument("--json", action="store_true", dest="json_output",
                        help="JSON output")
    parser.add_argument("--ids", action="store_true",
                        help="Show artifact IDs alongside titles")


if __name__ == "__main__":
    main()
