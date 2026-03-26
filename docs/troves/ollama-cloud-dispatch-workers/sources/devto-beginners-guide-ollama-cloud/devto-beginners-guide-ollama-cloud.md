---
source-id: "devto-beginners-guide-ollama-cloud"
title: "A Beginner's Guide to Ollama Cloud Models"
type: web
url: "https://dev.to/coderforfun/a-beginners-guide-to-ollama-cloud-models-3lc2"
fetched: 2026-03-25T02:00:00Z
---

# A Beginner's Guide to Ollama Cloud Models

By ELI, October 19, 2025 (updated December 6, 2025)

Ollama's cloud models allow users to run large language models without needing a powerful local GPU. Models are automatically offloaded to Ollama's cloud service.

## Available Cloud Models

- `deepseek-v3.1:671b-cloud`
- `gpt-oss:20b-cloud`
- `gpt-oss:120b-cloud`
- `kimi-k2:1t-cloud`
- `qwen3-coder:480b-cloud`
- `glm-4.6:cloud`
- `qwen3-vl:235b-cloud`

Browse latest at: ollama.com/search?c=cloud

## Cloud API Access

For direct API access:
1. Create an API key at ollama.com/settings
2. Set `OLLAMA_API_KEY` environment variable

```python
from ollama import Client

client = Client(
    host='https://ollama.com',
    headers={'Authorization': f'Bearer {ollama_api_key}'}
)

messages = [{'role': 'user', 'content': 'Why is the sky blue?'}]
for part in client.chat('gpt-oss:120b', messages=messages, stream=True):
    print(part.message.content, end='', flush=True)
```

## Capabilities

- **Tool calling**: Supported on deepseek-v3.1:671b-cloud, gpt-oss models. Includes built-in `web_search` and `web_fetch` tools.
- **Thinking traces**: Models can output reasoning steps separately from final output.
- **Streaming**: Real-time token delivery.
- **Structured outputs**: Enforce JSON schema on responses using Pydantic models.
- **Vision**: `qwen3-vl:235b-cloud` processes images alongside text.

## OpenAI-Compatible Endpoints

```
https://ollama.com/v1/models
https://ollama.com/v1/chat/completions
```

Authentication: `Authorization: Bearer $OLLAMA_API_KEY` header.
