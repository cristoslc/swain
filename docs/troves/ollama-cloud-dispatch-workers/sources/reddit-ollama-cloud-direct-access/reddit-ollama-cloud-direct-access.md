---
source-id: "reddit-ollama-cloud-direct-access"
title: "r/ollama: Direct cloud access — bypassing local client"
type: forum
url: "https://www.reddit.com/r/ollama/comments/1rmew6s/direct_cloud_access/"
fetched: 2026-03-25T02:00:00Z
---

# r/ollama: Direct cloud access?

## Question

> Right now, my openclaw gateway sends LLM prompts to Ollama, which then forwards the prompt to the Ollama cloud models. This seems inefficient. Is there a way to send the LLM prompts directly to the Ollama cloud servers using Ollama authentication (possibly an API key?), bypassing the local Ollama client?

## Answer

Ollama's cloud servers expose the same REST API as the local client, just at a different base URL. You authenticate with an API key instead of relying on the local process.

**Auth header:** `Authorization: Bearer $OLLAMA_API_KEY`

**Discover all available models:**
```bash
curl https://ollama.com/v1/models -H "Authorization: Bearer $OLLAMA_API_KEY"
```

**References:**
- Ollama Cloud overview: https://docs.ollama.com/cloud
- Ollama API Authentication: https://docs.ollama.com/api/authentication
