"""CLI entrypoint for Forge Context Engine."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .install_manifest import DEFAULT_SELECTED_TOOLS, ALL_SUPPORTED_TOOLS, parse_tools_args
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
        nargs="+",
        help=(
            "Select one or more tools. Accepts values like `codex`, `claude`, `copilot`, `opencode`, `all`, "
            "comma-separated lists, or space-separated lists such as `--tools codex claude`."
        ),
    )
    init_parser.add_argument(
        "--tool",
        action="append",
        help="Repeatable single-tool selector, for example `--tool codex --tool claude`.",
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
        "--tools",
        nargs="+",
        help=(
            "Select one or more tools. Accepts values like `codex`, `claude`, `copilot`, `opencode`, `all`, "
            "comma-separated lists, or space-separated lists such as `--tools codex claude`."
        ),
    )
    update_parser.add_argument(
        "--tool",
        action="append",
        help="Repeatable single-tool selector, for example `--tool codex --tool claude`.",
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
    try:
        tools = _resolve_explicit_tools(args)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 2

    return run_update(
        target=args.target,
        dry_run=args.dry_run,
        assume_yes=args.yes,
        selected_tools=tools,
    )


def _resolve_tools(args: argparse.Namespace) -> tuple[str, ...]:
    """Resolve tool selection from flags or a short interactive prompt."""

    explicit_tools = _resolve_explicit_tools(args)
    if explicit_tools is not None:
        return explicit_tools
    if args.yes or not sys.stdin.isatty():
        return DEFAULT_SELECTED_TOOLS

    options = ", ".join(f"{index + 1}:{tool}" for index, tool in enumerate(ALL_SUPPORTED_TOOLS))
    prompt = (
        "Enable AI tools [codex,claude] "
        f"(options: {options}, 0:all; you can type names, numbers, comma, or spaces; default: codex,claude): "
    )
    try:
        response = input(prompt).strip()
    except EOFError:
        return DEFAULT_SELECTED_TOOLS

    return parse_tools_args(response or ",".join(DEFAULT_SELECTED_TOOLS))


def _resolve_explicit_tools(args: argparse.Namespace) -> tuple[str, ...] | None:
    raw_values: list[str] = []
    raw_values.extend(args.tools or [])
    raw_values.extend(args.tool or [])
    if not raw_values:
        return None
    return parse_tools_args(raw_values)


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
