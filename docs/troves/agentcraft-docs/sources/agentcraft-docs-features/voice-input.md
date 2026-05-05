---
title: Voice Input
url: https://www.getagentcraft.com/docs/features/voice-input
fetched: 2026-05-04
type: documentation
---

# Voice Input

Talk to your agents with speech-to-text in the composer.

AgentCraft supports voice input in the composer. Hit the mic button, speak your prompt, and get real-time transcription with auto-send on silence.

## Using Voice Input

1. Click the microphone button in the composer (next to the send button)
2. Speak your prompt — text appears in real time as you talk
3. Pause speaking — after a brief silence, the message auto-sends

You can also click the mic button again to stop recording manually before auto-send triggers.

## How It Works

Voice input uses the Web Speech API built into modern browsers. Speech is transcribed locally by the browser — no audio is sent to AgentCraft servers.

Real-time transcription updates the composer text as you speak. When silence is detected for a configurable duration, the message is automatically submitted to the selected agent.

## Browser Support

| Browser | Support |
| --- | --- |
| Chrome / Chromium | Full support |
| Edge | Full support |
| Safari | Supported (macOS & iOS) |
| Firefox | Limited support |

## Desktop & Mobile

Voice input works on both the desktop UI and the mobile PWA. On mobile, it's especially useful for quick replies and approvals while away from your keyboard.