# Agent Guidelines

claude-foundry-safety: Safety guardrails plugin for claude-foundry. Blocks destructive commands, protects sensitive files, prevents unsafe git operations.

## Commands

| Task | Command |
|------|---------|
| Setup | `uv sync && uv run pre-commit install` |
| All checks | `uv run ruff check && uv run mypy . && uv run pytest` |
| Lint | `uv run ruff check` |
| Format | `uv run ruff format` |
| Type check | `uv run mypy .` |
| Test all | `uv run pytest` |
| Single test | `uv run pytest tests/test_file.py::TestClass::test_name -v` |

## Code Style (Python 3.10+)

- Line length: 88 chars, formatter: Ruff
- Type hints required on all functions
- Use `X | None` not `Optional[X]}`, use `list[str]` not `List[str]`
- Use relative imports within same package

## Architecture

```
scripts/safety_net.py           # Entry point
  └── safety_net_impl/hook.py   # Main hook logic
        ├── rules_git.py        # Git command rules
        ├── rules_rm.py         # rm command rules
        ├── rules_sensitive.py  # Sensitive file rules
        └── shell.py            # Shell parsing
```

## Testing

Inherit from `SafetyNetTestCase`:

```python
class MyTests(SafetyNetTestCase):
    def test_dangerous_blocked(self) -> None:
        self._assert_blocked("git reset --hard", "git reset --hard")

    def test_safe_allowed(self) -> None:
        self._assert_allowed("git status")
```

## Adding New Rules

1. Add reason constant in appropriate `rules_*.py`
2. Add detection logic
3. Add tests in `tests/test_safety_net_*.py`
4. Run checks: `uv run ruff check && uv run mypy . && uv run pytest`
