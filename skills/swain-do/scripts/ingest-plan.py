#!/usr/bin/env -S uv run python3
"""Ingest a superpowers plan file into bd (beads) as an epic with child tasks.

Parses the writing-plans format (### Task N: Title blocks) and registers
each task in bd with spec lineage tagging and sequential dependencies.

Usage:
  ingest-plan.py <plan-file> <origin-ref> [--dry-run] [--labels LABEL,...]

Examples:
  ingest-plan.py docs/plans/2026-03-06-auth-system.md SPEC-003
  ingest-plan.py docs/plans/2026-03-06-auth-system.md SPEC-003 --dry-run
  ingest-plan.py docs/plans/2026-03-06-auth-system.md SPEC-003 --labels epic:EPIC-009
"""

import argparse
import json
import os
import re
import subprocess
import sys


def parse_header(content: str) -> dict:
    """Extract plan header: title, goal, architecture, tech stack."""
    header = {}

    # Title from first H1
    m = re.search(r'^# (.+)$', content, re.MULTILINE)
    if m:
        header['title'] = m.group(1).strip()

    # Goal, Architecture, Tech Stack from **Key:** Value lines
    for key in ('Goal', 'Architecture', 'Tech Stack'):
        m = re.search(rf'^\*\*{key}:\*\*\s*(.+)$', content, re.MULTILINE)
        if m:
            header[key.lower().replace(' ', '_')] = m.group(1).strip()

    return header


def parse_tasks(content: str) -> list[dict]:
    """Split content on ### Task N: boundaries, extract title and body."""
    # Find all ### Task headings
    pattern = r'^### Task (\d+):\s*(.+)$'
    matches = list(re.finditer(pattern, content, re.MULTILINE))

    if not matches:
        return []

    tasks = []
    for i, match in enumerate(matches):
        task_num = int(match.group(1))
        title = match.group(2).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        body = content[start:end].strip()

        # Extract file paths from **Files:** section
        files = []
        files_match = re.search(r'^\*\*Files:\*\*\s*\n((?:- .+\n)+)', body, re.MULTILINE)
        if files_match:
            for line in files_match.group(1).strip().split('\n'):
                line = line.strip().lstrip('- ')
                if line:
                    files.append(line)

        tasks.append({
            'number': task_num,
            'title': title,
            'body': body,
            'files': files,
        })

    return tasks


def parse_plan(path: str) -> dict:
    """Parse a superpowers plan file into structured data."""
    with open(path) as f:
        content = f.read()

    header = parse_header(content)
    tasks = parse_tasks(content)

    if not tasks:
        print(f"Error: no '### Task N:' headings found in {path}", file=sys.stderr)
        sys.exit(1)

    return {'header': header, 'tasks': tasks, 'source': path}


def bd_create(args: list[str]) -> dict:
    """Run a bd create command and return parsed JSON response."""
    cmd = ['bd'] + args + ['--json']
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"bd error: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    return json.loads(result.stdout)


def bd_dep_add(child_id: str, parent_id: str):
    """Add a dependency: child depends on parent."""
    subprocess.run(
        ['bd', 'dep', 'add', child_id, parent_id],
        capture_output=True, text=True,
    )


def register_in_bd(plan: dict, origin_ref: str, extra_labels=None):
    """Create bd epic + child tasks from parsed plan."""
    header = plan['header']
    tasks = plan['tasks']
    title = header.get('title', os.path.basename(plan['source']))

    # Create epic
    epic_args = [
        'create', title,
        '-t', 'epic',
        '--external-ref', origin_ref,
        '-d', f"Ingested from {plan['source']}. "
              f"Goal: {header.get('goal', 'N/A')}. "
              f"Architecture: {header.get('architecture', 'N/A')}.",
    ]
    epic = bd_create(epic_args)
    epic_id = epic['id']
    print(f"Created epic: {epic_id} — {title}")

    # Create child tasks
    labels = [f'spec:{origin_ref}']
    if extra_labels:
        labels.extend(extra_labels)
    label_str = ','.join(labels)

    task_ids = []
    for task in tasks:
        # Truncate body for description (bd has limits)
        desc = task['body']
        if len(desc) > 4000:
            desc = desc[:3997] + '...'

        task_args = [
            'create', f"Task {task['number']}: {task['title']}",
            '-t', 'task',
            '--parent', epic_id,
            '-p', '1',
            '-d', desc,
            '--labels', label_str,
        ]
        result = bd_create(task_args)
        task_id = result['id']
        task_ids.append(task_id)
        print(f"  Created task: {task_id} — {task['title']}")

    # Wire sequential dependencies
    for i in range(1, len(task_ids)):
        bd_dep_add(task_ids[i], task_ids[i - 1])
        print(f"  Dep: {task_ids[i]} depends on {task_ids[i - 1]}")

    return {'epic_id': epic_id, 'task_ids': task_ids}


def main():
    parser = argparse.ArgumentParser(description='Ingest a superpowers plan file into bd')
    parser.add_argument('plan_file', help='Path to superpowers plan markdown file')
    parser.add_argument('origin_ref', help='Origin artifact ID (e.g., SPEC-003)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Parse only — output JSON without creating bd tasks')
    parser.add_argument('--labels', default='',
                        help='Additional comma-separated labels for all tasks')
    args = parser.parse_args()

    if not os.path.isfile(args.plan_file):
        print(f"Error: file not found: {args.plan_file}", file=sys.stderr)
        sys.exit(1)

    plan = parse_plan(args.plan_file)

    if args.dry_run:
        json.dump(plan, sys.stdout, indent=2)
        print()
        return

    extra_labels = [l.strip() for l in args.labels.split(',') if l.strip()] if args.labels else None
    result = register_in_bd(plan, args.origin_ref, extra_labels)
    print(f"\nIngestion complete: {len(result['task_ids'])} tasks under epic {result['epic_id']}")


if __name__ == '__main__':
    main()
