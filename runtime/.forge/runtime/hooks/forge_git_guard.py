"""Forge git guard: a Claude Code PreToolUse hook for Bash.

Blocks git actions that forge-orchestrate must never take. Exit code 2 blocks
the command and shows stderr to the agent. Standard library only.

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

PROTECTED = {"main", "master"}
SEGMENT_SPLIT = re.compile(r"&&|\|\||;|\||&|\n|\$\(|`|\(|\)")
COMMAND_PREFIXES = {"sudo", "env", "command", "exec", "nohup", "time", "xargs"}
SHELLS = {"sh", "bash", "zsh", "dash"}
GIT_VALUE_OPTIONS = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--config-env", "--super-prefix"}
WORKER_BLOCKED = {"commit", "push", "merge", "rebase", "tag", "reset", "checkout", "switch", "stash", "clean", "restore"}
MERGE_CLI = re.compile(r"\b(gh\s+pr|glab\s+mr)\s+merge\b")


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


def check(command: str, role: str, cwd: str, protected: set[str]) -> str | None:
    """Return a block reason, or None when the command is allowed."""
    if MERGE_CLI.search(command):
        return "merging an MR/PR is a human action"
    for tokens in _segments(command):
        args = _git_args(tokens)
        if not args:
            continue
        sub, rest = args[0], args[1:]
        if role == "worker" and sub in WORKER_BLOCKED:
            return f"workers must not run 'git {sub}'; only the orchestrator handles git"
        if sub == "tag":
            return "tagging is a human action"
        if sub == "merge":
            return "merging is a human action"
        if sub == "push":
            flags = [a for a in rest if a.startswith("-")]
            if any(f in {"-f", "--force", "--force-with-lease", "--mirror", "--tags", "--delete", "-d", "--all"} or f.startswith("--force") for f in flags):
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
    protected = set(PROTECTED)
    default = _default_branch(cwd)
    if default:
        protected.add(default)
    reason = check(command, role, cwd, protected)
    if reason:
        print(f"Blocked by Forge git guard: {reason}.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
