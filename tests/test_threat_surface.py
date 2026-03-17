"""Tests for threat surface detection heuristic (SPEC-062).

TDD RED phase: all tests written before implementation.
"""

import sys
from pathlib import Path

# Add the module to the path so we can import it
sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "swain-security-check" / "scripts"))

from threat_surface import detect_threat_surface, ThreatSurfaceResult


# ---------------------------------------------------------------------------
# Task 1 (aa-2t3i): Keyword-based threat surface detection
# ---------------------------------------------------------------------------

class TestTitleKeywordDetection:
    """Title keywords should trigger security-sensitive detection."""

    def test_jwt_token_validation(self):
        """'Add JWT token validation middleware' -> true, category: auth."""
        result = detect_threat_surface(title="Add JWT token validation middleware")
        assert result.is_security_sensitive is True
        assert "auth" in result.categories

    def test_login_keyword(self):
        result = detect_threat_surface(title="Fix login flow for mobile users")
        assert result.is_security_sensitive is True
        assert "auth" in result.categories

    def test_password_keyword(self):
        result = detect_threat_surface(title="Implement password reset endpoint")
        assert result.is_security_sensitive is True
        assert "auth" in result.categories

    def test_secret_keyword(self):
        result = detect_threat_surface(title="Rotate API secret keys")
        assert result.is_security_sensitive is True
        assert "secrets" in result.categories

    def test_encrypt_keyword(self):
        result = detect_threat_surface(title="Encrypt data at rest")
        assert result.is_security_sensitive is True
        assert "crypto" in result.categories

    def test_certificate_keyword(self):
        result = detect_threat_surface(title="Renew TLS certificate")
        assert result.is_security_sensitive is True
        assert "crypto" in result.categories

    def test_permission_keyword(self):
        result = detect_threat_surface(title="Add permission checks for admin routes")
        assert result.is_security_sensitive is True
        assert "auth" in result.categories

    def test_role_keyword(self):
        result = detect_threat_surface(title="Implement role-based access control")
        assert result.is_security_sensitive is True
        assert "auth" in result.categories

    def test_sanitize_keyword(self):
        result = detect_threat_surface(title="Sanitize HTML input in comments")
        assert result.is_security_sensitive is True
        assert "input-validation" in result.categories

    def test_validate_keyword(self):
        result = detect_threat_surface(title="Validate email format on registration")
        assert result.is_security_sensitive is True
        assert "input-validation" in result.categories

    def test_escape_keyword(self):
        result = detect_threat_surface(title="Escape SQL parameters in query builder")
        assert result.is_security_sensitive is True
        assert "input-validation" in result.categories

    def test_key_keyword(self):
        result = detect_threat_surface(title="Generate API key for service auth")
        assert result.is_security_sensitive is True
        # "key" can match auth or secrets depending on context; accept either
        assert "auth" in result.categories or "secrets" in result.categories

    def test_auth_keyword(self):
        result = detect_threat_surface(title="Refactor auth middleware")
        assert result.is_security_sensitive is True
        assert "auth" in result.categories

    def test_token_keyword(self):
        result = detect_threat_surface(title="Refresh token rotation")
        assert result.is_security_sensitive is True
        assert "auth" in result.categories

    def test_case_insensitive(self):
        """Keywords should match case-insensitively."""
        result = detect_threat_surface(title="Update PASSWORD hashing algorithm")
        assert result.is_security_sensitive is True
        assert "auth" in result.categories

    def test_non_security_title(self):
        """'Update README formatting' -> false."""
        result = detect_threat_surface(title="Update README formatting")
        assert result.is_security_sensitive is False
        assert result.categories == []

    def test_non_security_ui_task(self):
        result = detect_threat_surface(title="Fix button alignment on dashboard")
        assert result.is_security_sensitive is False
        assert result.categories == []

    def test_non_security_refactor(self):
        result = detect_threat_surface(title="Refactor database connection pooling")
        assert result.is_security_sensitive is False
        assert result.categories == []

    def test_multiple_keywords_dedup_categories(self):
        """Multiple auth keywords should not duplicate the category."""
        result = detect_threat_surface(title="Add login and password auth flow")
        assert result.is_security_sensitive is True
        assert result.categories.count("auth") == 1

    def test_multiple_categories(self):
        """A title with keywords from multiple categories returns all of them."""
        result = detect_threat_surface(title="Encrypt token and sanitize input")
        assert result.is_security_sensitive is True
        assert "crypto" in result.categories
        assert "auth" in result.categories
        assert "input-validation" in result.categories


# ---------------------------------------------------------------------------
# Task 2 (aa-grtp): Tag-based and SPEC-criteria detection
# ---------------------------------------------------------------------------

class TestTagBasedDetection:
    """Task tags should trigger security-sensitive detection."""

    def test_security_tag(self):
        """Task with tag 'security' -> true regardless of title."""
        result = detect_threat_surface(
            title="Update README formatting",
            tags=["security"],
        )
        assert result.is_security_sensitive is True

    def test_auth_tag(self):
        result = detect_threat_surface(
            title="Refactor module structure",
            tags=["auth"],
        )
        assert result.is_security_sensitive is True
        assert "auth" in result.categories

    def test_crypto_tag(self):
        result = detect_threat_surface(
            title="Update library version",
            tags=["crypto"],
        )
        assert result.is_security_sensitive is True
        assert "crypto" in result.categories

    def test_input_validation_tag(self):
        result = detect_threat_surface(
            title="Fix form handler",
            tags=["input-validation"],
        )
        assert result.is_security_sensitive is True
        assert "input-validation" in result.categories

    def test_non_security_tags(self):
        """Non-security tags should not trigger detection."""
        result = detect_threat_surface(
            title="Update README formatting",
            tags=["docs", "frontend", "cleanup"],
        )
        assert result.is_security_sensitive is False

    def test_mixed_tags(self):
        """Security tag among non-security tags should trigger."""
        result = detect_threat_surface(
            title="Update docs",
            tags=["docs", "security", "cleanup"],
        )
        assert result.is_security_sensitive is True

    def test_empty_tags(self):
        result = detect_threat_surface(title="Update README", tags=[])
        assert result.is_security_sensitive is False

    def test_none_tags(self):
        result = detect_threat_surface(title="Update README", tags=None)
        assert result.is_security_sensitive is False

    def test_tag_and_keyword_combine(self):
        """Both tag and keyword signals detected, no category duplication."""
        result = detect_threat_surface(
            title="Fix auth middleware",
            tags=["auth"],
        )
        assert result.is_security_sensitive is True
        assert result.categories.count("auth") == 1


class TestSpecCriteriaDetection:
    """SPEC acceptance criteria keywords should trigger detection."""

    def test_sanitize_in_criteria(self):
        """SPEC mentioning 'sanitize user input' -> true, category: input-validation."""
        result = detect_threat_surface(
            title="Implement form handler",
            spec_criteria="Must sanitize user input before storing",
        )
        assert result.is_security_sensitive is True
        assert "input-validation" in result.categories

    def test_token_in_criteria(self):
        result = detect_threat_surface(
            title="Add API endpoint",
            spec_criteria="Endpoint must validate bearer token",
        )
        assert result.is_security_sensitive is True
        assert "auth" in result.categories

    def test_encrypt_in_criteria(self):
        result = detect_threat_surface(
            title="Store user data",
            spec_criteria="All PII must be encrypted at rest",
        )
        assert result.is_security_sensitive is True
        assert "crypto" in result.categories

    def test_password_in_criteria(self):
        result = detect_threat_surface(
            title="User registration flow",
            spec_criteria="Password must be hashed with bcrypt before storage",
        )
        assert result.is_security_sensitive is True
        assert "auth" in result.categories

    def test_non_security_criteria(self):
        result = detect_threat_surface(
            title="Add dashboard widget",
            spec_criteria="Widget must display latest metrics and refresh every 30 seconds",
        )
        assert result.is_security_sensitive is False

    def test_criteria_case_insensitive(self):
        result = detect_threat_surface(
            title="Update user flow",
            spec_criteria="VALIDATE all form fields before submission",
        )
        assert result.is_security_sensitive is True
        assert "input-validation" in result.categories

    def test_criteria_only_no_title_match(self):
        """Security detected from criteria even when title is benign."""
        result = detect_threat_surface(
            title="Update form handler",
            spec_criteria="Must escape all HTML entities to prevent XSS",
        )
        assert result.is_security_sensitive is True
        assert "input-validation" in result.categories


# ---------------------------------------------------------------------------
# Task 3 (aa-wp4f): File-path-based detection and false positive rate
# ---------------------------------------------------------------------------

class TestFilePathDetection:
    """File paths should trigger security-sensitive detection."""

    def test_auth_directory(self):
        result = detect_threat_surface(
            title="Refactor module",
            file_paths=["src/auth/handler.py"],
        )
        assert result.is_security_sensitive is True
        assert "auth" in result.categories

    def test_crypto_directory(self):
        result = detect_threat_surface(
            title="Update utils",
            file_paths=["lib/crypto/aes.py"],
        )
        assert result.is_security_sensitive is True
        assert "crypto" in result.categories

    def test_middleware_auth(self):
        result = detect_threat_surface(
            title="Fix middleware",
            file_paths=["src/middleware/auth.py"],
        )
        assert result.is_security_sensitive is True
        assert "auth" in result.categories

    def test_env_file(self):
        result = detect_threat_surface(
            title="Update config",
            file_paths=[".env"],
        )
        assert result.is_security_sensitive is True
        assert "secrets" in result.categories

    def test_env_local_file(self):
        result = detect_threat_surface(
            title="Update config",
            file_paths=[".env.local"],
        )
        assert result.is_security_sensitive is True
        assert "secrets" in result.categories

    def test_credentials_file(self):
        result = detect_threat_surface(
            title="Update config",
            file_paths=["config/credentials.json"],
        )
        assert result.is_security_sensitive is True
        assert "secrets" in result.categories

    def test_secret_in_filename(self):
        result = detect_threat_surface(
            title="Update config",
            file_paths=["deploy/secret-values.yaml"],
        )
        assert result.is_security_sensitive is True
        assert "secrets" in result.categories

    def test_package_json(self):
        """Task modifying package.json -> true, category: dependency-change."""
        result = detect_threat_surface(
            title="Update dependencies",
            file_paths=["package.json"],
        )
        assert result.is_security_sensitive is True
        assert "dependency-change" in result.categories

    def test_package_lock_json(self):
        result = detect_threat_surface(
            title="Update lockfile",
            file_paths=["package-lock.json"],
        )
        assert result.is_security_sensitive is True
        assert "dependency-change" in result.categories

    def test_requirements_txt(self):
        result = detect_threat_surface(
            title="Update Python deps",
            file_paths=["requirements.txt"],
        )
        assert result.is_security_sensitive is True
        assert "dependency-change" in result.categories

    def test_pyproject_toml(self):
        result = detect_threat_surface(
            title="Update build config",
            file_paths=["pyproject.toml"],
        )
        assert result.is_security_sensitive is True
        assert "dependency-change" in result.categories

    def test_go_mod(self):
        result = detect_threat_surface(
            title="Update Go deps",
            file_paths=["go.mod"],
        )
        assert result.is_security_sensitive is True
        assert "dependency-change" in result.categories

    def test_non_security_paths(self):
        result = detect_threat_surface(
            title="Update styles",
            file_paths=["src/components/Button.tsx", "src/styles/main.css"],
        )
        assert result.is_security_sensitive is False

    def test_empty_paths(self):
        result = detect_threat_surface(
            title="Update README", file_paths=[]
        )
        assert result.is_security_sensitive is False

    def test_none_paths(self):
        result = detect_threat_surface(
            title="Update README", file_paths=None
        )
        assert result.is_security_sensitive is False

    def test_multiple_paths_one_security(self):
        """One security-relevant path among many should trigger."""
        result = detect_threat_surface(
            title="Large refactor",
            file_paths=[
                "src/components/Header.tsx",
                "src/auth/login.py",
                "src/utils/format.py",
            ],
        )
        assert result.is_security_sensitive is True
        assert "auth" in result.categories

    def test_nested_auth_path(self):
        result = detect_threat_surface(
            title="Fix handler",
            file_paths=["src/api/v2/auth/oauth.py"],
        )
        assert result.is_security_sensitive is True
        assert "auth" in result.categories

    def test_description_keyword_detection(self):
        """Description text should also be scanned for keywords."""
        result = detect_threat_surface(
            title="Fix handler",
            description="This handler needs to validate the authentication token",
        )
        assert result.is_security_sensitive is True


class TestFalsePositiveRate:
    """False positive rate must be < 20% on non-security tasks.

    We define a corpus of 20 clearly non-security tasks and verify that
    no more than 4 (20%) are incorrectly flagged as security-sensitive.
    """

    NON_SECURITY_TASKS = [
        {"title": "Update README formatting"},
        {"title": "Fix CSS alignment on homepage"},
        {"title": "Add loading spinner to dashboard"},
        {"title": "Refactor database connection pooling"},
        {"title": "Improve search result pagination"},
        {"title": "Add unit tests for date formatter"},
        {"title": "Update copyright year in footer"},
        {"title": "Fix broken image link in about page"},
        {"title": "Add dark mode toggle"},
        {"title": "Optimize SQL query for user listing"},
        {"title": "Fix typo in error message"},
        {"title": "Add CSV export for reports"},
        {"title": "Improve mobile navigation menu"},
        {"title": "Add breadcrumb component"},
        {"title": "Fix timezone handling in scheduler"},
        {"title": "Update color scheme per design spec"},
        {"title": "Add table sorting functionality"},
        {"title": "Fix memory leak in WebSocket handler"},
        {"title": "Improve build speed with caching"},
        {"title": "Add integration test for order flow"},
    ]

    def test_false_positive_rate_under_20_percent(self):
        false_positives = 0
        for task in self.NON_SECURITY_TASKS:
            result = detect_threat_surface(title=task["title"])
            if result.is_security_sensitive:
                false_positives += 1

        max_allowed = len(self.NON_SECURITY_TASKS) * 0.20
        assert false_positives <= max_allowed, (
            f"False positive rate too high: {false_positives}/{len(self.NON_SECURITY_TASKS)} "
            f"({false_positives / len(self.NON_SECURITY_TASKS) * 100:.0f}%) exceeds 20% threshold"
        )


class TestReturnType:
    """ThreatSurfaceResult should have the expected structure."""

    def test_result_has_required_fields(self):
        result = detect_threat_surface(title="anything")
        assert hasattr(result, "is_security_sensitive")
        assert hasattr(result, "categories")
        assert isinstance(result.is_security_sensitive, bool)
        assert isinstance(result.categories, list)

    def test_result_default_is_not_sensitive(self):
        result = ThreatSurfaceResult()
        assert result.is_security_sensitive is False
        assert result.categories == []

    def test_categories_are_strings(self):
        result = detect_threat_surface(title="Fix auth middleware")
        # When implemented, categories should be strings
        for cat in result.categories:
            assert isinstance(cat, str)

    def test_valid_categories_only(self):
        """All returned categories must be from the known set."""
        valid = {"auth", "input-validation", "crypto", "external-data",
                 "agent-context", "dependency-change", "secrets"}
        # Test with a title that should trigger detection
        result = detect_threat_surface(
            title="Encrypt token and sanitize input",
            tags=["security"],
            file_paths=["package.json", ".env", "src/auth/login.py"],
        )
        for cat in result.categories:
            assert cat in valid, f"Unexpected category: {cat}"
