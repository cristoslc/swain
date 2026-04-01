#!/usr/bin/env python3
"""Render a changelog entry from a JSON data file and Jinja2 template.

Usage:
    python render_changelog.py <data.json> [--template <path>]

The JSON file must have this structure:
{
  "version": "0.10.0-alpha",
  "date": "2026-03-21",
  "features": [
    {"prose": "**Bold lead-in** — paragraph for major work."},
    {"text": "Bullet item for smaller work"}
  ],
  "roadmap": [
    "VISION-004, INITIATIVE-019, EPIC-039 — session facilitation planning"
  ],
  "research": [
    "Google Stitch SDK trove — 7 sources collected"
  ],
  "supporting": [
    "Cross-reference enrichment across ~100 doc files"
  ]
}

Sections with empty arrays are omitted from the output.
Features items can be either:
  - {"prose": "..."} for paragraph-style entries (major work)
  - {"text": "..."} for bullet-style entries (smaller items)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Render changelog from JSON + Jinja2")
    parser.add_argument("data", help="Path to JSON data file")
    parser.add_argument("--template", default=None,
                        help="Path to Jinja2 template (default: templates/changelog.md.j2)")
    args = parser.parse_args()

    try:
        from jinja2 import Environment, FileSystemLoader
    except ImportError:
        print("jinja2 is required: uv pip install jinja2", file=sys.stderr)
        sys.exit(1)

    with open(args.data) as f:
        data = json.load(f)

    template_path = args.template
    if template_path is None:
        script_dir = str(Path(__file__).resolve().parent)
        template_dir = os.path.join(os.path.dirname(script_dir), "templates")
        template_name = "changelog.md.j2"
    else:
        template_dir = os.path.dirname(os.path.abspath(template_path))
        template_name = os.path.basename(template_path)

    env = Environment(
        loader=FileSystemLoader(template_dir),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template(template_name)
    print(template.render(**data))


if __name__ == "__main__":
    main()
