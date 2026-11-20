"""Forge git guard: a Claude Code PreToolUse hook for Bash.

Blocks git actions that forge-orchestrate must never take. Exit code 2 blocks
the command and shows stderr to the agent. Standard library only.

The blocked command rules per role live in `.forge/runtime/meta/git-guard-rules.json`
so other hosts can enforce the same rules for non-Claude workers.

Usage (hook command):
  python3 -B "$CLAUDE_PROJECT_DIR/.forge/runtime/hooks/forge_git_guard.py" orchestrator
  python3 -B "$CLAUDE_PROJECT_DIR/.forge/runtime/hooks/forge_git_guard.py" worker
"""

from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

RULES_PATH = Path(__file__).resolve().parents[1] / "meta" / "git-guard-rules.json"
SEGMENT_SPLIT = re.compile(r"&&|\|\||;|\||&|\n|\$\(|`|\(|\)")
COMMAND_PREFIXES = {"sudo", "env", "command", "exec", "nohup", "time", "xargs"}
SHELLS = {"sh", "bash", "zsh", "dash"}
GIT_VALUE_OPTIONS = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--config-env", "--super-prefix"}


def _str_list(value: object) -> bool:
    return isinstance(value, list) and all(isinstance(v, str) for v in value)


def _str_map(value: object) -> bool:
    return isinstance(value, dict) and all(isinstance(k, str) and isinstance(v, str) and v.strip() for k, v in value.items())


def load_rules(path: Path = RULES_PATH) -> dict:
    """Load and validate the rules; raise ValueError on any shape problem so the hook fails closed."""
    rules = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(rules, dict) or not isinstance(rules.get("roles"), dict) or not rules["roles"]:
        raise ValueError("'roles' must be a non-empty object")
    for key in ("protected_branches", "forbidden_push_flags"):
        if not _str_list(rules.get(key)):
            raise ValueError(f"'{key}' must be a list of strings")
    for role, role_rules in rules["roles"].items():
        if not isinstance(role_rules, dict):
            raise ValueError(f"role '{role}' must be an object")
        for key in ("blocked_git", "blocked_patterns"):
            if not _str_map(role_rules.get(key)):
                raise ValueError(f"role '{role}': '{key}' must map strings to non-empty strings")
        for pattern in role_rules["blocked_patterns"]:
            try:
                re.compile(pattern)  # patterns must stay simple: they run on every Bash command
            except re.error as exc:
                raise ValueError(f"role '{role}': bad pattern {pattern!r}: {exc}") from exc
    return rules


def _default_branch(cwd: str) -> str | None:
    try:
        out = subprocess.run(
            ["git", "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD"],
            cwd=cwd, capture_output=True, text=True, timeout=5,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None
    return out.split("/", 1)[1] if "/" in out else None


def _current_branch(cwd: str) -> str | None:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=cwd, capture_output=True, text=True, timeout=5,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None
    return out or None


def _tokens(segment: str) -> list[str]:
    try:
        tokens = shlex.split(segment)
    except ValueError:
        tokens = segment.split()
    while tokens and (("=" in tokens[0] and not tokens[0].startswith("-")) or os.path.basename(tokens[0]) in COMMAND_PREFIXES):
        tokens = tokens[1:]  # leading VAR=value assignments and wrappers such as sudo/env
    return tokens


def _segments(command: str, depth: int = 0) -> list[list[str]]:
    """Split a shell command into token lists, descending into `sh -c '...'`."""
    result: list[list[str]] = []
    for segment in SEGMENT_SPLIT.split(command):
        tokens = _tokens(segment.strip())
        if not tokens:
            continue
        if depth < 3 and os.path.basename(tokens[0]) in SHELLS and "-c" in tokens[1:-1]:
            result.extend(_segments(tokens[tokens.index("-c") + 1], depth + 1))
            continue
        result.append(tokens)
    return result


def _git_args(tokens: list[str]) -> list[str] | None:
    if not tokens or os.path.basename(tokens[0]) != "git":
        return None
    args = tokens[1:]
    while args and args[0].startswith("-"):
        args = args[2:] if args[0] in GIT_VALUE_OPTIONS else args[1:]  # global options such as -C, --no-pager
    return args


def check(command: str, role: str, cwd: str, protected: set[str], rules: dict) -> str | None:
    """Return a block reason, or None when the command is allowed."""
    role_rules = rules["roles"].get(role)
    if role_rules is None:
        return f"unknown role '{role}'"
    for pattern, reason in role_rules["blocked_patterns"].items():
        if re.search(pattern, command):
            return reason
    blocked_git = role_rules["blocked_git"]
    forbidden_flags = set(rules["forbidden_push_flags"])
    for tokens in _segments(command):
        args = _git_args(tokens)
        if not args:
            continue
        sub, rest = args[0], args[1:]
        if sub in blocked_git:
            return blocked_git[sub]
        if sub == "push":
            flags = [a for a in rest if a.startswith("-")]
            if any(f in forbidden_flags or f.startswith("--force") for f in flags):
                return f"forbidden push option: {' '.join(flags)}"
            positional = [a for a in rest if not a.startswith("-")]
            refspecs = positional[1:]
            if any(r.startswith("+") for r in refspecs):
                return "force push via '+refspec' is forbidden"
            if any(r.startswith(":") for r in refspecs):
                return "deleting a remote branch via ':ref' is forbidden"
            current = _current_branch(cwd)
            targets = {r.split(":")[-1].removeprefix("refs/heads/") for r in refspecs}
            if not refspecs or "HEAD" in targets or "@" in targets:
                targets = (targets - {"HEAD", "@"}) | ({current} if current else set())
            hit = targets & protected
            if hit:
                return f"push to protected branch {sorted(hit)[0]} is forbidden; push the forge/ feature branch only"
    return None


def main(argv: list[str]) -> int:
    role = argv[1] if len(argv) > 1 else "orchestrator"
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    if payload.get("tool_name") != "Bash":
        return 0
    command = (payload.get("tool_input") or {}).get("command") or ""
    cwd = payload.get("cwd") or os.getcwd()
    try:
        rules = load_rules()
    except Exception as exc:  # fail closed: a missing or broken rules file blocks; exit 1 would not
        print(f"Blocked by Forge git guard: cannot read {RULES_PATH.name}: {exc}.", file=sys.stderr)
        return 2
    protected = set(rules["protected_branches"])
    default = _default_branch(cwd)
    if default:
        protected.add(default)
    try:
        reason = check(command, role, cwd, protected, rules)
    except Exception as exc:  # fail closed: exit 1 would let Claude Code run the command
        reason = f"internal error: {exc!r}"
    if reason:
        print(f"Blocked by Forge git guard: {reason}.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
