"""Sensitive file read blocking rules for the safety net."""

import posixpath

_REASON_SENSITIVE_READ = (
    "Reading sensitive files is not allowed. "
    "This path may contain credentials or API keys."
)

# Sensitive directories (anything inside is blocked)
_SENSITIVE_DIRS = {
    ".ssh",
    ".config/gh",
    ".gemini",
    ".config/opencode",
    ".cursor",
    ".codex",
}

# Sensitive files (exact match after home prefix)
_SENSITIVE_FILES = {
    ".api_keys",
    ".gitconfig",
    ".claude/.credentials.json",
    ".claude/.claude.json",
}

# Commands that read file contents
_READ_COMMANDS = {
    "cat",
    "less",
    "more",
    "head",
    "tail",
    "bat",
    "batcat",
    "view",
    "strings",
    "xxd",
    "hexdump",
    "od",
    "tac",
    "nl",
}


def _analyze_sensitive_read(tokens: list[str]) -> str | None:
    """Analyze a file-reading command for sensitive path access.

    Args:
        tokens: Command tokens where tokens[0] is the command name.

    Returns:
        Reason string if blocked, None if allowed.
    """
    if not tokens:
        return None

    cmd = tokens[0].lower()
    if cmd not in _READ_COMMANDS:
        return None

    targets = _extract_file_targets(tokens)
    for target in targets:
        if _is_sensitive_path(target):
            return _REASON_SENSITIVE_READ

    return None


def _extract_file_targets(tokens: list[str]) -> list[str]:
    """Extract file path arguments from command tokens.

    Skips flags (tokens starting with -) unless after --.
    """
    targets: list[str] = []
    after_double_dash = False
    skip_next = False

    # Flags that take a value argument (command-specific)
    flags_with_value = {"-n", "-c", "-q", "--bytes", "--lines"}

    for tok in tokens[1:]:
        if skip_next:
            skip_next = False
            continue
        if after_double_dash:
            targets.append(tok)
            continue
        if tok == "--":
            after_double_dash = True
            continue
        if tok.startswith("-") and tok != "-":
            # Check if this flag takes a value
            if tok in flags_with_value:
                skip_next = True
            continue
        targets.append(tok)

    return targets


def _is_sensitive_path(path: str) -> bool:
    """Check if a path points to a sensitive file or directory."""
    # Normalize the path for comparison
    normalized = _normalize_home_path(path)
    if normalized is None:
        return False

    # Check exact file matches
    if normalized in _SENSITIVE_FILES:
        return True

    # Check directory matches (path is inside sensitive dir)
    for sensitive_dir in _SENSITIVE_DIRS:
        if normalized == sensitive_dir or normalized.startswith(sensitive_dir + "/"):
            return True

    return False


def _normalize_home_path(path: str) -> str | None:
    """Convert a path to a home-relative form for comparison.

    Returns the path relative to home (without leading ~/ or $HOME/),
    or None if the path is not under the home directory.
    """
    # Handle ~ prefix
    if path == "~":
        return ""
    if path.startswith("~/"):
        return posixpath.normpath(path[2:])

    # Handle $HOME prefix
    if path == "$HOME" or path == "${HOME}":
        return ""
    if path.startswith("$HOME/"):
        return posixpath.normpath(path[6:])
    if path.startswith("${HOME}/"):
        return posixpath.normpath(path[8:])

    # Handle /home/username paths
    if path.startswith("/home/"):
        parts = path.split("/")
        if len(parts) >= 3:
            # /home/username/... -> ...
            rest = "/".join(parts[3:])
            return posixpath.normpath(rest) if rest else ""

    return None
