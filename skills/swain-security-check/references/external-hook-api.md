## External Security Skill Hook Interface (SPEC-065)

External security skills can plug into swain-do's security gates via three hook points. All hooks are no-ops when no external skills are installed -- built-in guidance (SPEC-063) always runs independently.

### Hook points

| Hook | When | Input | Output | Capability key |
|------|------|-------|--------|----------------|
| **Pre-claim** | After threat surface detection, before briefing | Task metadata (title, tags, categories) | Markdown guidance blocks | `security-briefing` |
| **During-implementation** | While editing security-sensitive files | File paths being edited | Security context notes | `security-context` |
| **Completion** | After implementation, during review | Git diff of changes | Differential review findings | `security-review` |

### Skill detection

Skills are discovered by scanning for `SKILL.md` files in known directories:

```
.claude/skills/trailofbits-*/SKILL.md
.agents/skills/trailofbits-*/SKILL.md
.claude/skills/owasp-security/SKILL.md
.agents/skills/owasp-security/SKILL.md
```

### Known skills

| Skill | Detection pattern | Capabilities |
|-------|------------------|--------------|
| Trail of Bits sharp-edges | `trailofbits-sharp-edges` | `security-briefing` |
| Trail of Bits insecure-defaults | `trailofbits-insecure-defaults` | `security-briefing` |
| Trail of Bits differential-review | `trailofbits-differential-review` | `security-review` |
| OWASP Security | `owasp-security` | `security-briefing`, `security-context` |

### Adding a new external skill

To integrate a new security skill, call `register_skill()` -- no changes to core code are required:

```python
from external_hooks import register_skill

register_skill(
    name="snyk-security",
    detection_pattern="snyk-security",       # or "snyk-*" for glob matching
    hook_capabilities=["security-briefing", "security-review"],
)
```

The skill directory must contain a `SKILL.md` file at the detection path. The detection pattern supports exact names and glob-style wildcards (`*`, `?`).

### Python API

```python
from external_hooks import (
    detect_installed_skills,
    register_skill,
    run_pre_claim_hooks,
    run_implementation_hooks,
    run_completion_hooks,
)

# Detect which skills are installed
skills = detect_installed_skills()  # uses cwd
skills = detect_installed_skills(search_dirs=["/path/to/project"])

# Run hooks (all return list[str] of markdown blocks)
guidance = run_pre_claim_hooks(
    task_metadata={"title": "...", "tags": [...], "categories": [...]},
    installed_skills=skills,
)
notes = run_implementation_hooks(
    file_paths=["src/auth/handler.py"],
    installed_skills=skills,
)
findings = run_completion_hooks(
    git_diff="diff --git ...",
    installed_skills=skills,
)
```

### Design constraints

- External hooks are **additive** -- they never replace built-in SPEC-063 guidance
- Skills that do not support a given hook point are silently skipped
- Detection is filesystem-only (no network calls, no subprocess invocations)
- The interface is intentionally command-based and loosely coupled
