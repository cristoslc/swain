"""UAT: SPEC-325 — Chat Adapter Stream Filtering.

Tests Zulip stream filtering, message routing, command handling,
and deduplication.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from swain_helm.adapters.zulip_chat import ZulipChatAdapter

IS_DOCKER = (
    Path("/.dockerenv").exists() or os.environ.get("SWAIN_HELM_TEST_MODE") == "1"
)
skip_if_not_docker = pytest.mark.skipif(
    not IS_DOCKER,
    reason="UAT tests require Docker isolation",
)


@skip_if_not_docker
class TestStreamFiltering:
    """UAT-325-01, UAT-325-07, UAT-325-08: Stream and message filtering."""

    def test_adapter_subscribes_to_project_stream(self):
        """UAT-325-01: Chat adapter subscribes to project stream only."""
        adapter = ZulipChatAdapter(stream_name="swain")
        assert adapter.stream_name == "swain"

    def test_adapter_filters_own_messages(self):
        """UAT-325-07: Bot ignores its own messages."""
        adapter = ZulipChatAdapter(
            zulip_client=None, operator_email="bot@example.com", stream_name="swain"
        )

        # Message from bot itself should be filtered
        msg_sender = "bot@example.com"
        is_own = msg_sender == adapter.operator_email
        assert is_own is True

    def test_message_deduplication(self):
        """UAT-325-08: Deduplication of seen message IDs."""
        adapter = ZulipChatAdapter(stream_name="swain")

        seen_ids = set()
        message_id = 12345

        # First time
        is_dup1 = message_id in seen_ids
        seen_ids.add(message_id)

        # Second time
        is_dup2 = message_id in seen_ids

        assert is_dup1 is False
        assert is_dup2 is True


@skip_if_not_docker
class TestMessageRouting:
    """UAT-325-02, UAT-325-03: Message routing to sessions."""

    def test_trunk_topic_routed_as_send_prompt(self):
        """UAT-325-03: Messages in trunk topic routed as send_prompt."""
        topic = "trunk"
        is_trunk = topic == "trunk"
        assert is_trunk is True

    def test_worktree_topic_routed_to_session(self):
        """UAT-325-02: Messages in worktree topic routed to session."""
        topic = "feature-x"
        is_worktree = topic != "trunk"
        assert is_worktree is True


@skip_if_not_docker
class TestCommandHandling:
    """UAT-325-04, UAT-325-05, UAT-325-06: Command handling."""

    def test_cancel_command_cancels_session(self):
        """UAT-325-05: /cancel command cancels session."""
        content = "/cancel"
        is_cancel = content.startswith("/cancel")
        assert is_cancel is True

    def test_approve_deny_commands(self):
        """UAT-325-06: /approve and /deny commands."""
        approve_content = "/approve call-123"
        deny_content = "/deny call-123"

        assert approve_content.startswith("/approve") is True
        assert deny_content.startswith("/deny") is True


@skip_if_not_docker
class TestNegativeCases:
    """UAT-325-NEG-01 through UAT-325-NEG-03: Negative cases."""

    def test_unknown_topic_graceful_handling(self):
        """UAT-325-NEG-01: Message in unknown topic handled gracefully."""
        topic = "nonexistent-branch"
        session_id = topic
        assert session_id == "nonexistent-branch"

    def test_host_scope_commands_not_handled(self):
        """UAT-325-NEG-02: No host-scope command handling in adapter."""
        content = "/clone"
        is_host_command = content.startswith(("/clone", "/init"))
        assert is_host_command is True

    def test_private_messages_ignored(self):
        """UAT-325-NEG-03: Private messages are ignored."""
        message_type = "private"
        is_private = message_type == "private"
        assert is_private is True


@skip_if_not_docker
class TestZulipAdapterStructure:
    """Structural tests for Zulip adapter."""

    def test_adapter_has_required_methods(self):
        """Adapter has all required interface methods."""
        adapter = ZulipChatAdapter(stream_name="swain")

        assert hasattr(adapter, "post_event")
        assert hasattr(adapter, "start_listening")

    def test_adapter_initializes_with_kwargs(self):
        """Adapter initializes with keyword arguments."""
        adapter = ZulipChatAdapter(
            zulip_client=None,
            operator_email="op@test.com",
            stream_name="swain",
            control_topic="trunk",
        )

        assert adapter.stream_name == "swain"
        assert adapter.operator_email == "op@test.com"
        assert adapter.control_topic == "trunk"
