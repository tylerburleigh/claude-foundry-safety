"""Git command analysis rules for the safety net."""

from .shell import _short_opts

_REASON_GIT_CHECKOUT_DOUBLE_DASH = (
    "git checkout -- discards uncommitted changes permanently. Use 'git stash' first."
)
_REASON_GIT_CHECKOUT_REF_DOUBLE_DASH = (
    "git checkout <ref> -- <path> overwrites working tree. Use 'git stash' first."
)
_REASON_GIT_RESTORE = (
    "git restore discards uncommitted changes. Use 'git stash' or 'git diff' first."
)
_REASON_GIT_RESTORE_WORKTREE = (
    "git restore --worktree discards uncommitted changes permanently."
)
_REASON_GIT_RESET_HARD = (
    "git reset --hard destroys uncommitted changes. Use 'git stash' first."
)
_REASON_GIT_RESET_MERGE = "git reset --merge can lose uncommitted changes."
_REASON_GIT_CLEAN_FORCE = (
    "git clean -f removes untracked files permanently. "
    "Review with 'git clean -n' first."
)
_REASON_GIT_PUSH_FORCE = (
    "Force push can destroy remote history. Use --force-with-lease if necessary."
)
_REASON_GIT_BRANCH_DELETE_FORCE = (
    "git branch -D force-deletes without merge check. Use -d for safety."
)
_REASON_GIT_STASH_DROP = (
    "git stash drop permanently deletes stashed changes. "
    "List stashes first with 'git stash list'."
)
_REASON_GIT_STASH_CLEAR = "git stash clear permanently deletes ALL stashed changes."
_REASON_GIT_CHECKOUT_BRANCH = (
    "git checkout <branch> switches branches. Branch switching is not allowed."
)
_REASON_GIT_CHECKOUT_CREATE = (
    "git checkout -b creates a new branch. Branch creation is not allowed."
)
_REASON_GIT_SWITCH = "git switch changes branches. Branch switching is not allowed."
_REASON_GIT_SWITCH_CREATE = (
    "git switch -c creates a new branch. Branch creation is not allowed."
)
_REASON_GIT_BRANCH_CREATE = (
    "git branch <name> creates a new branch. Branch creation is not allowed."
)
_REASON_GIT_BRANCH_DELETE = (
    "git branch -d deletes a branch. Branch deletion is not allowed."
)
_REASON_GIT_REBASE = "git rebase rewrites commit history. Rebase is not allowed."
_REASON_GIT_COMMIT_AMEND = (
    "git commit --amend rewrites commit history. Amend is not allowed."
)
_REASON_GIT_TAG_DELETE = "git tag -d deletes a tag. Tag deletion is not allowed."


def _analyze_git(tokens: list[str]) -> str | None:
    sub, rest = _git_subcommand_and_rest(tokens)
    if not sub:
        return None

    sub = sub.lower()
    rest_lower = [t.lower() for t in rest]
    short = _short_opts(rest)

    if sub == "checkout":
        # Block checkout -- (discard changes)
        if "--" in rest:
            idx = rest.index("--")
            return (
                _REASON_GIT_CHECKOUT_DOUBLE_DASH
                if idx == 0
                else _REASON_GIT_CHECKOUT_REF_DOUBLE_DASH
            )
        # Block branch creation
        if "-b" in rest_lower or "--orphan" in rest_lower:
            return _REASON_GIT_CHECKOUT_CREATE
        # Block branch switching (positional arg or "-" for previous branch)
        positional = [t for t in rest if not t.startswith("-") or t == "-"]
        if positional:
            return _REASON_GIT_CHECKOUT_BRANCH
        return None

    if sub == "switch":
        if "-h" in rest_lower or "--help" in rest_lower:
            return None
        if "-c" in rest_lower or "--create" in rest_lower:
            return _REASON_GIT_SWITCH_CREATE
        return _REASON_GIT_SWITCH

    if sub == "restore":
        if "-h" in rest_lower or "--help" in rest_lower or "--version" in rest_lower:
            return None
        if "--worktree" in rest_lower:
            return _REASON_GIT_RESTORE_WORKTREE
        if "--staged" in rest_lower:
            return None
        return _REASON_GIT_RESTORE

    if sub == "reset":
        if "--hard" in rest_lower:
            return _REASON_GIT_RESET_HARD
        if "--merge" in rest_lower:
            return _REASON_GIT_RESET_MERGE
        return None

    if sub == "clean":
        has_force = "--force" in rest_lower or "f" in short
        if has_force:
            return _REASON_GIT_CLEAN_FORCE
        return None

    if sub == "push":
        has_force_with_lease = any(
            t.startswith("--force-with-lease") for t in rest_lower
        )
        has_force = "--force" in rest_lower or "f" in short
        if has_force and not has_force_with_lease:
            return _REASON_GIT_PUSH_FORCE
        if "--force" in rest_lower and has_force_with_lease:
            return _REASON_GIT_PUSH_FORCE
        if "f" in short and has_force_with_lease:
            return _REASON_GIT_PUSH_FORCE
        return None

    if sub == "branch":
        # Block any deletion (-d or -D)
        if "-D" in rest or "D" in short or "-d" in rest or "d" in short:
            return _REASON_GIT_BRANCH_DELETE
        # Allow listing: no args, or only flags
        if not rest or all(t.startswith("-") for t in rest):
            return None
        # Has positional arg = creating a branch
        return _REASON_GIT_BRANCH_CREATE

    if sub == "stash":
        if not rest_lower:
            return None
        if rest_lower[0] == "drop":
            return _REASON_GIT_STASH_DROP
        if rest_lower[0] == "clear":
            return _REASON_GIT_STASH_CLEAR
        return None

    if sub == "rebase":
        if "-h" in rest_lower or "--help" in rest_lower:
            return None
        return _REASON_GIT_REBASE

    if sub == "commit":
        if "--amend" in rest_lower:
            return _REASON_GIT_COMMIT_AMEND
        return None

    if sub == "tag":
        if "-d" in rest_lower or "--delete" in rest_lower or "d" in short:
            return _REASON_GIT_TAG_DELETE
        return None

    return None


def _git_subcommand_and_rest(tokens: list[str]) -> tuple[str | None, list[str]]:
    if not tokens or tokens[0].lower() != "git":
        return None, []

    opts_with_value = {
        "-c",
        "-C",
        "--exec-path",
        "--git-dir",
        "--namespace",
        "--super-prefix",
        "--work-tree",
    }
    opts_no_value = {
        "-p",
        "-P",
        "-h",
        "--help",
        "--no-pager",
        "--paginate",
        "--version",
        "--bare",
        "--no-replace-objects",
        "--literal-pathspecs",
        "--noglob-pathspecs",
        "--icase-pathspecs",
    }

    i = 1
    while i < len(tokens):
        tok = tokens[i]
        if tok == "--":
            i += 1
            break

        if not tok.startswith("-") or tok == "-":
            break

        if tok in opts_no_value:
            i += 1
            continue

        if tok in opts_with_value:
            i += 2
            continue

        if tok.startswith("--"):
            if "=" in tok:
                opt, _value = tok.split("=", 1)
                if opt in opts_with_value:
                    i += 1
                    continue
            i += 1
            continue

        # Short options, possibly with attached values (e.g. -Crepo, -cname=value)
        if tok.startswith("-C") and len(tok) > 2:
            i += 1
            continue
        if tok.startswith("-c") and len(tok) > 2:
            i += 1
            continue

        i += 1

    if i >= len(tokens):
        return None, []

    sub = tokens[i]
    return sub, tokens[i + 1 :]
