---
source-id: "016"
title: "Raw Source — tests/ (parser, execute, inspect, amendify tests)"
type: local
path: "cognee/cognee_skills/tests/"
url: "https://github.com/topoteretes/cognee/tree/demo/graphskill_COG-4178/cognee/cognee_skills/tests"
fetched: 2026-03-15T21:10:00Z
hash: "sha256:placeholder"
---

# tests/test_parser.py

```python
"""Unit tests for the SKILL.md parser — no LLM or database required."""

from pathlib import Path
import tempfile

import pytest

from cognee.cognee_skills.parser.skill_parser import (
    parse_skill_file,
    parse_skill_folder,
    parse_skills_folder,
    _parse_frontmatter,
)

EXAMPLE_SKILLS_DIR = Path(__file__).resolve().parent.parent / "example_skills"


class TestParseFrontmatter:
    def test_basic_frontmatter(self):
        text = "---\nname: test-skill\ndescription: A test skill.\n---\n\n# Body"
        fm, body = _parse_frontmatter(text)
        assert fm["name"] == "test-skill"
        assert fm["description"] == "A test skill."
        assert body == "# Body"

    def test_multiline_description(self):
        text = "---\nname: multi\ndescription: >\n  First line\n  second line\n---\nBody text"
        fm, body = _parse_frontmatter(text)
        assert fm["name"] == "multi"
        assert "First line" in fm["description"]
        assert "second line" in fm["description"]
        assert body == "Body text"

    def test_no_frontmatter(self):
        text = "# Just a markdown file\n\nNo frontmatter here."
        fm, body = _parse_frontmatter(text)
        assert fm == {}
        assert "Just a markdown file" in body

    def test_yaml_list_tags(self):
        text = "---\nname: tagged\ntags:\n  - python\n  - testing\n  - ci\n---\n# Body"
        fm, body = _parse_frontmatter(text)
        assert fm["name"] == "tagged"
        assert fm["tags"] == ["python", "testing", "ci"]

    def test_yaml_inline_list(self):
        text = "---\nname: inline\ntags: [alpha, beta, gamma]\n---\n# Body"
        fm, body = _parse_frontmatter(text)
        assert fm["tags"] == ["alpha", "beta", "gamma"]

    def test_yaml_nested_object(self):
        text = "---\nname: nested\nconfig:\n  timeout: 30\n  retries: 3\n---\n# Body"
        fm, body = _parse_frontmatter(text)
        assert fm["config"] == {"timeout": 30, "retries": 3}

    def test_yaml_colon_in_value(self):
        text = '---\nname: colon-test\ndescription: "URL: https://example.com"\n---\n# Body'
        fm, body = _parse_frontmatter(text)
        assert fm["description"] == "URL: https://example.com"

    def test_invalid_yaml_returns_empty(self):
        text = "---\n: invalid yaml [[\n---\n# Body"
        fm, body = _parse_frontmatter(text)
        assert fm == {}
        assert body == "# Body"


class TestFieldAliases:
    """Parser accepts alternative frontmatter key names from multiple community formats."""

    def test_title_alias_for_name(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            f = Path(tmpdir) / "SKILL.md"
            f.write_text("---\ntitle: My Skill\ndescription: Does stuff.\n---\n\n# Body\n\nDo things.")
            skill = parse_skill_file(f)
            assert skill is not None
            assert skill.name == "My Skill"

    def test_summary_alias_for_description(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            f = Path(tmpdir) / "SKILL.md"
            f.write_text("---\nname: aliased\nsummary: A short summary.\n---\n\n# Body")
            skill = parse_skill_file(f)
            assert skill is not None
            assert skill.description == "A short summary."

    def test_categories_alias_for_tags(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            f = Path(tmpdir) / "SKILL.md"
            f.write_text("---\nname: tagged\ncategories:\n  - code\n  - review\n---\n\n# Body")
            skill = parse_skill_file(f)
            assert skill is not None
            assert "code" in skill.tags
            assert "review" in skill.tags

    def test_openclaw_nested_tags(self):
        """VoltAgent/OpenClaw format: metadata.openclaw.tags"""
        with tempfile.TemporaryDirectory() as tmpdir:
            f = Path(tmpdir) / "SKILL.md"
            f.write_text(
                "---\nname: openclaw-skill\nmetadata:\n  openclaw:\n    tags:\n      - ai\n      - tools\n---\n\n# Body"
            )
            skill = parse_skill_file(f)
            assert skill is not None
            assert "ai" in skill.tags
            assert "tools" in skill.tags

    def test_allowed_tools_hyphen(self):
        """Anthropic spec: allowed-tools list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            f = Path(tmpdir) / "SKILL.md"
            f.write_text(
                "---\nname: tool-skill\nallowed-tools:\n  - Read\n  - Edit\n  - Bash\n---\n\n# Body"
            )
            skill = parse_skill_file(f)
            assert skill is not None
            assert "Read" in skill.tools
            assert "Edit" in skill.tools

    def test_allowed_tools_underscore(self):
        """Alternative: allowed_tools."""
        with tempfile.TemporaryDirectory() as tmpdir:
            f = Path(tmpdir) / "SKILL.md"
            f.write_text("---\nname: tool-skill2\nallowed_tools: Read Edit Bash\n---\n\n# Body")
            skill = parse_skill_file(f)
            assert skill is not None
            assert "Read" in skill.tools


class TestDescriptionInference:
    """Description can be inferred from body when not in frontmatter."""

    def test_description_from_first_paragraph(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            f = Path(tmpdir) / "SKILL.md"
            f.write_text(
                "---\nname: no-desc\n---\n\n# Heading\n\n"
                "This is the first non-heading paragraph which is long enough to be used."
            )
            skill = parse_skill_file(f)
            assert skill is not None
            assert "first non-heading paragraph" in skill.description

    def test_description_skips_heading(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            f = Path(tmpdir) / "SKILL.md"
            f.write_text(
                "---\nname: skip-heading\n---\n\n# This is a heading\n\n"
                "This paragraph comes after the heading and should be the description."
            )
            skill = parse_skill_file(f)
            assert skill is not None
            assert "paragraph" in skill.description
            assert "heading" not in skill.description.lower().split()[0]

    def test_description_from_frontmatter_takes_priority(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            f = Path(tmpdir) / "SKILL.md"
            f.write_text(
                "---\nname: has-desc\ndescription: Explicit description.\n---\n\n"
                "This paragraph should NOT be used as description."
            )
            skill = parse_skill_file(f)
            assert skill is not None
            assert skill.description == "Explicit description."


class TestTriggerExtraction:
    """Trigger phrases extracted from multiple sources."""

    def test_triggers_from_frontmatter(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            f = Path(tmpdir) / "SKILL.md"
            f.write_text(
                "---\nname: triggered\ntriggers:\n  - summarize this\n  - compress context\n---\n\n# Body"
            )
            skill = parse_skill_file(f)
            assert skill is not None
            assert "summarize this" in skill.triggers

    def test_triggers_from_when_to_activate_section(self):
        """muratcankoylan convention: ## When to Activate section."""
        with tempfile.TemporaryDirectory() as tmpdir:
            f = Path(tmpdir) / "SKILL.md"
            f.write_text(
                "---\nname: activate-skill\n---\n\n# Description\n\n"
                "Some description text here that is long enough.\n\n"
                "## When to Activate\n\n"
                "- User asks to summarize content\n"
                "- Context window is getting large\n"
                "- Need to compress information\n\n"
                "## Other Section\n\nMore content."
            )
            skill = parse_skill_file(f)
            assert skill is not None
            assert any("summarize" in t for t in skill.triggers)
            assert any("compress" in t for t in skill.triggers)


class TestEntryFileDiscovery:
    """Parser tries multiple candidate filenames per folder."""

    def test_skill_md_uppercase(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir) / "my-skill"
            d.mkdir()
            (d / "SKILL.md").write_text("---\nname: upper\ndescription: desc\n---\n\n# Body")
            skill = parse_skill_folder(d)
            assert skill is not None
            assert skill.name == "upper"

    def test_skill_md_lowercase(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir) / "my-skill"
            d.mkdir()
            (d / "skill.md").write_text("---\nname: lower\ndescription: desc\n---\n\n# Body")
            skill = parse_skill_folder(d)
            assert skill is not None
            assert skill.name == "lower"

    def test_readme_fallback(self):
        """README.md used when no SKILL.md / skill.md present."""
        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir) / "readme-skill"
            d.mkdir()
            (d / "README.md").write_text(
                "---\nname: from-readme\ndescription: desc\n---\n\n# Body\n\nContent here."
            )
            skill = parse_skill_folder(d)
            assert skill is not None
            assert skill.name == "from-readme"

    def test_uppercase_skill_md_preferred_over_readme(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir) / "prefer-skill"
            d.mkdir()
            (d / "SKILL.md").write_text(
                "---\nname: from-skill-md\ndescription: desc\n---\n\n# Body"
            )
            (d / "README.md").write_text(
                "---\nname: from-readme\ndescription: desc\n---\n\n# Body"
            )
            skill = parse_skill_folder(d)
            assert skill is not None
            assert skill.name == "from-skill-md"

    def test_no_entry_file_returns_none(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir) / "empty-skill"
            d.mkdir()
            (d / "notes.txt").write_text("just a text file")
            skill = parse_skill_folder(d)
            assert skill is None


class TestParseSkillFile:
    def test_parse_flat_skill_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_file = Path(tmpdir) / "my-skill.md"
            skill_file.write_text(
                "---\nname: my-skill\ndescription: A flat skill.\n---\n\n# Instructions\n\nDo the thing."
            )

            skill = parse_skill_file(skill_file)
            assert skill is not None
            assert skill.skill_id == Path(tmpdir).name
            assert skill.name == "my-skill"
            assert "Do the thing" in skill.instructions

    def test_parse_flat_skill_with_custom_key(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_file = Path(tmpdir) / "my-skill.md"
            skill_file.write_text("---\nname: My Skill\ndescription: Test.\n---\n\n# Body")

            skill = parse_skill_file(skill_file, skill_key="custom-key")
            assert skill is not None
            assert skill.skill_id == "custom-key"
            assert skill.name == "My Skill"

    def test_parse_nonexistent_file(self):
        result = parse_skill_file(Path("/nonexistent/SKILL.md"))
        assert result is None


class TestParseSkillFolder:
    def test_parse_summarize(self):
        skill_dir = EXAMPLE_SKILLS_DIR / "summarize"
        if not skill_dir.exists():
            pytest.skip("example_skills/summarize not found")

        skill = parse_skill_folder(skill_dir)
        assert skill is not None
        assert skill.skill_id == "summarize"
        assert skill.name == "summarize"
        assert len(skill.description) > 0
        assert len(skill.instructions) > 0
        assert skill.content_hash != ""

    def test_parse_code_review(self):
        skill_dir = EXAMPLE_SKILLS_DIR / "code-review"
        if not skill_dir.exists():
            pytest.skip("example_skills/code-review not found")

        skill = parse_skill_folder(skill_dir)
        assert skill is not None
        assert skill.skill_id == "code-review"
        assert skill.name == "code-review"

    def test_missing_skill_md(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = parse_skill_folder(Path(tmpdir))
            assert result is None

    def test_resources_detected(self):
        skill_dir = EXAMPLE_SKILLS_DIR / "summarize"
        if not skill_dir.exists():
            pytest.skip("example_skills/summarize not found")

        skill = parse_skill_folder(skill_dir)
        assert skill is not None
        resource_names = [r.name for r in skill.resources]
        assert len(resource_names) >= 0


class TestParseSkillsFolder:
    def test_parse_all_example_skills(self):
        if not EXAMPLE_SKILLS_DIR.exists():
            pytest.skip("example_skills/ not found")

        skills = parse_skills_folder(EXAMPLE_SKILLS_DIR)
        skill_ids = {s.skill_id for s in skills}
        assert len(skills) >= 3
        assert "summarize" in skill_ids
        assert "code-review" in skill_ids
        assert "data-extraction" in skill_ids

    def test_nonexistent_folder_raises(self):
        with pytest.raises(FileNotFoundError):
            parse_skills_folder("/nonexistent/path")

    def test_empty_folder(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skills = parse_skills_folder(tmpdir)
            assert skills == []

    def test_flat_skill_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "alpha.md").write_text(
                "---\nname: Alpha\ndescription: First.\n---\n# Alpha instructions"
            )
            (root / "beta.md").write_text(
                "---\nname: Beta\ndescription: Second.\n---\n# Beta instructions"
            )

            skills = parse_skills_folder(root)
            ids = {s.skill_id for s in skills}
            assert "alpha" in ids
            assert "beta" in ids
            assert len(skills) == 2

    def test_mixed_folders_and_flat_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            sub = root / "folder-skill"
            sub.mkdir()
            (sub / "SKILL.md").write_text(
                "---\nname: Folder Skill\ndescription: In a folder.\n---\n# Body"
            )

            (root / "flat-skill.md").write_text(
                "---\nname: Flat Skill\ndescription: A flat file.\n---\n# Body"
            )

            skills = parse_skills_folder(root)
            ids = {s.skill_id for s in skills}
            assert "folder-skill" in ids
            assert "flat-skill" in ids
            assert len(skills) == 2

    def test_folder_takes_precedence_over_flat_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            sub = root / "my-skill"
            sub.mkdir()
            (sub / "SKILL.md").write_text(
                "---\nname: From Folder\ndescription: Folder version.\n---\n# Body"
            )

            (root / "my-skill.md").write_text(
                "---\nname: From Flat\ndescription: Flat version.\n---\n# Body"
            )

            skills = parse_skills_folder(root)
            assert len(skills) == 1
            assert skills[0].name == "From Folder"
```

---

# tests/test_execute.py

```python
"""Tests for cognee.cognee_skills.execute — unit tests with mocked LLM."""

import asyncio
import unittest
from unittest.mock import AsyncMock, patch, MagicMock


def _make_mock_response(content: str):
    """Build a mock litellm response."""
    msg = MagicMock()
    msg.content = content
    choice = MagicMock()
    choice.message = msg
    resp = MagicMock()
    resp.choices = [choice]
    return resp


SAMPLE_SKILL = {
    "skill_id": "summarize",
    "name": "Summarize",
    "instructions": "Condense the input into 2-3 key bullet points.",
    "instruction_summary": "Summarizes text into bullet points.",
    "description": "A summarization skill.",
    "tags": ["context-management"],
    "complexity": "simple",
    "source_path": "",
    "task_patterns": [],
}

MOCK_EVALUATION = {"score": 0.85, "reason": "Good summary"}


class TestExecuteSkill(unittest.TestCase):
    @patch("cognee.cognee_skills.execute.litellm.acompletion")
    @patch("cognee.cognee_skills.execute.get_llm_config")
    def test_execute_returns_output(self, mock_config, mock_acompletion):
        mock_config.return_value = MagicMock(llm_model="openai/gpt-4o-mini", llm_api_key="test")
        mock_acompletion.return_value = _make_mock_response("- Point 1\n- Point 2")

        from cognee.cognee_skills.execute import execute_skill

        result = asyncio.run(
            execute_skill(skill=SAMPLE_SKILL, task_text="Summarize this article about AI")
        )

        assert result["success"] is True
        assert result["output"] == "- Point 1\n- Point 2"
        assert result["skill_id"] == "summarize"
        assert result["model"] == "openai/gpt-4o-mini"
        assert result["latency_ms"] >= 0
        assert result["error"] is None

        # Verify the LLM was called with correct structure
        call_args = mock_acompletion.call_args
        messages = call_args.kwargs["messages"]
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert "Summarize" in messages[0]["content"]
        assert "Condense the input" in messages[0]["content"]
        assert messages[1]["role"] == "user"
        assert "Summarize this article about AI" in messages[1]["content"]

    @patch("cognee.cognee_skills.execute.litellm.acompletion")
    @patch("cognee.cognee_skills.execute.get_llm_config")
    def test_execute_with_context(self, mock_config, mock_acompletion):
        mock_config.return_value = MagicMock(llm_model="openai/gpt-4o-mini", llm_api_key="test")
        mock_acompletion.return_value = _make_mock_response("Done")

        from cognee.cognee_skills.execute import execute_skill

        result = asyncio.run(
            execute_skill(
                skill=SAMPLE_SKILL,
                task_text="Summarize this",
                context="The article is about quantum computing.",
            )
        )

        assert result["success"] is True
        call_args = mock_acompletion.call_args
        user_msg = call_args.kwargs["messages"][1]["content"]
        assert "quantum computing" in user_msg

    @patch("cognee.cognee_skills.execute.litellm.acompletion")
    @patch("cognee.cognee_skills.execute.get_llm_config")
    def test_execute_handles_llm_error(self, mock_config, mock_acompletion):
        mock_config.return_value = MagicMock(llm_model="openai/gpt-4o-mini", llm_api_key="test")
        mock_acompletion.side_effect = Exception("API rate limit exceeded")

        from cognee.cognee_skills.execute import execute_skill

        result = asyncio.run(execute_skill(skill=SAMPLE_SKILL, task_text="Summarize this"))

        assert result["success"] is False
        assert result["output"] == ""
        assert "rate limit" in result["error"]
        assert result["latency_ms"] >= 0

    @patch("cognee.cognee_skills.execute.litellm.acompletion")
    @patch("cognee.cognee_skills.execute.get_llm_config")
    def test_evaluate_output(self, mock_config, mock_acompletion):
        """evaluate_output scores output quality via a second LLM call."""
        mock_config.return_value = MagicMock(llm_model="openai/gpt-4o-mini", llm_api_key="test")
        mock_acompletion.return_value = _make_mock_response(
            '{"score": 0.75, "reason": "Decent but missing key points"}'
        )

        from cognee.cognee_skills.execute import evaluate_output

        result = asyncio.run(
            evaluate_output(
                skill=SAMPLE_SKILL,
                task_text="Summarize this article",
                output="Some summary text",
            )
        )

        assert result["score"] == 0.75
        assert "missing key points" in result["reason"]

    @patch("cognee.cognee_skills.execute.litellm.acompletion")
    @patch("cognee.cognee_skills.execute.get_llm_config")
    def test_evaluate_output_handles_error(self, mock_config, mock_acompletion):
        """evaluate_output returns score 1.0 on failure (optimistic fallback)."""
        mock_config.return_value = MagicMock(llm_model="openai/gpt-4o-mini", llm_api_key="test")
        mock_acompletion.side_effect = Exception("API error")

        from cognee.cognee_skills.execute import evaluate_output

        result = asyncio.run(
            evaluate_output(skill=SAMPLE_SKILL, task_text="task", output="output")
        )

        assert result["score"] == 1.0
        assert "Evaluation failed" in result["reason"]

    @patch("cognee.cognee_skills.execute.litellm.acompletion")
    @patch("cognee.cognee_skills.execute.get_llm_config")
    def test_evaluate_output_clamps_score(self, mock_config, mock_acompletion):
        """evaluate_output clamps score to [0.0, 1.0]."""
        mock_config.return_value = MagicMock(llm_model="openai/gpt-4o-mini", llm_api_key="test")
        mock_acompletion.return_value = _make_mock_response('{"score": 1.5, "reason": "great"}')

        from cognee.cognee_skills.execute import evaluate_output

        result = asyncio.run(
            evaluate_output(skill=SAMPLE_SKILL, task_text="task", output="output")
        )

        assert result["score"] == 1.0

    def test_client_execute_skill_not_found(self):
        """Client.execute returns error when skill doesn't exist."""
        from cognee.cognee_skills.client import Skills

        client = Skills()

        async def _run():
            with patch.object(client, "load", new_callable=AsyncMock, return_value=None):
                return await client.execute("nonexistent", "do something")

        result = asyncio.run(_run())

        assert result["success"] is False
        assert "not found" in result["error"]

    @patch("cognee.cognee_skills.execute.litellm.acompletion")
    @patch("cognee.cognee_skills.execute.get_llm_config")
    def test_client_execute_auto_observe(self, mock_config, mock_acompletion):
        """Client.execute auto-records the run when auto_observe=True."""
        mock_config.return_value = MagicMock(llm_model="openai/gpt-4o-mini", llm_api_key="test")
        mock_acompletion.return_value = _make_mock_response("Result text")

        from cognee.cognee_skills.client import Skills

        client = Skills()

        async def _run():
            with patch.object(client, "load", new_callable=AsyncMock, return_value=SAMPLE_SKILL):
                with patch.object(client, "_resolve_pattern", new_callable=AsyncMock, return_value="summarize:compress-text"):
                    with patch.object(client, "observe", new_callable=AsyncMock) as mock_observe:
                        with patch("cognee.cognee_skills.client.evaluate_output", new_callable=AsyncMock, return_value=MOCK_EVALUATION):
                            result = await client.execute("summarize", "do something")
                            return result, mock_observe

        result, mock_observe = asyncio.run(_run())

        assert result["success"] is True
        assert result["quality_score"] == 0.85
        mock_observe.assert_called_once()
        obs_args = mock_observe.call_args[0][0]
        assert obs_args["selected_skill_id"] == "summarize"
        assert obs_args["success_score"] == 0.85  # uses quality score, not binary
        assert obs_args["task_pattern_id"] == "summarize:compress-text"

    @patch("cognee.cognee_skills.execute.litellm.acompletion")
    @patch("cognee.cognee_skills.execute.get_llm_config")
    def test_client_execute_no_observe(self, mock_config, mock_acompletion):
        """Client.execute skips observation when auto_observe=False."""
        mock_config.return_value = MagicMock(llm_model="openai/gpt-4o-mini", llm_api_key="test")
        mock_acompletion.return_value = _make_mock_response("Result")

        from cognee.cognee_skills.client import Skills

        client = Skills()

        async def _run():
            with patch.object(client, "load", new_callable=AsyncMock, return_value=SAMPLE_SKILL):
                with patch("cognee.cognee_skills.client.evaluate_output", new_callable=AsyncMock, return_value=MOCK_EVALUATION):
                    with patch.object(client, "observe", new_callable=AsyncMock) as mock_observe:
                        result = await client.execute("summarize", "do something", auto_observe=False)
                        return result, mock_observe

        result, mock_observe = asyncio.run(_run())

        assert result["success"] is True
        assert result["quality_score"] == 0.85
        mock_observe.assert_not_called()

    @patch("cognee.cognee_skills.execute.litellm.acompletion")
    @patch("cognee.cognee_skills.execute.get_llm_config")
    def test_client_execute_no_evaluate(self, mock_config, mock_acompletion):
        """Client.execute skips evaluation when auto_evaluate=False."""
        mock_config.return_value = MagicMock(llm_model="openai/gpt-4o-mini", llm_api_key="test")
        mock_acompletion.return_value = _make_mock_response("Result")

        from cognee.cognee_skills.client import Skills

        client = Skills()

        async def _run():
            with patch.object(client, "load", new_callable=AsyncMock, return_value=SAMPLE_SKILL):
                with patch.object(client, "_resolve_pattern", new_callable=AsyncMock, return_value=""):
                    with patch.object(client, "observe", new_callable=AsyncMock) as mock_observe:
                        result = await client.execute(
                            "summarize", "do something", auto_evaluate=False
                        )
                        return result, mock_observe

        result, mock_observe = asyncio.run(_run())

        assert result["success"] is True
        assert "quality_score" not in result
        # Without evaluation, observe uses binary score
        obs_args = mock_observe.call_args[0][0]
        assert obs_args["success_score"] == 1.0

    @patch("cognee.cognee_skills.execute.litellm.acompletion")
    @patch("cognee.cognee_skills.execute.get_llm_config")
    def test_client_execute_auto_amendify_on_failure(self, mock_config, mock_acompletion):
        """Client.execute triggers auto_amendify when execution fails and auto_amendify=True."""
        mock_config.return_value = MagicMock(llm_model="openai/gpt-4o-mini", llm_api_key="test")
        mock_acompletion.side_effect = Exception("LLM error")

        from cognee.cognee_skills.client import Skills

        client = Skills()

        amendify_result = {
            "inspection": {"inspection_id": "i1", "root_cause": "bad instructions"},
            "amendment": {"amendment_id": "a1", "status": "proposed"},
            "applied": {"success": True, "status": "applied"},
        }

        async def _run():
            with patch.object(client, "load", new_callable=AsyncMock, return_value=SAMPLE_SKILL):
                with patch.object(client, "_resolve_pattern", new_callable=AsyncMock, return_value=""):
                    with patch.object(client, "observe", new_callable=AsyncMock):
                        with patch.object(
                            client,
                            "auto_amendify",
                            new_callable=AsyncMock,
                            return_value=amendify_result,
                        ) as mock_amendify:
                            result = await client.execute(
                                "summarize",
                                "do something",
                                auto_amendify=True,
                                amendify_min_runs=1,
                            )
                            return result, mock_amendify

        result, mock_amendify = asyncio.run(_run())

        assert result["success"] is False
        assert result["amended"] is not None
        assert result["amended"]["applied"]["success"] is True
        mock_amendify.assert_called_once()

    @patch("cognee.cognee_skills.execute.litellm.acompletion")
    @patch("cognee.cognee_skills.execute.get_llm_config")
    def test_client_execute_auto_amendify_on_low_quality(self, mock_config, mock_acompletion):
        """Client.execute triggers auto_amendify when quality score is below threshold."""
        mock_config.return_value = MagicMock(llm_model="openai/gpt-4o-mini", llm_api_key="test")
        mock_acompletion.return_value = _make_mock_response("Bad output")

        from cognee.cognee_skills.client import Skills

        client = Skills()

        low_eval = {"score": 0.2, "reason": "Off-topic"}
        amendify_result = {
            "inspection": {"inspection_id": "i1", "root_cause": "bad instructions"},
            "amendment": {"amendment_id": "a1", "status": "proposed"},
            "applied": {"success": True, "status": "applied"},
        }

        async def _run():
            with patch.object(client, "load", new_callable=AsyncMock, return_value=SAMPLE_SKILL):
                with patch.object(client, "_resolve_pattern", new_callable=AsyncMock, return_value=""):
                    with patch.object(client, "observe", new_callable=AsyncMock):
                        with patch("cognee.cognee_skills.client.evaluate_output", new_callable=AsyncMock, return_value=low_eval):
                            with patch.object(
                                client,
                                "auto_amendify",
                                new_callable=AsyncMock,
                                return_value=amendify_result,
                            ) as mock_amendify:
                                result = await client.execute(
                                    "summarize",
                                    "do something",
                                    auto_amendify=True,
                                    amendify_min_runs=1,
                                )
                                return result, mock_amendify

        result, mock_amendify = asyncio.run(_run())

        assert result["success"] is True  # LLM didn't error
        assert result["quality_score"] == 0.2  # but quality is low
        assert result["amended"] is not None  # so amendify triggers
        mock_amendify.assert_called_once()

    @patch("cognee.cognee_skills.execute.litellm.acompletion")
    @patch("cognee.cognee_skills.execute.get_llm_config")
    def test_client_execute_auto_amendify_skipped_on_success(self, mock_config, mock_acompletion):
        """Client.execute does NOT trigger auto_amendify when quality is high."""
        mock_config.return_value = MagicMock(llm_model="openai/gpt-4o-mini", llm_api_key="test")
        mock_acompletion.return_value = _make_mock_response("Success")

        from cognee.cognee_skills.client import Skills

        client = Skills()

        async def _run():
            with patch.object(client, "load", new_callable=AsyncMock, return_value=SAMPLE_SKILL):
                with patch.object(client, "_resolve_pattern", new_callable=AsyncMock, return_value=""):
                    with patch.object(client, "observe", new_callable=AsyncMock):
                        with patch("cognee.cognee_skills.client.evaluate_output", new_callable=AsyncMock, return_value=MOCK_EVALUATION):
                            with patch.object(
                                client, "auto_amendify", new_callable=AsyncMock
                            ) as mock_amendify:
                                result = await client.execute(
                                    "summarize", "do something", auto_amendify=True
                                )
                                return result, mock_amendify

        result, mock_amendify = asyncio.run(_run())

        assert result["success"] is True
        assert result["quality_score"] == 0.85
        assert "amended" not in result
        mock_amendify.assert_not_called()

    def test_client_auto_amendify_returns_none_no_failures(self):
        """auto_amendify returns None when there aren't enough failed runs."""
        from cognee.cognee_skills.client import Skills

        client = Skills()

        async def _run():
            with patch.object(client, "inspect", new_callable=AsyncMock, return_value=None):
                return await client.auto_amendify("summarize")

        result = asyncio.run(_run())
        assert result is None

    def test_client_auto_amendify_full_pipeline(self):
        """auto_amendify chains inspect → preview_amendify → amendify."""
        from cognee.cognee_skills.client import Skills

        client = Skills()

        mock_inspection = {
            "inspection_id": "i1",
            "skill_id": "summarize",
            "skill_name": "Summarize",
            "failure_category": "instruction_gap",
            "root_cause": "Missing details",
            "severity": "high",
            "improvement_hypothesis": "Add more detail",
            "analyzed_run_count": 3,
            "avg_success_score": 0.2,
            "inspection_confidence": 0.9,
        }
        mock_amendment = {
            "amendment_id": "a1",
            "skill_id": "summarize",
            "skill_name": "Summarize",
            "inspection_id": "i1",
            "change_explanation": "Added detail",
            "expected_improvement": "Better output",
            "status": "proposed",
            "amendment_confidence": 0.8,
            "pre_amendment_avg_score": 0.2,
        }
        mock_apply = {"success": True, "status": "applied", "amendment_id": "a1"}

        async def _run():
            with patch.object(
                client, "inspect", new_callable=AsyncMock, return_value=mock_inspection
            ):
                with patch.object(
                    client,
                    "preview_amendify",
                    new_callable=AsyncMock,
                    return_value=mock_amendment,
                ) as mock_pa:
                    with patch.object(
                        client,
                        "amendify",
                        new_callable=AsyncMock,
                        return_value=mock_apply,
                    ) as mock_am:
                        result = await client.auto_amendify("summarize", min_runs=1)
                        return result, mock_pa, mock_am

        result, mock_pa, mock_am = asyncio.run(_run())

        assert result["inspection"]["inspection_id"] == "i1"
        assert result["amendment"]["amendment_id"] == "a1"
        assert result["applied"]["success"] is True
        mock_pa.assert_called_once_with(skill_id="summarize", inspection_id="i1", node_set="skills")
        mock_am.assert_called_once_with(
            amendment_id="a1",
            write_to_disk=False,
            validate=False,
            validation_task_text="",
            node_set="skills",
        )


if __name__ == "__main__":
    unittest.main()
```

---

# tests/test_inspect.py

```python
"""Tests for cognee.cognee_skills.inspect — unit tests with mocked LLM + graph."""

import asyncio
import unittest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4

from cognee.cognee_skills.models.skill_inspection import InspectionResult


def _make_skill_node(skill_id="test-skill", name="Test Skill"):
    nid = uuid4()
    props = {
        "type": "Skill",
        "skill_id": skill_id,
        "name": name,
        "instructions": "Do the thing step by step.",
        "content_hash": "abc123",
    }
    return (nid, props)


def _make_failed_run(skill_id="test-skill", score=0.2, run_id=None, error_type="llm_error"):
    nid = uuid4()
    props = {
        "type": "SkillRun",
        "run_id": run_id or str(uuid4()),
        "selected_skill_id": skill_id,
        "success_score": score,
        "task_text": "Summarize this document",
        "error_type": error_type,
        "error_message": "Model failed to follow instructions",
        "result_summary": "Incomplete output",
    }
    return (nid, props)


MOCK_INSPECTION_RESULT = InspectionResult(
    failure_category="instruction_gap",
    root_cause="Instructions lack detail on edge cases",
    severity="high",
    improvement_hypothesis="Add examples for edge cases in the instructions",
    confidence=0.85,
)


class TestInspectSkill(unittest.TestCase):
    @patch("cognee.cognee_skills.inspect.add_data_points", new_callable=AsyncMock)
    @patch("cognee.cognee_skills.inspect.get_llm_config")
    @patch("cognee.cognee_skills.inspect.LLMGateway.acreate_structured_output", new_callable=AsyncMock)
    @patch("cognee.cognee_skills.inspect.get_graph_engine", new_callable=AsyncMock)
    def test_inspect_returns_inspection(self, mock_engine_fn, mock_llm, mock_config, mock_add_dp):
        skill_node = _make_skill_node()
        run1 = _make_failed_run(score=0.1)
        run2 = _make_failed_run(score=0.3)

        engine = AsyncMock()
        engine.get_nodeset_subgraph = AsyncMock(return_value=([skill_node, run1, run2], []))
        mock_engine_fn.return_value = engine
        mock_llm.return_value = MOCK_INSPECTION_RESULT
        mock_config.return_value = MagicMock(llm_model="openai/gpt-4o-mini")

        from cognee.cognee_skills.inspect import inspect_skill

        result = asyncio.run(inspect_skill("test-skill", min_runs=1))

        assert result is not None
        assert result.skill_id == "test-skill"
        assert result.failure_category == "instruction_gap"
        assert result.severity == "high"
        assert result.analyzed_run_count == 2
        assert result.avg_success_score == 0.2
        assert result.inspection_confidence == 0.85
        mock_add_dp.assert_called_once()

    @patch("cognee.cognee_skills.inspect.get_graph_engine", new_callable=AsyncMock)
    def test_inspect_no_failed_runs(self, mock_engine_fn):
        skill_node = _make_skill_node()

        engine = AsyncMock()
        engine.get_nodeset_subgraph = AsyncMock(return_value=([skill_node], []))
        mock_engine_fn.return_value = engine

        from cognee.cognee_skills.inspect import inspect_skill

        result = asyncio.run(inspect_skill("test-skill", min_runs=1))

        assert result is None

    @patch("cognee.cognee_skills.inspect.add_data_points", new_callable=AsyncMock)
    @patch("cognee.cognee_skills.inspect.get_llm_config")
    @patch("cognee.cognee_skills.inspect.LLMGateway.acreate_structured_output", new_callable=AsyncMock)
    @patch("cognee.cognee_skills.inspect.get_graph_engine", new_callable=AsyncMock)
    def test_inspect_aggregates_multiple_runs(
        self, mock_engine_fn, mock_llm, mock_config, mock_add_dp
    ):
        skill_node = _make_skill_node()
        runs = [_make_failed_run(score=0.1 * i, run_id=f"run-{i}") for i in range(5)]

        engine = AsyncMock()
        engine.get_nodeset_subgraph = AsyncMock(return_value=([skill_node] + runs, []))
        mock_engine_fn.return_value = engine
        mock_llm.return_value = MOCK_INSPECTION_RESULT
        mock_config.return_value = MagicMock(llm_model="openai/gpt-4o-mini")

        from cognee.cognee_skills.inspect import inspect_skill

        result = asyncio.run(inspect_skill("test-skill", min_runs=1))

        assert result is not None
        assert result.analyzed_run_count == 5
        assert len(result.analyzed_run_ids) == 5

    @patch("cognee.cognee_skills.inspect.get_graph_engine", new_callable=AsyncMock)
    def test_inspect_insufficient_runs(self, mock_engine_fn):
        skill_node = _make_skill_node()
        run1 = _make_failed_run(score=0.2)

        engine = AsyncMock()
        engine.get_nodeset_subgraph = AsyncMock(return_value=([skill_node, run1], []))
        mock_engine_fn.return_value = engine

        from cognee.cognee_skills.inspect import inspect_skill

        # Requires 3 runs but only 1 exists
        result = asyncio.run(inspect_skill("test-skill", min_runs=3))

        assert result is None


if __name__ == "__main__":
    unittest.main()
```

---

# tests/test_amendify.py

```python
"""Tests for cognee.cognee_skills.amendify — unit tests with mocked graph engine."""

import asyncio
import unittest
from unittest.mock import AsyncMock, patch, MagicMock, call
from uuid import uuid4


def _make_amendment_node(amendment_id="amend-001", status="proposed"):
    nid = uuid4()
    props = {
        "type": "SkillAmendment",
        "nid": str(nid),
        "id": str(nid),
        "amendment_id": amendment_id,
        "skill_id": "test-skill",
        "skill_name": "Test Skill",
        "inspection_id": "insp-001",
        "original_instructions": "Do the thing step by step.",
        "amended_instructions": "Do the thing step by step.\n\nAlso handle edge cases.",
        "change_explanation": "Added edge case handling",
        "expected_improvement": "Fewer failures on edge cases",
        "status": status,
        "pre_amendment_avg_score": 0.2,
        "amendment_model": "",
        "amendment_confidence": 0.0,
        "applied_at_ms": 0,
        "post_amendment_avg_score": 0.0,
        "post_amendment_run_count": 0,
    }
    return (nid, props)


def _make_skill_node(skill_id="test-skill"):
    nid = uuid4()
    props = {
        "type": "Skill",
        "id": str(nid),
        "skill_id": skill_id,
        "name": "Test Skill",
        "description": "A test skill.",
        "instructions": "Do the thing step by step.",
        "instruction_summary": "Does the thing.",
        "content_hash": "abc123",
        "source_path": "",
        "tags": [],
        "complexity": "simple",
    }
    return (nid, props)


class TestAmendify(unittest.TestCase):
    @patch("cognee.cognee_skills.amendify.add_data_points", new_callable=AsyncMock)
    @patch("cognee.cognee_skills.amendify._make_change_event")
    @patch("cognee.cognee_skills.amendify.get_graph_engine", new_callable=AsyncMock)
    @patch("cognee.cognee_skills.tasks.enrich_skills.enrich_skills", new_callable=AsyncMock)
    @patch(
        "cognee.cognee_skills.tasks.materialize_task_patterns.materialize_task_patterns",
        new_callable=AsyncMock,
    )
    def test_amendify_updates_skill(
        self, mock_mat, mock_enrich, mock_engine_fn, mock_event, mock_add_dp
    ):
        amendment_node = _make_amendment_node()
        skill_node = _make_skill_node()

        engine = AsyncMock()
        engine.get_nodeset_subgraph = AsyncMock(return_value=([amendment_node, skill_node], []))
        mock_engine_fn.return_value = engine

        mock_event.return_value = MagicMock()
        mock_enrich.return_value = []

        from cognee.cognee_skills.amendify import amendify

        result = asyncio.run(amendify("amend-001"))

        assert result["success"] is True
        assert result["status"] == "applied"
        assert result["skill_id"] == "test-skill"

        # Verify add_data_points was called (skill update + change event + amendment status)
        assert mock_add_dp.call_count >= 3

    @patch("cognee.cognee_skills.amendify.add_data_points", new_callable=AsyncMock)
    @patch("cognee.cognee_skills.amendify._make_change_event")
    @patch("cognee.cognee_skills.amendify.get_graph_engine", new_callable=AsyncMock)
    @patch("cognee.cognee_skills.tasks.enrich_skills.enrich_skills", new_callable=AsyncMock)
    @patch(
        "cognee.cognee_skills.tasks.materialize_task_patterns.materialize_task_patterns",
        new_callable=AsyncMock,
    )
    def test_amendify_emits_change_event(
        self, mock_mat, mock_enrich, mock_engine_fn, mock_event, mock_add_dp
    ):
        amendment_node = _make_amendment_node()
        skill_node = _make_skill_node()

        engine = AsyncMock()
        engine.get_nodeset_subgraph = AsyncMock(return_value=([amendment_node, skill_node], []))
        mock_engine_fn.return_value = engine

        event_obj = MagicMock()
        mock_event.return_value = event_obj
        mock_enrich.return_value = []

        from cognee.cognee_skills.amendify import amendify

        asyncio.run(amendify("amend-001"))

        # Verify change event was created with change_type="amended"
        mock_event.assert_called_once()
        call_kwargs = mock_event.call_args
        assert call_kwargs[0][2] == "amended"  # change_type arg
        # Verify the event was persisted
        mock_add_dp.assert_called()

    @patch("cognee.cognee_skills.amendify.add_data_points", new_callable=AsyncMock)
    @patch("cognee.cognee_skills.amendify._make_change_event")
    @patch("cognee.cognee_skills.amendify.get_graph_engine", new_callable=AsyncMock)
    @patch("cognee.cognee_skills.tasks.enrich_skills.enrich_skills", new_callable=AsyncMock)
    @patch(
        "cognee.cognee_skills.tasks.materialize_task_patterns.materialize_task_patterns",
        new_callable=AsyncMock,
    )
    def test_rollback_restores_original(
        self, mock_mat, mock_enrich, mock_engine_fn, mock_event, mock_add_dp
    ):
        amendment_node = _make_amendment_node(status="applied")
        skill_node = _make_skill_node()

        engine = AsyncMock()
        engine.get_nodeset_subgraph = AsyncMock(return_value=([amendment_node, skill_node], []))
        mock_engine_fn.return_value = engine

        mock_event.return_value = MagicMock()
        mock_enrich.return_value = []

        from cognee.cognee_skills.amendify import rollback_amendify

        result = asyncio.run(rollback_amendify("amend-001"))

        assert result is True

        # Verify change event was emitted with rolled_back type
        mock_event.assert_called_once()
        assert mock_event.call_args[0][2] == "rolled_back"

        # Verify add_data_points was called (skill restore + event + amendment status)
        assert mock_add_dp.call_count >= 3

    @patch("cognee.cognee_skills.amendify.get_graph_engine", new_callable=AsyncMock)
    def test_rollback_fails_for_non_applied_amendment(self, mock_engine_fn):
        amendment_node = _make_amendment_node(status="proposed")

        engine = AsyncMock()
        engine.get_nodeset_subgraph = AsyncMock(return_value=([amendment_node], []))
        mock_engine_fn.return_value = engine

        from cognee.cognee_skills.amendify import rollback_amendify

        result = asyncio.run(rollback_amendify("amend-001"))

        assert result is False

    @patch("cognee.cognee_skills.amendify.get_graph_engine", new_callable=AsyncMock)
    def test_amendify_not_found(self, mock_engine_fn):
        engine = AsyncMock()
        engine.get_nodeset_subgraph = AsyncMock(return_value=([], []))
        mock_engine_fn.return_value = engine

        from cognee.cognee_skills.amendify import amendify

        result = asyncio.run(amendify("nonexistent"))

        assert result["success"] is False
        assert "not found" in result["error"]

    @patch("cognee.cognee_skills.amendify.get_graph_engine", new_callable=AsyncMock)
    def test_amendify_rejects_already_applied(self, mock_engine_fn):
        """Cannot apply an amendment that's already been applied."""
        amendment_node = _make_amendment_node(status="applied")

        engine = AsyncMock()
        engine.get_nodeset_subgraph = AsyncMock(return_value=([amendment_node], []))
        mock_engine_fn.return_value = engine

        from cognee.cognee_skills.amendify import amendify

        result = asyncio.run(amendify("amend-001"))

        assert result["success"] is False
        assert "applied" in result["error"]

    @patch("cognee.cognee_skills.amendify.add_data_points", new_callable=AsyncMock)
    @patch("cognee.cognee_skills.amendify.get_graph_engine", new_callable=AsyncMock)
    def test_evaluate_amendify(self, mock_engine_fn, mock_add_dp):
        """evaluate_amendify computes post-amendment stats from runs after applied_at_ms."""
        amendment_node = _make_amendment_node(status="applied")
        # Add applied_at_ms to amendment
        amendment_node[1]["applied_at_ms"] = 1000

        # Runs: one before amendment (should be excluded), two after
        pre_run = (
            uuid4(),
            {
                "type": "SkillRun",
                "selected_skill_id": "test-skill",
                "success_score": 0.1,
                "started_at_ms": 500,
            },
        )
        post_run1 = (
            uuid4(),
            {
                "type": "SkillRun",
                "selected_skill_id": "test-skill",
                "success_score": 0.8,
                "started_at_ms": 2000,
            },
        )
        post_run2 = (
            uuid4(),
            {
                "type": "SkillRun",
                "selected_skill_id": "test-skill",
                "success_score": 0.9,
                "started_at_ms": 3000,
            },
        )

        engine = AsyncMock()
        engine.get_nodeset_subgraph = AsyncMock(
            return_value=([amendment_node, pre_run, post_run1, post_run2], [])
        )
        mock_engine_fn.return_value = engine

        from cognee.cognee_skills.amendify import evaluate_amendify

        result = asyncio.run(evaluate_amendify("amend-001"))

        assert result["run_count"] == 2
        assert abs(result["post_avg"] - 0.85) < 0.01
        assert result["improvement"] > 0
        assert result["recommendation"] == "keep"

        # Verify amendment stats were persisted via add_data_points
        mock_add_dp.assert_called_once()


if __name__ == "__main__":
    unittest.main()
```
