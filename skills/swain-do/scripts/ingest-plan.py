#!/usr/bin/env -S uv run python3
"""Ingest a superpowers plan file into tk (ticket) as an epic with child tasks.

Parses the writing-plans format (### Task N: Title blocks) and registers
each task in tk with spec lineage tagging and sequential dependencies.

Usage:
  ingest-plan.py <plan-file> <origin-ref> [--dry-run] [--tags TAG,...]

Examples:
  ingest-plan.py docs/plans/2026-03-06-auth-system.md SPEC-003
  ingest-plan.py docs/plans/2026-03-06-auth-system.md SPEC-003 --dry-run
  ingest-plan.py docs/plans/2026-03-06-auth-system.md SPEC-003 --tags epic:EPIC-009
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


def tk_create(args: list[str]) -> str:
    """Run a tk create command and return the created ticket ID from stdout."""
    cmd = ['tk'] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"tk error: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    # tk create prints "Created <id>" — extract the ID
    output = result.stdout.strip()
    m = re.search(r'Created\s+(\S+)', output)
    if m:
        return m.group(1)
    # Fallback: return the last word on the first line
    return output.split()[-1] if output else ''


def tk_dep(child_id: str, parent_id: str):
    """Add a dependency: child depends on parent."""
    subprocess.run(
        ['tk', 'dep', child_id, parent_id],
        capture_output=True, text=True,
    )


def register_in_tk(plan: dict, origin_ref: str, extra_tags=None):
    """Create tk epic + child tasks from parsed plan."""
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
    epic_id = tk_create(epic_args)
    print(f"Created epic: {epic_id} — {title}")

    # Create child tasks
    tags = [f'spec:{origin_ref}']
    if extra_tags:
        tags.extend(extra_tags)
    tag_str = ','.join(tags)

    task_ids = []
    for task in tasks:
        # Truncate body for description (keep reasonable)
        desc = task['body']
        if len(desc) > 4000:
            desc = desc[:3997] + '...'

        task_args = [
            'create', f"Task {task['number']}: {task['title']}",
            '-t', 'task',
            '--parent', epic_id,
            '-p', '1',
            '-d', desc,
            '--tags', tag_str,
        ]
        task_id = tk_create(task_args)
        task_ids.append(task_id)
        print(f"  Created task: {task_id} — {task['title']}")

    # Wire sequential dependencies
    for i in range(1, len(task_ids)):
        tk_dep(task_ids[i], task_ids[i - 1])
        print(f"  Dep: {task_ids[i]} depends on {task_ids[i - 1]}")

    return {'epic_id': epic_id, 'task_ids': task_ids}


def main():
    parser = argparse.ArgumentParser(description='Ingest a superpowers plan file into tk')
    parser.add_argument('plan_file', help='Path to superpowers plan markdown file')
    parser.add_argument('origin_ref', help='Origin artifact ID (e.g., SPEC-003)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Parse only — output JSON without creating tk tasks')
    parser.add_argument('--tags', default='',
                        help='Additional comma-separated tags for all tasks')
    args = parser.parse_args()

    if not os.path.isfile(args.plan_file):
        print(f"Error: file not found: {args.plan_file}", file=sys.stderr)
        sys.exit(1)

    plan = parse_plan(args.plan_file)

    if args.dry_run:
        json.dump(plan, sys.stdout, indent=2)
        print()
        return

    extra_tags = [t.strip() for t in args.tags.split(',') if t.strip()] if args.tags else None
    result = register_in_tk(plan, args.origin_ref, extra_tags)
    print(f"\nIngestion complete: {len(result['task_ids'])} tasks under epic {result['epic_id']}")


if __name__ == '__main__':
    main()
