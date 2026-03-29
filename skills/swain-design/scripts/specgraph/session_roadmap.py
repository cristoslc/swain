"""SESSION-ROADMAP.md generation for session-scoped decision support (SPEC-118).

Generates a focus-lane-scoped working surface with 7 sections:
1. Evidence Basis — ROADMAP.md hash, focus lane, artifacts consulted
2. Decision Set — items needing operator input, filtered to focus lane
3. Recommended Next — highest-leverage item by unblock score
4. Session Goal — agent-proposed with justification and ≤2 alternatives
5. Progress — changes since last session (git diff of artifact commits)
6. Decision Records — accumulated decisions from JSONL log
7. Walk-Away Signal — remaining decisions or "done"
"""
from __future__ import annotations

import os
import subprocess

from .priority import rank_recommendations
from .session_decisions import read_decision_records


def _compute_descendants(artifact_id: str, edges: list[dict]) -> set[str]:
    """Compute all transitive descendants of an artifact via parent edges."""
    children: set[str] = set()
    queue = [artifact_id]
    while queue:
        current = queue.pop()
        for edge in edges:
            if edge.get("to") == current and edge.get("type", "").startswith("parent-"):
                child = edge.get("from", "")
                if child and child not in children:
                    children.add(child)
                    queue.append(child)
    return children


def _get_roadmap_hash(repo_root: str) -> str:
    """Get the git blob hash of ROADMAP.md, or 'n/a' if not tracked."""
    roadmap_path = os.path.join(repo_root, "ROADMAP.md")
    if not os.path.isfile(roadmap_path):
        return "n/a"
    try:
        result = subprocess.run(
            ["git", "hash-object", roadmap_path],
            capture_output=True, text=True, cwd=repo_root, timeout=5,
        )
        return result.stdout.strip()[:8] if result.returncode == 0 else "n/a"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return "n/a"


def _get_head_commit(repo_root: str) -> str:
    """Get current HEAD short hash."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, cwd=repo_root, timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else "unknown"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return "unknown"


def _get_recent_session_commits(repo_root: str, limit: int = 10) -> list[str]:
    """Get recent commits with full messages that reference SESSION-ROADMAP or session artifacts."""
    try:
        result = subprocess.run(
            ["git", "log", f"-{limit}", "--format=%H%n%B%n---END---"],
            capture_output=True, text=True, cwd=repo_root, timeout=10,
        )
        if result.returncode != 0:
            return []
        return result.stdout.strip().split("---END---")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []


def _get_progress_commits(
    child_ids: set[str], repo_root: str, limit: int = 5,
) -> list[dict]:
    """Get recent commits whose full messages reference any child artifact ID."""
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-50", "--all"],
            capture_output=True, text=True, cwd=repo_root, timeout=10,
        )
        if result.returncode != 0:
            return []
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []

    commits = []
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        for cid in child_ids:
            if cid in line:
                parts = line.split(" ", 1)
                commits.append({
                    "hash": parts[0],
                    "message": parts[1] if len(parts) > 1 else "",
                })
                break
        if len(commits) >= limit:
            break
    return commits


def render_session_roadmap(
    focus_id: str,
    nodes: dict,
    edges: list[dict],
    repo_root: str = "",
) -> str:
    """Render a SESSION-ROADMAP.md for the given focus lane.

    Args:
        focus_id: Initiative or Vision artifact ID to scope the session
        nodes: Full graph nodes dict
        edges: Full graph edges list
        repo_root: Project root for file operations and git queries
    """
    focus_node = nodes.get(focus_id, {})
    focus_title = focus_node.get("title", focus_id)
    descendants = _compute_descendants(focus_id, edges)
    all_scope_ids = descendants | {focus_id}

    # Compute scoped recommendations
    recs = rank_recommendations(nodes, edges)
    scoped_recs = [r for r in recs if r["id"] in all_scope_ids]
    decision_recs = [r for r in scoped_recs if r["is_decision"]]
    impl_recs = [r for r in scoped_recs if not r["is_decision"]]

    # Read decision log
    decision_records = read_decision_records(repo_root)

    # Progress commits
    progress_commits = _get_progress_commits(descendants, repo_root)

    lines: list[str] = []

    # Title
    lines.append(f"# SESSION-ROADMAP: {focus_title}")
    lines.append("")
    lines.append("<!-- Generated by chart.sh session. Committed on session close. -->")
    lines.append("")

    # --- Section 1: Evidence Basis ---
    lines.append("## Evidence Basis")
    lines.append("")
    roadmap_hash = _get_roadmap_hash(repo_root)
    head_hash = _get_head_commit(repo_root)
    lines.append(f"- **Focus lane:** {focus_id} ({focus_title})")
    lines.append(f"- **ROADMAP.md hash:** `{roadmap_hash}`")
    lines.append(f"- **HEAD:** `{head_hash}`")
    lines.append(f"- **Artifacts in scope:** {len(descendants)}")
    # List the direct children consulted
    direct_children = []
    for e in edges:
        if e.get("to") == focus_id and e.get("type", "").startswith("parent-"):
            child = e.get("from", "")
            if child in nodes:
                direct_children.append(child)
    if direct_children:
        lines.append(f"- **Direct children:** {', '.join(sorted(direct_children))}")
    lines.append("")

    # --- Section 2: Decision Set ---
    lines.append("## Decision Set")
    lines.append("")
    if decision_recs:
        lines.append("| Artifact | Title | Unblocks |")
        lines.append("|----------|-------|----------|")
        for rec in decision_recs:
            node = nodes.get(rec["id"], {})
            title = node.get("title", rec["id"])
            unblocks = str(rec["unblock_count"]) if rec["unblock_count"] > 0 else "—"
            lines.append(f"| {rec['id']} | {title} | {unblocks} |")
    else:
        lines.append("No decisions needed in this focus area right now.")
    lines.append("")

    # --- Section 3: Recommended Next ---
    lines.append("## Recommended Next")
    lines.append("")
    if scoped_recs:
        top = scoped_recs[0]
        node = nodes.get(top["id"], {})
        title = node.get("title", top["id"])
        weight_label = {3: "high", 2: "medium", 1: "low"}.get(top["vision_weight"], "medium")
        rationale_parts = []
        if top["unblock_count"] > 0:
            rationale_parts.append(f"unblocks {top['unblock_count']}")
        rationale_parts.append(f"weight: {weight_label}")
        rationale = ", ".join(rationale_parts)
        lines.append(f"> **{top['id']}**: {title} — {rationale}")
    else:
        lines.append("No actionable items in this focus area.")
    lines.append("")

    # --- Section 4: Session Goal ---
    lines.append("## Session Goal")
    lines.append("")
    _render_session_goal(lines, decision_recs, impl_recs, nodes, focus_title)
    lines.append("")

    # --- Section 5: Progress ---
    lines.append("## Progress")
    lines.append("")
    if progress_commits:
        lines.append("Recent commits touching this focus area:")
        lines.append("")
        for c in progress_commits:
            lines.append(f"- `{c['hash']}` {c['message']}")
    else:
        lines.append("No recent commits reference artifacts in this focus area.")
    lines.append("")

    # --- Section 6: Decision Records ---
    lines.append("## Decision Records")
    lines.append("")
    if decision_records:
        lines.append("| Timestamp | Artifact | Action | Commit |")
        lines.append("|-----------|----------|--------|--------|")
        for rec in decision_records:
            ts = rec.get("timestamp", "—")[:19]  # Trim to seconds
            lines.append(
                f"| {ts} | {rec.get('artifact', '—')} | {rec.get('action', '—')} | `{rec.get('commit', '—')}` |"
            )
    else:
        lines.append("No decisions recorded yet this session.")
    lines.append("")

    # --- Section 7: Walk-Away Signal ---
    lines.append("## Walk-Away Signal")
    lines.append("")
    total_decisions = len(decision_recs)
    recorded = len([r for r in decision_records if r.get("artifact") in {d["id"] for d in decision_recs}])
    remaining = total_decisions - recorded
    if remaining <= 0 and total_decisions == 0:
        lines.append("No decisions needed — this focus area has no pending operator actions.")
    elif remaining <= 0:
        lines.append("All pending decisions have been addressed this session.")
    else:
        lines.append(f"**{remaining} decision(s) remaining** in this focus area.")
        remaining_ids = [d["id"] for d in decision_recs if d["id"] not in {r.get("artifact") for r in decision_records}]
        if remaining_ids:
            lines.append(f"Remaining: {', '.join(remaining_ids)}")
    lines.append("")

    return "\n".join(lines)


def _render_session_goal(
    lines: list[str],
    decision_recs: list[dict],
    impl_recs: list[dict],
    nodes: dict,
    focus_title: str,
) -> None:
    """Render the session goal with recommendation + ≤2 alternatives."""
    all_actionable = decision_recs + impl_recs

    if not all_actionable:
        lines.append(f"**Recommended goal:** Review the {focus_title} scope for completeness.")
        lines.append("")
        lines.append("No actionable items to drive a goal from.")
        return

    # Recommendation: address the top decision items (bounded to 3-5)
    if decision_recs:
        top_decisions = decision_recs[:min(5, len(decision_recs))]
        decision_ids = ", ".join(d["id"] for d in top_decisions)
        lines.append(f"**Recommended goal:** Address {len(top_decisions)} pending decision(s): {decision_ids}")
        lines.append("")
        lines.append(f"*Justification:* These are operator-gated items blocking downstream work in {focus_title}. "
                      f"Resolving them unblocks {sum(d['unblock_count'] for d in top_decisions)} downstream item(s).")
    else:
        # No decisions — recommend implementation
        top_impl = impl_recs[:3]
        impl_ids = ", ".join(d["id"] for d in top_impl)
        lines.append(f"**Recommended goal:** Progress implementation on {impl_ids}")
        lines.append("")
        lines.append(f"*Justification:* No operator decisions are pending. These items are the highest-leverage "
                      f"implementation work in {focus_title}.")

    # Alternatives (max 2)
    lines.append("")
    alternatives_shown = 0

    if decision_recs and impl_recs and alternatives_shown < 2:
        top_impl = impl_recs[0]
        impl_node = nodes.get(top_impl["id"], {})
        lines.append(f"**Alternative 1:** Shift to implementation — start with {top_impl['id']} ({impl_node.get('title', '')})")
        lines.append(f"*Rationale:* If decisions need more thought, make progress on ready implementation work instead.")
        alternatives_shown += 1

    if len(decision_recs) > 5 and alternatives_shown < 2:
        lines.append(f"**Alternative {alternatives_shown + 1}:** Triage all {len(decision_recs)} decisions — "
                      f"batch-approve or defer lower-priority items to reduce backlog")
        lines.append(f"*Rationale:* A large decision backlog may indicate scope creep or items that should be dropped.")
        alternatives_shown += 1

    if alternatives_shown < 2 and all_actionable:
        lines.append(f"**Alternative {alternatives_shown + 1}:** Review scope — audit {focus_title} for "
                      f"items that can be deferred or dropped")
        lines.append(f"*Rationale:* Reducing scope is a valid session goal when the backlog grows faster than throughput.")
