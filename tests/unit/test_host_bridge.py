"""RED tests for the host bridge kernel — the hub daemon."""
from swain_helm.protocol import Event, Command
from swain_helm.bridges.host import HostBridge


class TestHostBridgeRouting:
    def test_project_event_forwarded_to_chat_adapter(self):
        chat_events = []
        host = HostBridge(
            domain="personal",
            on_chat_event=chat_events.append,
        )
        host.register_project("swain")

        event = Event.text_output(bridge="swain", session_id="s1", content="hi")
        host.route_project_event(event)
        assert len(chat_events) == 1
        assert chat_events[0].type == "text_output"
        assert chat_events[0].bridge == "swain"

    def test_command_routed_to_correct_project(self):
        project_commands: dict[str, list] = {"swain": [], "rk": []}
        host = HostBridge(domain="personal")
        host.register_project("swain", on_command=project_commands["swain"].append)
        host.register_project("rk", on_command=project_commands["rk"].append)

        cmd = Command.send_prompt(bridge="swain", session_id="s1", text="hello")
        host.route_chat_command(cmd)
        assert len(project_commands["swain"]) == 1
        assert len(project_commands["rk"]) == 0

    def test_host_command_handled_locally(self):
        project_commands = []
        host = HostBridge(domain="personal")
        host.register_project("swain", on_command=project_commands.append)

        cmd = Command.stop_bridge(project="swain")
        host.route_chat_command(cmd)
        # stop_bridge is a host command — should not route to project
        assert len(project_commands) == 0

    def test_unknown_bridge_command_logged_not_crashed(self):
        host = HostBridge(domain="personal")
        cmd = Command.send_prompt(bridge="nonexistent", session_id="s1", text="hi")
        # Should not raise
        host.route_chat_command(cmd)


class TestHostBridgeProjectManagement:
    def test_register_project(self):
        host = HostBridge(domain="personal")
        host.register_project("swain")
        assert "swain" in host.projects

    def test_unregister_project(self):
        host = HostBridge(domain="personal")
        host.register_project("swain")
        host.unregister_project("swain")
        assert "swain" not in host.projects

    def test_list_projects(self):
        host = HostBridge(domain="personal")
        host.register_project("swain")
        host.register_project("rk")
        assert set(host.projects) == {"swain", "rk"}


class TestHostBridgeEvents:
    def test_host_events_forwarded_to_chat(self):
        chat_events = []
        host = HostBridge(domain="personal", on_chat_event=chat_events.append)

        event = Event.host_status(bridges_running=2, disk="50%", load="1.2")
        host.emit_host_event(event)
        assert len(chat_events) == 1
        assert chat_events[0].type == "host_status"
