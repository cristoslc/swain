---
title: Remote Access & Mobile
url: https://www.getagentcraft.com/docs/features/remote-access
fetched: 2026-05-04
type: documentation
---

# Remote Access & Mobile

Command your agents from anywhere with secure tunnels and a mobile PWA.

AgentCraft lets you access your command center from anywhere. One-click secure tunnel sharing, an installable mobile PWA, and push notifications with quick-reply for plan approvals and permissions.

## Setting Up Remote Access

Open the Remote Access modal from the top bar. Choose a TTL preset for how long the tunnel should stay active, then click to create the tunnel. AgentCraft generates a secure URL you can open on any device.

### TTL Presets

| Duration | Use Case |
| --- | --- |
| 15 min | Quick check from your phone |
| 1 hour | Working away from your desk |
| 4 hours | Extended remote session |
| 8 hours | Full workday |

The tunnel automatically expires after the selected TTL. You can manually close it at any time.

## Mobile PWA

The remote URL is a fully installable Progressive Web App. On mobile:

1. Open the tunnel URL in your browser
2. Tap "Add to Home Screen" (or the browser's install prompt)
3. Launch AgentCraft from your home screen like a native app

The mobile UI is optimized for touch with a full agent list, chat interface, and quest management.

### Mobile UI Tabs

| Tab | Description |
| --- | --- |
| Agents | View all active heroes with status indicators |
| Chat | Full chat interface with the selected agent |
| Quests | Browse and manage quest board |

## Push Notifications

When agents need your attention — plan approvals, permission requests, or completed missions — you'll receive push notifications on your device.

### Quick-Reply

Notifications include quick-reply actions so you can approve or deny without opening the app:

- Plan approval — Approve or reject an agent's proposed plan
- Permission request — Grant or deny tool/file access
- Message — Reply directly to an agent's question

## Security

- Tunnels use authentication tokens validated on every request
- TTL expiry automatically tears down the tunnel
- Each tunnel session gets a unique token
- No data is stored on intermediate servers — traffic is proxied directly