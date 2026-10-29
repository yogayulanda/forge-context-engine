"""CLI entrypoint for Forge Context Engine."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import autopilot
from .install_manifest import DEFAULT_SELECTED_TOOLS, ALL_SUPPORTED_TOOLS, parse_tools_args
from .runtime_ops import run_init, run_migrate_context, run_update
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

    migrate_parser = subparsers.add_parser(
        "migrate-context",
        help="Migrate legacy Forge context layouts to numbered v2 context files.",
    )
    migrate_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview context migration changes without writing files.",
    )
    migrate_parser.add_argument(
        "--target",
        type=Path,
        help="Optional automation/test target path. Current directory remains the default UX.",
    )
    migrate_parser.set_defaults(handler=_handle_migrate_context)

    _add_run_parser(subparsers)

    return parser


def _add_run_parser(subparsers: argparse._SubParsersAction) -> None:
    run_parser = subparsers.add_parser(
        "run",
        help="Opt-in autopilot control plane (specs/autopilot.md).",
    )
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true", help="Machine-readable output for orchestrators.")
    common.add_argument("--target", type=Path, help="Repository root. Defaults to the current directory.")
    run_sub = run_parser.add_subparsers(dest="run_command", required=True)

    start = run_sub.add_parser("start", parents=[common], help="Start a run from md:<path> or text:<path>.")
    start.add_argument("source")
    start.add_argument("--title")

    run_sub.add_parser("list", parents=[common], help="List runs with stage, status, and PR links.")

    status = run_sub.add_parser("status", parents=[common], help="Show a run as a stage checklist.")
    status.add_argument("run_id", nargs="?")

    dispatch = run_sub.add_parser("dispatch", parents=[common], help="Spawn the role agent configured for a stage.")
    dispatch.add_argument("run_id")
    dispatch.add_argument("--stage", required=True)
    dispatch.add_argument("--prompt-file", type=Path, required=True)

    submit = run_sub.add_parser("submit", parents=[common], help="Record an artifact the orchestrator produced itself.")
    submit.add_argument("run_id")
    submit.add_argument("--stage", required=True)
    submit.add_argument("--file", type=Path, required=True)

    gate = run_sub.add_parser("gate", parents=[common], help="Evaluate a stage gate and advance on pass.")
    gate.add_argument("run_id")
    gate.add_argument("--stage", required=True)

    report = run_sub.add_parser("report", parents=[common], help="Write the run report.")
    report.add_argument("run_id")

    stop = run_sub.add_parser("stop", parents=[common], help="Cancel a run; keep worktree and state.")
    stop.add_argument("run_id")

    resume = run_sub.add_parser("resume", parents=[common], help="Resume a blocked run at its current stage.")
    resume.add_argument("run_id")

    run_parser.set_defaults(handler=_handle_run)


def _handle_run(args: argparse.Namespace) -> int:
    repo = autopilot.Repo((args.target or Path.cwd()).resolve())
    try:
        result = _dispatch_run(repo, args)
    except autopilot.AutopilotError as exc:
        if args.json:
            print(json.dumps({"ok": False, "error": str(exc)}))
        else:
            print(f"ERROR: {exc}")
        return 2
    if args.json:
        print(json.dumps({"ok": True, **result}, indent=2))
    else:
        print(result.get("text") or json.dumps(result, indent=2))
    return 0


def _dispatch_run(repo: autopilot.Repo, args: argparse.Namespace) -> dict:
    command = args.run_command
    if command == "start":
        state = autopilot.start_run(repo, args.source, args.title)
        return {"run_id": state["run_id"], "stage": state["stage"], "worktree": state["worktree"],
                "branch": state["branch"], "text": autopilot.render_status(state)}
    if command == "list":
        runs = autopilot.list_runs(repo)
        text = "\n".join(f"{r['run_id']}  {r['status']}  {r['stage']}  {r['pr_url']}" for r in runs) or "no runs"
        return {"runs": [{k: r[k] for k in ("run_id", "status", "stage", "pr_url")} for r in runs], "text": text}
    if command == "status":
        run_id = args.run_id
        if not run_id:
            runs = autopilot.list_runs(repo)
            if not runs:
                raise autopilot.AutopilotError("no runs")
            run_id = runs[-1]["run_id"]
        state = autopilot.load_state(repo, run_id)
        return {**{k: state[k] for k in ("run_id", "status", "stage", "blocked_reason", "high_risk", "decisions", "pr_url")},
                "text": autopilot.render_status(state)}
    if command == "dispatch":
        return autopilot.dispatch(repo, args.run_id, args.stage, args.prompt_file)
    if command == "submit":
        return autopilot.submit(repo, args.run_id, args.stage, args.file)
    if command == "gate":
        return autopilot.gate(repo, args.run_id, args.stage)
    if command == "report":
        state = autopilot.load_state(repo, args.run_id)
        return {"run_id": args.run_id, "report": str(autopilot.write_report(repo, state))}
    if command == "stop":
        state = autopilot.stop_run(repo, args.run_id)
        return {"run_id": args.run_id, "status": state["status"]}
    if command == "resume":
        state = autopilot.resume_run(repo, args.run_id)
        return {"run_id": args.run_id, "status": state["status"], "stage": state["stage"]}
    raise autopilot.AutopilotError(f"unknown run command: {command}")


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


def _handle_migrate_context(args: argparse.Namespace) -> int:
    return run_migrate_context(
        target=args.target,
        dry_run=args.dry_run,
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
        "Enable AI tools [codex,copilot] "
        f"(options: {options}, 0:all; you can type names, numbers, comma, or spaces; default: codex,copilot): "
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
