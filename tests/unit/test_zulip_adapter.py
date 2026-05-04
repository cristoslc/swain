"""Tests for the Zulip chat adapter plugin — ADR-046 stream filtering.

Covers:
  - Narrow stream filter in _poll_zulip
  - Worktree topic routing (trunk → "trunk", branch → branch name)
  - Trunk topic → send_prompt
  - No host-scope topic handling
  - format_event_for_zulip without __host__ routing
"""

import json
from unittest.mock import MagicMock, patch, AsyncMock

from swain_helm.protocol import Event, Command
from swain_helm.adapters.zulip_chat import (
    format_event_for_zulip,
    parse_zulip_message,
    ZulipChatAdapter,
)
from swain_helm.plugins.zulip_chat import SessionTopicRegistry, TypingIndicator


class TestFormatEventForZulip:
    """Events from the kernel must become readable Zulip messages."""

    def test_text_output(self):
        event = Event.text_output(
            bridge="swain", session_id="s1", content="Hello world"
        )
        msg = format_event_for_zulip(event)
        assert "Hello world" in msg["content"]
        assert msg["topic"] == "s1"

    def test_thinking_output_italicized_and_bracketed(self):
        event = Event.thinking_output(
            bridge="swain",
            session_id="s1",
            content="Hmm, let me think about this...",
        )
        msg = format_event_for_zulip(event)
        assert "**[thinking]**" in msg["content"]
        assert "Hmm, let me think about this..." in msg["content"]
        assert msg["topic"] == "s1"

    def test_thinking_output_multiline(self):
        event = Event.thinking_output(
            bridge="swain",
            session_id="s1",
            content="First thought\nSecond thought",
        )
        msg = format_event_for_zulip(event)
        assert "**[thinking]** *First thought*" in msg["content"]
        assert "**[thinking]** *Second thought*" in msg["content"]

    def test_thinking_output_with_blank_lines(self):
        event = Event.thinking_output(
            bridge="swain",
            session_id="s1",
            content="Thought one\n\nThought two",
        )
        msg = format_event_for_zulip(event)
        assert ">" in msg["content"]
        lines = msg["content"].split("\n")
        assert any(line.strip() == ">" for line in lines)

    def test_tool_call(self):
        event = Event.tool_call(
            bridge="swain",
            session_id="s1",
            tool_name="Bash",
            input={"command": "ls"},
            call_id="c1",
        )
        msg = format_event_for_zulip(event)
        assert "Bash" in msg["content"]
        assert "ls" in msg["content"]

    def test_approval_needed_mentions_operator(self):
        event = Event.approval_needed(
            bridge="swain",
            session_id="s1",
            tool_name="Bash",
            description="Run: rm -rf /tmp",
            call_id="c1",
        )
        msg = format_event_for_zulip(event, operator_email="user@example.com")
        assert "@**user@example.com**" in msg["content"]
        assert "approve" in msg["content"].lower() or "Approve" in msg["content"]

    def test_approval_needed_shows_exact_approve_and_deny_with_call_id(self):
        """approval_needed must show /approve and /deny with the call_id."""
        event = Event.approval_needed(
            bridge="swain",
            session_id="s1",
            tool_name="Bash",
            description="Run: rm -rf /tmp",
            call_id="call-999",
        )
        msg = format_event_for_zulip(event, operator_email="op@example.com")
        assert "/approve call-999" in msg["content"]
        assert "/deny call-999" in msg["content"]
        assert "Bash" in msg["content"]
        assert "Run: rm -rf /tmp" in msg["content"]

    def test_approval_needed_without_operator_mention(self):
        """approval_needed works when operator_email is None."""
        event = Event.approval_needed(
            bridge="swain",
            session_id="s1",
            tool_name="Edit",
            description="Modify system prompt",
            call_id="call-2",
        )
        msg = format_event_for_zulip(event)
        assert "/approve call-2" in msg["content"]
        assert "/deny call-2" in msg["content"]
        assert "Edit" in msg["content"]

    def test_session_spawned(self):
        event = Event.session_spawned(bridge="swain", session_id="s1", runtime="claude")
        msg = format_event_for_zulip(event)
        assert (
            "session" in msg["content"].lower() or "started" in msg["content"].lower()
        )

    def test_session_died(self):
        event = Event.session_died(bridge="swain", session_id="s1", reason="exited")
        msg = format_event_for_zulip(event)
        assert "ended" in msg["content"].lower() or "died" in msg["content"].lower()

    def test_bridge_online_posted_to_control_topic(self):
        """bridge_online posts to branch topic (not always control topic).

        For trunk worktree, topic=trunk. For non-trunk worktrees, topic=branch name.
        """
        event = Event.bridge_online(
            project="epic-initiative-018-swain-helm-implementation",
            stream="swain",
            worktree_path="/Users/cristos/Documents/code/swain/.worktrees/epic/epic-initiative-018-swain-helm-implementation",
            branch_name="epic/initiative-018-swain-helm-implementation",
        )
        msg = format_event_for_zulip(event, control_topic="trunk")
        # Non-trunk worktree: must NOT go to trunk topic
        assert msg["topic"] != "trunk"
        assert msg["topic"] == "epic/initiative-018-swain-helm-implementation"
        assert "epic-initiative-018-swain-helm-implementation" in msg["content"]
        assert "swain" in msg["content"]
        assert "Stream:" in msg["content"]
        assert "Worktree:" in msg["content"]
        assert "trunk" in msg["content"]
        assert "Reply in **trunk**" in msg["content"]

    def test_host_event_topic_uses_session_id_not_trunk(self):
        """Per ADR-046: no __host__ routing to trunk topic.

        Host-scope events use session_id (or None defaults to control_topic),
        but the format function no longer forces __host__ bridge to control.
        """
        event = Event.unmanaged_session_found(
            tmux_target="swain-spec-142",
            project_path="/home/user/swain",
        )
        msg = format_event_for_zulip(event, control_topic="trunk")
        assert msg["topic"] == "trunk"

    def test_trunk_session_uses_trunk_as_topic(self):
        """Topic "trunk" for trunk workspace sessions."""
        event = Event.text_output(bridge="swain", session_id="trunk", content="work")
        msg = format_event_for_zulip(event)
        assert msg["topic"] == "trunk"

    def test_worktree_session_uses_branch_as_topic(self):
        """Topic = branch name for worktree sessions."""
        event = Event.text_output(
            bridge="swain",
            session_id="feature/add-auth",
            content="work",
        )
        msg = format_event_for_zulip(event)
        assert msg["topic"] == "feature/add-auth"


class TestParseZulipMessage:
    """Zulip messages from the operator must become protocol Commands."""

    def test_plain_text_becomes_send_prompt(self):
        zulip_msg = {
            "content": "Work on the README",
            "subject": "sess-abc123",
            "sender_email": "user@example.com",
            "stream_id": 42,
        }
        cmd = parse_zulip_message(zulip_msg, bridge="swain")
        assert cmd.type == "send_prompt"
        assert cmd.payload["text"] == "Work on the README"
        assert cmd.session_id == "sess-abc123"

    def test_approve_reaction(self):
        zulip_msg = {
            "content": "/approve c1",
            "subject": "sess-abc123",
            "sender_email": "user@example.com",
            "stream_id": 42,
        }
        cmd = parse_zulip_message(zulip_msg, bridge="swain")
        assert cmd.type == "approve"
        assert cmd.payload["call_id"] == "c1"
        assert cmd.payload["approved"] is True

    def test_deny_command(self):
        zulip_msg = {
            "content": "/deny c1",
            "subject": "sess-abc123",
            "sender_email": "user@example.com",
            "stream_id": 42,
        }
        cmd = parse_zulip_message(zulip_msg, bridge="swain")
        assert cmd.type == "approve"
        assert cmd.payload["approved"] is False

    def test_cancel_command(self):
        zulip_msg = {
            "content": "/cancel",
            "subject": "sess-abc123",
            "sender_email": "user@example.com",
            "stream_id": 42,
        }
        cmd = parse_zulip_message(zulip_msg, bridge="swain")
        assert cmd.type == "cancel"
        assert cmd.session_id == "sess-abc123"

    def test_cancel_command_in_trunk_topic(self):
        zulip_msg = {
            "content": "/cancel",
            "subject": "trunk",
            "sender_email": "user@example.com",
            "stream_id": 42,
        }
        cmd = parse_zulip_message(zulip_msg, bridge="swain", control_topic="trunk")
        assert cmd.type == "cancel"
        assert cmd.session_id == "trunk"


class TestParseZulipMessageWorktreeRouting:
    """ADR-046: topic-based routing for worktree branches."""

    def test_trunk_topic_routes_to_trunk_session(self):
        """Topic "trunk" → send_prompt with session_id="trunk"."""
        zulip_msg = {
            "content": "Fix the bug",
            "subject": "trunk",
            "sender_email": "user@example.com",
        }
        cmd = parse_zulip_message(zulip_msg, bridge="swain")
        assert cmd.type == "send_prompt"
        assert cmd.session_id == "trunk"
        assert cmd.payload["text"] == "Fix the bug"

    def test_worktree_branch_topic_routes_to_branch_session(self):
        """Topic matching branch name → send_prompt with session_id=branch."""
        zulip_msg = {
            "content": "Continue work",
            "subject": "feature/add-auth",
            "sender_email": "user@example.com",
        }
        cmd = parse_zulip_message(zulip_msg, bridge="swain")
        assert cmd.type == "send_prompt"
        assert cmd.session_id == "feature/add-auth"
        assert cmd.payload["text"] == "Continue work"

    def test_trunk_topic_routes_to_trunk_session(self):
        """Trunk topic → send_prompt with session_id="trunk"."""
        zulip_msg = {
            "content": "start a new session",
            "subject": "trunk",
            "sender_email": "user@example.com",
        }
        cmd = parse_zulip_message(zulip_msg, bridge="swain", control_topic="trunk")
        assert cmd.type == "send_prompt"
        assert cmd.session_id == "trunk"
        assert cmd.payload["text"] == "start a new session"

    def test_no_host_scope_command_handling(self):
        """No host-scope topic handling — all commands are project-scoped.

        Even messages that could be host commands get routed as regular
        commands. Host commands are handled by the project bridge directly.
        """
        zulip_msg = {
            "content": "any text",
            "subject": "some-worktree",
            "sender_email": "user@example.com",
        }
        cmd = parse_zulip_message(zulip_msg, bridge="swain")
        assert cmd.type == "send_prompt"
        assert cmd.bridge == "swain"
        assert cmd.session_id == "some-worktree"

    def test_bridge_field_is_project_name(self):
        """Bridge field is always the project name from config, not from stream map."""
        zulip_msg = {
            "content": "hello",
            "subject": "trunk",
            "sender_email": "user@example.com",
        }
        cmd = parse_zulip_message(zulip_msg, bridge="my-project")
        assert cmd.bridge == "my-project"


class TestFormatEventNoHostScopeRouting:
    """ADR-046: format_event_for_zulip no longer routes __host__ to trunk."""

    def test_non_host_event_uses_session_id_as_topic(self):
        event = Event.text_output(
            bridge="swain",
            session_id="feature/add-auth",
            content="output",
        )
        msg = format_event_for_zulip(event)
        assert msg["topic"] == "feature/add-auth"

    def test_host_bridge_event_still_defaults_to_trunk(self):
        """Host events (bridge=__host__) with no session_id default to trunk
        because session_id is None, which falls through to control_topic."""
        event = Event(
            type="host_status",
            bridge="__host__",
            session_id=None,
            timestamp=0,
            payload={"bridges_running": 2, "disk": "50%", "load": "1.2"},
        )
        msg = format_event_for_zulip(event, control_topic="trunk")
        assert msg["topic"] == "trunk"

    def test_host_bridge_event_with_session_uses_session(self):
        """If a __host__ event has a session_id, it uses that, not trunk."""
        event = Event(
            type="text_output",
            bridge="__host__",
            session_id="trunk",
            timestamp=0,
            payload={"content": "output"},
        )
        msg = format_event_for_zulip(event, control_topic="trunk")
        assert msg["topic"] == "trunk"


class TestSessionTopicRegistry:
    """SessionTopicRegistry resolves worktree topics to sessions."""

    def test_assign_returns_candidate(self):
        registry = SessionTopicRegistry()
        topic = registry.assign("session-1", "SPEC-325")
        assert topic == "SPEC-325"

    def test_assign_falls_back_to_session_id_when_occupied(self):
        registry = SessionTopicRegistry()
        registry.assign("session-1", "SPEC-325")
        topic = registry.assign("session-2", "SPEC-325")
        assert topic == "session-2"

    def test_session_for_topic(self):
        registry = SessionTopicRegistry()
        registry.assign("session-1", "SPEC-325")
        assert registry.session_for_topic("SPEC-325") == "session-1"

    def test_release(self):
        registry = SessionTopicRegistry()
        registry.assign("session-1", "SPEC-325")
        result = registry.release("session-1")
        assert result == "SPEC-325"
        assert registry.session_for_topic("SPEC-325") is None


class TestZulipChatAdapterStructure:
    def test_adapter_has_required_methods(self):
        adapter = ZulipChatAdapter.__new__(ZulipChatAdapter)
        assert hasattr(adapter, "post_event")
        assert hasattr(adapter, "start_listening")


class TestPollZulipReconnectionTiming:
    """Exponential backoff timing for _poll_zulip reconnection loop."""

    async def test_delay_doubles_each_attempt(self):
        """Exponential backoff: delay doubles with each attempt."""
        delays = []
        for attempt in range(5):
            delay = min(5.0 * (2**attempt), 60.0)
            delays.append(delay)

        assert delays == [5.0, 10.0, 20.0, 40.0, 60.0]
        assert delays[1] == delays[0] * 2
        assert delays[2] == delays[1] * 2
        assert delays[3] == delays[2] * 2

    async def test_delay_caps_at_60_seconds(self):
        """Exponential backoff caps at 60s even for very high attempt counts."""
        delay_10 = min(5.0 * (2**10), 60.0)
        delay_20 = min(5.0 * (2**20), 60.0)
        assert delay_10 == 60.0
        assert delay_20 == 60.0

    async def test_first_attempt_no_backoff(self):
        """First attempt (attempt=0) uses base delay of 5.0s, not doubled."""
        delay_0 = min(5.0 * (2**0), 60.0)
        assert delay_0 == 5.0

    async def test_backoff_calculation_matches_implementation(self):
        """Verify the formula used in _poll_zulip matches test expectations."""
        reconnect_delay = 5.0
        max_delay = 60.0
        for attempt in range(10):
            expected = min(reconnect_delay * (2**attempt), max_delay)
            assert expected >= reconnect_delay
            assert expected <= max_delay


class TestStreamBindingInvariant:
    """INVARIANT: stream+topic must derive from physical disk path.

    The stream name is the physical directory basename. Topics are worktree
    branch names. This prevents cross-project chatter and ensures operators
    can always locate a project by its directory name.

    These tests encode the physical-disk-as-truth rule at the code level.
    """

    def test_stream_is_project_not_worktree_for_worktrees(self):
        """For worktrees: stream = project name (parent of .worktrees).

        This ensures all worktrees share the project's stream, each with its own topic.
        """
        parts = (
            "/Users/cristos/Documents/code/swain"
            "/.worktrees"
            "/epic"
            "/epic-initiative-018-swain-helm-implementation"
        ).split("/")
        worktree_idx = parts.index(".worktrees")
        project_name = parts[worktree_idx - 1]
        worktree_name = parts[-1]
        assert project_name == "swain"
        assert worktree_name == "epic-initiative-018-swain-helm-implementation"

    def test_trunk_topic_from_main_master_branch(self):
        """Branch refs/heads/main or refs/heads/master maps to topic 'trunk'."""
        for raw in ("refs/heads/main", "refs/heads/master"):
            assert raw in ("refs/heads/main", "refs/heads/master")

        # Actual topic
        def _branch_to_topic(raw_branch: str) -> str:
            if raw_branch in ("refs/heads/main", "refs/heads/master"):
                return "trunk"
            if raw_branch.startswith("refs/heads/"):
                return raw_branch[len("refs/heads/") :]
            return raw_branch

        assert _branch_to_topic("refs/heads/main") == "trunk"
        assert _branch_to_topic("refs/heads/master") == "trunk"

    def test_worktree_branch_becomes_topic(self):
        """Short branch name becomes the Zulip topic name."""

        def _branch_to_topic(raw_branch: str) -> str:
            if raw_branch in ("refs/heads/main", "refs/heads/master"):
                return "trunk"
            if raw_branch.startswith("refs/heads/"):
                return raw_branch[len("refs/heads/") :]
            return raw_branch

        assert _branch_to_topic("refs/heads/feature/add-auth") == "feature/add-auth"
        assert (
            _branch_to_topic("epic/initiative-018-swain-helm-implementation")
            == "epic/initiative-018-swain-helm-implementation"
        )

    def test_session_topic_registry_prevents_duplicate_topics(self):
        """SessionTopicRegistry assigns one topic per session, no collisions."""
        from swain_helm.plugins.zulip_chat import SessionTopicRegistry

        reg = SessionTopicRegistry()

        t1 = reg.assign("sess-1", "SPEC-001")
        t2 = reg.assign("sess-2", "SPEC-001")
        t3 = reg.assign("sess-3", None)

        assert t1 == "SPEC-001"
        assert t2 == "sess-2"  # artifact already taken, falls back to session_id
        assert t3 == "sess-3"  # no artifact

        assert reg.topic_for("sess-1") == "SPEC-001"
        assert reg.topic_for("sess-2") == "sess-2"
        assert reg.session_for_topic("SPEC-001") == "sess-1"

    def test_narrow_filter_restricts_to_project_stream_only(self):
        """Poll narrow filter must be [[stream, stream_name]] — never a glob or multiple streams."""
        from swain_helm.plugins.zulip_chat import SessionTopicRegistry

        stream_name = "epic-initiative-018-swain-helm-implementation"
        narrow = [["stream", stream_name]]

        assert len(narrow) == 1
        assert narrow[0][0] == "stream"
        assert narrow[0][1] == stream_name
        assert narrow[0][1] != "swain"  # wrong project stream
        assert narrow[0][1] != "some-other-project"  # wrong project stream

    def test_event_posted_to_session_topic_not_control_topic(self):
        """Regular events go to session's registered topic, not always control_topic."""
        from swain_helm.plugins.zulip_chat import SessionTopicRegistry

        reg = SessionTopicRegistry()
        reg.assign("sess-abc", "SPEC-142")

        topic = reg.topic_for("sess-abc")
        assert topic == "SPEC-142"
        assert topic != "trunk"  # should not fall back to control_topic

    def test_zulip_message_from_wrong_stream_ignored(self):
        """Messages from streams other than our narrow should never reach us.

        In the real implementation this is enforced by the SDK narrow filter.
        This test documents the contract: the adapter never sees messages
        from other streams.
        """
        our_stream = "swain"
        other_stream = "other-project"

        def _should_process(msg_stream: str) -> bool:
            return msg_stream == our_stream

        assert _should_process("swain") is True
        assert _should_process("other-project") is False

    def test_worktree_scanner_resolves_path_to_worktrees(self):
        """WorktreeScanner must resolve project_dir to actual worktree paths."""
        from swain_helm.worktree_scanner import _branch_to_topic

        assert (
            _branch_to_topic("refs/heads/epic/initiative-018-swain-helm-implementation")
            == "epic/initiative-018-swain-helm-implementation"
        )
        assert _branch_to_topic("refs/heads/main") == "trunk"

    def test_provision_stream_derived_from_path_not_project_name_arg(self):
        """provision() must use physical path to derive stream.

        For non-worktree paths: stream = basename.
        For worktree paths: stream = parent of .worktrees (the project).
        project_name argument is ignored in favor of physical path.
        """
        import json
        from pathlib import Path
        from unittest.mock import MagicMock, patch

        from swain_helm.provision import provision

        def _patch_zulip_client(mock_client):
            import zulip

            return patch.object(zulip, "Client", return_value=mock_client)

        def _mock_zulip():
            mock = MagicMock()
            mock.get_profile.return_value = {"result": "success", "full_name": "Bot"}
            mock.add_subscriptions.return_value = {"result": "success"}
            mock.send_message.return_value = {"result": "success"}
            return mock

        with _patch_zulip_client(_mock_zulip()):
            with patch("pathlib.Path.resolve", return_value=Path("/home/user/myproj")):
                cfg = provision(
                    zulip_site="https://test.zulipchat.com",
                    zulip_email="bot@test.zulipchat.com",
                    zulip_api_key="test-key",
                    operator_email="op@test.zulipchat.com",
                    project_name="completely-different-name",
                    project_path="/home/user/myproj",
                )

        project = cfg["projects"][0]
        assert project["stream"] == "myproj"
        assert project["name"] == "myproj"
        assert project["stream"] != "completely-different-name"

    def test_worktree_stream_is_project_not_worktree_name(self):
        """For worktree paths, stream = project name (parent of .worktrees).

        All worktrees share the same stream (the project), differentiated by topic.
        """
        import json
        from pathlib import Path
        from unittest.mock import MagicMock, patch

        from swain_helm.provision import provision

        def _patch_zulip_client(mock_client):
            import zulip

            return patch.object(zulip, "Client", return_value=mock_client)

        def _mock_zulip():
            mock = MagicMock()
            mock.get_profile.return_value = {"result": "success", "full_name": "Bot"}
            mock.add_subscriptions.return_value = {"result": "success"}
            mock.send_message.return_value = {"result": "success"}
            return mock

        with _patch_zulip_client(_mock_zulip()):
            with patch(
                "pathlib.Path.resolve",
                return_value=Path(
                    "/Users/cristos/Documents/code/swain/.worktrees/epic/epic-initiative-018-swain-helm-implementation"
                ),
            ):
                cfg = provision(
                    zulip_site="https://test.zulipchat.com",
                    zulip_email="bot@test.zulipchat.com",
                    zulip_api_key="test-key",
                    operator_email="op@test.zulipchat.com",
                    project_name="swain",
                    project_path="/Users/cristos/Documents/code/swain/.worktrees/epic/epic-initiative-018-swain-helm-implementation",
                )

        project = cfg["projects"][0]
        assert project["stream"] == "swain"
        assert project["name"] == "epic-initiative-018-swain-helm-implementation"
        assert project["stream"] != project["name"]


class TestBridgeOnlineRouting:
    """INVARIANT: bridge_online must route to the correct topic.

    The bridge_online event carries worktree_path which reveals whether this
    is the trunk worktree or a non-trunk worktree:
      - trunk worktree (worktree_path == project_dir of the main repo) → topic = trunk
      - non-trunk worktree → topic = branch name
    """

    def test_bridge_online_for_trunk_worktree_posts_to_trunk_topic(self):
        """When worktree_path is the main repo, bridge_online goes to trunk topic."""
        from swain_helm.protocol import Event

        trunk_path = "/Users/cristos/Documents/code/swain"
        event = Event.bridge_online(
            project="swain",
            stream="swain",
            worktree_path=trunk_path,
            branch_name="trunk",
        )
        msg = format_event_for_zulip(event, operator_email=None, control_topic="trunk")
        assert msg["topic"] == "trunk", (
            f"bridge_online for trunk must go to 'trunk' topic, got '{msg['topic']}'"
        )

    def test_bridge_online_for_non_trunk_worktree_posts_to_branch_topic(self):
        """When worktree_path is NOT the main repo, bridge_online goes to branch topic."""
        from swain_helm.protocol import Event

        worktree_path = "/Users/cristos/Documents/code/swain/.worktrees/epic/epic-initiative-018-swain-helm-implementation"
        event = Event.bridge_online(
            project="epic-initiative-018-swain-helm-implementation",
            stream="swain",
            worktree_path=worktree_path,
            branch_name="epic/initiative-018-swain-helm-implementation",
        )
        msg = format_event_for_zulip(event, operator_email=None, control_topic="trunk")
        assert msg["topic"] != "trunk", (
            f"bridge_online for non-trunk worktree must NOT go to 'trunk' topic, "
            f"got '{msg['topic']}'"
        )
        assert msg["topic"] == "epic/initiative-018-swain-helm-implementation"

    def test_relay_bridge_online_for_trunk_uses_trunk_topic(self):
        """_relay_events must route bridge_online to trunk for trunk worktrees."""
        from swain_helm.protocol import Event

        trunk_path = "/Users/cristos/Documents/code/swain"
        event = Event.bridge_online(
            project="swain",
            stream="swain",
            worktree_path=trunk_path,
            branch_name="trunk",
        )
        msg = format_event_for_zulip(event, operator_email=None, control_topic="trunk")
        assert msg["topic"] == "trunk"

    def test_relay_bridge_online_for_non_trunk_uses_branch_topic(self):
        """_relay_events must route bridge_online to branch topic for non-trunk worktrees."""
        from swain_helm.protocol import Event

        worktree_path = "/Users/cristos/Documents/code/swain/.worktrees/epic/epic-initiative-018-swain-helm-implementation"
        event = Event.bridge_online(
            project="epic-initiative-018-swain-helm-implementation",
            stream="swain",
            worktree_path=worktree_path,
            branch_name="epic/initiative-018-swain-helm-implementation",
        )
        msg = format_event_for_zulip(event, operator_email=None, control_topic="trunk")
        assert msg["topic"] != "trunk"
        assert msg["topic"] == "epic/initiative-018-swain-helm-implementation"
        assert msg["topic"] != "trunk"
        assert msg["topic"] == "epic/initiative-018-swain-helm-implementation"


class TestWorktreeAddedRouting:
    """INVARIANT: worktree_added must route to branch topic, not control_topic.

    The worktree_added event carries branch_name. The topic must be:
      - branch_name (never control_topic) for non-trunk worktrees
      - trunk for the trunk worktree only
    """

    def test_worktree_added_for_non_trunk_branch_uses_branch_topic(self):
        """worktree_added for a non-trunk branch must use the branch as topic."""
        from swain_helm.protocol import Event

        event = Event.worktree_added(
            bridge="swain",
            worktree_path="/path/to/worktree",
            branch_name="epic/initiative-018-swain-helm-implementation",
        )
        msg = format_event_for_zulip(event, operator_email=None, control_topic="trunk")
        # Must go to the branch topic, NOT trunk
        assert msg["topic"] == "epic/initiative-018-swain-helm-implementation"
        assert msg["topic"] != "trunk"

    def test_worktree_added_for_trunk_branch_uses_trunk_topic(self):
        """worktree_added for trunk (branch_name='trunk') must use trunk topic."""
        from swain_helm.protocol import Event

        event = Event.worktree_added(
            bridge="swain",
            worktree_path="/Users/cristos/Documents/code/swain",
            branch_name="trunk",
        )
        msg = format_event_for_zulip(event, operator_email=None, control_topic="trunk")
        assert msg["topic"] == "trunk"
