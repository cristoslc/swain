#!/usr/bin/env bash
# Thin wrapper — runs yt-dlp transiently via uv without a global install.
exec uv run --with yt-dlp yt-dlp "$@"
