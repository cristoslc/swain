## Readability protocol

Artifact-producing skills run a Flesch-Kincaid readability check after finalizing artifact body text, before committing. This ensures all swain artifacts stay at or below a 10th-grade reading level.

### When to run

Run the check after the artifact body is complete and all structural validation (ADR compliance, alignment check, specwatch) has passed. The readability check is the last quality gate before commit.

### Invocation

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
bash "$REPO_ROOT/.agents/bin/readability-check.sh" <artifact-path>
```

### Handling results

**PASS** — No action needed. Proceed to commit.

**SKIP** — The file has fewer than 50 words of prose after stripping non-prose content. No action needed.

**FAIL** — The prose exceeds the grade-level threshold. Revise the failing sections:
1. Break long sentences into shorter ones (aim for 15-20 words per sentence)
2. Replace complex words with simpler alternatives
3. Use active voice instead of passive
4. Remove unnecessary qualifiers and jargon
5. Re-run the check

**Maximum 3 rewrite attempts.** If the score still exceeds the threshold after three revisions, note the score in the commit message (e.g., `readability: grade 10.2 after 3 attempts`) and proceed. Do not block the operation indefinitely.

### Integration points

| Skill | Hook point |
|-------|-----------|
| swain-design | After step 8b (unanchored check), before step 9 (specwatch scan) |
| swain-retro | After retro content generation, before embedding in EPIC or committing |
| Any artifact-producing skill | After body text is finalized, before commit |

Skills do not need code changes to adopt this protocol. The governance rule in AGENTS.md directs all artifact-producing agents to run the check. This protocol doc provides the details.
