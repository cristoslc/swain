# Implementation Plans

Implementation plans bridge declarative specs (`docs/`) and execution tracking. They are not doc-type artifacts. All CLI operations are handled by the **swain-do** skill — invoke it to bootstrap the task backend before creating plans.

## TDD methodology

Implementation plans follow **test-driven development** as the default methodology. Every plan should structure tasks so that tests are written before the code they verify — the classic red-green-refactor cycle. This matters because tests written after implementation tend to confirm what was built rather than what was specified; writing tests first forces the plan to stay anchored to the acceptance criteria.

**Task ordering principles:**

1. **Test first.** For each functional unit, the plan should contain a test task *before* its implementation task. The test task writes a failing test derived from the artifact's acceptance criteria. The implementation task makes it pass.
2. **Small cycles.** Prefer many small red-green pairs over a single "write all tests" → "write all code" split. Each cycle should cover one acceptance criterion or one behavioral facet.
3. **Refactor explicitly.** When a cycle produces working but rough code, include a refactor task after the green phase. Not every cycle needs one — only when the implementation warrants cleanup.
4. **Integration tests bookend the plan.** Start with a skeleton integration test that exercises the end-to-end path (it will fail until the pieces exist). The final task verifies it passes.

When superpowers is present, the brainstorming step should produce a TDD-structured plan. When seeding manually, decompose the spec's acceptance criteria into red-green task pairs.

## Workflow

1. If superpowers is present, use the [superpowers integration](#superpowers-integration) flow to author the plan. Otherwise, seed manually from the spec's "Implementation Approach" section, structuring tasks as TDD cycles derived from acceptance criteria.
2. Create an implementation plan linked via an **origin ref** (e.g., `SPEC-003`). Create tasks with dependencies, each tagged with **spec tags** for originating specs. Order test-writing tasks before their corresponding implementation tasks.
3. When a task impacts additional specs, add spec tags and cross-plan dependencies.

## Closing the loop

- Progress lives in the execution backend, not the spec doc.
- When all plan tasks are complete, transition the Spec to **Testing** (not directly to Implemented). The Testing phase is where acceptance criteria are verified against evidence — see `spec-definition.md § Testing phase`.
- In the Testing phase, populate the Spec's **Verification** table: map each acceptance criterion to its evidence (test name, file, demo) and record Pass/Fail/Skip.
- Run `scripts/spec-verify.sh <artifact-path>` before transitioning from Testing → Implemented. The script confirms every criterion has evidence.
- Only after verification passes, transition the Spec to **Implemented**.
- Note cross-spec tasks in each affected artifact's lifecycle entry (e.g., "Implemented — shared serializer also covers SPEC-007").
- If execution reveals the spec is unworkable, the swain-do skill's escalation protocol flows control back to the swain-design skill for spec updates before re-planning.

## Superpowers integration

When superpowers (obra/superpowers) is installed, route implementation through its brainstorming → writing-plans pipeline to produce higher-quality plans before handing off to swain-do.

**Detection:** Check whether the `brainstorming` and `writing-plans` skills exist:

```bash
ls .claude/skills/brainstorming/SKILL.md .claude/skills/writing-plans/SKILL.md 2>/dev/null
```

If both exist, superpowers is available. If either is missing, use the current direct-to-swain-do flow.

**Routing when superpowers IS present:**

1. Invoke the `brainstorming` skill with the artifact's context — pass the problem statement, acceptance criteria, and scope from the artifact's frontmatter and body.
2. Brainstorming produces a design and invokes `writing-plans` automatically.
3. `writing-plans` saves a plan file to `docs/plans/YYYY-MM-DD-<feature-name>.md`.
4. After the plan file is saved, invoke swain-do's plan ingestion:
   ```bash
   python3 .claude/skills/swain-do/scripts/ingest-plan.py \
     docs/plans/<plan-file>.md <ARTIFACT-ID>
   ```
5. This creates a bd epic with child tasks, sequential dependencies, and spec lineage tags.

**Routing when superpowers is NOT present:**

Use the current flow — invoke swain-do directly for ad-hoc task breakdown.

**If the user rejects the brainstorming design:** Stop cleanly. No plan file is produced, no bd tasks are created. The user can either retry brainstorming or fall back to the direct flow.

**Superpowers is a recommended companion, not a hard dependency.** Never install it automatically or block implementation if it's missing.

## Fallback

If swain-do is unavailable, fall back to the agent's built-in todo system (`todo`, `in_progress`, `blocked`, `done`). Maintain lineage by including artifact IDs in task titles (e.g., `[SPEC-003] Add export endpoint`).
