"""Runtime init/update operations for the Forge CLI."""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

from .fs_ops import resolve_target_paths, sha256_text, to_manifest_path
from .install_manifest import (
    DEFAULT_SELECTED_TOOLS,
    ForgeInstallManifest,
    PROFILE_SERVICE,
    PROFILE_WORKSPACE,
    build_manifest,
    dump_manifest,
    load_manifest,
)
from .managed_blocks import upsert_managed_block
from .runtime_templates import iter_template_files, read_template
from .version import __version__


FORGE_LOCAL_GITIGNORE = ".forge/temp/\n.forge/cache/\n"
COPILOT_TEMPLATE_PATH = ".github/copilot-instructions.md"
ENTRYPOINT_TEMPLATE_MAP = {
    "AGENTS.md": ("base", "AGENTS.md"),
    "CLAUDE.md": ("base", "CLAUDE.md"),
    COPILOT_TEMPLATE_PATH: ("copilot", ".github/copilot-instructions.md"),
}
REGULAR_MANAGED_HASH_EXCLUDES = {
    ".forge/forge-install.yaml",
    "AGENTS.md",
    "CLAUDE.md",
    COPILOT_TEMPLATE_PATH,
}
RUNTIME_MARKERS = (
    ".forge/adapter.md",
    ".forge/forge.config.yaml",
    ".forge/context/modes/ask.md",
)


@dataclass
class Operation:
    """One planned or executed filesystem operation."""

    status: str
    path: str
    detail: str = ""


@dataclass
class OperationReport:
    """Aggregate result for CLI commands."""

    dry_run: bool
    operations: list[Operation] = field(default_factory=list)

    def add(self, status: str, path: str, detail: str = "") -> None:
        self.operations.append(Operation(status=status, path=path, detail=detail))

    def statuses(self, *wanted: str) -> list[Operation]:
        return [op for op in self.operations if op.status in wanted]

    def print(self) -> None:
        print(f"DRY-RUN: {'yes' if self.dry_run else 'no'}")
        for op in self.operations:
            message = f"{op.status.upper():9} {op.path}"
            if op.detail:
                message = f"{message} - {op.detail}"
            print(message)


def run_init(
    *,
    target: Path | None,
    profile: str,
    selected_tools: tuple[str, ...],
    dry_run: bool,
    assume_yes: bool,
) -> int:
    """Initialize a service or workspace repo with Forge runtime files."""

    paths = resolve_target_paths(target)
    report = OperationReport(dry_run=dry_run)

    manifest_path = paths.forge_root / "forge-install.yaml"
    if manifest_path.exists():
        print(f"Forge is already initialized in {paths.target_root}. Use `forge update`.")
        return 1

    if _detect_runtime(paths.target_root):
        print(
            f"Existing Forge runtime detected in {paths.target_root} without a manifest. "
            "Use `forge update` for adoption-preview."
        )
        return 1

    desired_files = _build_init_files(
        target_root=paths.target_root,
        profile=profile,
        selected_tools=selected_tools,
    )

    conflicts = _apply_init_files(paths.target_root, desired_files, report, dry_run)
    _ensure_local_only_dirs(paths.target_root, report, dry_run)

    if conflicts:
        report.print()
        print("Initialization stopped with conflicts. No existing files were overwritten.")
        return 1

    manifest = _manifest_for_target(
        target_root=paths.target_root,
        profile=profile,
        selected_tools=selected_tools,
        desired_files=desired_files,
    )
    manifest_text = dump_manifest(manifest)
    _apply_regular_file(
        target_root=paths.target_root,
        path=manifest_path,
        content=manifest_text,
        report=report,
        dry_run=dry_run,
        init_mode=True,
    )

    report.print()
    return 0


def run_update(*, target: Path | None, dry_run: bool, assume_yes: bool) -> int:
    """Update only Forge-managed files using manifest state or adoption-preview."""

    paths = resolve_target_paths(target)
    report = OperationReport(dry_run=dry_run)
    manifest_path = paths.forge_root / "forge-install.yaml"

    if manifest_path.exists():
        manifest = load_manifest(manifest_path)
        _update_from_manifest(paths.target_root, manifest, report, dry_run)
        report.print()
        return 0 if not report.statuses("conflict") else 1

    if not _detect_runtime(paths.target_root):
        print(
            f"No Forge runtime detected in {paths.target_root}. "
            "Run `forge init` or `forge init --workspace` first."
        )
        return 1

    adopted_profile = _detect_profile(paths.target_root)
    adopted_tools = _detect_tools(paths.target_root)
    manifest = _manifest_from_current_runtime(
        target_root=paths.target_root,
        profile=adopted_profile,
        selected_tools=adopted_tools,
    )

    print("Adoption preview:")
    print(f"- target: {paths.target_root}")
    print(f"- profile: {adopted_profile}")
    print(f"- selected tools: {', '.join(adopted_tools)}")
    print(f"- managed paths: {', '.join(manifest.managed_paths)}")
    print(f"- user-owned paths: {', '.join(manifest.user_owned_paths)}")
    print(f"- local-only paths: {', '.join(manifest.local_only_paths)}")

    if dry_run:
        report.add("skipped", ".forge/forge-install.yaml", "adoption preview only")
        report.print()
        return 0

    if not assume_yes and not _confirm("Proceed with adoption and managed update? [y/N]: "):
        print("Adoption cancelled.")
        return 1

    manifest_text = dump_manifest(manifest)
    _apply_regular_file(
        target_root=paths.target_root,
        path=manifest_path,
        content=manifest_text,
        report=report,
        dry_run=False,
        init_mode=True,
    )
    _update_from_manifest(paths.target_root, manifest, report, dry_run=False)
    report.print()
    return 0 if not report.statuses("conflict") else 1


def _update_from_manifest(
    target_root: Path,
    manifest: ForgeInstallManifest,
    report: OperationReport,
    dry_run: bool,
) -> None:
    all_desired_files = _build_init_files(
        target_root=target_root,
        profile=manifest.profile,
        selected_tools=manifest.selected_tools,
    )
    desired_files = {
        rel_path: content
        for rel_path, content in all_desired_files.items()
        if _is_managed_file(rel_path, manifest.profile, manifest.selected_tools)
    }

    for rel_path, content in desired_files.items():
        if rel_path.endswith("workspace.yaml") and manifest.profile != PROFILE_WORKSPACE:
            continue
        path = target_root / rel_path
        if rel_path in ENTRYPOINT_TEMPLATE_MAP:
            _apply_entrypoint_file(
                target_root=target_root,
                path=path,
                content=content,
                report=report,
                dry_run=dry_run,
            )
            continue

        expected_hash = manifest.managed_file_hashes.get(rel_path)
        _apply_regular_file(
            target_root=target_root,
            path=path,
            content=content,
            report=report,
            dry_run=dry_run,
            init_mode=False,
            expected_hash=expected_hash,
        )

    _ensure_local_only_dirs(target_root, report, dry_run)

    updated_manifest = _manifest_for_target(
        target_root=target_root,
        profile=manifest.profile,
        selected_tools=manifest.selected_tools,
        desired_files=all_desired_files,
        installed_at=manifest.installed_at,
    )
    manifest_text = dump_manifest(updated_manifest)
    _apply_regular_file(
        target_root=target_root,
        path=target_root / ".forge/forge-install.yaml",
        content=manifest_text,
        report=report,
        dry_run=dry_run,
        init_mode=False,
    )


def _build_init_files(
    *,
    target_root: Path,
    profile: str,
    selected_tools: tuple[str, ...],
) -> dict[str, str]:
    files = {
        rel: content
        for rel, content in iter_template_files("base").items()
        if rel not in {"AGENTS.md", "CLAUDE.md"}
    }

    files[".forge/forge.config.yaml"] = _render_forge_config(selected_tools)
    files[".forge/.gitignore"] = FORGE_LOCAL_GITIGNORE

    if "codex" in selected_tools:
        files["AGENTS.md"] = read_template("base", "AGENTS.md")
    if "claude" in selected_tools:
        files["CLAUDE.md"] = read_template("base", "CLAUDE.md")
    if "copilot" in selected_tools:
        files[COPILOT_TEMPLATE_PATH] = read_template("copilot", COPILOT_TEMPLATE_PATH)
    if profile == PROFILE_WORKSPACE:
        files[".forge/workspace.yaml"] = _render_workspace_yaml(target_root.name, selected_tools)

    return files


def _apply_init_files(
    target_root: Path,
    desired_files: dict[str, str],
    report: OperationReport,
    dry_run: bool,
) -> bool:
    conflicts = False
    for rel_path, content in desired_files.items():
        path = target_root / rel_path
        if rel_path in ENTRYPOINT_TEMPLATE_MAP:
            if _apply_entrypoint_file(
                target_root=target_root,
                path=path,
                content=content,
                report=report,
                dry_run=dry_run,
            ):
                conflicts = True
            continue
        if _apply_regular_file(
            target_root=target_root,
            path=path,
            content=content,
            report=report,
            dry_run=dry_run,
            init_mode=True,
        ):
            conflicts = True
    return conflicts


def _apply_entrypoint_file(
    *,
    target_root: Path,
    path: Path,
    content: str,
    report: OperationReport,
    dry_run: bool,
) -> bool:
    rel_path = to_manifest_path(target_root, path)
    if path.exists():
        existing = path.read_text(encoding="utf-8")
        updated, action = upsert_managed_block(existing, content)
        if updated == existing:
            report.add("skipped", rel_path, "already current")
            return False
        if dry_run:
            report.add(action, rel_path, "entrypoint managed block")
            return False
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(updated, encoding="utf-8")
        report.add(action, rel_path, "entrypoint managed block")
        return False

    if dry_run:
        report.add("created", rel_path, "entrypoint managed block")
        return False

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(upsert_managed_block("", content)[0], encoding="utf-8")
    report.add("created", rel_path, "entrypoint managed block")
    return False


def _apply_regular_file(
    *,
    target_root: Path,
    path: Path,
    content: str,
    report: OperationReport,
    dry_run: bool,
    init_mode: bool,
    expected_hash: str | None = None,
) -> bool:
    rel_path = to_manifest_path(target_root, path)
    if path.exists():
        existing = path.read_text(encoding="utf-8")
        if existing == content:
            report.add("skipped", rel_path, "already current")
            return False
        if init_mode:
            report.add("conflict", rel_path, "existing file would be overwritten")
            return True
        if rel_path == ".forge/forge-install.yaml":
            if dry_run:
                report.add("updated", rel_path, "install manifest refresh")
                return False
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            report.add("updated", rel_path, "install manifest refresh")
            return False
        if expected_hash is None:
            report.add("conflict", rel_path, "managed file hash unavailable for safe update")
            return True
        if sha256_text(existing) != expected_hash:
            report.add("conflict", rel_path, "managed file modified locally")
            return True
        if dry_run:
            report.add("updated", rel_path, "managed file refresh")
            return False
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        report.add("updated", rel_path, "managed file refresh")
        return False

    if dry_run:
        report.add("created", rel_path, "managed file")
        return False

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    report.add("created", rel_path, "managed file")
    return False


def _ensure_local_only_dirs(target_root: Path, report: OperationReport, dry_run: bool) -> None:
    for rel in (".forge/temp", ".forge/cache", ".forge/context-patches", ".forge/context/repo-map"):
        path = target_root / rel
        if path.exists():
            report.add("skipped", rel, "directory exists")
            continue
        if dry_run:
            report.add("created", rel, "directory")
            continue
        path.mkdir(parents=True, exist_ok=True)
        report.add("created", rel, "directory")


def _manifest_for_target(
    *,
    target_root: Path,
    profile: str,
    selected_tools: tuple[str, ...],
    desired_files: dict[str, str],
    installed_at: str | None = None,
) -> ForgeInstallManifest:
    managed_hashes = {
        path: sha256_text(content)
        for path, content in desired_files.items()
        if _is_managed_file(path, profile, selected_tools) and path not in REGULAR_MANAGED_HASH_EXCLUDES
    }
    return build_manifest(
        profile=profile,
        selected_tools=selected_tools,
        managed_file_hashes=managed_hashes,
        installed_at=installed_at,
    )


def _manifest_from_current_runtime(
    *,
    target_root: Path,
    profile: str,
    selected_tools: tuple[str, ...],
) -> ForgeInstallManifest:
    desired_files = _build_init_files(
        target_root=target_root,
        profile=profile,
        selected_tools=selected_tools,
    )
    managed_hashes: dict[str, str] = {}
    for rel_path in desired_files:
        if not _is_managed_file(rel_path, profile, selected_tools):
            continue
        if rel_path in REGULAR_MANAGED_HASH_EXCLUDES:
            continue
        path = target_root / rel_path
        if path.exists():
            managed_hashes[rel_path] = sha256_text(path.read_text(encoding="utf-8"))
    return build_manifest(
        profile=profile,
        selected_tools=selected_tools,
        managed_file_hashes=managed_hashes,
    )


def _render_forge_config(selected_tools: tuple[str, ...]) -> str:
    adapters = _yaml_list(selected_tools)
    default_adapter = selected_tools[0]
    package_targets = _yaml_list(selected_tools)
    return (
        "# forge-context-engine - Engine Configuration\n"
        "# Not a narrative context file. Customize during Context Initialization for the target repo.\n\n"
        "forge:\n"
        f'  version: "{__version__}"\n\n'
        "run:\n"
        "  interaction: manual\n"
        "  output: human\n"
        "  output_detail: standard\n"
        "  write_behavior: draft\n"
        "  failure_behavior: stop\n\n"
        "workflow:\n"
        "  default_mode: ask\n"
        "  disabled_modes: []\n\n"
        "context:\n"
        "  root: .forge/context\n"
        "  budget_profile: standard\n\n"
        "policy:\n"
        "  high_risk_areas:\n"
        "    - payments\n"
        "    - authentication\n"
        "    - authorization\n"
        "    - public_api\n"
        "    - database_migrations\n"
        "    - secrets\n"
        "    - external_provider_integration\n"
        "    - file_upload\n"
        "  require_human_confirmation_for:\n"
        "    - domain_rule_change\n"
        "    - data_mutation_change\n"
        "    - architecture_boundary_change\n"
        "    - external_contract_change\n"
        "    - security_boundary_change\n"
        "    - migration_change\n\n"
        "team:\n"
        "  context_update_flow: reviewable_patch\n"
        "  require_context_impact_check: true\n\n"
        "artifacts:\n"
        "  output_dir: .forge/generated\n"
        "  patch_dir: .forge/context-patches\n"
        "  temp_dir: .forge/temp\n"
        "  cache_dir: .forge/cache\n"
        "  commit_policy: manual\n"
        "  mr_policy: include_when_relevant\n\n"
        "tools:\n"
        "  adapters:\n"
        f"{adapters}"
        f"  default_adapter: {default_adapter}\n"
        "  validation_commands: []\n"
        "  package_targets:\n"
        f"{package_targets}"
    )


def _render_workspace_yaml(name: str, selected_tools: tuple[str, ...]) -> str:
    tools = "".join(f"  - {tool}\n" for tool in selected_tools or DEFAULT_SELECTED_TOOLS)
    return (
        "version: 1\n"
        f"name: {name}\n"
        "linked_services: []\n"
        "default_tools:\n"
        f"{tools}"
    )


def _yaml_list(items: tuple[str, ...]) -> str:
    return "".join(f"    - {item}\n" for item in items)


def _detect_runtime(target_root: Path) -> bool:
    return any((target_root / marker).exists() for marker in RUNTIME_MARKERS)


def _detect_profile(target_root: Path) -> str:
    if (target_root / ".forge/workspace.yaml").exists():
        return PROFILE_WORKSPACE
    return PROFILE_SERVICE


def _detect_tools(target_root: Path) -> tuple[str, ...]:
    selected: list[str] = []
    if (target_root / "AGENTS.md").exists():
        selected.append("codex")
    if (target_root / "CLAUDE.md").exists():
        selected.append("claude")
    if (target_root / ".github/copilot-instructions.md").exists():
        selected.append("copilot")
    return tuple(selected) or DEFAULT_SELECTED_TOOLS


def _is_managed_file(rel_path: str, profile: str, selected_tools: tuple[str, ...]) -> bool:
    if rel_path == ".forge/.gitignore":
        return True
    if rel_path == "AGENTS.md":
        return "codex" in selected_tools
    if rel_path == "CLAUDE.md":
        return "claude" in selected_tools
    if rel_path == COPILOT_TEMPLATE_PATH:
        return "copilot" in selected_tools
    if rel_path in {".forge/adapter.md", ".forge/forge.config.yaml"}:
        return True
    if rel_path == ".forge/workspace.yaml":
        return profile == PROFILE_WORKSPACE
    return rel_path.startswith(".forge/context/00-meta/") or rel_path.startswith(".forge/context/modes/")


def _confirm(prompt: str) -> bool:
    if not sys.stdin.isatty():
        print("Confirmation required. Re-run with --yes in non-interactive mode.")
        return False
    try:
        response = input(prompt).strip().lower()
    except EOFError:
        return False
    return response in {"y", "yes"}
