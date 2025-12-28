# claude-foundry-safety

Safety guardrails for [claude-foundry](https://github.com/tylerburleigh/claude-foundry). This Claude Code plugin protects your development environment by blocking destructive commands, preventing access to sensitive files, and enforcing safe git operations.

## Features

- **Destructive Command Blocking** - Prevents `rm -rf`, `git reset --hard`, and other dangerous operations
- **Sensitive File Protection** - Blocks reading of SSH keys, API keys, credentials, and config files
- **Git Safety** - Prevents branch switching, unauthorized rebasing, force pushes, and history rewriting
- **Shell Wrapper Detection** - Catches dangerous commands hidden in `bash -c`, `sh -c`, or interpreter one-liners

## Installation

```bash
# Add the marketplace
/plugin marketplace add tylerburleigh/claude-foundry-safety

# Install the plugin
/plugin install claude-foundry-safety
```

Restart Claude Code after installation.

## What Gets Blocked

### Git Operations

| Command | Reason |
|---------|--------|
| `git checkout <branch>` | Branch switching not allowed |
| `git checkout -b`, `git switch -c` | Branch creation not allowed |
| `git branch -d/-D` | Branch deletion not allowed |
| `git checkout -- <files>` | Discards uncommitted changes |
| `git restore <files>` | Discards uncommitted changes |
| `git reset --hard` | Destroys uncommitted changes |
| `git rebase` | History rewriting not allowed |
| `git commit --amend` | History rewriting not allowed |
| `git push --force` | Destroys remote history |
| `git tag -d` | Tag deletion not allowed |
| `git clean -f` | Removes untracked files |
| `git stash drop/clear` | Deletes stashed changes |

### Sensitive Files

Reading these paths is blocked via `cat`, `less`, `head`, `tail`, `bat`, `view`, `strings`, `xxd`, etc:

| Path | Contents |
|------|----------|
| `~/.ssh/*` | SSH keys |
| `~/.api_keys` | API keys |
| `~/.config/gh/*` | GitHub CLI auth |
| `~/.gemini/*` | Gemini CLI config |
| `~/.config/opencode/*` | OpenCode config |
| `~/.cursor/*` | Cursor config |
| `~/.codex/*` | Codex config |
| `~/.gitconfig` | Git credentials |
| `~/.claude/.credentials.json` | Claude credentials |

### Filesystem

| Command | Reason |
|---------|--------|
| `rm -rf /` or `~` | Root/home deletion blocked |
| `rm -rf` outside cwd | Must be within working directory |

## What's Allowed

| Command | Why |
|---------|-----|
| `git branch` (no args) | Just lists branches |
| `git branch -v/-a` | List operations |
| `git tag` (no args) | Lists tags |
| `git tag v1.0` | Creating tags |
| `git commit -m "..."` | Normal commits |
| `git restore --staged` | Only unstages, safe |
| `git push --force-with-lease` | Safe force push |
| `rm -rf /tmp/...` | Temp directories |
| `rm -rf ./path` | Within cwd |
| `cat ~/.bashrc` | Non-sensitive files |

## Strict Mode

Enable stricter blocking:

```bash
export SAFETY_NET_STRICT=1
```

This additionally blocks:
- Unparseable commands
- All `rm -rf` except temp paths

## Development

```bash
# Setup
uv sync && uv run pre-commit install

# Run tests
uv run pytest

# All checks (ruff, mypy, vulture, pytest)
uv run ruff check && uv run mypy . && uv run pytest
```

## Project Structure

```
.claude-plugin/
  plugin.json           # Plugin metadata
  marketplace.json      # Marketplace config
hooks/
  hooks.json            # Hook registration
scripts/
  safety_net.py         # Entry point
  safety_net_impl/
    hook.py             # Main hook logic
    rules_git.py        # Git command rules
    rules_rm.py         # rm command rules
    rules_sensitive.py  # Sensitive file rules
    shell.py            # Shell parsing
tests/
  test_safety_net_git.py
  test_safety_net_rm.py
  test_safety_net_sensitive.py
```

## Acknowledgments

This project is a fork of [claude-code-safety-net](https://github.com/kenryu42/claude-code-safety-net) by [kenryu42](https://github.com/kenryu42). Extended with additional git operation blocking and sensitive file protection for use with claude-foundry.

## License

MIT
