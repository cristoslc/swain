---
id: pamv22c-zl6z
status: closed
deps: []
links: []
created: 2026-04-03T02:32:38Z
type: epic
priority: 1
assignee: Cristos L-C
external-ref: SPEC-233
---
# SPEC-233 hierarchy projection output

Create the machine-readable chart projection output for hierarchy placement. Covers output shape, narrowest-parent placement, unparented state, and tests.


## Notes

**2026-04-03T02:39:15Z**

SPEC-233 plan complete. Evidence: python3 -m pytest skills/swain-design/scripts/tests/test_graph.py skills/swain-design/scripts/tests/test_chart_wrapper.py -q => 27 passed.

**2026-04-03T02:50:42Z**

Final verification: python3 -m pytest skills/swain-design/scripts/tests/test_graph.py skills/swain-design/scripts/tests/test_chart_wrapper.py skills/swain-design/scripts/tests/test_materialize_hierarchy.py -q => 35 passed; bash .agents/bin/chart.sh build => Graph built with 424 nodes and 1881 edges.
