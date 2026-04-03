---
id: pamv22c-sk86
status: closed
deps: [pamv22c-zl6z]
links: []
created: 2026-04-03T02:32:38Z
type: epic
priority: 1
assignee: Cristos L-C
external-ref: SPEC-234
---
# SPEC-234 materialized child views

Build lifecycle-scoped child-folder symlink projection and _unparented README surfaces using the chart projection output.


## Notes

**2026-04-03T02:41:21Z**

SPEC-234 plan complete. Evidence: python3 -m pytest skills/swain-design/scripts/tests/test_graph.py skills/swain-design/scripts/tests/test_chart_wrapper.py skills/swain-design/scripts/tests/test_materialize_hierarchy.py -q => 30 passed.

**2026-04-03T02:50:42Z**

Final verification: python3 -m pytest skills/swain-design/scripts/tests/test_graph.py skills/swain-design/scripts/tests/test_chart_wrapper.py skills/swain-design/scripts/tests/test_materialize_hierarchy.py -q => 35 passed; bash .agents/bin/chart.sh build => Graph built with 424 nodes and 1881 edges.
