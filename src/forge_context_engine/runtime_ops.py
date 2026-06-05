"""Runtime init/update operations for the Forge CLI."""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

from .fs_ops import normalize_text, resolve_target_paths, sha256_text, to_manifest_path
from .install_manifest import (
    DEFAULT_SELECTED_TOOLS,
    ForgeInstallManifest,
    PROFILE_SERVICE,
    PROFILE_WORKSPACE,
    USER_OWNED_PATHS_BASELINE,
    LOCAL_ONLY_PATHS_BASELINE,
    build_manifest,
    dump_manifest,
    load_manifest,
)
from .managed_blocks import has_managed_block, upsert_managed_block
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
UI_LANGUAGE_EN = "en"
UI_LANGUAGE_ID = "id"
SUPPORTED_UI_LANGUAGES = (UI_LANGUAGE_EN, UI_LANGUAGE_ID)
DETAIL_CURRENT = "already current"
DETAIL_MANAGED_FILE = "managed file"
DETAIL_MANAGED_REFRESH = "managed file refresh"
DETAIL_ENTRYPOINT = "entrypoint managed block"
DETAIL_INSTALL_MANIFEST = "install manifest refresh"
DETAIL_CONFLICT_EXISTING = "existing file would be overwritten"
DETAIL_CONFLICT_HASH = "managed file hash unavailable for safe update"
DETAIL_CONFLICT_LOCAL = "managed file modified locally"
DETAIL_PRESERVED_NON_SELECTED = "existing non-selected entrypoint preserved"
DETAIL_ADOPTION_PREVIEW = "adoption preview only"
DETAIL_LEGACY_PRESERVED = "legacy managed file preserved; current hash adopted"
DETAIL_LEGACY_CONFIG_MIGRATION = "legacy config migration"
DETAIL_ENTRYPOINT_ADOPTED = "existing Forge-like wrapper adopted"


MESSAGES = {
    UI_LANGUAGE_EN: {
        "init_title": "Forge init",
        "update_title": "Forge update",
        "dry_run_suffix": "dry-run",
        "target": "Target",
        "profile": "Profile",
        "selected_tools": "Selected tools",
        "detected_tools": "Detected tools",
        "tool_selection_change": "Tool selection change",
        "mode": "Mode",
        "managed_files": "Managed file checks",
        "preserved_paths": "Preserved paths",
        "user_owned": "user-owned",
        "local_only": "local-only",
        "notes": "Notes",
        "summary": "Summary",
        "managed_checked": "Managed files checked",
        "created": "Created",
        "updated": "Updated",
        "unchanged": "Unchanged",
        "skipped": "Skipped",
        "conflicts": "Conflicts",
        "preserved_user_count": "User-owned paths preserved",
        "preserved_local_count": "Local-only paths preserved",
        "initialized_use_update": "Forge is already initialized in {target}. Use `forge update`.",
        "initialized_use_update_tools": (
            "Forge is already initialized in {target}. "
            "Use `forge update --tools {tools}` to change enabled tools."
        ),
        "runtime_without_manifest": (
            "Existing Forge runtime detected in {target} without a manifest. "
            "Use `forge update` for adoption-preview."
        ),
        "runtime_without_manifest_tools": (
            "Existing Forge runtime detected in {target} without a manifest. "
            "Use `forge update --tools {tools}` to adopt and change enabled tools."
        ),
        "init_conflicts": "Initialization stopped with conflicts. No existing files were overwritten.",
        "no_runtime": "No Forge runtime detected in {target}. Run `forge init` or `forge init --workspace` first.",
        "adoption_detected_narrower": (
            "Detected tools were narrowed from existing entrypoints. "
            "Use `forge update --tools {tools}` to add more tools."
        ),
        "adoption_override": "Using `--tools {tools}` for adoption instead of detected entrypoints.",
        "adoption_confirm": "Proceed with adoption and managed update? [y/N]: ",
        "adoption_cancelled": "Adoption cancelled.",
        "confirm_non_interactive": "Confirmation required. Re-run with --yes in non-interactive mode.",
        "adoption_mode": "adoption",
        "manifest_mode": "manifest",
    },
    UI_LANGUAGE_ID: {
        "init_title": "Forge init",
        "update_title": "Forge update",
        "dry_run_suffix": "dry-run",
        "target": "Target",
        "profile": "Profile",
        "selected_tools": "Selected tools",
        "detected_tools": "Detected tools",
        "tool_selection_change": "Perubahan tool",
        "mode": "Mode",
        "managed_files": "Pemeriksaan file terkelola",
        "preserved_paths": "Path yang dipertahankan",
        "user_owned": "user-owned",
        "local_only": "local-only",
        "notes": "Catatan",
        "summary": "Ringkasan",
        "managed_checked": "Managed files checked",
        "created": "Created",
        "updated": "Updated",
        "unchanged": "Unchanged",
        "skipped": "Skipped",
        "conflicts": "Conflicts",
        "preserved_user_count": "User-owned paths preserved",
        "preserved_local_count": "Local-only paths preserved",
        "initialized_use_update": "Forge sudah diinisialisasi di {target}. Gunakan `forge update`.",
        "initialized_use_update_tools": (
            "Forge sudah diinisialisasi di {target}. "
            "Gunakan `forge update --tools {tools}` untuk mengubah tool yang aktif."
        ),
        "runtime_without_manifest": (
            "Runtime Forge sudah ada di {target} tanpa manifest. "
            "Gunakan `forge update` untuk adoption-preview."
        ),
        "runtime_without_manifest_tools": (
            "Runtime Forge sudah ada di {target} tanpa manifest. "
            "Gunakan `forge update --tools {tools}` untuk adopt sekaligus mengubah tool yang aktif."
        ),
        "init_conflicts": "Inisialisasi dihentikan karena ada konflik. File yang sudah ada tidak ditimpa.",
        "no_runtime": "Runtime Forge tidak ditemukan di {target}. Jalankan `forge init` atau `forge init --workspace` terlebih dahulu.",
        "adoption_detected_narrower": (
            "Tool terdeteksi lebih sempit dari entrypoint yang ada. "
            "Gunakan `forge update --tools {tools}` untuk menambahkan tool."
        ),
        "adoption_override": "Menggunakan `--tools {tools}` untuk adoption, bukan entrypoint yang terdeteksi.",
        "adoption_confirm": "Lanjutkan adoption dan managed update? [y/N]: ",
        "adoption_cancelled": "Adoption dibatalkan.",
        "confirm_non_interactive": "Butuh konfirmasi. Jalankan ulang dengan `--yes` pada mode non-interaktif.",
        "adoption_mode": "adoption",
        "manifest_mode": "manifest",
    },
}

STATUS_LABELS = {
    UI_LANGUAGE_EN: {
        "created": "created",
        "updated": "updated",
        "unchanged": "unchanged",
        "skipped": "skipped",
        "conflict": "conflict",
    },
    UI_LANGUAGE_ID: {
        "created": "dibuat",
        "updated": "diperbarui",
        "unchanged": "tetap",
        "skipped": "dilewati",
        "conflict": "konflik",
    },
}


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
    notes: list[str] = field(default_factory=list)
    preserved_user_paths: list[str] = field(default_factory=list)
    preserved_local_paths: list[str] = field(default_factory=list)
    managed_hash_overrides: dict[str, str] = field(default_factory=dict)
    managed_checked: int = 0

    def add(self, status: str, path: str, detail: str = "") -> None:
        self.operations.append(Operation(status=status, path=path, detail=detail))
        if status in {"created", "updated", "unchanged", "conflict"}:
            self.managed_checked += 1

    def add_note(self, note: str) -> None:
        self.notes.append(note)

    def mark_preserved(self, kind: str, path: str) -> None:
        if kind == "user":
            self.preserved_user_paths.append(path)
            return
        self.preserved_local_paths.append(path)

    def override_hash(self, path: str, digest: str) -> None:
        self.managed_hash_overrides[path] = digest

    def statuses(self, *wanted: str) -> list[Operation]:
        return [op for op in self.operations if op.status in wanted]

    def count(self, status: str) -> int:
        return sum(1 for op in self.operations if op.status == status)

    def print(self, *, locale: str, title: str, context: list[tuple[str, str]]) -> None:
        messages = MESSAGES[locale]
        status_labels = STATUS_LABELS[locale]
        rendered_title = f"{title} ({messages['dry_run_suffix']})" if self.dry_run else title
        print(rendered_title)
        for label, value in context:
            print(f"{label}: {value}")

        if self.notes:
            print()
            print(f"{messages['notes']}:")
            for note in self.notes:
                print(f"- {note}")

        if self.operations:
            print()
            print(f"{messages['managed_files']}:")
            for op in self.operations:
                label = status_labels[op.status]
                line = f"  {label:10} {op.path}"
                if op.detail:
                    line = f"{line} - {op.detail}"
                print(line)

        if self.preserved_user_paths or self.preserved_local_paths:
            print()
            print(f"{messages['preserved_paths']}:")
            if self.preserved_user_paths:
                print(f"  {messages['user_owned']}: {', '.join(self.preserved_user_paths)}")
            if self.preserved_local_paths:
                print(f"  {messages['local_only']}: {', '.join(self.preserved_local_paths)}")

        print()
        print(f"{messages['summary']}:")
        print(f"  {messages['managed_checked']}: {self.managed_checked}")
        print(f"  {messages['created']}: {self.count('created')}")
        print(f"  {messages['updated']}: {self.count('updated')}")
        print(f"  {messages['unchanged']}: {self.count('unchanged')}")
        print(f"  {messages['skipped']}: {self.count('skipped')}")
        print(f"  {messages['conflicts']}: {self.count('conflict')}")
        print(f"  {messages['preserved_user_count']}: {len(self.preserved_user_paths)}")
        print(f"  {messages['preserved_local_count']}: {len(self.preserved_local_paths)}")


def run_init(
    *,
    target: Path | None,
    profile: str,
    selected_tools: tuple[str, ...],
    dry_run: bool,
    assume_yes: bool,
) -> int:
    """Initialize a service or workspace repo with Forge runtime files."""

    del assume_yes
    paths = resolve_target_paths(target)
    locale = _read_ui_language(paths.target_root)
    report = OperationReport(dry_run=dry_run)
    manifest_path = paths.forge_root / "forge-install.yaml"

    if manifest_path.exists():
        if selected_tools != DEFAULT_SELECTED_TOOLS:
            print(
                _msg(
                    locale,
                    "initialized_use_update_tools",
                    target=str(paths.target_root),
                    tools=",".join(selected_tools),
                )
            )
        else:
            print(_msg(locale, "initialized_use_update", target=str(paths.target_root)))
        return 1

    if _detect_runtime(paths.target_root):
        if selected_tools != DEFAULT_SELECTED_TOOLS:
            print(
                _msg(
                    locale,
                    "runtime_without_manifest_tools",
                    target=str(paths.target_root),
                    tools=",".join(selected_tools),
                )
            )
        else:
            print(_msg(locale, "runtime_without_manifest", target=str(paths.target_root)))
        return 1

    desired_files = _build_init_files(
        target_root=paths.target_root,
        profile=profile,
        selected_tools=selected_tools,
        ui_language=UI_LANGUAGE_EN,
    )
    conflicts = _apply_init_files(paths.target_root, desired_files, report, dry_run)
    _ensure_local_only_dirs(paths.target_root, report, dry_run)
    _mark_preserved_baselines(report)

    if conflicts:
        _print_report(
            report=report,
            locale=UI_LANGUAGE_EN,
            title=_msg(UI_LANGUAGE_EN, "init_title"),
            target_root=paths.target_root,
            profile=profile,
            selected_tools=selected_tools,
            mode="manifest",
        )
        print(_msg(UI_LANGUAGE_EN, "init_conflicts"))
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
    _print_report(
        report=report,
        locale=UI_LANGUAGE_EN,
        title=_msg(UI_LANGUAGE_EN, "init_title"),
        target_root=paths.target_root,
        profile=profile,
        selected_tools=selected_tools,
        mode="manifest",
    )
    return 0


def run_update(
    *,
    target: Path | None,
    dry_run: bool,
    assume_yes: bool,
    selected_tools: tuple[str, ...] | None,
) -> int:
    """Update only Forge-managed files using manifest state or adoption-preview."""

    paths = resolve_target_paths(target)
    locale = _read_ui_language(paths.target_root)
    report = OperationReport(dry_run=dry_run)
    manifest_path = paths.forge_root / "forge-install.yaml"

    if manifest_path.exists():
        manifest = load_manifest(manifest_path)
        effective_tools = selected_tools or manifest.selected_tools
        if effective_tools != manifest.selected_tools:
            report.add_note(
                f"{_msg(locale, 'tool_selection_change')}: "
                f"{', '.join(manifest.selected_tools)} -> {', '.join(effective_tools)}"
            )
        if not dry_run:
            preview = OperationReport(dry_run=True)
            preview.notes.extend(report.notes)
            _update_from_manifest(
                target_root=paths.target_root,
                manifest=manifest,
                selected_tools=effective_tools,
                ui_language=locale,
                report=preview,
                dry_run=True,
            )
            if preview.statuses("conflict"):
                _print_report(
                    report=preview,
                    locale=locale,
                    title=_msg(locale, "update_title"),
                    target_root=paths.target_root,
                    profile=manifest.profile,
                    selected_tools=effective_tools,
                    mode="manifest",
                )
                return 1
        _update_from_manifest(
            target_root=paths.target_root,
            manifest=manifest,
            selected_tools=effective_tools,
            ui_language=locale,
            report=report,
            dry_run=dry_run,
        )
        _print_report(
            report=report,
            locale=locale,
            title=_msg(locale, "update_title"),
            target_root=paths.target_root,
            profile=manifest.profile,
            selected_tools=effective_tools,
            mode="manifest",
        )
        return 0 if not report.statuses("conflict") else 1

    if not _detect_runtime(paths.target_root):
        print(_msg(locale, "no_runtime", target=str(paths.target_root)))
        return 1

    adopted_profile = _detect_profile(paths.target_root)
    detected_tools = _detect_tools(paths.target_root)
    effective_tools = selected_tools or detected_tools
    if selected_tools and selected_tools != detected_tools:
        report.add_note(_msg(locale, "adoption_override", tools=",".join(selected_tools)))
    elif selected_tools is None and detected_tools != DEFAULT_SELECTED_TOOLS:
        report.add_note(
            _msg(locale, "adoption_detected_narrower", tools=",".join(DEFAULT_SELECTED_TOOLS))
        )

    manifest = _manifest_from_current_runtime(
        target_root=paths.target_root,
        profile=adopted_profile,
        selected_tools=effective_tools,
    )
    if dry_run:
        report.add("skipped", ".forge/forge-install.yaml", DETAIL_ADOPTION_PREVIEW)
        _update_from_manifest(
            target_root=paths.target_root,
            manifest=manifest,
            selected_tools=effective_tools,
            ui_language=locale,
            report=report,
            dry_run=True,
        )
        _print_report(
            report=report,
            locale=locale,
            title=_msg(locale, "update_title"),
            target_root=paths.target_root,
            profile=adopted_profile,
            selected_tools=effective_tools,
            mode="adoption",
            detected_tools=detected_tools,
        )
        return 0

    if not assume_yes and not _confirm(_msg(locale, "adoption_confirm"), locale=locale):
        print(_msg(locale, "adoption_cancelled"))
        return 1

    preview = OperationReport(dry_run=True)
    preview.notes.extend(report.notes)
    manifest_text = dump_manifest(manifest)
    _apply_regular_file(
        target_root=paths.target_root,
        path=manifest_path,
        content=manifest_text,
        report=preview,
        dry_run=True,
        init_mode=True,
    )
    _update_from_manifest(
        target_root=paths.target_root,
        manifest=manifest,
        selected_tools=effective_tools,
        ui_language=locale,
        report=preview,
        dry_run=True,
    )
    if preview.statuses("conflict"):
        _print_report(
            report=preview,
            locale=locale,
            title=_msg(locale, "update_title"),
            target_root=paths.target_root,
            profile=adopted_profile,
            selected_tools=effective_tools,
            mode="adoption",
            detected_tools=detected_tools,
        )
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
    _update_from_manifest(
        target_root=paths.target_root,
        manifest=manifest,
        selected_tools=effective_tools,
        ui_language=locale,
        report=report,
        dry_run=False,
    )
    _print_report(
        report=report,
        locale=locale,
        title=_msg(locale, "update_title"),
        target_root=paths.target_root,
        profile=adopted_profile,
        selected_tools=effective_tools,
        mode="adoption",
        detected_tools=detected_tools,
    )
    return 0 if not report.statuses("conflict") else 1


def _update_from_manifest(
    *,
    target_root: Path,
    manifest: ForgeInstallManifest,
    selected_tools: tuple[str, ...],
    ui_language: str,
    report: OperationReport,
    dry_run: bool,
) -> None:
    all_desired_files = _build_init_files(
        target_root=target_root,
        profile=manifest.profile,
        selected_tools=selected_tools,
        ui_language=ui_language,
    )
    desired_files = {
        rel_path: content
        for rel_path, content in all_desired_files.items()
        if _is_managed_file(rel_path, manifest.profile, selected_tools)
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

    _preserve_non_selected_entrypoints(
        target_root=target_root,
        selected_tools=selected_tools,
        report=report,
    )
    _ensure_local_only_dirs(target_root, report, dry_run)

    updated_manifest = _manifest_for_target(
        target_root=target_root,
        profile=manifest.profile,
        selected_tools=selected_tools,
        desired_files=all_desired_files,
        installed_at=manifest.installed_at,
        hash_overrides=report.managed_hash_overrides,
    )
    _mark_preserved_paths(report, updated_manifest)
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
    ui_language: str,
) -> dict[str, str]:
    files = {
        rel: content
        for rel, content in iter_template_files("base").items()
        if rel not in {"AGENTS.md", "CLAUDE.md", ".forge/forge.config.yaml"}
    }

    files[".forge/forge.config.yaml"] = _render_forge_config(
        selected_tools=selected_tools,
        ui_language=ui_language,
    )
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
        if not has_managed_block(existing) and _is_wrapper_like_entrypoint(existing):
            report.add("unchanged", rel_path, DETAIL_ENTRYPOINT_ADOPTED)
            return False
        updated, action = upsert_managed_block(existing, content)
        if normalize_text(updated) == normalize_text(existing):
            report.add("unchanged", rel_path, DETAIL_CURRENT)
            return False
        if dry_run:
            report.add(action, rel_path, DETAIL_ENTRYPOINT)
            return False
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(updated, encoding="utf-8")
        report.add(action, rel_path, DETAIL_ENTRYPOINT)
        return False

    if dry_run:
        report.add("created", rel_path, DETAIL_ENTRYPOINT)
        return False

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(upsert_managed_block("", content)[0], encoding="utf-8")
    report.add("created", rel_path, DETAIL_ENTRYPOINT)
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
        if normalize_text(existing) == normalize_text(content):
            report.add("unchanged", rel_path, DETAIL_CURRENT)
            return False
        if init_mode:
            report.add("conflict", rel_path, DETAIL_CONFLICT_EXISTING)
            return True
        if rel_path == ".forge/forge.config.yaml" and _looks_like_legacy_forge_config(existing):
            backup_path = _next_legacy_config_backup_path(target_root)
            backup_rel = to_manifest_path(target_root, backup_path)
            report.add_note(
                f"Legacy config migration: back up .forge/forge.config.yaml to {backup_rel} before overwrite."
            )
            if dry_run:
                report.add("updated", rel_path, DETAIL_LEGACY_CONFIG_MIGRATION)
                return False
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            backup_path.write_text(existing, encoding="utf-8")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            report.add("updated", rel_path, DETAIL_LEGACY_CONFIG_MIGRATION)
            return False
        if rel_path == ".forge/forge-install.yaml":
            if dry_run:
                report.add("updated", rel_path, DETAIL_INSTALL_MANIFEST)
                return False
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            report.add("updated", rel_path, DETAIL_INSTALL_MANIFEST)
            return False
        if expected_hash is None:
            report.override_hash(rel_path, sha256_text(existing))
            report.add("skipped", rel_path, DETAIL_LEGACY_PRESERVED)
            return False
        if sha256_text(existing) != expected_hash:
            report.add("conflict", rel_path, DETAIL_CONFLICT_LOCAL)
            return True
        if dry_run:
            report.add("updated", rel_path, DETAIL_MANAGED_REFRESH)
            return False
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        report.add("updated", rel_path, DETAIL_MANAGED_REFRESH)
        return False

    if dry_run:
        report.add("created", rel_path, DETAIL_MANAGED_FILE)
        return False

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    report.add("created", rel_path, DETAIL_MANAGED_FILE)
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
    hash_overrides: dict[str, str] | None = None,
) -> ForgeInstallManifest:
    managed_hashes = {
        path: (hash_overrides or {}).get(path, sha256_text(content))
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
    ui_language = _read_ui_language(target_root)
    desired_files = _build_init_files(
        target_root=target_root,
        profile=profile,
        selected_tools=selected_tools,
        ui_language=ui_language,
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


def _render_forge_config(*, selected_tools: tuple[str, ...], ui_language: str) -> str:
    adapters = _yaml_list(selected_tools)
    default_adapter = selected_tools[0]
    package_targets = _yaml_list(selected_tools)
    return (
        "# forge-context-engine - Engine Configuration\n"
        "# Not a narrative context file. Customize during Context Initialization for the target repo.\n\n"
        "forge:\n"
        f'  version: "{__version__}"\n\n'
        "ui:\n"
        f"  language: {ui_language}\n\n"
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


def _looks_like_legacy_forge_config(content: str) -> bool:
    legacy_markers = (
        "forge_version:",
        "systems:",
        "loading:",
        "runtime:",
        "size_budget:",
        "governance:",
    )
    current_markers = ("forge:\n", "\nui:\n", "\nworkflow:\n", "\ntools:\n")
    return any(marker in content for marker in legacy_markers) and not all(
        marker in content for marker in current_markers
    )


def _next_legacy_config_backup_path(target_root: Path) -> Path:
    base = target_root / ".forge" / "forge.config.legacy.yaml"
    if not base.exists():
        return base

    index = 1
    while True:
        candidate = target_root / ".forge" / f"forge.config.legacy.{index}.yaml"
        if not candidate.exists():
            return candidate
        index += 1


def _is_wrapper_like_entrypoint(content: str) -> bool:
    wrapper_markers = (
        ".forge/forge.config.yaml",
        ".forge/context/00-meta/context-manifest.md",
        ".forge/context/00-meta/conventions.md",
    )
    guidance_markers = (
        ".forge/adapter.md",
        ".forge/context",
        "Thin adapter",
        "Context Adapter",
    )
    return (
        sum(marker in content for marker in wrapper_markers) >= 2
        and sum(marker in content for marker in guidance_markers) >= 1
    )


def _preserve_non_selected_entrypoints(
    *,
    target_root: Path,
    selected_tools: tuple[str, ...],
    report: OperationReport,
) -> None:
    selected_paths = {
        "codex": "AGENTS.md",
        "claude": "CLAUDE.md",
        "copilot": COPILOT_TEMPLATE_PATH,
    }
    for tool, rel_path in selected_paths.items():
        if tool in selected_tools:
            continue
        if (target_root / rel_path).exists():
            report.add("skipped", rel_path, DETAIL_PRESERVED_NON_SELECTED)


def _mark_preserved_baselines(report: OperationReport) -> None:
    for path in USER_OWNED_PATHS_BASELINE:
        report.mark_preserved("user", path)
    for path in LOCAL_ONLY_PATHS_BASELINE:
        report.mark_preserved("local", path)


def _mark_preserved_paths(report: OperationReport, manifest: ForgeInstallManifest) -> None:
    for path in manifest.user_owned_paths:
        report.mark_preserved("user", path)
    for path in manifest.local_only_paths:
        report.mark_preserved("local", path)


def _print_report(
    *,
    report: OperationReport,
    locale: str,
    title: str,
    target_root: Path,
    profile: str,
    selected_tools: tuple[str, ...],
    mode: str,
    detected_tools: tuple[str, ...] | None = None,
) -> None:
    context = [
        (_msg(locale, "target"), str(target_root)),
        (_msg(locale, "profile"), profile),
        (_msg(locale, "selected_tools"), ", ".join(selected_tools)),
        (_msg(locale, "mode"), _msg(locale, f"{mode}_mode")),
    ]
    if detected_tools is not None:
        context.append((_msg(locale, "detected_tools"), ", ".join(detected_tools)))
    report.print(locale=locale, title=title, context=context)


def _read_ui_language(target_root: Path) -> str:
    config_path = target_root / ".forge/forge.config.yaml"
    if not config_path.exists():
        return UI_LANGUAGE_EN

    in_ui = False
    for raw in config_path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not raw.startswith(" "):
            in_ui = stripped == "ui:"
            continue
        if not in_ui:
            continue
        child = stripped
        if child.startswith("language:"):
            value = _strip_yaml_scalar(child.split(":", 1)[1].strip()).lower()
            if value in SUPPORTED_UI_LANGUAGES:
                return value
            return UI_LANGUAGE_EN
    return UI_LANGUAGE_EN


def _strip_yaml_scalar(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def _msg(locale: str, key: str, **kwargs: str) -> str:
    language = locale if locale in MESSAGES else UI_LANGUAGE_EN
    template = MESSAGES[language][key]
    return template.format(**kwargs)


def _confirm(prompt: str, *, locale: str) -> bool:
    if not sys.stdin.isatty():
        print(_msg(locale, "confirm_non_interactive"))
        return False
    try:
        response = input(prompt).strip().lower()
    except EOFError:
        return False
    return response in {"y", "yes"}
