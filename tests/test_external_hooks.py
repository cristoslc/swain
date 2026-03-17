"""Tests for external security skill hook interface (SPEC-065).

TDD RED phase: all tests written before implementation.

Tests cover:
  - Skill detection via known SKILL.md paths (swa-pnhz)
  - Hook point integration: pre-claim, during-implementation, completion (swa-h35y)
"""

import sys
from pathlib import Path

# Add the module to the path so we can import it
sys.path.insert(
    0,
    str(
        Path(__file__).parent.parent
        / "skills"
        / "swain-security-check"
        / "scripts"
    ),
)

from external_hooks import (
    detect_installed_skills,
    register_skill,
    run_completion_hooks,
    run_implementation_hooks,
    run_pre_claim_hooks,
)

# ---------------------------------------------------------------------------
# Task swa-pnhz: External skill detection tests
# ---------------------------------------------------------------------------


class TestDetectInstalledSkills:
    """Detect external security skills via known SKILL.md paths."""

    def test_no_skills_installed_returns_empty(self, tmp_path):
        """When no skill directories exist, return empty dict."""
        result = detect_installed_skills(search_dirs=[str(tmp_path)])
        assert result == {}

    def test_detects_trailofbits_sharp_edges(self, tmp_path):
        """Detect trailofbits-sharp-edges skill in .claude/skills/."""
        skill_dir = tmp_path / ".claude" / "skills" / "trailofbits-sharp-edges"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Sharp Edges\n")

        result = detect_installed_skills(search_dirs=[str(tmp_path)])
        assert "trailofbits-sharp-edges" in result
        assert result["trailofbits-sharp-edges"] == str(skill_dir)

    def test_detects_trailofbits_in_agents_dir(self, tmp_path):
        """Detect trailofbits skill in .agents/skills/ (alternate location)."""
        skill_dir = tmp_path / ".agents" / "skills" / "trailofbits-insecure-defaults"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Insecure Defaults\n")

        result = detect_installed_skills(search_dirs=[str(tmp_path)])
        assert "trailofbits-insecure-defaults" in result
        assert result["trailofbits-insecure-defaults"] == str(skill_dir)

    def test_detects_trailofbits_differential_review(self, tmp_path):
        """Detect trailofbits-differential-review skill."""
        skill_dir = tmp_path / ".claude" / "skills" / "trailofbits-differential-review"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Differential Review\n")

        result = detect_installed_skills(search_dirs=[str(tmp_path)])
        assert "trailofbits-differential-review" in result

    def test_detects_owasp_security(self, tmp_path):
        """Detect owasp-security skill in .claude/skills/."""
        skill_dir = tmp_path / ".claude" / "skills" / "owasp-security"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# OWASP Security\n")

        result = detect_installed_skills(search_dirs=[str(tmp_path)])
        assert "owasp-security" in result
        assert result["owasp-security"] == str(skill_dir)

    def test_detects_owasp_in_agents_dir(self, tmp_path):
        """Detect owasp-security in .agents/skills/ (alternate location)."""
        skill_dir = tmp_path / ".agents" / "skills" / "owasp-security"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# OWASP Security\n")

        result = detect_installed_skills(search_dirs=[str(tmp_path)])
        assert "owasp-security" in result

    def test_detects_multiple_skills(self, tmp_path):
        """Detect multiple skills simultaneously."""
        tob_dir = tmp_path / ".claude" / "skills" / "trailofbits-sharp-edges"
        tob_dir.mkdir(parents=True)
        (tob_dir / "SKILL.md").write_text("# Sharp Edges\n")

        owasp_dir = tmp_path / ".agents" / "skills" / "owasp-security"
        owasp_dir.mkdir(parents=True)
        (owasp_dir / "SKILL.md").write_text("# OWASP\n")

        result = detect_installed_skills(search_dirs=[str(tmp_path)])
        assert len(result) == 2
        assert "trailofbits-sharp-edges" in result
        assert "owasp-security" in result

    def test_ignores_directory_without_skill_md(self, tmp_path):
        """A directory matching the pattern but without SKILL.md is ignored."""
        skill_dir = tmp_path / ".claude" / "skills" / "trailofbits-sharp-edges"
        skill_dir.mkdir(parents=True)
        # No SKILL.md created

        result = detect_installed_skills(search_dirs=[str(tmp_path)])
        assert result == {}

    def test_ignores_non_matching_skill_names(self, tmp_path):
        """Skills not matching known patterns are not detected."""
        skill_dir = tmp_path / ".claude" / "skills" / "my-custom-security"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Custom\n")

        result = detect_installed_skills(search_dirs=[str(tmp_path)])
        assert result == {}

    def test_multiple_search_dirs(self, tmp_path):
        """Skills are detected across multiple search directories."""
        dir_a = tmp_path / "project_a"
        dir_b = tmp_path / "project_b"

        skill_a = dir_a / ".claude" / "skills" / "trailofbits-sharp-edges"
        skill_a.mkdir(parents=True)
        (skill_a / "SKILL.md").write_text("# Sharp Edges\n")

        skill_b = dir_b / ".agents" / "skills" / "owasp-security"
        skill_b.mkdir(parents=True)
        (skill_b / "SKILL.md").write_text("# OWASP\n")

        result = detect_installed_skills(search_dirs=[str(dir_a), str(dir_b)])
        assert "trailofbits-sharp-edges" in result
        assert "owasp-security" in result

    def test_default_search_dir_is_cwd(self, tmp_path, monkeypatch):
        """When no search_dirs given, use current working directory."""
        skill_dir = tmp_path / ".claude" / "skills" / "owasp-security"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# OWASP\n")

        monkeypatch.chdir(tmp_path)
        result = detect_installed_skills()
        assert "owasp-security" in result


class TestRegisterSkill:
    """Registering new skills adds detection patterns without core code changes."""

    def test_register_adds_new_detection_pattern(self, tmp_path):
        """After registration, new skill pattern is detected."""
        # Register a hypothetical new skill
        register_skill(
            name="snyk-security",
            detection_pattern="snyk-security",
            hook_capabilities=["security-briefing", "security-review"],
        )

        # Create the skill directory
        skill_dir = tmp_path / ".claude" / "skills" / "snyk-security"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Snyk Security\n")

        result = detect_installed_skills(search_dirs=[str(tmp_path)])
        assert "snyk-security" in result

    def test_register_with_glob_pattern(self, tmp_path):
        """Registration with glob-style pattern matches multiple skills."""
        register_skill(
            name="snyk",
            detection_pattern="snyk-*",
            hook_capabilities=["security-briefing"],
        )

        skill_dir = tmp_path / ".claude" / "skills" / "snyk-code-review"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Snyk Code Review\n")

        result = detect_installed_skills(search_dirs=[str(tmp_path)])
        assert "snyk-code-review" in result

    def test_register_returns_none(self):
        """register_skill returns None (side-effect only)."""
        result = register_skill(
            name="test-skill",
            detection_pattern="test-skill",
            hook_capabilities=["security-briefing"],
        )
        assert result is None


# ---------------------------------------------------------------------------
# Task swa-h35y: Hook point integration tests
# ---------------------------------------------------------------------------


class TestPreClaimHooks:
    """Pre-claim hooks return additional security guidance as markdown."""

    def test_no_skills_returns_empty_list(self):
        """With no installed skills, pre-claim returns empty list."""
        result = run_pre_claim_hooks(
            task_metadata={"title": "Fix auth", "tags": ["security"], "categories": ["auth"]},
            installed_skills={},
        )
        assert result == []

    def test_returns_list_of_strings(self, tmp_path):
        """Pre-claim hooks return a list of markdown guidance strings."""
        skill_dir = tmp_path / ".claude" / "skills" / "trailofbits-sharp-edges"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Sharp Edges\n")

        skills = {"trailofbits-sharp-edges": str(skill_dir)}
        result = run_pre_claim_hooks(
            task_metadata={"title": "Fix auth", "tags": ["security"], "categories": ["auth"]},
            installed_skills=skills,
        )
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, str)

    def test_includes_skill_name_in_output(self, tmp_path):
        """Each guidance block should identify which skill produced it."""
        skill_dir = tmp_path / ".claude" / "skills" / "trailofbits-sharp-edges"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Sharp Edges\n")

        skills = {"trailofbits-sharp-edges": str(skill_dir)}
        result = run_pre_claim_hooks(
            task_metadata={"title": "Fix auth", "tags": ["security"], "categories": ["auth"]},
            installed_skills=skills,
        )
        if result:  # Only check if the skill produced output
            combined = "\n".join(result)
            assert "trailofbits-sharp-edges" in combined

    def test_multiple_skills_produce_multiple_blocks(self, tmp_path):
        """Multiple installed skills each produce their own guidance block."""
        tob_dir = tmp_path / ".claude" / "skills" / "trailofbits-sharp-edges"
        tob_dir.mkdir(parents=True)
        (tob_dir / "SKILL.md").write_text("# Sharp Edges\n")

        owasp_dir = tmp_path / ".claude" / "skills" / "owasp-security"
        owasp_dir.mkdir(parents=True)
        (owasp_dir / "SKILL.md").write_text("# OWASP\n")

        skills = {
            "trailofbits-sharp-edges": str(tob_dir),
            "owasp-security": str(owasp_dir),
        }
        result = run_pre_claim_hooks(
            task_metadata={"title": "Fix auth", "tags": ["security"], "categories": ["auth"]},
            installed_skills=skills,
        )
        assert isinstance(result, list)
        # Each skill that supports pre-claim should produce a block
        # (exact count depends on which skills support the hook)

    def test_task_metadata_contains_required_fields(self, tmp_path):
        """Task metadata should accept title, tags, and categories."""
        skill_dir = tmp_path / ".claude" / "skills" / "owasp-security"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# OWASP\n")

        skills = {"owasp-security": str(skill_dir)}
        # Should not raise with standard metadata fields
        result = run_pre_claim_hooks(
            task_metadata={
                "title": "Encrypt user data",
                "tags": ["crypto", "security"],
                "categories": ["crypto", "auth"],
            },
            installed_skills=skills,
        )
        assert isinstance(result, list)


class TestImplementationHooks:
    """During-implementation hooks return security co-pilot notes."""

    def test_no_skills_returns_empty_list(self):
        """With no installed skills, implementation hooks return empty list."""
        result = run_implementation_hooks(
            file_paths=["src/auth/handler.py"],
            installed_skills={},
        )
        assert result == []

    def test_returns_list_of_strings(self, tmp_path):
        """Implementation hooks return a list of security note strings."""
        skill_dir = tmp_path / ".claude" / "skills" / "owasp-security"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# OWASP\n")

        skills = {"owasp-security": str(skill_dir)}
        result = run_implementation_hooks(
            file_paths=["src/auth/handler.py"],
            installed_skills=skills,
        )
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, str)

    def test_accepts_multiple_file_paths(self, tmp_path):
        """Implementation hooks accept a list of file paths."""
        skill_dir = tmp_path / ".claude" / "skills" / "owasp-security"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# OWASP\n")

        skills = {"owasp-security": str(skill_dir)}
        result = run_implementation_hooks(
            file_paths=["src/auth/handler.py", "src/crypto/aes.py", "package.json"],
            installed_skills=skills,
        )
        assert isinstance(result, list)

    def test_includes_skill_name_in_output(self, tmp_path):
        """Each security note should identify which skill produced it."""
        skill_dir = tmp_path / ".claude" / "skills" / "owasp-security"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# OWASP\n")

        skills = {"owasp-security": str(skill_dir)}
        result = run_implementation_hooks(
            file_paths=["src/auth/handler.py"],
            installed_skills=skills,
        )
        if result:
            combined = "\n".join(result)
            assert "owasp-security" in combined


class TestCompletionHooks:
    """Completion hooks return differential review findings."""

    def test_no_skills_returns_empty_list(self):
        """With no installed skills, completion hooks return empty list."""
        result = run_completion_hooks(
            git_diff="diff --git a/src/auth.py b/src/auth.py\n+password = input()",
            installed_skills={},
        )
        assert result == []

    def test_returns_list_of_strings(self, tmp_path):
        """Completion hooks return a list of finding strings."""
        skill_dir = tmp_path / ".claude" / "skills" / "trailofbits-differential-review"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Differential Review\n")

        skills = {"trailofbits-differential-review": str(skill_dir)}
        result = run_completion_hooks(
            git_diff="diff --git a/src/auth.py b/src/auth.py\n+password = input()",
            installed_skills=skills,
        )
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, str)

    def test_accepts_git_diff_string(self, tmp_path):
        """Completion hooks accept a git diff as a string."""
        skill_dir = tmp_path / ".claude" / "skills" / "trailofbits-differential-review"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Differential Review\n")

        skills = {"trailofbits-differential-review": str(skill_dir)}
        # Should not raise with a multiline diff
        result = run_completion_hooks(
            git_diff=(
                "diff --git a/src/crypto.py b/src/crypto.py\n"
                "--- a/src/crypto.py\n"
                "+++ b/src/crypto.py\n"
                "@@ -1,3 +1,5 @@\n"
                "+import hashlib\n"
                "+md5_hash = hashlib.md5(data)\n"
            ),
            installed_skills=skills,
        )
        assert isinstance(result, list)

    def test_includes_skill_name_in_output(self, tmp_path):
        """Each finding should identify which skill produced it."""
        skill_dir = tmp_path / ".claude" / "skills" / "trailofbits-differential-review"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Differential Review\n")

        skills = {"trailofbits-differential-review": str(skill_dir)}
        result = run_completion_hooks(
            git_diff="diff --git a/src/auth.py b/src/auth.py\n+password = input()",
            installed_skills=skills,
        )
        if result:
            combined = "\n".join(result)
            assert "trailofbits-differential-review" in combined


class TestHookNoOpFallback:
    """All hooks are no-ops when no external skills are installed."""

    def test_pre_claim_noop(self):
        """Pre-claim with no skills returns empty list, no errors."""
        result = run_pre_claim_hooks(
            task_metadata={"title": "anything", "tags": [], "categories": []},
            installed_skills={},
        )
        assert result == []

    def test_implementation_noop(self):
        """Implementation with no skills returns empty list, no errors."""
        result = run_implementation_hooks(
            file_paths=["anything.py"],
            installed_skills={},
        )
        assert result == []

    def test_completion_noop(self):
        """Completion with no skills returns empty list, no errors."""
        result = run_completion_hooks(
            git_diff="",
            installed_skills={},
        )
        assert result == []

    def test_hooks_do_not_affect_builtin_guidance(self):
        """External hooks are additive; they never replace built-in guidance.

        This is a design constraint test — the hook functions return
        *additional* blocks, not replacements for SPEC-063 output.
        """
        # With empty skills, all hooks return empty lists
        pre = run_pre_claim_hooks(
            task_metadata={"title": "Fix auth", "tags": ["security"], "categories": ["auth"]},
            installed_skills={},
        )
        impl = run_implementation_hooks(
            file_paths=["src/auth/handler.py"],
            installed_skills={},
        )
        comp = run_completion_hooks(
            git_diff="diff --git a/foo b/foo",
            installed_skills={},
        )
        # All empty — built-in guidance (from security_briefing.py) is unaffected
        assert pre == []
        assert impl == []
        assert comp == []


class TestSkillHookCapabilities:
    """Skills declare which hook points they support."""

    def test_skill_without_briefing_capability_skipped_in_pre_claim(self, tmp_path):
        """A skill that only supports security-review is skipped during pre-claim."""
        skill_dir = tmp_path / ".claude" / "skills" / "trailofbits-differential-review"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Differential Review\n")

        # This skill should only support completion hooks, not pre-claim
        skills = {"trailofbits-differential-review": str(skill_dir)}
        result = run_pre_claim_hooks(
            task_metadata={"title": "Fix auth", "tags": ["security"], "categories": ["auth"]},
            installed_skills=skills,
        )
        # differential-review should not produce pre-claim output
        assert result == []

    def test_skill_without_review_capability_skipped_in_completion(self, tmp_path):
        """A skill that only supports security-briefing is skipped during completion."""
        skill_dir = tmp_path / ".claude" / "skills" / "trailofbits-sharp-edges"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Sharp Edges\n")

        # sharp-edges supports pre-claim, not completion
        skills = {"trailofbits-sharp-edges": str(skill_dir)}
        result = run_completion_hooks(
            git_diff="diff --git a/foo b/foo",
            installed_skills=skills,
        )
        assert result == []
