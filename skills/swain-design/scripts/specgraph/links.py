"""OSC 8 hyperlink helper utilities for specgraph output.

These helpers emit OSC 8 terminal hyperlinks when stdout is a TTY,
matching the link helpers in specgraph.sh. When stdout is not a TTY
(piped, CI, etc.) they return plain text with no escape sequences.

OSC 8 format:
    \\x1b]8;;{url}\\x1b\\{text}\\x1b]8;;\\x1b\\

Note:
    ``repo_root`` must be an absolute path with no trailing slash
    (e.g. ``/home/user/myrepo``, not ``/home/user/myrepo/``).
"""

import sys


def is_tty() -> bool:
    """Return True if sys.stdout is a TTY."""
    return sys.stdout.isatty()


def _osc8_link(url: str, text: str) -> str:
    """Wrap text in an OSC 8 hyperlink escape sequence."""
    return f"\x1b]8;;{url}\x1b\\{text}\x1b]8;;\x1b\\"


def art_link(artifact_id: str, filepath: str, repo_root: str) -> str:
    """Return an OSC 8 hyperlink to the artifact file when stdout is a TTY.

    When stdout is not a TTY (piped, CI, etc.), returns just the artifact_id.
    When filepath is empty, returns just the artifact_id regardless of TTY.

    URL format: file:///{repo_root}/{filepath}
    OSC 8 format: \\x1b]8;;{url}\\x1b\\{text}\\x1b]8;;\\x1b\\

    Args:
        artifact_id: The artifact identifier (e.g. "SPEC-001") used as link text.
        filepath: Relative path to the artifact file from repo_root.
        repo_root: Absolute path to the repository root.

    Returns:
        OSC 8 hyperlink string if TTY and filepath is non-empty, else artifact_id.
    """
    if not filepath or not is_tty():
        return artifact_id
    url = f"file://{repo_root}/{filepath}"
    return _osc8_link(url, artifact_id)


def file_link(text: str, filepath: str, repo_root: str) -> str:
    """Return an OSC 8 hyperlink to a file path when stdout is a TTY.

    Same OSC 8 format as art_link, but text is the display text (not
    necessarily an artifact ID).

    When stdout is not a TTY (piped, CI, etc.), returns just the text.
    When filepath is empty, returns just the text regardless of TTY.

    URL format: file:///{repo_root}/{filepath}
    OSC 8 format: \\x1b]8;;{url}\\x1b\\{text}\\x1b]8;;\\x1b\\

    Args:
        text: Display text for the hyperlink.
        filepath: Relative path to the file from repo_root.
        repo_root: Absolute path to the repository root (no trailing slash).

    Returns:
        OSC 8 hyperlink string if TTY and filepath is non-empty, else text.
    """
    if not filepath or not is_tty():
        return text
    url = f"file://{repo_root}/{filepath}"
    return _osc8_link(url, text)
