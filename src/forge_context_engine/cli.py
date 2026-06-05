"""CLI entrypoint for Forge Context Engine."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .install_manifest import DEFAULT_SELECTED_TOOLS, parse_tools_arg
from .runtime_ops import run_init, run_update
from .version import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="forge",
        description="Forge Context Engine CLI",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command")

    init_parser = subparsers.add_parser(
        "init",
        help="Initialize Forge runtime files in the current repository (Batch B).",
    )
    init_parser.add_argument(
        "--workspace",
        action="store_true",
        help="Initialize the workspace profile instead of the default service profile.",
    )
    init_parser.add_argument(
        "--tools",
        help="Select tools: codex, claude, copilot, all, or comma combinations such as codex,claude.",
    )
    init_parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip confirmation prompts for operations that are already safe by policy.",
    )
    init_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview planned changes without writing files.",
    )
    init_parser.add_argument(
        "--target",
        type=Path,
        help="Optional automation/test target path. Current directory remains the default UX.",
    )
    init_parser.set_defaults(handler=_handle_init)

    update_parser = subparsers.add_parser(
        "update",
        help="Update Forge-managed runtime files in the current repository (Batch B).",
    )
    update_parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip confirmation prompts for operations that are already safe by policy.",
    )
    update_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview planned changes without writing files.",
    )
    update_parser.add_argument(
        "--target",
        type=Path,
        help="Optional automation/test target path. Current directory remains the default UX.",
    )
    update_parser.set_defaults(handler=_handle_update)

    return parser


def _handle_init(args: argparse.Namespace) -> int:
    try:
        tools = _resolve_tools(args)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 2

    profile = "workspace" if args.workspace else "service"
    return run_init(
        target=args.target,
        profile=profile,
        selected_tools=tools,
        dry_run=args.dry_run,
        assume_yes=args.yes,
    )


def _handle_update(args: argparse.Namespace) -> int:
    return run_update(
        target=args.target,
        dry_run=args.dry_run,
        assume_yes=args.yes,
    )


def _resolve_tools(args: argparse.Namespace) -> tuple[str, ...]:
    """Resolve tool selection from flags or a short interactive prompt."""

    if args.tools:
        return parse_tools_arg(args.tools)
    if args.yes or not sys.stdin.isatty():
        return DEFAULT_SELECTED_TOOLS

    prompt = (
        "Enable AI tools [codex,claude] "
        "(options: codex, claude, copilot, all; default: codex,claude): "
    )
    try:
        response = input(prompt).strip()
    except EOFError:
        return DEFAULT_SELECTED_TOOLS

    return parse_tools_arg(response or ",".join(DEFAULT_SELECTED_TOOLS))


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    handler = getattr(args, "handler", None)
    if handler is None:
        parser.print_help()
        return 0
    return handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
