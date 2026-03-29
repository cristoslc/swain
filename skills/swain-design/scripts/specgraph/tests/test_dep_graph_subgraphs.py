"""Tests for dependency graph initiative subgraphs (SPEC-112)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from specgraph.roadmap import collect_roadmap_items, render_dependency_graph


def _make_graph_with_initiatives():
    """Two initiatives, each with 2 epics. Cross-initiative dependency."""
    nodes = {
        "VISION-001": {"type": "Vision", "title": "Core", "status": "Active", "priority_weight": "high"},
        "INITIATIVE-001": {"type": "Initiative", "title": "Auth", "status": "Active"},
        "INITIATIVE-002": {"type": "Initiative", "title": "Billing", "status": "Active"},
        "EPIC-001": {"type": "Epic", "title": "Login", "status": "Active"},
        "EPIC-002": {"type": "Epic", "title": "SSO", "status": "Active"},
        "EPIC-003": {"type": "Epic", "title": "Payments", "status": "Active"},
        "EPIC-004": {"type": "Epic", "title": "Invoices", "status": "Active"},
    }
    edges = [
        {"from": "INITIATIVE-001", "to": "VISION-001", "type": "parent-vision"},
        {"from": "INITIATIVE-002", "to": "VISION-001", "type": "parent-vision"},
        {"from": "EPIC-001", "to": "INITIATIVE-001", "type": "parent-initiative"},
        {"from": "EPIC-002", "to": "INITIATIVE-001", "type": "parent-initiative"},
        {"from": "EPIC-003", "to": "INITIATIVE-002", "type": "parent-initiative"},
        {"from": "EPIC-004", "to": "INITIATIVE-002", "type": "parent-initiative"},
        # Cross-initiative dep: Payments depends on Login
        {"from": "EPIC-003", "to": "EPIC-001", "type": "depends-on"},
        # Within-initiative dep: SSO depends on Login
        {"from": "EPIC-002", "to": "EPIC-001", "type": "depends-on"},
    ]
    return nodes, edges


def _make_graph_standalone():
    """Standalone epics (no initiative) with dependency."""
    nodes = {
        "EPIC-001": {"type": "Epic", "title": "Standalone A", "status": "Active", "priority_weight": "high"},
        "EPIC-002": {"type": "Epic", "title": "Standalone B", "status": "Active", "priority_weight": "high"},
    }
    edges = [
        {"from": "EPIC-002", "to": "EPIC-001", "type": "depends-on"},
    ]
    return nodes, edges


def _make_graph_all_single_node_subgraphs():
    """Each initiative has exactly one epic — should fall back to flat."""
    nodes = {
        "VISION-001": {"type": "Vision", "title": "Core", "status": "Active", "priority_weight": "high"},
        "INITIATIVE-001": {"type": "Initiative", "title": "Auth", "status": "Active"},
        "INITIATIVE-002": {"type": "Initiative", "title": "Billing", "status": "Active"},
        "EPIC-001": {"type": "Epic", "title": "Login", "status": "Active"},
        "EPIC-002": {"type": "Epic", "title": "Payments", "status": "Active"},
    }
    edges = [
        {"from": "INITIATIVE-001", "to": "VISION-001", "type": "parent-vision"},
        {"from": "INITIATIVE-002", "to": "VISION-001", "type": "parent-vision"},
        {"from": "EPIC-001", "to": "INITIATIVE-001", "type": "parent-initiative"},
        {"from": "EPIC-002", "to": "INITIATIVE-002", "type": "parent-initiative"},
        {"from": "EPIC-002", "to": "EPIC-001", "type": "depends-on"},
    ]
    return nodes, edges


def test_subgraphs_present_with_multi_node_initiatives():
    nodes, edges = _make_graph_with_initiatives()
    items = collect_roadmap_items(nodes, edges)
    result = render_dependency_graph(items, nodes)
    assert result is not None
    assert "subgraph" in result
    assert "Auth" in result
    assert "Billing" in result


def test_cross_initiative_edges_cross_boundaries():
    nodes, edges = _make_graph_with_initiatives()
    items = collect_roadmap_items(nodes, edges)
    result = render_dependency_graph(items, nodes)
    assert result is not None
    # Should have edges between nodes in different subgraphs
    assert "blocks" in result


def test_standalone_epics_outside_subgraph():
    nodes, edges = _make_graph_standalone()
    items = collect_roadmap_items(nodes, edges)
    result = render_dependency_graph(items, nodes)
    assert result is not None
    # Standalone epics should NOT be in a subgraph
    assert "subgraph" not in result


def test_single_node_subgraphs_fall_back_to_flat():
    nodes, edges = _make_graph_all_single_node_subgraphs()
    items = collect_roadmap_items(nodes, edges)
    result = render_dependency_graph(items, nodes)
    assert result is not None
    # All single-node subgraphs → flat layout
    assert "subgraph" not in result


def test_mixed_standalone_and_initiative():
    """Mix of initiative-grouped and standalone epics."""
    nodes = {
        "VISION-001": {"type": "Vision", "title": "Core", "status": "Active", "priority_weight": "high"},
        "INITIATIVE-001": {"type": "Initiative", "title": "Auth", "status": "Active"},
        "EPIC-001": {"type": "Epic", "title": "Login", "status": "Active"},
        "EPIC-002": {"type": "Epic", "title": "SSO", "status": "Active"},
        "EPIC-003": {"type": "Epic", "title": "Standalone", "status": "Active", "priority_weight": "high"},
    }
    edges = [
        {"from": "INITIATIVE-001", "to": "VISION-001", "type": "parent-vision"},
        {"from": "EPIC-001", "to": "INITIATIVE-001", "type": "parent-initiative"},
        {"from": "EPIC-002", "to": "INITIATIVE-001", "type": "parent-initiative"},
        {"from": "EPIC-003", "to": "EPIC-001", "type": "depends-on"},
        {"from": "EPIC-002", "to": "EPIC-001", "type": "depends-on"},
    ]
    nodes_dict, edges_list = nodes, edges
    items = collect_roadmap_items(nodes_dict, edges_list)
    result = render_dependency_graph(items, nodes_dict)
    assert result is not None
    assert "subgraph" in result  # Auth has 2 nodes
    assert "Standalone" in result  # standalone appears outside subgraph
