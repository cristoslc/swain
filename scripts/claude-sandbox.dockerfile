# claude-sandbox.dockerfile — Minimal Docker image for Claude Code (SPEC-049)
# Provides a reproducible environment for running Claude Code in Tier 2 isolation.
#
# Build: docker build -t claude-sandbox -f scripts/claude-sandbox.dockerfile .
# Run:   ./scripts/claude-sandbox --docker

FROM node:22-bookworm-slim

# Install essential tools available inside the sandbox
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Install Claude Code CLI
RUN npm install -g @anthropic-ai/claude-code

# Do not bake credentials — they are injected at runtime via env vars
# ANTHROPIC_API_KEY, GITHUB_TOKEN, GH_TOKEN are forwarded by the launcher

# Use a non-root user for better isolation on Linux
RUN useradd -m -s /bin/bash claude
USER claude

WORKDIR /workspace

# Default entrypoint passes through to claude
ENTRYPOINT ["claude"]
CMD ["--help"]
