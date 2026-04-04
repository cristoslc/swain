---
id: pamv22c-auly
status: closed
deps: [pamv22c-sk86]
links: []
created: 2026-04-03T02:32:38Z
type: epic
priority: 1
assignee: Cristos L-C
external-ref: SPEC-235
---
# SPEC-235 automatic hierarchy reconciliation

Wire chart rebuild plus materializer reconciliation into mutating workflows with idempotent drift cleanup and collision handling.


## Notes

**2026-04-03T02:44:17Z**

SPEC-235 plan complete. Evidence: python3 -m pytest skills/swain-design/scripts/tests/test_graph.py skills/swain-design/scripts/tests/test_chart_wrapper.py skills/swain-design/scripts/tests/test_materialize_hierarchy.py -q => 33 passed.

**2026-04-03T02:50:42Z**

Final verification: python3 -m pytest skills/swain-design/scripts/tests/test_graph.py skills/swain-design/scripts/tests/test_chart_wrapper.py skills/swain-design/scripts/tests/test_materialize_hierarchy.py -q => 35 passed; bash .agents/bin/chart.sh build => Graph built with 424 nodes and 1881 edges.
