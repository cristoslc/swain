# TDD Enforcement

Implementation tasks follow strict RED-GREEN-REFACTOR methodology with anti-rationalization safeguards. These rules apply regardless of whether superpowers is installed — they are baked into swain-do's methodology.

## Anti-rationalization table

When creating implementation plans, every task that involves writing code must follow this discipline:

| Rationalization | Why it's wrong | Rule |
|----------------|---------------|------|
| "I'll write the test after the code since I know what I'm building" | Tests written after confirm what was built, not what was specified. They miss edge cases the spec intended. | Write the failing test FIRST. The test is derived from the acceptance criterion, not the implementation. |
| "This is too simple to need a test" | Simplicity today becomes complexity tomorrow. Untested code is unverified code. | Every behavioral change gets a test. If it's truly simple, the test is also simple. |
| "I'll refactor first to make testing easier" | Refactoring without tests means refactoring without a safety net. | RED first. Write the test against the current interface, then refactor under test coverage. |
| "The integration test covers this" | Integration tests are slow and don't isolate failures. A unit test failing tells you exactly what broke. | Unit tests for logic, integration tests for wiring. Both are needed. |
| "I need to see the implementation to know what to test" | This means the spec is unclear, not that you should skip TDD. | If you can't write the test, the acceptance criterion needs clarification — escalate to swain-design. |

## Task ordering

1. **Test first.** For each functional unit, create a test task before its implementation task. The test task writes a failing test derived from the artifact's acceptance criteria.
2. **Small cycles.** Prefer many small red-green pairs over a single "write all tests" → "write all code" split.
3. **Refactor explicitly.** Include a refactor task after green when the implementation warrants cleanup.
4. **Integration tests bookend the plan.** Start with a skeleton integration test (it will fail). The final task verifies it passes.

## Completion verification

No task may be claimed as complete without fresh verification evidence. This applies universally — not just to SPEC acceptance criteria, but to any tk task.

### What counts as evidence

| Task type | Acceptable evidence |
|-----------|-------------------|
| Code implementation | Test passes, manual verification output, screenshot |
| Documentation | Content review, link check, rendered preview |
| Configuration | Applied and tested in target environment |
| Research | Findings documented with sources |

### Enforcement

When closing a task, add a note with evidence before closing:

```bash
# Good — includes evidence
tk add-note <id> "JWT middleware added; test_jwt_validation passes"
tk close <id>

# Bad — no evidence
tk close <id>
```

If a task is closed without evidence, it should be reopened and completed properly. The verification discipline prevents "completion drift" where tasks are marked done based on intent rather than observed behavior.
