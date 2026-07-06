"""Runtime init/update operations for the Forge CLI."""

from __future__ import annotations

import sys
from dataclasses import dataclass, field, replace
from pathlib import Path
import re
import shutil

from .context_builder import build_repo_context_seed
from .fs_ops import normalize_text, resolve_target_paths, sha256_text, to_manifest_path
from .install_manifest import (
    CONTEXT_PROFILE_VERSION_CURRENT,
    CONTEXT_PROFILE_VERSION_LEGACY,
    DEPRECATED_RUNTIME_ARCHIVE_USER_OWNED_PATHS,
    DEFAULT_SELECTED_TOOLS,
    ForgeInstallManifest,
    LEGACY_ARCHIVE_USER_OWNED_PATHS,
    PROFILE_SERVICE,
    PROFILE_WORKSPACE,
    LOCAL_ONLY_PATHS_BASELINE,
    build_managed_paths,
    build_user_owned_paths,
    build_manifest,
    dump_manifest,
    load_manifest,
)
from .managed_blocks import has_managed_block, upsert_managed_block
from .runtime_templates import iter_template_files, read_template
from .version import __version__


FORGE_LOCAL_GITIGNORE = """# Forge local cache/scratch
/cache/
/temp/

# Generated artifacts are local by default.
# Keep README.md tracked so the directory exists and explains the policy.
/generated/**
!/generated/
!/generated/README.md

# Context patch proposals are local by default.
# Force-add a specific patch if your team wants to review/commit it.
/context-patches/**
!/context-patches/
!/context-patches/README.md

# Migration/deprecated archives are local safety backups by default.
# Force-add archive content only when your team intentionally wants migration history in git.
/context-archive/**
!/context-archive/
!/context-archive/README.md

# Local personal Forge config
/forge.local.yaml
"""
CLAUDE_COMMANDS_PREFIX = ".claude/commands/"
CLAUDE_GITIGNORE_PATH = ".claude/.gitignore"
COPILOT_TEMPLATE_PATH = ".github/copilot-instructions.md"
COPILOT_SKILLS_PREFIX = ".github/skills/"
LEGACY_COPILOT_PROMPTS_PREFIX = ".github/prompts/"
TEMPLATE_SKILLS_PREFIX = "skills/"
CANONICAL_SKILLS_PREFIX = ".forge/skills/"
OPENCODE_SKILLS_PREFIX = ".opencode/skills/"
OPENCODE_CONFIG_PATH = ".opencode/opencode.json"
OPENCODE_SIGNAL_PATHS = (
    OPENCODE_CONFIG_PATH,
    OPENCODE_SKILLS_PREFIX.rstrip("/"),
)
OPTIONAL_TEMPLATE_PREFIXES = (CLAUDE_COMMANDS_PREFIX, ".github/prompts/", TEMPLATE_SKILLS_PREFIX)
LEGACY_CONTEXT_TEMPLATE_PREFIXES = (
    ".forge/context/01-core/",
    ".forge/context/knowledge/",
    ".forge/context/systems/",
    ".forge/context/layers/",
    ".forge/context/generated/",
    ".forge/context/repo-map/",
    ".forge/context/decisions/",
    ".forge/context/unknowns/",
)
CONTEXT_LAYOUT_LEGACY_V1 = "legacy-v1"
CONTEXT_LAYOUT_V2 = "v2"
CONTEXT_LAYOUT_MIXED = "mixed"
CONTEXT_LAYOUT_EMPTY_OR_UNKNOWN = "empty-or-unknown"
LEGACY_CONTEXT_LAYOUT_PATHS = (
    ".forge/context/01-core",
    ".forge/context/knowledge",
    ".forge/context/repo-map",
    ".forge/context/systems",
)
LEGACY_CONTEXT_ARCHIVE_PATHS = (
    *LEGACY_CONTEXT_LAYOUT_PATHS,
    ".forge/context/layers",
    ".forge/context/generated",
    ".forge/context/decisions",
    ".forge/context/unknowns",
)
SERVICE_V2_CONTEXT_FILES = (
    ".forge/context/00-index.md",
    ".forge/context/01-service-overview.md",
    ".forge/context/02-architecture.md",
    ".forge/context/03-domain-boundaries.md",
    ".forge/context/04-interfaces-and-contracts.md",
    ".forge/context/05-data-and-persistence.md",
    ".forge/context/06-business-rules-and-flows.md",
    ".forge/context/07-integrations-and-dependencies.md",
    ".forge/context/08-security-and-access.md",
    ".forge/context/09-errors-and-resilience.md",
    ".forge/context/10-observability-and-support.md",
    ".forge/context/11-testing-and-quality.md",
    ".forge/context/12-runtime-deployment-and-config.md",
    ".forge/context/13-operations-and-runbook.md",
    ".forge/context/14-decisions-assumptions-and-constraints.md",
    ".forge/context/98-glossary.md",
    ".forge/context/99-open-questions.md",
)
WORKSPACE_V2_CONTEXT_FILES = (
    ".forge/context/00-index.md",
    ".forge/context/01-platform-overview.md",
    ".forge/context/02-system-map.md",
    ".forge/context/03-service-catalog.md",
    ".forge/context/04-domain-boundaries.md",
    ".forge/context/05-cross-service-flows.md",
    ".forge/context/06-interfaces-and-contracts.md",
    ".forge/context/07-data-ownership-and-consistency.md",
    ".forge/context/08-security-and-access.md",
    ".forge/context/09-observability-and-support.md",
    ".forge/context/10-testing-and-quality.md",
    ".forge/context/11-runtime-deployment-and-config.md",
    ".forge/context/12-release-and-feature-flags.md",
    ".forge/context/13-operations-and-runbook.md",
    ".forge/context/14-decisions-assumptions-and-constraints.md",
    ".forge/context/98-glossary.md",
    ".forge/context/99-open-questions.md",
)
MIGRATION_PROPOSAL_ROOT = ".forge/context-patches/migrations/v2-context-profile"
MIGRATION_PROPOSAL_CONTEXT_ROOT = f"{MIGRATION_PROPOSAL_ROOT}/context"
MIGRATION_PROPOSAL_MARKDOWN = f"{MIGRATION_PROPOSAL_ROOT}/MIGRATION.md"
LEGACY_CONTEXT_ARCHIVE_ROOT = ".forge/context-archive/legacy-v1"
DEPRECATED_RUNTIME_ARCHIVE_ROOT = ".forge/context-archive/deprecated-runtime"
DEPRECATED_ROOT_WRAPPERS_ARCHIVE_ROOT = ".forge/context-archive/deprecated-root-wrappers"
LEGACY_WRAPPER_MARKERS = (
    ".forge/context/00-meta",
    ".forge/context/modes",
    "00-meta/",
    "01-core/",
    "knowledge/inferred.md",
    "knowledge/confirmations.md",
    "unknowns.md",
    "systems/<name>/system.md",
    "source_commit",
    "last_verified",
)
ENTRYPOINT_TEMPLATE_MAP = {
    "AGENTS.md": ("base", "AGENTS.md"),
    "CLAUDE.md": ("base", "CLAUDE.md"),
    COPILOT_TEMPLATE_PATH: ("base", ".github/copilot-instructions.md"),
}
LEGACY_COPILOT_PROMPT_FILES = (
    ".github/prompts/forge-init.prompt.md",
    ".github/prompts/forge-ask.prompt.md",
    ".github/prompts/forge-plan.prompt.md",
    ".github/prompts/forge-implement.prompt.md",
    ".github/prompts/forge-implementation.prompt.md",
    ".github/prompts/forge-execute.prompt.md",
    ".github/prompts/forge-review.prompt.md",
    ".github/prompts/forge-ai-readiness.prompt.md",
    ".github/prompts/forge-verify-context.prompt.md",
    ".github/prompts/forge-incident.prompt.md",
    ".github/prompts/forge-refactor.prompt.md",
    ".github/prompts/forge-test.prompt.md",
    ".github/prompts/forge-update-context.prompt.md",
)
REGULAR_MANAGED_HASH_EXCLUDES = {
    ".forge/forge-install.yaml",
    "AGENTS.md",
    "CLAUDE.md",
    COPILOT_TEMPLATE_PATH,
}
RUNTIME_MARKERS = (
    ".forge/adapter.md",
    ".forge/forge.config.yaml",
    ".forge/runtime/modes/ask.md",
)
LEGACY_RUNTIME_MARKERS = (
    ".forge/context/modes/ask.md",
    ".forge/context/00-meta/conventions.md",
)
DEPRECATED_RUNTIME_PATHS = (
    ".forge/context/00-meta",
    ".forge/context/modes",
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
DETAIL_CONFLICT_PROPOSAL = "existing migration proposal file differs"
DETAIL_CONFLICT_MIGRATION = "context migration target already exists"
DETAIL_CONFLICT_ARCHIVE = "deprecated runtime archive target already exists"
DETAIL_CONFLICT_HASH = "managed file hash unavailable for safe update"
DETAIL_CONFLICT_LOCAL = "managed file modified locally"
DETAIL_PRESERVED_NON_SELECTED = "existing non-selected entrypoint preserved"
DETAIL_ADOPTION_PREVIEW = "adoption preview only"
DETAIL_LEGACY_PRESERVED = "legacy managed file preserved; current hash adopted"
DETAIL_LEGACY_CONFIG_MIGRATION = "legacy config migration"
DETAIL_ENTRYPOINT_ADOPTED = "existing Forge-like wrapper adopted"
DETAIL_WORKSPACE_PRESERVED = "user-edited workspace file preserved"
DETAIL_ENTRYPOINT_LEGACY_REPLACED = "legacy wrapper archived and replaced"
DETAIL_ENTRYPOINT_MANUAL_REVIEW = "entrypoint contains unmanaged content; manual review required"
DETAIL_OBSOLETE_MANAGED_CLEANUP = "obsolete managed path cleanup"
DETAIL_OBSOLETE_MANAGED_PRESERVED = "obsolete managed path preserved; manual review required"
DETAIL_MIGRATION_V2_WRITE = "v2 context migration"
DETAIL_MIGRATION_ARCHIVE = "legacy-v1 context archive"
DETAIL_MIGRATION_MANIFEST = "context profile version migration"
DETAIL_DEPRECATED_RUNTIME = "deprecated managed runtime path preserved"
DETAIL_DEPRECATED_RUNTIME_CLEANUP = "deprecated managed runtime path cleanup"
DETAIL_DEPRECATED_RUNTIME_ARCHIVE = "deprecated runtime path archived for review"


MESSAGES = {
    UI_LANGUAGE_EN: {
        "init_title": "Forge init",
        "update_title": "Forge update",
        "migrate_title": "Forge migrate-context",
        "dry_run_suffix": "dry-run",
        "target": "Target",
        "profile": "Profile",
        "detected_profile": "Detected Forge profile",
        "context_profile_version": "Detected context profile version",
        "context_layout": "Detected context layout",
        "context_migration": "Migration",
        "migration_proposal": "Migration",
        "migration_mode": "Migration mode",
        "files_changed": "Files changed",
        "user_owned_context": "User-owned context",
        "selected_tools": "Selected tools",
        "detected_tools": "Detected tools",
        "tool_selection_change": "Tool selection change",
        "mode": "Mode",
        "managed_files": "Managed file checks",
        "proposal_files": "Migration changes",
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
        "conflict_help": "Conflict resolution guidance",
        "conflict_reason_existing": "Reason: Forge would need to overwrite an existing file during init.",
        "conflict_reason_proposal": "Reason: a migration proposal file already exists with different content, so Forge stopped before overwriting it.",
        "conflict_reason_migration": "Reason: a direct migration target already exists, so Forge stopped before overwriting `.forge/context` or the legacy archive.",
        "conflict_reason_archive": "Reason: archiving this deprecated runtime path would overwrite an existing archive destination, so Forge stopped before moving it.",
        "conflict_reason_local": "Reason: this Forge-managed file differs from the last recorded managed hash, so Forge stopped to avoid overwriting local changes.",
        "conflict_reason_generic": "Reason: this path could not be updated safely without risking local changes.",
        "conflict_action_review": "Review local changes first: `git diff -- {path}`",
        "conflict_action_migrate": "Review, move, rename, or remove the existing migration target or archive path before rerunning `forge migrate-context`.",
        "conflict_action_archive": "Review, move, rename, or remove the existing deprecated runtime archive path before rerunning `forge update`.",
        "conflict_action_replace": "If the local changes are not needed, replace the file with the current Forge-managed version, then rerun `forge update`.",
        "conflict_action_merge": "If both local changes and new Forge updates matter, merge them manually, then rerun `forge update`.",
        "conflict_action_init": "If you want to keep the existing file, move or rename it before rerunning `forge init`, or initialize Forge in a clean target.",
        "update_conflicts": "Update stopped with conflicts. No conflicting managed files were overwritten.",
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
        "migrate_title": "Forge migrate-context",
        "dry_run_suffix": "dry-run",
        "target": "Target",
        "profile": "Profile",
        "detected_profile": "Detected Forge profile",
        "context_profile_version": "Detected context profile version",
        "context_layout": "Detected context layout",
        "context_migration": "Migration",
        "migration_proposal": "Migration",
        "migration_mode": "Migration mode",
        "files_changed": "Files changed",
        "user_owned_context": "User-owned context",
        "selected_tools": "Selected tools",
        "detected_tools": "Detected tools",
        "tool_selection_change": "Perubahan tool",
        "mode": "Mode",
        "managed_files": "Pemeriksaan file terkelola",
        "proposal_files": "Perubahan migrasi",
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
        "conflict_help": "Panduan penyelesaian konflik",
        "conflict_reason_existing": "Alasan: Forge perlu menimpa file yang sudah ada saat init.",
        "conflict_reason_proposal": "Alasan: file proposal migrasi sudah ada dengan isi berbeda, jadi Forge berhenti sebelum menimpanya.",
        "conflict_reason_migration": "Alasan: target migrasi langsung sudah ada, jadi Forge berhenti sebelum menimpa `.forge/context` atau arsip legacy.",
        "conflict_reason_archive": "Alasan: pengarsipan path runtime deprecated ini akan menimpa tujuan arsip yang sudah ada, jadi Forge berhenti sebelum memindahkannya.",
        "conflict_reason_local": "Alasan: file Forge-managed ini berbeda dari hash managed terakhir yang tercatat, jadi Forge berhenti agar perubahan lokal tidak tertimpa.",
        "conflict_reason_generic": "Alasan: path ini tidak bisa diperbarui dengan aman tanpa berisiko menimpa perubahan lokal.",
        "conflict_action_review": "Tinjau perubahan lokal dulu: `git diff -- {path}`",
        "conflict_action_migrate": "Tinjau, pindahkan, rename, atau hapus target migrasi atau path arsip yang sudah ada sebelum menjalankan ulang `forge migrate-context`.",
        "conflict_action_archive": "Tinjau, pindahkan, rename, atau hapus path arsip runtime deprecated yang sudah ada sebelum menjalankan ulang `forge update`.",
        "conflict_action_replace": "Jika perubahan lokal tidak diperlukan, ganti file dengan versi Forge-managed terbaru, lalu jalankan ulang `forge update`.",
        "conflict_action_merge": "Jika perubahan lokal dan update Forge sama-sama penting, merge manual dulu, lalu jalankan ulang `forge update`.",
        "conflict_action_init": "Jika ingin mempertahankan file yang ada, pindahkan atau rename file tersebut sebelum menjalankan ulang `forge init`, atau inisialisasi Forge di target yang bersih.",
        "update_conflicts": "Update dihentikan karena ada konflik. File managed yang konflik tidak ditimpa.",
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


@dataclass(frozen=True)
class ArchiveSalvageCandidate:
    """Low-trust archive review item that may contain repo-specific knowledge."""

    path: str
    category: str
    snippet: str


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

    def print(
        self,
        *,
        locale: str,
        title: str,
        context: list[tuple[str, str]],
        operations_label: str | None = None,
    ) -> None:
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
            print(f"{operations_label or messages['managed_files']}:")
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

        self._print_conflict_help(locale=locale)

    def _print_conflict_help(self, *, locale: str) -> None:
        conflicts = self.statuses("conflict")
        if not conflicts:
            return

        messages = MESSAGES[locale]
        print()
        print(f"{messages['conflict_help']}:")
        for op in conflicts:
            print(f"- {op.path}")
            print(f"  {_conflict_reason(locale, op.detail)}")
            print(f"  {_msg(locale, 'conflict_action_review', path=op.path)}")
            if op.detail == DETAIL_CONFLICT_MIGRATION:
                print(f"  {messages['conflict_action_migrate']}")
                continue
            if op.detail == DETAIL_CONFLICT_PROPOSAL:
                print(f"  {messages['conflict_action_migrate']}")
                continue
            if op.detail == DETAIL_CONFLICT_ARCHIVE:
                print(f"  {messages['conflict_action_archive']}")
                continue
            if op.detail == DETAIL_CONFLICT_EXISTING:
                print(f"  {messages['conflict_action_init']}")
                continue
            print(f"  {messages['conflict_action_replace']}")
            print(f"  {messages['conflict_action_merge']}")


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
    desired_files.update(
        build_repo_context_seed(target_root=paths.target_root, profile=profile).files
    )
    conflicts = _apply_init_files(paths.target_root, desired_files, report, dry_run)
    _ensure_local_only_dirs(paths.target_root, report, dry_run)
    _mark_preserved_baselines(report, profile=profile)

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
        context_profile_version=CONTEXT_PROFILE_VERSION_CURRENT,
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
        context_layout = _detect_context_layout(paths.target_root, manifest.profile)
        effective_tools = _merge_selected_tools(manifest.selected_tools, selected_tools)
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
                    context_profile_version=_reported_context_profile_version(
                        context_layout,
                        manifest.context_profile_version,
                    ),
                    context_layout=context_layout,
                )
                print(_msg(locale, "update_conflicts"))
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
            context_profile_version=_reported_context_profile_version(
                context_layout,
                manifest.context_profile_version,
            ),
            context_layout=context_layout,
        )
        return 0 if not report.statuses("conflict") else 1

    if not _detect_runtime(paths.target_root):
        print(_msg(locale, "no_runtime", target=str(paths.target_root)))
        return 1

    adopted_profile = _detect_profile(paths.target_root)
    adopted_layout = _detect_context_layout(paths.target_root, adopted_profile)
    adopted_context_profile_version = _detect_context_profile_version(paths.target_root)
    detected_tools = _detect_tools(paths.target_root)
    effective_tools = _merge_selected_tools(detected_tools, selected_tools)
    if selected_tools and selected_tools != detected_tools:
        report.add_note(_msg(locale, "adoption_override", tools=",".join(selected_tools)))
    elif selected_tools is None and detected_tools != DEFAULT_SELECTED_TOOLS:
        report.add_note(
            _msg(locale, "adoption_detected_narrower", tools=",".join(DEFAULT_SELECTED_TOOLS))
        )

    manifest = _manifest_from_current_runtime(
        target_root=paths.target_root,
        profile=adopted_profile,
        context_profile_version=adopted_context_profile_version,
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
            context_profile_version=_display_context_profile_version(adopted_context_profile_version),
            context_layout=adopted_layout,
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
            context_profile_version=_display_context_profile_version(adopted_context_profile_version),
            context_layout=adopted_layout,
        )
        print(_msg(locale, "update_conflicts"))
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
        context_profile_version=_display_context_profile_version(adopted_context_profile_version),
        context_layout=adopted_layout,
    )
    if report.statuses("conflict"):
        print(_msg(locale, "update_conflicts"))
        return 1
    return 0


def run_migrate_context(*, target: Path | None, dry_run: bool) -> int:
    """Migrate legacy-v1 context layout to numbered v2 context files."""

    paths = resolve_target_paths(target)
    locale = _read_ui_language(paths.target_root)
    report = OperationReport(dry_run=dry_run)
    manifest_path = paths.forge_root / "forge-install.yaml"

    manifest: ForgeInstallManifest | None = None
    if manifest_path.exists():
        manifest = load_manifest(manifest_path)
        profile = manifest.profile
        context_layout = _detect_context_layout(paths.target_root, profile)
        context_profile_version = _reported_context_profile_version(
            context_layout,
            manifest.context_profile_version,
        )
    else:
        if not _detect_runtime(paths.target_root):
            print(_msg(locale, "no_runtime", target=str(paths.target_root)))
            return 1
        profile = _detect_profile(paths.target_root)
        context_layout = _detect_context_layout(paths.target_root, profile)
        context_profile_version = _display_context_profile_version(
            _detect_context_profile_version(paths.target_root)
        )

    migration_mode = "dry-run" if dry_run else "apply"
    migration_status = _migration_proposal_status(context_layout, outcome="not-run")
    files_changed = "none"

    if context_layout == CONTEXT_LAYOUT_LEGACY_V1:
        desired_context_files = build_repo_context_seed(
            target_root=paths.target_root,
            profile=profile,
        ).files
        archive_review_notes = _build_archive_salvage_review_notes(
            target_root=paths.target_root,
            desired_context_files=desired_context_files,
        )
        effective_tools = manifest.selected_tools if manifest is not None else _detect_tools(paths.target_root)
        manifest_text, manifest_write_status = _build_migrated_manifest_text(
            target_root=paths.target_root,
            manifest=manifest,
            profile=profile,
            selected_tools=effective_tools,
        )
        preview = OperationReport(dry_run=True)
        _plan_context_migration(
            target_root=paths.target_root,
            desired_context_files=desired_context_files,
            manifest_text=manifest_text,
            manifest_write_status=manifest_write_status,
            report=preview,
            dry_run=True,
        )
        if preview.statuses("conflict"):
            migration_status = _migration_proposal_status(context_layout, outcome="blocked")
            report.operations.extend(preview.statuses("conflict"))
            report.add_note(
                "Migration stopped before writing because at least one numbered v2 target path or legacy archive path would be overwritten."
            )
        elif dry_run:
            migration_status = _migration_proposal_status(context_layout, outcome="would-migrate")
            report.operations.extend(preview.operations)
            report.add_note(
                f"Would write {len(desired_context_files)} numbered v2 context files into `.forge/context/`, archive legacy-v1 paths under `{LEGACY_CONTEXT_ARCHIVE_ROOT}/`, and {manifest_write_status} `.forge/forge-install.yaml`."
            )
            for note in archive_review_notes:
                report.add_note(note)
        else:
            _plan_context_migration(
                target_root=paths.target_root,
                desired_context_files=desired_context_files,
                manifest_text=manifest_text,
                manifest_write_status=manifest_write_status,
                report=report,
                dry_run=False,
            )
            migration_status = _migration_proposal_status(context_layout, outcome="completed")
            files_changed = str(report.count("created") + report.count("updated"))
            report.add_note(
                "Migration completed: numbered v2 context files were written into `.forge/context/`, legacy-v1 context was archived, and `.forge/forge-install.yaml` was updated to context profile version 2."
            )
            for note in archive_review_notes:
                report.add_note(note)
    elif context_layout == CONTEXT_LAYOUT_V2:
        migration_status = _migration_proposal_status(context_layout, outcome="already-current")
        report.add_note("Repository already uses numbered v2 context files. No migration is needed.")
    elif context_layout == CONTEXT_LAYOUT_MIXED:
        migration_status = _migration_proposal_status(context_layout, outcome="not-run")
        report.add_note(
            "Mixed context layout detected. Forge did not overwrite existing v2 files, archive legacy paths, or update the manifest automatically. Manual review is required before migrating."
        )
    else:
        migration_status = _migration_proposal_status(context_layout, outcome="not-run")
        report.add_note(
            "Migration cannot be safely performed because the context layout could not be classified as legacy-v1 or v2. Review `.forge/context` manually, restore a recognizable legacy-v1 or v2 layout, or run `forge update --dry-run` to inspect the current Forge context state."
        )

    _print_migration_report(
        report=report,
        locale=locale,
        target_root=paths.target_root,
        profile=profile,
        context_profile_version=context_profile_version,
        context_layout=context_layout,
        migration_mode=migration_mode,
        proposal_status=migration_status,
        files_changed=files_changed,
    )
    return 0 if not report.statuses("conflict") else 1


def _conflict_reason(locale: str, detail: str) -> str:
    if detail == DETAIL_CONFLICT_MIGRATION:
        return _msg(locale, "conflict_reason_migration")
    if detail == DETAIL_CONFLICT_ARCHIVE:
        return _msg(locale, "conflict_reason_archive")
    if detail == DETAIL_CONFLICT_PROPOSAL:
        return _msg(locale, "conflict_reason_proposal")
    if detail == DETAIL_CONFLICT_EXISTING:
        return _msg(locale, "conflict_reason_existing")
    if detail == DETAIL_CONFLICT_LOCAL:
        return _msg(locale, "conflict_reason_local")
    return _msg(locale, "conflict_reason_generic")


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

    _cleanup_obsolete_managed_paths(
        target_root=target_root,
        manifest=manifest,
        selected_tools=selected_tools,
        report=report,
        dry_run=dry_run,
    )
    _cleanup_legacy_copilot_prompt_files(
        target_root=target_root,
        report=report,
        dry_run=dry_run,
    )
    _preserve_non_selected_entrypoints(
        target_root=target_root,
        selected_tools=selected_tools,
        report=report,
    )
    if manifest.context_profile_version == CONTEXT_PROFILE_VERSION_CURRENT:
        context_layout = _detect_context_layout(target_root, manifest.profile)
        if context_layout == CONTEXT_LAYOUT_V2:
            _cleanup_deprecated_runtime_paths(
                target_root=target_root,
                desired_files=all_desired_files,
                report=report,
                dry_run=dry_run,
            )
        else:
            _report_deprecated_runtime_paths(target_root=target_root, report=report)
    else:
        _report_deprecated_runtime_paths(target_root=target_root, report=report)
    _ensure_local_only_dirs(target_root, report, dry_run)

    updated_manifest = _manifest_for_target(
        target_root=target_root,
        profile=manifest.profile,
        context_profile_version=manifest.context_profile_version,
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
    template_files = iter_template_files("base")
    files = {
        rel: content
        for rel, content in template_files.items()
        if rel
        not in {
            "AGENTS.md",
            "CLAUDE.md",
            CLAUDE_GITIGNORE_PATH,
            ".github/copilot-instructions.md",
            ".forge/forge.config.yaml",
        }
        and not rel.startswith(OPTIONAL_TEMPLATE_PREFIXES)
        and not rel.startswith(LEGACY_CONTEXT_TEMPLATE_PREFIXES)
    }
    files.update(
        {
            _map_canonical_skill_path(rel): content
            for rel, content in template_files.items()
            if rel.startswith(TEMPLATE_SKILLS_PREFIX)
        }
    )

    files[".forge/forge.config.yaml"] = _render_forge_config(
        profile=profile,
        selected_tools=selected_tools,
        ui_language=ui_language,
    )
    files[".forge/.gitignore"] = FORGE_LOCAL_GITIGNORE

    if "codex" in selected_tools or "opencode" in selected_tools:
        files["AGENTS.md"] = read_template("base", "AGENTS.md")
    if "opencode" in selected_tools:
        files.update(
            {
                _map_opencode_skill_path(rel): _render_opencode_skill(rel, content)
                for rel, content in template_files.items()
                if rel.startswith(TEMPLATE_SKILLS_PREFIX)
            }
        )
        files[OPENCODE_CONFIG_PATH] = _render_opencode_config()
    if "claude" in selected_tools:
        files["CLAUDE.md"] = read_template("base", "CLAUDE.md")
        files[CLAUDE_GITIGNORE_PATH] = read_template("base", CLAUDE_GITIGNORE_PATH)
        files.update({rel: content for rel, content in template_files.items() if rel.startswith(CLAUDE_COMMANDS_PREFIX)})
    if "copilot" in selected_tools:
        files[COPILOT_TEMPLATE_PATH] = read_template("base", COPILOT_TEMPLATE_PATH)
        files.update(
            {
                _map_copilot_skill_path(rel): content
                for rel, content in template_files.items()
                if rel.startswith(TEMPLATE_SKILLS_PREFIX)
            }
        )
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
        legacy_cleanup = _plan_legacy_entrypoint_cleanup(
            target_root=target_root,
            rel_path=rel_path,
            existing=existing,
        )
        if legacy_cleanup is not None:
            status, detail, archive_rel_path = legacy_cleanup
            if status == "conflict":
                report.add("conflict", rel_path, detail)
                report.add_note(
                    f"Wrapper {rel_path} contains unmanaged content outside the Forge-managed block and was preserved for manual review."
                )
                return True
            if dry_run:
                report.add("updated", rel_path, detail)
                report.add_note(
                    f"Wrapper {rel_path} would be archived to {archive_rel_path} and replaced with the current thin wrapper."
                )
                return False
            archive_path = target_root / archive_rel_path
            archive_path.parent.mkdir(parents=True, exist_ok=True)
            archive_path.write_text(existing, encoding="utf-8")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(upsert_managed_block("", content)[0], encoding="utf-8")
            report.add("updated", rel_path, detail)
            report.add_note(
                f"Wrapper {rel_path} was archived to {archive_rel_path} and replaced with the current thin wrapper."
            )
            return False
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
            if rel_path == ".forge/workspace.yaml":
                report.override_hash(rel_path, sha256_text(existing))
                report.add("skipped", rel_path, DETAIL_WORKSPACE_PRESERVED)
                return False
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
    for rel in (".forge/temp", ".forge/cache", ".forge/context-patches"):
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
    context_profile_version: str,
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
    manifest = build_manifest(
        profile=profile,
        context_profile_version=context_profile_version,
        selected_tools=selected_tools,
        managed_file_hashes=managed_hashes,
        installed_at=installed_at,
    )
    include_legacy_archive = any(
        (target_root / rel_path).exists() for rel_path in LEGACY_ARCHIVE_USER_OWNED_PATHS
    )
    include_deprecated_runtime_archive = any(
        (target_root / rel_path).exists() for rel_path in DEPRECATED_RUNTIME_ARCHIVE_USER_OWNED_PATHS
    )
    if context_profile_version == CONTEXT_PROFILE_VERSION_CURRENT and (
        include_legacy_archive or include_deprecated_runtime_archive
    ):
        return replace(
            manifest,
            user_owned_paths=build_user_owned_paths(
                profile=profile,
                context_profile_version=context_profile_version,
                include_legacy_archive=include_legacy_archive,
                include_deprecated_runtime_archive=include_deprecated_runtime_archive,
            ),
        )
    return manifest


def _manifest_from_current_runtime(
    *,
    target_root: Path,
    profile: str,
    context_profile_version: str,
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
    manifest = build_manifest(
        profile=profile,
        context_profile_version=context_profile_version,
        selected_tools=selected_tools,
        managed_file_hashes=managed_hashes,
    )
    include_legacy_archive = any(
        (target_root / rel_path).exists() for rel_path in LEGACY_ARCHIVE_USER_OWNED_PATHS
    )
    include_deprecated_runtime_archive = any(
        (target_root / rel_path).exists() for rel_path in DEPRECATED_RUNTIME_ARCHIVE_USER_OWNED_PATHS
    )
    if context_profile_version == CONTEXT_PROFILE_VERSION_CURRENT and (
        include_legacy_archive or include_deprecated_runtime_archive
    ):
        return replace(
            manifest,
            user_owned_paths=build_user_owned_paths(
                profile=profile,
                context_profile_version=context_profile_version,
                include_legacy_archive=include_legacy_archive,
                include_deprecated_runtime_archive=include_deprecated_runtime_archive,
            ),
        )
    return manifest


def _render_forge_config(
    *, profile: str, selected_tools: tuple[str, ...], ui_language: str
) -> str:
    adapters = _yaml_list(selected_tools)
    default_adapter = selected_tools[0]
    package_targets = _yaml_list(selected_tools)
    return (
        "# forge-context-engine - Engine Configuration\n"
        "# Not a narrative context file. Customize during Context Initialization for the target repo.\n\n"
        "forge:\n"
        f'  version: "{__version__}"\n'
        f"  profile: {profile}\n\n"
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
        "workspace:\n"
        f"  name: {name}\n"
        '  description: ""\n'
        "  default_context_policy: selective\n"
        "linked_services: []\n"
        "boundaries:\n"
        '  - "Workspace context coordinates services; service context owns repo-specific facts."\n'
        '  - "Do not duplicate service-level implementation details here."\n'
        "loading_policy:\n"
        '  default: "service-first"\n'
        '  cross_repo: "load workspace summary, then only relevant linked service context"\n'
        "default_tools:\n"
        f"{tools}"
    )


def _render_opencode_config() -> str:
    return (
        "{\n"
        '  "$schema": "https://opencode.ai/config.json",\n'
        '  "permission": {\n'
        '    "skill": {\n'
        '      "forge-*": "allow"\n'
        "    }\n"
        "  },\n"
        '  "skills": {\n'
        '    "paths": ["./.opencode/skills"]\n'
        "  }\n"
        "}\n"
    )


def _map_canonical_skill_path(relative_path: str) -> str:
    return relative_path.replace(TEMPLATE_SKILLS_PREFIX, CANONICAL_SKILLS_PREFIX, 1)


def _map_opencode_skill_path(relative_path: str) -> str:
    return relative_path.replace(TEMPLATE_SKILLS_PREFIX, OPENCODE_SKILLS_PREFIX, 1)

def _map_copilot_skill_path(relative_path: str) -> str:
    return relative_path.replace(TEMPLATE_SKILLS_PREFIX, COPILOT_SKILLS_PREFIX, 1)


def _render_opencode_skill(relative_path: str, content: str) -> str:
    if content.startswith("---\n"):
        return content

    parts = relative_path.split("/")
    if len(parts) < 3:
        return content

    skill_name = parts[1]
    description = _skill_description(content, skill_name)
    return (
        "---\n"
        f"name: {skill_name}\n"
        f"description: {description}\n"
        "compatibility: opencode\n"
        "---\n\n"
        f"{content.lstrip()}"
    )


def _skill_description(content: str, skill_name: str) -> str:
    for line in content.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return stripped.rstrip(".")
    return f"Use the {skill_name} Forge skill"


def _yaml_list(items: tuple[str, ...]) -> str:
    return "".join(f"    - {item}\n" for item in items)


def _merge_selected_tools(current_tools: tuple[str, ...], requested_tools: tuple[str, ...] | None) -> tuple[str, ...]:
    if requested_tools is None:
        return current_tools
    return requested_tools


def _detect_runtime(target_root: Path) -> bool:
    return any((target_root / marker).exists() for marker in (*RUNTIME_MARKERS, *LEGACY_RUNTIME_MARKERS))


def _detect_profile(target_root: Path) -> str:
    if (target_root / ".forge/workspace.yaml").exists():
        return PROFILE_WORKSPACE
    return PROFILE_SERVICE


def _detect_context_layout(target_root: Path, profile: str) -> str:
    context_root = target_root / ".forge/context"
    if not context_root.exists() or not context_root.is_dir():
        return CONTEXT_LAYOUT_EMPTY_OR_UNKNOWN

    has_legacy = any((target_root / rel_path).exists() for rel_path in LEGACY_CONTEXT_LAYOUT_PATHS)
    expected_files = WORKSPACE_V2_CONTEXT_FILES if profile == PROFILE_WORKSPACE else SERVICE_V2_CONTEXT_FILES
    has_all_v2 = all((target_root / rel_path).exists() for rel_path in expected_files)
    has_any_v2 = any((target_root / rel_path).exists() for rel_path in expected_files)

    if has_legacy and has_any_v2:
        return CONTEXT_LAYOUT_MIXED
    if has_all_v2:
        return CONTEXT_LAYOUT_V2
    if has_legacy:
        return CONTEXT_LAYOUT_LEGACY_V1
    return CONTEXT_LAYOUT_EMPTY_OR_UNKNOWN


def _detect_context_profile_version(target_root: Path) -> str:
    context_layout = _detect_context_layout(target_root, _detect_profile(target_root))
    if context_layout in {CONTEXT_LAYOUT_V2, CONTEXT_LAYOUT_MIXED}:
        return CONTEXT_PROFILE_VERSION_CURRENT
    if context_layout == CONTEXT_LAYOUT_LEGACY_V1:
        return CONTEXT_PROFILE_VERSION_LEGACY
    return CONTEXT_PROFILE_VERSION_LEGACY


def _display_context_profile_version(context_profile_version: str) -> str:
    if context_profile_version == CONTEXT_PROFILE_VERSION_CURRENT:
        return CONTEXT_PROFILE_VERSION_CURRENT
    if context_profile_version == CONTEXT_PROFILE_VERSION_LEGACY:
        return CONTEXT_LAYOUT_LEGACY_V1
    return "unknown"


def _reported_context_profile_version(
    context_layout: str,
    manifest_context_profile_version: str | None = None,
) -> str:
    if manifest_context_profile_version is not None:
        return _display_context_profile_version(manifest_context_profile_version)
    if context_layout == CONTEXT_LAYOUT_V2:
        return CONTEXT_PROFILE_VERSION_CURRENT
    if context_layout in {CONTEXT_LAYOUT_LEGACY_V1, CONTEXT_LAYOUT_EMPTY_OR_UNKNOWN}:
        return CONTEXT_LAYOUT_LEGACY_V1
    return "unknown"


def _migration_note(context_layout: str) -> str:
    if context_layout == CONTEXT_LAYOUT_LEGACY_V1:
        return "not applied automatically; v2 context profiles are available"
    if context_layout == CONTEXT_LAYOUT_V2:
        return "not applied automatically"
    if context_layout == CONTEXT_LAYOUT_MIXED:
        return "not applied automatically; no cleanup performed for mixed layouts"
    return "not applied automatically; context layout could not be safely classified"


def _migration_proposal_status(context_layout: str, *, outcome: str) -> str:
    if context_layout == CONTEXT_LAYOUT_LEGACY_V1:
        if outcome == "would-migrate":
            return f"would migrate legacy-v1 context to numbered v2 files in `.forge/context/` and archive legacy paths under `{LEGACY_CONTEXT_ARCHIVE_ROOT}/`"
        if outcome == "completed":
            return f"completed; wrote numbered v2 context files into `.forge/context/` and archived legacy paths under `{LEGACY_CONTEXT_ARCHIVE_ROOT}/`"
        if outcome == "blocked":
            return "not run; an existing v2 target path or archive destination would be overwritten"
        return "not run; direct migration is available for legacy-v1 context"
    if context_layout == CONTEXT_LAYOUT_V2:
        return "not needed; repository already uses numbered v2 context files"
    if context_layout == CONTEXT_LAYOUT_MIXED:
        return "not run; mixed layout detected and manual review is required"
    return "not run; migration cannot be safely performed"


def _user_owned_context_note(context_layout: str) -> str:
    if context_layout == CONTEXT_LAYOUT_V2:
        return "preserved; numbered v2 context files remain user-owned"
    if context_layout == CONTEXT_LAYOUT_LEGACY_V1:
        return "preserved; legacy-v1 context remains user-owned"
    if context_layout == CONTEXT_LAYOUT_MIXED:
        return "preserved; legacy and v2 context both remain user-owned"
    return "preserved"


def _build_migrated_manifest_text(
    *,
    target_root: Path,
    manifest: ForgeInstallManifest | None,
    profile: str,
    selected_tools: tuple[str, ...],
) -> tuple[str, str]:
    include_legacy_archive = True

    if manifest is None:
        base_manifest = _manifest_from_current_runtime(
            target_root=target_root,
            profile=profile,
            context_profile_version=CONTEXT_PROFILE_VERSION_LEGACY,
            selected_tools=selected_tools,
        )
        migrated = replace(
            base_manifest,
            context_profile_version=CONTEXT_PROFILE_VERSION_CURRENT,
            user_owned_paths=build_user_owned_paths(
                profile=profile,
                context_profile_version=CONTEXT_PROFILE_VERSION_CURRENT,
                include_legacy_archive=include_legacy_archive,
            ),
        )
        return dump_manifest(migrated), "create"

    migrated = replace(
        manifest,
        context_profile_version=CONTEXT_PROFILE_VERSION_CURRENT,
        user_owned_paths=build_user_owned_paths(
            profile=manifest.profile,
            context_profile_version=CONTEXT_PROFILE_VERSION_CURRENT,
            include_legacy_archive=include_legacy_archive,
        ),
    )
    if dump_manifest(migrated) == dump_manifest(manifest):
        return dump_manifest(migrated), "leave unchanged"
    return dump_manifest(migrated), "update"


def _plan_context_migration(
    *,
    target_root: Path,
    desired_context_files: dict[str, str],
    manifest_text: str,
    manifest_write_status: str,
    report: OperationReport,
    dry_run: bool,
) -> None:
    for rel_path, content in sorted(desired_context_files.items()):
        _apply_context_migration_file(
            target_root=target_root,
            path=target_root / rel_path,
            content=content,
            report=report,
            dry_run=dry_run,
        )

    for source_rel, archive_rel in _legacy_archive_pairs(target_root):
        _apply_legacy_archive_move(
            target_root=target_root,
            source=target_root / source_rel,
            archive=target_root / archive_rel,
            report=report,
            dry_run=dry_run,
        )

    _apply_migration_manifest(
        target_root=target_root,
        content=manifest_text,
        report=report,
        dry_run=dry_run,
        write_status=manifest_write_status,
    )


def _legacy_archive_pairs(target_root: Path) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for rel_path in LEGACY_CONTEXT_ARCHIVE_PATHS:
        source = target_root / rel_path
        if source.exists():
            pairs.append((rel_path, f"{LEGACY_CONTEXT_ARCHIVE_ROOT}/{Path(rel_path).name}"))
    return pairs


def _build_archive_salvage_review_notes(
    *,
    target_root: Path,
    desired_context_files: dict[str, str],
) -> list[str]:
    candidates = _collect_archive_salvage_candidates(
        target_root=target_root,
        active_context_files=desired_context_files,
    )
    if not candidates:
        return []

    notes = [
        "Archive salvage review: `.forge/context-archive/**` is low-trust historical reference only. Review these items manually before discarding or citing archive material.",
    ]
    for candidate in candidates[:8]:
        notes.append(
            f"Review suggestion ({candidate.category}): {candidate.path} -> {candidate.snippet}"
        )
    return notes


def _collect_archive_salvage_candidates(
    *,
    target_root: Path,
    active_context_files: dict[str, str],
) -> list[ArchiveSalvageCandidate]:
    active_text = "\n".join(active_context_files.values())
    normalized_active = _normalize_salvage_text(active_text)
    candidates: list[ArchiveSalvageCandidate] = []
    seen: set[tuple[str, str]] = set()

    for source_rel, archive_rel in _legacy_archive_pairs(target_root):
        if _should_ignore_archive_path(source_rel):
            continue
        source_path = target_root / source_rel
        if source_path.is_file():
            extracted = _extract_archive_salvage_candidates_from_file(
                rel_path=archive_rel,
                content=source_path.read_text(encoding="utf-8"),
                normalized_active=normalized_active,
            )
            for candidate in extracted:
                key = (candidate.category, candidate.snippet)
                if key not in seen:
                    seen.add(key)
                    candidates.append(candidate)
            continue
        if not source_path.exists():
            continue
        for file_path in sorted(path for path in source_path.rglob("*") if path.is_file()):
            rel_under_source = file_path.relative_to(source_path).as_posix()
            candidate_rel_path = f"{archive_rel}/{rel_under_source}"
            extracted = _extract_archive_salvage_candidates_from_file(
                rel_path=candidate_rel_path,
                content=file_path.read_text(encoding="utf-8"),
                normalized_active=normalized_active,
            )
            for candidate in extracted:
                key = (candidate.category, candidate.snippet)
                if key not in seen:
                    seen.add(key)
                    candidates.append(candidate)

    return candidates


def _should_ignore_archive_path(rel_path: str) -> bool:
    ignored_prefixes = (
        ".forge/context/01-core",
        ".forge/context/knowledge",
        ".forge/context/00-meta",
        ".forge/context/modes",
    )
    return rel_path.startswith(ignored_prefixes)


def _extract_archive_salvage_candidates_from_file(
    *,
    rel_path: str,
    content: str,
    normalized_active: str,
) -> list[ArchiveSalvageCandidate]:
    candidates: list[ArchiveSalvageCandidate] = []
    for raw in content.splitlines():
        candidate = _classify_archive_candidate_line(rel_path=rel_path, raw=raw)
        if candidate is None:
            continue
        normalized_candidate = _normalize_salvage_text(candidate.snippet)
        if not normalized_candidate or normalized_candidate in normalized_active:
            continue
        candidates.append(candidate)
    return candidates


def _classify_archive_candidate_line(
    *,
    rel_path: str,
    raw: str,
) -> ArchiveSalvageCandidate | None:
    text = raw.strip()
    if not text or text.startswith("#"):
        return None
    text = re.sub(r"^[-*+]\s+", "", text)
    text = re.sub(r"^\d+\.\s+", "", text)
    if len(text) < 18:
        return None
    if _looks_like_legacy_mechanics(text):
        return None

    lowered = text.lower()
    rel_lower = rel_path.lower()
    if (
        "?" in text
        or "open question" in lowered
        or "unknown" in lowered
        or "unclear" in lowered
        or "need to confirm" in lowered
        or "should we" in lowered
        or rel_lower.startswith(f"{LEGACY_CONTEXT_ARCHIVE_ROOT}/unknowns/")
    ):
        return ArchiveSalvageCandidate(rel_path, "open question", text)

    rule_keywords = (
        "schema",
        "retention",
        "compliance",
        "sla",
        "must ",
        "must not",
        "cannot ",
        "required",
        "constraint",
        "boundary",
        "foreign key",
        "unique",
        "idempotent",
    )
    if any(keyword in lowered for keyword in rule_keywords):
        return ArchiveSalvageCandidate(rel_path, "rule/constraint", text)

    decision_keywords = (
        "decision",
        "decided",
        "assumption",
        "assume",
        "business rule",
        "policy",
    )
    if any(keyword in lowered for keyword in decision_keywords):
        return ArchiveSalvageCandidate(rel_path, "decision/assumption", text)
    return None


def _looks_like_legacy_mechanics(text: str) -> bool:
    lowered = text.lower()
    legacy_markers = (
        ".forge/context/00-meta",
        ".forge/context/modes",
        ".forge/runtime/modes",
        "01-core",
        "knowledge/inferred.md",
        "knowledge/confirmations.md",
        "claude.md",
        ".claude/",
        ".github/prompts",
        "copilot-instructions.md",
        "agents.md",
        "begin forge managed block",
        "end forge managed block",
        "/forge-",
        "invoke shared skill:",
        "old forge mode routing",
        "old forge lifecycle",
        "thin wrapper",
    )
    return any(marker in lowered for marker in legacy_markers)


def _normalize_salvage_text(text: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", text.lower()))


def _apply_context_migration_file(
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
        if normalize_text(existing) == normalize_text(content):
            report.add("unchanged", rel_path, DETAIL_CURRENT)
            return False
        report.add("conflict", rel_path, DETAIL_CONFLICT_MIGRATION)
        return True

    if dry_run:
        report.add("created", rel_path, DETAIL_MIGRATION_V2_WRITE)
        return False

    _write_text_atomic(path, content)
    report.add("created", rel_path, DETAIL_MIGRATION_V2_WRITE)
    return False


def _apply_legacy_archive_move(
    *,
    target_root: Path,
    source: Path,
    archive: Path,
    report: OperationReport,
    dry_run: bool,
) -> bool:
    source_rel = to_manifest_path(target_root, source)
    archive_rel = to_manifest_path(target_root, archive)
    if archive.exists():
        report.add("conflict", archive_rel, DETAIL_CONFLICT_MIGRATION)
        return True

    if dry_run:
        report.add("created", archive_rel, f"{DETAIL_MIGRATION_ARCHIVE} from {source_rel}")
        return False

    archive.parent.mkdir(parents=True, exist_ok=True)
    source.rename(archive)
    report.add("updated", archive_rel, f"{DETAIL_MIGRATION_ARCHIVE} from {source_rel}")
    return False


def _apply_migration_manifest(
    *,
    target_root: Path,
    content: str,
    report: OperationReport,
    dry_run: bool,
    write_status: str,
) -> bool:
    del write_status
    path = target_root / ".forge/forge-install.yaml"
    rel_path = to_manifest_path(target_root, path)
    if path.exists():
        existing = path.read_text(encoding="utf-8")
        if normalize_text(existing) == normalize_text(content):
            report.add("unchanged", rel_path, DETAIL_CURRENT)
            return False
        if dry_run:
            report.add("updated", rel_path, DETAIL_MIGRATION_MANIFEST)
            return False
        _write_text_atomic(path, content)
        report.add("updated", rel_path, DETAIL_MIGRATION_MANIFEST)
        return False

    if dry_run:
        report.add("created", rel_path, DETAIL_MIGRATION_MANIFEST)
        return False

    _write_text_atomic(path, content)
    report.add("created", rel_path, DETAIL_MIGRATION_MANIFEST)
    return False


def _write_text_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f".{path.name}.tmp")
    temp_path.write_text(content, encoding="utf-8")
    temp_path.replace(path)

def _plan_legacy_entrypoint_cleanup(
    *,
    target_root: Path,
    rel_path: str,
    existing: str,
) -> tuple[str, str, str | None] | None:
    if not has_managed_block(existing):
        return None

    start_marker = "<!-- BEGIN FORGE MANAGED BLOCK -->"
    end_marker = "<!-- END FORGE MANAGED BLOCK -->"
    start = existing.index(start_marker)
    end = existing.index(end_marker) + len(end_marker)
    prefix = existing[:start].strip()
    suffix = existing[end:].strip()
    if not prefix and not suffix:
        return None

    archive_rel_path = _deprecated_root_wrapper_archive_path(rel_path)
    if (target_root / archive_rel_path).exists():
        return ("conflict", DETAIL_ENTRYPOINT_MANUAL_REVIEW, archive_rel_path)

    unmanaged = "\n".join(part for part in (prefix, suffix) if part)
    if _looks_like_known_legacy_wrapper_content(unmanaged):
        return ("updated", DETAIL_ENTRYPOINT_LEGACY_REPLACED, archive_rel_path)
    return ("conflict", DETAIL_ENTRYPOINT_MANUAL_REVIEW, None)

def _plan_obsolete_entrypoint_cleanup(
    *,
    target_root: Path,
    rel_path: str,
    existing: str,
    current_content: str,
) -> tuple[str, str, str | None]:
    legacy_cleanup = _plan_legacy_entrypoint_cleanup(
        target_root=target_root,
        rel_path=rel_path,
        existing=existing,
    )
    if legacy_cleanup is not None:
        return legacy_cleanup

    expected = upsert_managed_block("", current_content)[0]
    if normalize_text(existing) == normalize_text(expected):
        return ("updated", DETAIL_OBSOLETE_MANAGED_CLEANUP, None)
    return ("conflict", DETAIL_ENTRYPOINT_MANUAL_REVIEW, None)

def _deprecated_root_wrapper_archive_path(rel_path: str) -> str:
    return f"{DEPRECATED_ROOT_WRAPPERS_ARCHIVE_ROOT}/{Path(rel_path).name}"

def _looks_like_known_legacy_wrapper_content(content: str) -> bool:
    normalized = content.strip()
    if not normalized:
        return False
    return any(marker in normalized for marker in LEGACY_WRAPPER_MARKERS)


def _detect_tools(target_root: Path) -> tuple[str, ...]:
    selected: list[str] = []
    if (target_root / "AGENTS.md").exists():
        selected.append("codex")
    if (target_root / "CLAUDE.md").exists() or (target_root / ".claude" / "commands").exists():
        selected.append("claude")
    if (
        (target_root / ".github/copilot-instructions.md").exists()
        or (target_root / ".github" / "skills").exists()
        or (target_root / ".github" / "prompts").exists()
    ):
        selected.append("copilot")
    if any((target_root / rel_path).exists() for rel_path in OPENCODE_SIGNAL_PATHS):
        selected.append("opencode")
    return tuple(selected) or DEFAULT_SELECTED_TOOLS


def _is_managed_file(rel_path: str, profile: str, selected_tools: tuple[str, ...]) -> bool:
    if rel_path == ".forge/.gitignore":
        return True
    if rel_path in {
        ".forge/generated/README.md",
        ".forge/context-patches/README.md",
        ".forge/context-archive/README.md",
    }:
        return True
    if rel_path == "AGENTS.md":
        return "codex" in selected_tools or "opencode" in selected_tools
    if rel_path == OPENCODE_CONFIG_PATH:
        return "opencode" in selected_tools
    if rel_path.startswith(OPENCODE_SKILLS_PREFIX):
        return "opencode" in selected_tools
    if rel_path == "CLAUDE.md":
        return "claude" in selected_tools
    if rel_path == CLAUDE_GITIGNORE_PATH:
        return "claude" in selected_tools
    if rel_path.startswith(CLAUDE_COMMANDS_PREFIX):
        return "claude" in selected_tools
    if rel_path == COPILOT_TEMPLATE_PATH:
        return "copilot" in selected_tools
    if rel_path.startswith(COPILOT_SKILLS_PREFIX):
        return "copilot" in selected_tools
    if rel_path in {".forge/adapter.md", ".forge/forge.config.yaml"}:
        return True
    if rel_path.startswith(CANONICAL_SKILLS_PREFIX):
        return True
    if rel_path == ".forge/workspace.yaml":
        return profile == PROFILE_WORKSPACE
    return rel_path.startswith(".forge/runtime/meta/") or rel_path.startswith(".forge/runtime/modes/")


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
        ".forge/runtime/meta/context-manifest.md",
        ".forge/runtime/meta/conventions.md",
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
    tool_paths = {
        "codex": "AGENTS.md",
        "opencode": "AGENTS.md",
        "claude": "CLAUDE.md",
        "copilot": COPILOT_TEMPLATE_PATH,
    }
    active_paths = {tool_paths[tool] for tool in selected_tools if tool in tool_paths}
    for rel_path in {path for path in tool_paths.values() if path not in active_paths}:
        if (target_root / rel_path).exists():
            report.add("skipped", rel_path, DETAIL_PRESERVED_NON_SELECTED)

def _cleanup_obsolete_managed_paths(
    *,
    target_root: Path,
    manifest: ForgeInstallManifest,
    selected_tools: tuple[str, ...],
    report: OperationReport,
    dry_run: bool,
) -> None:
    active_managed_paths = set(build_managed_paths(manifest.profile, selected_tools))
    for rel_path in manifest.managed_paths:
        if rel_path in active_managed_paths:
            continue
        if rel_path.endswith("/"):
            _cleanup_obsolete_managed_directory(
                target_root=target_root,
                rel_path=rel_path.rstrip("/"),
                manifest=manifest,
                report=report,
                dry_run=dry_run,
            )
            continue
        _cleanup_obsolete_managed_file(
            target_root=target_root,
            rel_path=rel_path,
            manifest=manifest,
            report=report,
            dry_run=dry_run,
        )

def _cleanup_legacy_copilot_prompt_files(
    *,
    target_root: Path,
    report: OperationReport,
    dry_run: bool,
) -> None:
    removed_any = False
    for rel_path in LEGACY_COPILOT_PROMPT_FILES:
        path = target_root / rel_path
        if not path.exists():
            continue
        report.add("updated", rel_path, DETAIL_OBSOLETE_MANAGED_CLEANUP)
        if dry_run:
            continue
        path.unlink()
        removed_any = True

    prompts_dir = target_root / LEGACY_COPILOT_PROMPTS_PREFIX.rstrip("/")
    if removed_any and prompts_dir.exists():
        try:
            prompts_dir.rmdir()
        except OSError:
            pass

def _cleanup_obsolete_managed_file(
    *,
    target_root: Path,
    rel_path: str,
    manifest: ForgeInstallManifest,
    report: OperationReport,
    dry_run: bool,
) -> None:
    path = target_root / rel_path
    if not path.exists():
        return

    if rel_path in ENTRYPOINT_TEMPLATE_MAP:
        section, template_rel_path = ENTRYPOINT_TEMPLATE_MAP[rel_path]
        existing = path.read_text(encoding="utf-8")
        status, detail, archive_rel_path = _plan_obsolete_entrypoint_cleanup(
            target_root=target_root,
            rel_path=rel_path,
            existing=existing,
            current_content=read_template(section, template_rel_path),
        )
        if status == "conflict":
            report.add("conflict", rel_path, detail)
            report.add_note(f"Obsolete wrapper {rel_path} was preserved for manual review.")
            return
        if dry_run:
            report.add("updated", rel_path, detail)
            return
        if archive_rel_path is not None:
            archive_path = target_root / archive_rel_path
            archive_path.parent.mkdir(parents=True, exist_ok=True)
            archive_path.write_text(existing, encoding="utf-8")
        path.unlink()
        report.add("updated", rel_path, detail)
        return

    expected_hash = manifest.managed_file_hashes.get(rel_path)
    existing = path.read_text(encoding="utf-8")
    if expected_hash is None or sha256_text(existing) != expected_hash:
        report.add("conflict", rel_path, DETAIL_OBSOLETE_MANAGED_PRESERVED)
        report.add_note(
            f"Obsolete managed file {rel_path} was preserved because local changes or an unknown hash prevent safe cleanup."
        )
        return
    if dry_run:
        report.add("updated", rel_path, DETAIL_OBSOLETE_MANAGED_CLEANUP)
        return
    path.unlink()
    report.add("updated", rel_path, DETAIL_OBSOLETE_MANAGED_CLEANUP)

def _cleanup_obsolete_managed_directory(
    *,
    target_root: Path,
    rel_path: str,
    manifest: ForgeInstallManifest,
    report: OperationReport,
    dry_run: bool,
) -> None:
    path = target_root / rel_path
    if not path.exists():
        return

    unknown_files: list[str] = []
    for child in sorted(path.rglob("*")):
        if not child.is_file():
            continue
        child_rel = to_manifest_path(target_root, child)
        expected_hash = manifest.managed_file_hashes.get(child_rel)
        existing = child.read_text(encoding="utf-8")
        if expected_hash is None or sha256_text(existing) != expected_hash:
            unknown_files.append(child_rel)
    if unknown_files:
        report.add("conflict", rel_path, DETAIL_OBSOLETE_MANAGED_PRESERVED)
        report.add_note(
            f"Obsolete managed path {rel_path} was preserved because it contains user-edited or unknown files: {', '.join(unknown_files)}."
        )
        return
    if dry_run:
        report.add("updated", rel_path, DETAIL_OBSOLETE_MANAGED_CLEANUP)
        return
    shutil.rmtree(path)
    report.add("updated", rel_path, DETAIL_OBSOLETE_MANAGED_CLEANUP)

def _report_deprecated_runtime_paths(*, target_root: Path, report: OperationReport) -> None:
    for rel_path in DEPRECATED_RUNTIME_PATHS:
        if (target_root / rel_path).exists():
            report.add("skipped", rel_path, DETAIL_DEPRECATED_RUNTIME)

def _cleanup_deprecated_runtime_paths(
    *,
    target_root: Path,
    desired_files: dict[str, str],
    report: OperationReport,
    dry_run: bool,
) -> None:
    expected_files = _deprecated_runtime_expected_files(desired_files)
    for rel_path in DEPRECATED_RUNTIME_PATHS:
        path = target_root / rel_path
        if not path.exists():
            continue

        unexpected_files = _deprecated_runtime_unexpected_files(
            target_root=target_root,
            root=path,
            expected_files=expected_files,
        )
        if unexpected_files:
            archive_rel_path = _deprecated_runtime_archive_path(rel_path)
            archive_path = target_root / archive_rel_path
            if archive_path.exists():
                report.add("conflict", archive_rel_path, DETAIL_CONFLICT_ARCHIVE)
                report.add_note(
                    "Deprecated runtime path "
                    f"{rel_path} was preserved because it contains user-edited or unknown files, "
                    f"but the archive destination {archive_rel_path} already exists. "
                    f"Review these files before rerunning update: {', '.join(unexpected_files)}."
                )
                continue

            report.add("updated", rel_path, DETAIL_DEPRECATED_RUNTIME_ARCHIVE)
            report.add_note(
                "Deprecated runtime path "
                f"{rel_path} contains user-edited or unknown files and "
                f"{'would be' if dry_run else 'was'} archived to {archive_rel_path} for review: "
                f"{', '.join(unexpected_files)}."
            )
            if not dry_run:
                archive_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(path), str(archive_path))
            continue

        if dry_run:
            report.add("updated", rel_path, DETAIL_DEPRECATED_RUNTIME_CLEANUP)
            continue

        shutil.rmtree(path)
        report.add("updated", rel_path, DETAIL_DEPRECATED_RUNTIME_CLEANUP)

def _deprecated_runtime_expected_files(desired_files: dict[str, str]) -> dict[str, str]:
    expected: dict[str, str] = {}
    for rel_path, content in desired_files.items():
        deprecated_path = _map_deprecated_runtime_path(rel_path)
        if deprecated_path is None:
            continue
        expected[deprecated_path] = content
    return expected

def _deprecated_runtime_unexpected_files(
    *,
    target_root: Path,
    root: Path,
    expected_files: dict[str, str],
) -> list[str]:
    unexpected: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel_path = to_manifest_path(target_root, path)
        expected = expected_files.get(rel_path)
        if expected is None:
            unexpected.append(rel_path)
            continue
        existing = path.read_text(encoding="utf-8")
        if normalize_text(existing) != normalize_text(expected):
            unexpected.append(rel_path)
    return unexpected

def _deprecated_runtime_archive_path(rel_path: str) -> str:
    suffix = rel_path.removeprefix(".forge/context/")
    return f"{DEPRECATED_RUNTIME_ARCHIVE_ROOT}/{suffix}"

def _map_deprecated_runtime_path(rel_path: str) -> str | None:
    if rel_path.startswith(".forge/runtime/meta/"):
        return rel_path.replace(".forge/runtime/meta/", ".forge/context/00-meta/", 1)
    if rel_path.startswith(".forge/runtime/modes/"):
        return rel_path.replace(".forge/runtime/modes/", ".forge/context/modes/", 1)
    return None


def _mark_preserved_baselines(report: OperationReport, *, profile: str) -> None:
    for path in build_user_owned_paths(
        profile=profile,
        context_profile_version=CONTEXT_PROFILE_VERSION_CURRENT,
    ):
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
    context_profile_version: str | None = None,
    context_layout: str | None = None,
) -> None:
    profile_label = _msg(locale, "detected_profile") if title == _msg(locale, "update_title") else _msg(locale, "profile")
    context = [
        (_msg(locale, "target"), str(target_root)),
        (profile_label, profile),
        (_msg(locale, "selected_tools"), ", ".join(selected_tools)),
        (_msg(locale, "mode"), _msg(locale, f"{mode}_mode")),
    ]
    if context_profile_version is not None:
        context.append((_msg(locale, "context_profile_version"), context_profile_version))
    if context_layout is not None:
        context.append((_msg(locale, "context_layout"), context_layout))
        context.append((_msg(locale, "context_migration"), _migration_note(context_layout)))
        context.append((_msg(locale, "user_owned_context"), _user_owned_context_note(context_layout)))
    if detected_tools is not None:
        context.append((_msg(locale, "detected_tools"), ", ".join(detected_tools)))
    report.print(locale=locale, title=title, context=context)


def _print_migration_report(
    *,
    report: OperationReport,
    locale: str,
    target_root: Path,
    profile: str,
    context_profile_version: str,
    context_layout: str,
    migration_mode: str,
    proposal_status: str,
    files_changed: str,
) -> None:
    context = [
        (_msg(locale, "target"), str(target_root)),
        (_msg(locale, "detected_profile"), profile),
        (_msg(locale, "context_profile_version"), context_profile_version),
        (_msg(locale, "context_layout"), context_layout),
        (_msg(locale, "migration_mode"), migration_mode),
        (_msg(locale, "migration_proposal"), proposal_status),
        (_msg(locale, "files_changed"), files_changed),
        (_msg(locale, "user_owned_context"), _user_owned_context_note(context_layout)),
    ]
    report.print(
        locale=locale,
        title=_msg(locale, "migrate_title"),
        context=context,
        operations_label=_msg(locale, "proposal_files"),
    )


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
