from __future__ import annotations

import io
import re
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from forge_context_engine.install_manifest import (
    CONTEXT_PROFILE_VERSION_CURRENT,
    CONTEXT_PROFILE_VERSION_LEGACY,
    load_manifest,
    load_manifest_text,
)
from forge_context_engine.runtime_ops import run_init, run_update
from forge_context_engine.runtime_ops import (
    CONTEXT_LAYOUT_EMPTY_OR_UNKNOWN,
    CONTEXT_LAYOUT_LEGACY_V1,
    CONTEXT_LAYOUT_MIXED,
    CONTEXT_LAYOUT_V2,
    DEPRECATED_RUNTIME_ARCHIVE_ROOT,
    LEGACY_CONTEXT_ARCHIVE_ROOT,
    SERVICE_V2_CONTEXT_FILES,
    WORKSPACE_V2_CONTEXT_FILES,
    _build_init_files,
    _detect_context_layout,
    run_migrate_context,
)


def _snapshot_tree(root: Path) -> dict[str, str]:
    if not root.exists():
        return {}
    snapshot: dict[str, str] = {}
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        snapshot[str(path.relative_to(root))] = path.read_text(encoding="utf-8")
    return snapshot


def _convert_repo_to_legacy_layout(target: Path, profile: str) -> str:
    manifest_path = target / ".forge/forge-install.yaml"
    manifest_text = manifest_path.read_text(encoding="utf-8")
    manifest_path.write_text(
        manifest_text.replace('context_profile_version: "2"\n', ""),
        encoding="utf-8",
    )

    expected_files = WORKSPACE_V2_CONTEXT_FILES if profile == "workspace" else SERVICE_V2_CONTEXT_FILES
    for rel_path in expected_files:
        path = target / rel_path
        if path.exists():
            path.unlink()

    legacy_product = target / ".forge/context/01-core/product.md"
    legacy_unknowns = target / ".forge/context/knowledge/unknowns.md"
    legacy_layer = target / ".forge/context/layers/application.md"
    legacy_overview = target / ".forge/context/repo-map/overview.md"
    legacy_system = target / ".forge/context/systems/legacy/system.md"
    legacy_generated = target / ".forge/context/generated/summary.md"
    legacy_decision = target / ".forge/context/decisions/decision-001.md"
    legacy_question = target / ".forge/context/unknowns/open-questions.md"
    legacy_product.parent.mkdir(parents=True, exist_ok=True)
    legacy_unknowns.parent.mkdir(parents=True, exist_ok=True)
    legacy_layer.parent.mkdir(parents=True, exist_ok=True)
    legacy_overview.parent.mkdir(parents=True, exist_ok=True)
    legacy_system.parent.mkdir(parents=True, exist_ok=True)
    legacy_generated.parent.mkdir(parents=True, exist_ok=True)
    legacy_decision.parent.mkdir(parents=True, exist_ok=True)
    legacy_question.parent.mkdir(parents=True, exist_ok=True)
    legacy_product.write_text("legacy product\n", encoding="utf-8")
    legacy_unknowns.write_text("legacy unknowns\n", encoding="utf-8")
    legacy_layer.write_text("legacy layer\n", encoding="utf-8")
    legacy_overview.write_text("legacy repo map\n", encoding="utf-8")
    legacy_system.write_text("legacy system\n", encoding="utf-8")
    legacy_generated.write_text("legacy generated\n", encoding="utf-8")
    legacy_decision.write_text("legacy decision\n", encoding="utf-8")
    legacy_question.write_text("legacy question\n", encoding="utf-8")
    return manifest_text

def _seed_deprecated_runtime_paths(
    target: Path,
    *,
    profile: str = "service",
    selected_tools: tuple[str, ...] = ("codex",),
) -> set[str]:
    desired_files = _build_init_files(
        target_root=target,
        profile=profile,
        selected_tools=selected_tools,
        ui_language="en",
    )
    seeded: set[str] = set()
    for rel_path, content in desired_files.items():
        if rel_path.startswith(".forge/runtime/meta/"):
            deprecated_path = rel_path.replace(".forge/runtime/meta/", ".forge/context/00-meta/", 1)
        elif rel_path.startswith(".forge/runtime/modes/"):
            deprecated_path = rel_path.replace(".forge/runtime/modes/", ".forge/context/modes/", 1)
        else:
            continue
        path = target / deprecated_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        seeded.add(deprecated_path)
    return seeded


def _assert_contains_all(testcase: unittest.TestCase, text: str, phrases: tuple[str, ...]) -> None:
    for phrase in phrases:
        testcase.assertIn(phrase, text)


class ContextProfileTests(unittest.TestCase):
    def test_detect_legacy_v1_layout(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / ".forge/context/01-core").mkdir(parents=True)
            (target / ".forge/context/knowledge").mkdir(parents=True)

            self.assertEqual(_detect_context_layout(target, "service"), CONTEXT_LAYOUT_LEGACY_V1)

    def test_detect_v2_service_layout(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Service Repo\n\nV2 layout.\n", encoding="utf-8")
            with redirect_stdout(io.StringIO()):
                run_init(
                    target=target,
                    profile="service",
                    selected_tools=("codex",),
                    dry_run=False,
                    assume_yes=True,
                )

            self.assertEqual(_detect_context_layout(target, "service"), CONTEXT_LAYOUT_V2)

    def test_detect_v2_workspace_layout(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Workspace Repo\n\nV2 layout.\n", encoding="utf-8")
            with redirect_stdout(io.StringIO()):
                run_init(
                    target=target,
                    profile="workspace",
                    selected_tools=("codex",),
                    dry_run=False,
                    assume_yes=True,
                )

            self.assertEqual(_detect_context_layout(target, "workspace"), CONTEXT_LAYOUT_V2)

    def test_detect_mixed_layout(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Mixed Repo\n\nMixed layout.\n", encoding="utf-8")
            with redirect_stdout(io.StringIO()):
                run_init(
                    target=target,
                    profile="service",
                    selected_tools=("codex",),
                    dry_run=False,
                    assume_yes=True,
                )

            (target / ".forge/context/01-core").mkdir(parents=True, exist_ok=True)
            self.assertEqual(_detect_context_layout(target, "service"), CONTEXT_LAYOUT_MIXED)

    def test_detect_empty_or_unknown_layout(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / ".forge/context").mkdir(parents=True)

            self.assertEqual(_detect_context_layout(target, "service"), CONTEXT_LAYOUT_EMPTY_OR_UNKNOWN)

    def test_fresh_service_init_creates_v2_service_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Billing API\n\nService for invoice reads.\n", encoding="utf-8")
            (target / "pyproject.toml").write_text(
                '[project]\nname = "billing-api"\nrequires-python = ">=3.12"\n',
                encoding="utf-8",
            )

            with redirect_stdout(io.StringIO()):
                status = run_init(
                    target=target,
                    profile="service",
                    selected_tools=("codex", "claude"),
                    dry_run=False,
                    assume_yes=True,
                )

            self.assertEqual(status, 0)

            expected_files = {
                *SERVICE_V2_CONTEXT_FILES,
                ".forge/generated/README.md",
                ".forge/skills/forge-update-context/SKILL.md",
                ".forge/runtime/meta/conventions.md",
                ".forge/runtime/meta/context-manifest.md",
                ".forge/runtime/modes/ask.md",
                ".forge/runtime/modes/plan.md",
                ".forge/runtime/modes/update-context.md",
                ".claude/commands/forge-update-context.md",
            }
            for rel_path in expected_files:
                self.assertTrue((target / rel_path).exists(), rel_path)

            forbidden_paths = {
                ".forge/context/layers",
                ".forge/context/01-core",
                ".forge/context/knowledge",
                ".forge/context/systems",
                ".forge/context/generated",
                ".forge/context/repo-map",
                ".forge/context/decisions",
                ".forge/context/unknowns",
                ".forge/context/00-meta",
                ".forge/context/modes",
            }
            for rel_path in forbidden_paths:
                self.assertFalse((target / rel_path).exists(), rel_path)

            legacy_seed_files = {
                ".forge/context/01-core/product.md",
                ".forge/context/01-core/architecture.md",
                ".forge/context/01-core/principles.md",
                ".forge/context/01-core/constraints.md",
                ".forge/context/knowledge/inferred.md",
                ".forge/context/knowledge/unknowns.md",
                ".forge/context/repo-map/overview.md",
                ".forge/context/systems/billing-api/system.md",
            }
            for rel_path in legacy_seed_files:
                self.assertFalse((target / rel_path).exists(), rel_path)

            manifest = load_manifest(target / ".forge" / "forge-install.yaml")
            self.assertEqual(manifest.context_profile_version, CONTEXT_PROFILE_VERSION_CURRENT)
            self.assertIn(".forge/context/00-index.md", manifest.user_owned_paths)
            self.assertIn(".forge/context/01-service-overview.md", manifest.user_owned_paths)
            self.assertIn(".forge/context-patches/", manifest.user_owned_paths)
            self.assertIn(".forge/generated/", manifest.user_owned_paths)
            self.assertIn(".forge/generated/README.md", manifest.managed_paths)
            self.assertNotIn(".forge/runtime/meta/", manifest.user_owned_paths)
            self.assertNotIn(".forge/context/01-core/", manifest.user_owned_paths)

    def test_fresh_workspace_init_creates_v2_workspace_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Platform Workspace\n\nLinks multiple services.\n", encoding="utf-8")
            (target / "services" / "payments").mkdir(parents=True)
            (target / "services" / "payments" / "README.md").write_text("payments\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                status = run_init(
                    target=target,
                    profile="workspace",
                    selected_tools=("codex", "claude"),
                    dry_run=False,
                    assume_yes=True,
                )

            self.assertEqual(status, 0)

            expected_files = {
                *WORKSPACE_V2_CONTEXT_FILES,
                ".forge/generated/README.md",
                ".forge/skills/forge-update-context/SKILL.md",
                ".forge/runtime/meta/conventions.md",
                ".forge/runtime/meta/context-manifest.md",
                ".forge/runtime/modes/ask.md",
                ".forge/runtime/modes/update-context.md",
                ".forge/workspace.yaml",
                ".claude/commands/forge-update-context.md",
            }
            for rel_path in expected_files:
                self.assertTrue((target / rel_path).exists(), rel_path)

            forbidden_paths = {
                ".forge/context/layers",
                ".forge/context/01-core",
                ".forge/context/knowledge",
                ".forge/context/systems",
                ".forge/context/generated",
                ".forge/context/repo-map",
                ".forge/context/decisions",
                ".forge/context/unknowns",
                ".forge/context/00-meta",
                ".forge/context/modes",
                ".forge/context/01-service-overview.md",
            }
            for rel_path in forbidden_paths:
                self.assertFalse((target / rel_path).exists(), rel_path)

            legacy_seed_files = {
                ".forge/context/01-core/product.md",
                ".forge/context/knowledge/inferred.md",
                ".forge/context/repo-map/overview.md",
                ".forge/context/systems/platform-workspace/system.md",
            }
            for rel_path in legacy_seed_files:
                self.assertFalse((target / rel_path).exists(), rel_path)

            manifest = load_manifest(target / ".forge" / "forge-install.yaml")
            self.assertEqual(manifest.context_profile_version, CONTEXT_PROFILE_VERSION_CURRENT)
            self.assertIn(".forge/generated/README.md", manifest.managed_paths)

    def test_update_preserves_user_owned_v2_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Example Service\n\nUser-owned context test.\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                status = run_init(
                    target=target,
                    profile="service",
                    selected_tools=("codex",),
                    dry_run=False,
                    assume_yes=True,
                )
            self.assertEqual(status, 0)

            overview = target / ".forge/context/01-service-overview.md"
            original = overview.read_text(encoding="utf-8")
            edited = original + "\nUser-owned note.\n"
            overview.write_text(edited, encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                update_status = run_update(
                    target=target,
                    dry_run=False,
                    assume_yes=True,
                    selected_tools=None,
                )

            self.assertEqual(update_status, 0)
            self.assertEqual(overview.read_text(encoding="utf-8"), edited)

    def test_update_recreates_generated_dir_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Example Service\n\nGenerated dir repair.\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                status = run_init(
                    target=target,
                    profile="service",
                    selected_tools=("codex",),
                    dry_run=False,
                    assume_yes=True,
                )
            self.assertEqual(status, 0)

            shutil.rmtree(target / ".forge/generated")
            self.assertFalse((target / ".forge/generated").exists())

            output = io.StringIO()
            with redirect_stdout(output):
                update_status = run_update(
                    target=target,
                    dry_run=False,
                    assume_yes=True,
                    selected_tools=None,
                )

            self.assertEqual(update_status, 0)
            self.assertTrue((target / ".forge/generated/README.md").exists())
            self.assertIn(".forge/generated/README.md", output.getvalue())

    def test_update_dry_run_reports_service_v2_layout(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Service Repo\n\nDry-run reporting.\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                run_init(
                    target=target,
                    profile="service",
                    selected_tools=("codex",),
                    dry_run=False,
                    assume_yes=True,
                )

            output = io.StringIO()
            with redirect_stdout(output):
                status = run_update(
                    target=target,
                    dry_run=True,
                    assume_yes=True,
                    selected_tools=None,
                )

            self.assertEqual(status, 0)
            rendered = output.getvalue()
            self.assertIn("Detected Forge profile: service", rendered)
            self.assertNotIn("\nProfile: service\n", rendered)
            self.assertIn("Detected context profile version: 2", rendered)
            self.assertIn("Detected context layout: v2", rendered)
            self.assertIn("Migration: not applied automatically", rendered)
            self.assertIn("User-owned context: preserved; numbered v2 context files remain user-owned", rendered)

    def test_update_dry_run_reports_workspace_v2_layout(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Workspace Repo\n\nDry-run reporting.\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                run_init(
                    target=target,
                    profile="workspace",
                    selected_tools=("codex",),
                    dry_run=False,
                    assume_yes=True,
                )

            output = io.StringIO()
            with redirect_stdout(output):
                status = run_update(
                    target=target,
                    dry_run=True,
                    assume_yes=True,
                    selected_tools=None,
                )

            self.assertEqual(status, 0)
            rendered = output.getvalue()
            self.assertIn("Detected Forge profile: workspace", rendered)
            self.assertIn("Detected context profile version: 2", rendered)
            self.assertIn("Detected context layout: v2", rendered)

    def test_update_dry_run_reports_legacy_v1_without_migration(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Legacy Repo\n\nDry-run reporting.\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                run_init(
                    target=target,
                    profile="service",
                    selected_tools=("codex",),
                    dry_run=False,
                    assume_yes=True,
                )

            manifest_path = target / ".forge/forge-install.yaml"
            manifest_path.write_text(
                manifest_path.read_text(encoding="utf-8").replace('context_profile_version: "2"\n', ""),
                encoding="utf-8",
            )
            for rel_path in SERVICE_V2_CONTEXT_FILES:
                path = target / rel_path
                if path.exists():
                    path.unlink()
            (target / ".forge/context/01-core").mkdir(parents=True, exist_ok=True)
            (target / ".forge/context/knowledge").mkdir(parents=True, exist_ok=True)

            output = io.StringIO()
            with redirect_stdout(output):
                status = run_update(
                    target=target,
                    dry_run=True,
                    assume_yes=True,
                    selected_tools=None,
                )

            self.assertEqual(status, 0)
            rendered = output.getvalue()
            self.assertIn("Detected context profile version: legacy-v1", rendered)
            self.assertIn("Detected context layout: legacy-v1", rendered)
            self.assertIn("Migration: not applied automatically; v2 context profiles are available", rendered)
            self.assertIn("User-owned context: preserved; legacy-v1 context remains user-owned", rendered)

    def test_update_dry_run_reports_mixed_layout_without_cleanup(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Mixed Repo\n\nDry-run reporting.\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                run_init(
                    target=target,
                    profile="service",
                    selected_tools=("codex",),
                    dry_run=False,
                    assume_yes=True,
                )

            (target / ".forge/context/01-core").mkdir(parents=True, exist_ok=True)

            output = io.StringIO()
            with redirect_stdout(output):
                status = run_update(
                    target=target,
                    dry_run=True,
                    assume_yes=True,
                    selected_tools=None,
                )

            self.assertEqual(status, 0)
            rendered = output.getvalue()
            self.assertIn("Detected context layout: mixed", rendered)
            self.assertIn("Migration: not applied automatically; no cleanup performed for mixed layouts", rendered)
            self.assertIn("User-owned context: preserved; legacy and v2 context both remain user-owned", rendered)

    def test_update_dry_run_writes_no_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Service Repo\n\nDry-run no-write check.\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                run_init(
                    target=target,
                    profile="service",
                    selected_tools=("codex",),
                    dry_run=False,
                    assume_yes=True,
                )

            before = (target / ".forge/context/01-service-overview.md").read_text(encoding="utf-8")
            with redirect_stdout(io.StringIO()):
                status = run_update(
                    target=target,
                    dry_run=True,
                    assume_yes=True,
                    selected_tools=None,
                )

            self.assertEqual(status, 0)
            after = (target / ".forge/context/01-service-overview.md").read_text(encoding="utf-8")
            self.assertEqual(before, after)

    def test_migrate_context_dry_run_on_legacy_writes_no_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Legacy Repo\n\nMigration dry-run.\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                run_init(
                    target=target,
                    profile="service",
                    selected_tools=("codex",),
                    dry_run=False,
                    assume_yes=True,
                )

            _convert_repo_to_legacy_layout(target, profile="service")
            before_context = _snapshot_tree(target / ".forge/context")
            before_manifest = (target / ".forge/forge-install.yaml").read_text(encoding="utf-8")

            output = io.StringIO()
            with redirect_stdout(output):
                status = run_migrate_context(target=target, dry_run=True)

            self.assertEqual(status, 0)
            self.assertEqual(before_context, _snapshot_tree(target / ".forge/context"))
            self.assertFalse((target / LEGACY_CONTEXT_ARCHIVE_ROOT).exists())
            self.assertEqual((target / ".forge/forge-install.yaml").read_text(encoding="utf-8"), before_manifest)
            rendered = output.getvalue()
            self.assertIn("Detected context layout: legacy-v1", rendered)
            self.assertIn("Migration mode: dry-run", rendered)
            self.assertIn("would migrate legacy-v1 context to numbered v2 files", rendered)
            self.assertIn("legacy-v1 context archive", rendered)
            self.assertIn("context profile version migration", rendered)
            for rel_path in (
                ".forge/context-archive/legacy-v1/01-core",
                ".forge/context-archive/legacy-v1/knowledge",
                ".forge/context-archive/legacy-v1/layers",
                ".forge/context-archive/legacy-v1/repo-map",
                ".forge/context-archive/legacy-v1/systems",
                ".forge/context-archive/legacy-v1/generated",
                ".forge/context-archive/legacy-v1/decisions",
                ".forge/context-archive/legacy-v1/unknowns",
            ):
                self.assertIn(rel_path, rendered)
            self.assertIn("Files changed: none", rendered)

    def test_migrate_context_on_legacy_writes_v2_files_into_forge_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Legacy Repo\n\nMigration write test.\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                run_init(
                    target=target,
                    profile="service",
                    selected_tools=("codex",),
                    dry_run=False,
                    assume_yes=True,
                )

            _convert_repo_to_legacy_layout(target, profile="service")

            with redirect_stdout(io.StringIO()):
                status = run_migrate_context(target=target, dry_run=False)

            self.assertEqual(status, 0)
            for rel_path in SERVICE_V2_CONTEXT_FILES:
                self.assertTrue((target / rel_path).exists(), rel_path)

    def test_migrate_context_on_legacy_archives_legacy_v1_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Legacy Repo\n\nArchive legacy paths.\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                run_init(
                    target=target,
                    profile="service",
                    selected_tools=("codex",),
                    dry_run=False,
                    assume_yes=True,
                )

            _convert_repo_to_legacy_layout(target, profile="service")

            with redirect_stdout(io.StringIO()):
                status = run_migrate_context(target=target, dry_run=False)

            self.assertEqual(status, 0)
            for name in (
                "01-core",
                "knowledge",
                "layers",
                "repo-map",
                "systems",
                "generated",
                "decisions",
                "unknowns",
            ):
                self.assertFalse((target / ".forge/context" / name).exists(), name)
                self.assertTrue((target / LEGACY_CONTEXT_ARCHIVE_ROOT / name).exists(), name)

    def test_migrate_context_on_legacy_preserves_legacy_files_in_archive(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Legacy Repo\n\nLegacy file preservation.\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                run_init(
                    target=target,
                    profile="service",
                    selected_tools=("codex",),
                    dry_run=False,
                    assume_yes=True,
                )

            _convert_repo_to_legacy_layout(target, profile="service")
            legacy_files = [
                target / ".forge/context/01-core/product.md",
                target / ".forge/context/knowledge/unknowns.md",
                target / ".forge/context/layers/application.md",
                target / ".forge/context/repo-map/overview.md",
                target / ".forge/context/systems/legacy/system.md",
                target / ".forge/context/generated/summary.md",
                target / ".forge/context/decisions/decision-001.md",
                target / ".forge/context/unknowns/open-questions.md",
            ]

            with redirect_stdout(io.StringIO()):
                status = run_migrate_context(target=target, dry_run=False)

            self.assertEqual(status, 0)
            archived_files = [
                target / LEGACY_CONTEXT_ARCHIVE_ROOT / "01-core/product.md",
                target / LEGACY_CONTEXT_ARCHIVE_ROOT / "knowledge/unknowns.md",
                target / LEGACY_CONTEXT_ARCHIVE_ROOT / "layers/application.md",
                target / LEGACY_CONTEXT_ARCHIVE_ROOT / "repo-map/overview.md",
                target / LEGACY_CONTEXT_ARCHIVE_ROOT / "systems/legacy/system.md",
                target / LEGACY_CONTEXT_ARCHIVE_ROOT / "generated/summary.md",
                target / LEGACY_CONTEXT_ARCHIVE_ROOT / "decisions/decision-001.md",
                target / LEGACY_CONTEXT_ARCHIVE_ROOT / "unknowns/open-questions.md",
            ]
            for path in legacy_files:
                self.assertFalse(path.exists(), str(path))
            for path in archived_files:
                self.assertTrue(path.exists(), str(path))

    def test_migrate_context_on_legacy_preserves_current_generated_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Legacy Repo\n\nCurrent generated preservation.\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                run_init(
                    target=target,
                    profile="service",
                    selected_tools=("codex",),
                    dry_run=False,
                    assume_yes=True,
                )

            _convert_repo_to_legacy_layout(target, profile="service")
            current_generated = target / ".forge/generated/manual-note.md"
            current_generated.parent.mkdir(parents=True, exist_ok=True)
            current_generated.write_text("keep me\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                status = run_migrate_context(target=target, dry_run=False)

            self.assertEqual(status, 0)
            self.assertTrue(current_generated.exists())
            self.assertEqual(current_generated.read_text(encoding="utf-8"), "keep me\n")
            self.assertFalse((target / LEGACY_CONTEXT_ARCHIVE_ROOT / "generated/manual-note.md").exists())

    def test_migrate_context_on_legacy_updates_manifest_to_v2(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Legacy Repo\n\nManifest migration.\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                run_init(
                    target=target,
                    profile="service",
                    selected_tools=("codex",),
                    dry_run=False,
                    assume_yes=True,
                )

            _convert_repo_to_legacy_layout(target, profile="service")

            with redirect_stdout(io.StringIO()):
                status = run_migrate_context(target=target, dry_run=False)

            self.assertEqual(status, 0)
            manifest = load_manifest(target / ".forge/forge-install.yaml")
            self.assertEqual(manifest.context_profile_version, CONTEXT_PROFILE_VERSION_CURRENT)
            self.assertIn(".forge/context/01-service-overview.md", manifest.user_owned_paths)
            self.assertIn(".forge/context/99-open-questions.md", manifest.user_owned_paths)
            self.assertIn(".forge/context-patches/", manifest.user_owned_paths)
            self.assertIn(".forge/generated/", manifest.user_owned_paths)
            self.assertIn(".forge/context-archive/legacy-v1/", manifest.user_owned_paths)
            self.assertIn(".forge/context/00-index.md", manifest.user_owned_paths)
            self.assertNotIn(".forge/context/01-core/", manifest.user_owned_paths)
            self.assertNotIn(".forge/context/layers/", manifest.user_owned_paths)
            self.assertNotIn(".forge/context/repo-map/", manifest.user_owned_paths)
            self.assertNotIn(".forge/context/systems/", manifest.user_owned_paths)
            self.assertNotIn(".forge/context/knowledge/", manifest.user_owned_paths)
            self.assertNotIn(".forge/context/decisions/", manifest.user_owned_paths)
            self.assertNotIn(".forge/context/unknowns/", manifest.user_owned_paths)

    def test_update_dry_run_after_migration_reports_v2_user_owned_paths_not_active_legacy_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Legacy Repo\n\nPost-migration update report.\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                run_init(
                    target=target,
                    profile="service",
                    selected_tools=("codex",),
                    dry_run=False,
                    assume_yes=True,
                )

            _convert_repo_to_legacy_layout(target, profile="service")

            with redirect_stdout(io.StringIO()):
                migrate_status = run_migrate_context(target=target, dry_run=False)

            self.assertEqual(migrate_status, 0)

            output = io.StringIO()
            with redirect_stdout(output):
                update_status = run_update(
                    target=target,
                    dry_run=True,
                    assume_yes=True,
                    selected_tools=None,
                )

            self.assertEqual(update_status, 0)
            rendered = output.getvalue()
            self.assertIn("Detected context profile version: 2", rendered)
            self.assertIn("Detected context layout: v2", rendered)
            self.assertIn(".forge/context/01-service-overview.md", rendered)
            self.assertIn(".forge/context/99-open-questions.md", rendered)
            self.assertIn(".forge/context-patches/", rendered)
            self.assertIn(".forge/generated/", rendered)
            self.assertIn(".forge/context-archive/legacy-v1/", rendered)
            self.assertNotIn(".forge/context/01-core/", rendered)
            self.assertNotIn(".forge/context/layers/", rendered)
            self.assertNotIn(".forge/context/repo-map/", rendered)
            self.assertNotIn(".forge/context/systems/", rendered)
            self.assertNotIn(".forge/context/knowledge/", rendered)
            self.assertNotIn(".forge/context/decisions/", rendered)
            self.assertNotIn(".forge/context/unknowns/", rendered)

    def test_update_cleans_deprecated_runtime_paths_when_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Service Repo\n\nDeprecated runtime cleanup.\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                run_init(
                    target=target,
                    profile="service",
                    selected_tools=("codex",),
                    dry_run=False,
                    assume_yes=True,
                )

            seeded = _seed_deprecated_runtime_paths(target)
            self.assertTrue(seeded)
            self.assertTrue((target / ".forge/context/00-meta").exists())
            self.assertTrue((target / ".forge/context/modes").exists())

            with redirect_stdout(io.StringIO()):
                status = run_update(
                    target=target,
                    dry_run=False,
                    assume_yes=True,
                    selected_tools=None,
                )

            self.assertEqual(status, 0)
            self.assertFalse((target / ".forge/context/00-meta").exists())
            self.assertFalse((target / ".forge/context/modes").exists())

    def test_update_archives_user_edited_deprecated_runtime_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Service Repo\n\nDeprecated runtime archive.\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                run_init(
                    target=target,
                    profile="service",
                    selected_tools=("codex",),
                    dry_run=False,
                    assume_yes=True,
                )

            _seed_deprecated_runtime_paths(target)
            edited = target / ".forge/context/modes/ask.md"
            edited.write_text(edited.read_text(encoding="utf-8") + "\nuser edit\n", encoding="utf-8")
            extra = target / ".forge/context/00-meta/custom.md"
            extra.write_text("custom\n", encoding="utf-8")
            archive_meta = target / DEPRECATED_RUNTIME_ARCHIVE_ROOT / "00-meta"
            archive_modes = target / DEPRECATED_RUNTIME_ARCHIVE_ROOT / "modes"

            output = io.StringIO()
            with redirect_stdout(output):
                status = run_update(
                    target=target,
                    dry_run=False,
                    assume_yes=True,
                    selected_tools=None,
                )

            self.assertEqual(status, 0)
            self.assertFalse((target / ".forge/context/00-meta").exists())
            self.assertFalse((target / ".forge/context/modes").exists())
            self.assertEqual((archive_modes / "ask.md").read_text(encoding="utf-8").splitlines()[-1], "user edit")
            self.assertTrue((archive_meta / "custom.md").exists())
            rendered = output.getvalue()
            self.assertIn("deprecated runtime path archived for review", rendered)
            self.assertIn(f"{DEPRECATED_RUNTIME_ARCHIVE_ROOT}/00-meta", rendered)
            self.assertIn(f"{DEPRECATED_RUNTIME_ARCHIVE_ROOT}/modes", rendered)
            manifest = load_manifest(target / ".forge/forge-install.yaml")
            self.assertIn(f"{DEPRECATED_RUNTIME_ARCHIVE_ROOT}/", manifest.user_owned_paths)

    def test_update_dry_run_deprecated_runtime_cleanup_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Service Repo\n\nDeprecated runtime dry-run.\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                run_init(
                    target=target,
                    profile="service",
                    selected_tools=("codex",),
                    dry_run=False,
                    assume_yes=True,
                )

            _seed_deprecated_runtime_paths(target)
            edited = target / ".forge/context/modes/ask.md"
            edited.write_text(edited.read_text(encoding="utf-8") + "\nuser edit\n", encoding="utf-8")
            before = _snapshot_tree(target / ".forge/context")
            archive_root = target / DEPRECATED_RUNTIME_ARCHIVE_ROOT

            output = io.StringIO()
            with redirect_stdout(output):
                status = run_update(
                    target=target,
                    dry_run=True,
                    assume_yes=True,
                    selected_tools=None,
                )

            self.assertEqual(status, 0)
            self.assertEqual(before, _snapshot_tree(target / ".forge/context"))
            self.assertFalse(archive_root.exists())
            self.assertTrue((target / ".forge/context/00-meta").exists())
            self.assertTrue((target / ".forge/context/modes").exists())
            rendered = output.getvalue()
            self.assertIn(".forge/context/00-meta - deprecated managed runtime path cleanup", rendered)
            self.assertIn(".forge/context/modes - deprecated runtime path archived for review", rendered)
            self.assertIn(f"{DEPRECATED_RUNTIME_ARCHIVE_ROOT}/modes", rendered)

    def test_v2_update_is_idempotent_after_deprecated_runtime_cleanup_and_archive(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Service Repo\n\nDeprecated runtime idempotence.\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                run_init(
                    target=target,
                    profile="service",
                    selected_tools=("codex",),
                    dry_run=False,
                    assume_yes=True,
                )

            _seed_deprecated_runtime_paths(target)
            edited = target / ".forge/context/modes/ask.md"
            edited.write_text(edited.read_text(encoding="utf-8") + "\nuser edit\n", encoding="utf-8")
            with redirect_stdout(io.StringIO()):
                first_status = run_update(
                    target=target,
                    dry_run=False,
                    assume_yes=True,
                    selected_tools=None,
                )

            self.assertEqual(first_status, 0)

            output = io.StringIO()
            with redirect_stdout(output):
                second_status = run_update(
                    target=target,
                    dry_run=True,
                    assume_yes=True,
                    selected_tools=None,
                )

            self.assertEqual(second_status, 0)
            self.assertFalse((target / ".forge/context/00-meta").exists())
            self.assertFalse((target / ".forge/context/modes").exists())
            rendered = output.getvalue()
            self.assertIn("Created: 0", rendered)
            self.assertIn("Updated: 0", rendered)
            self.assertIn("Conflicts: 0", rendered)
            self.assertNotIn(".forge/context/00-meta", rendered)
            self.assertNotIn(".forge/context/modes", rendered)

    def test_update_dry_run_reports_new_update_context_managed_files_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Service Repo\n\nManaged file additions.\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                status = run_init(
                    target=target,
                    profile="service",
                    selected_tools=("codex", "claude"),
                    dry_run=False,
                    assume_yes=True,
                )

            self.assertEqual(status, 0)
            for rel_path in (
                ".forge/skills/forge-update-context/SKILL.md",
                ".forge/runtime/modes/update-context.md",
                ".claude/commands/forge-update-context.md",
            ):
                (target / rel_path).unlink()

            output = io.StringIO()
            with redirect_stdout(output):
                update_status = run_update(
                    target=target,
                    dry_run=True,
                    assume_yes=True,
                    selected_tools=None,
                )

            self.assertEqual(update_status, 0)
            rendered = output.getvalue()
            self.assertIn(".forge/skills/forge-update-context/SKILL.md", rendered)
            self.assertIn(".forge/runtime/modes/update-context.md", rendered)
            self.assertIn(".claude/commands/forge-update-context.md", rendered)

    def test_update_recreates_update_context_managed_files_and_is_idempotent_afterward(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Service Repo\n\nManaged file recreation.\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                status = run_init(
                    target=target,
                    profile="service",
                    selected_tools=("codex", "claude"),
                    dry_run=False,
                    assume_yes=True,
                )

            self.assertEqual(status, 0)
            for rel_path in (
                ".forge/skills/forge-update-context/SKILL.md",
                ".forge/runtime/modes/update-context.md",
                ".claude/commands/forge-update-context.md",
            ):
                (target / rel_path).unlink()

            with redirect_stdout(io.StringIO()):
                update_status = run_update(
                    target=target,
                    dry_run=False,
                    assume_yes=True,
                    selected_tools=None,
                )

            self.assertEqual(update_status, 0)
            for rel_path in (
                ".forge/skills/forge-update-context/SKILL.md",
                ".forge/runtime/modes/update-context.md",
                ".claude/commands/forge-update-context.md",
            ):
                self.assertTrue((target / rel_path).exists(), rel_path)

            output = io.StringIO()
            with redirect_stdout(output):
                second_status = run_update(
                    target=target,
                    dry_run=True,
                    assume_yes=True,
                    selected_tools=None,
                )

            self.assertEqual(second_status, 0)
            rendered = output.getvalue()
            self.assertIn("Created: 0", rendered)
            self.assertIn("Updated: 0", rendered)
            self.assertIn("Conflicts: 0", rendered)

    def test_init_with_claude_selected_installs_wrapper_commands_and_local_gitignore(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Claude Repo\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                status = run_init(
                    target=target,
                    profile="service",
                    selected_tools=("codex", "claude"),
                    dry_run=False,
                    assume_yes=True,
                )

            self.assertEqual(status, 0)
            self.assertTrue((target / "CLAUDE.md").exists())
            self.assertTrue((target / ".claude/commands/forge-update-context.md").exists())
            self.assertTrue((target / ".claude/.gitignore").exists())
            gitignore = (target / ".claude/.gitignore").read_text(encoding="utf-8")
            self.assertIn("settings.local.json", gitignore)
            self.assertIn("!commands/**", gitignore)

    def test_update_adds_copilot_wrappers_and_skills_when_tools_enable_copilot(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Agents Only\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                status = run_init(
                    target=target,
                    profile="service",
                    selected_tools=("codex",),
                    dry_run=False,
                    assume_yes=True,
                )
            self.assertEqual(status, 0)

            preview = io.StringIO()
            with redirect_stdout(preview):
                dry_status = run_update(
                    target=target,
                    dry_run=True,
                    assume_yes=True,
                    selected_tools=("codex", "copilot"),
                )

            self.assertEqual(dry_status, 0)
            rendered = preview.getvalue()
            self.assertIn(".github/copilot-instructions.md", rendered)
            self.assertIn(".github/skills/forge-update-context/SKILL.md", rendered)
            self.assertIn(".github/skills/forge-verify-context/SKILL.md", rendered)
            self.assertNotIn("CLAUDE.md", rendered)

            with redirect_stdout(io.StringIO()):
                update_status = run_update(
                    target=target,
                    dry_run=False,
                    assume_yes=True,
                    selected_tools=("codex", "copilot"),
                )

            self.assertEqual(update_status, 0)
            self.assertTrue((target / ".github/copilot-instructions.md").exists())
            self.assertTrue((target / ".github/skills/forge-update-context/SKILL.md").exists())
            self.assertTrue((target / ".github/skills/forge-verify-context/SKILL.md").exists())
            self.assertFalse((target / "CLAUDE.md").exists())
            self.assertFalse((target / ".claude").exists())

            second_preview = io.StringIO()
            with redirect_stdout(second_preview):
                second_status = run_update(
                    target=target,
                    dry_run=True,
                    assume_yes=True,
                    selected_tools=None,
                )

            self.assertEqual(second_status, 0)
            second_rendered = second_preview.getvalue()
            self.assertIn("Created: 0", second_rendered)
            self.assertIn("Updated: 0", second_rendered)
            self.assertIn("Conflicts: 0", second_rendered)

    def test_explicit_tool_replacement_removes_managed_claude_files_and_preserves_user_edited_claude_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Tool Swap Repo\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                status = run_init(
                    target=target,
                    profile="service",
                    selected_tools=("codex", "claude"),
                    dry_run=False,
                    assume_yes=True,
                )

            self.assertEqual(status, 0)
            self.assertTrue((target / "CLAUDE.md").exists())
            self.assertTrue((target / ".claude/.gitignore").exists())
            self.assertTrue((target / ".claude/commands/forge-update-context.md").exists())

            preview = io.StringIO()
            with redirect_stdout(preview):
                dry_status = run_update(
                    target=target,
                    dry_run=True,
                    assume_yes=True,
                    selected_tools=("codex", "copilot"),
                )

            self.assertEqual(dry_status, 0)
            rendered = preview.getvalue()
            self.assertIn("codex, claude -> codex, copilot", rendered)
            self.assertIn(".github/copilot-instructions.md", rendered)
            self.assertIn("CLAUDE.md", rendered)
            self.assertEqual((target / "CLAUDE.md").exists(), True)

            with redirect_stdout(io.StringIO()):
                update_status = run_update(
                    target=target,
                    dry_run=False,
                    assume_yes=True,
                    selected_tools=("codex", "copilot"),
                )

            self.assertEqual(update_status, 0)
            self.assertTrue((target / "AGENTS.md").exists())
            self.assertTrue((target / ".github/copilot-instructions.md").exists())
            self.assertTrue((target / ".github/skills/forge-update-context/SKILL.md").exists())
            self.assertTrue((target / ".github/skills/forge-verify-context/SKILL.md").exists())
            self.assertTrue((target / ".forge/skills/forge-update-context/SKILL.md").exists())
            self.assertFalse((target / ".github/prompts").exists())
            self.assertFalse((target / "CLAUDE.md").exists())
            self.assertFalse((target / ".claude/.gitignore").exists())
            self.assertFalse((target / ".claude/commands").exists())

            manifest = load_manifest(target / ".forge/forge-install.yaml")
            self.assertEqual(manifest.selected_tools, ("codex", "copilot"))

            second_preview = io.StringIO()
            with redirect_stdout(second_preview):
                second_status = run_update(
                    target=target,
                    dry_run=True,
                    assume_yes=True,
                    selected_tools=None,
                )

            self.assertEqual(second_status, 0)
            second_rendered = second_preview.getvalue()
            self.assertIn("Created: 0", second_rendered)
            self.assertIn("Updated: 0", second_rendered)
            self.assertIn("Conflicts: 0", second_rendered)

        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Tool Swap Conflict Repo\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                status = run_init(
                    target=target,
                    profile="service",
                    selected_tools=("codex", "claude"),
                    dry_run=False,
                    assume_yes=True,
                )

            self.assertEqual(status, 0)
            claude_path = target / "CLAUDE.md"
            original = claude_path.read_text(encoding="utf-8")
            claude_path.write_text("Project operator notes.\n\n" + original, encoding="utf-8")

            output = io.StringIO()
            with redirect_stdout(output):
                conflict_status = run_update(
                    target=target,
                    dry_run=False,
                    assume_yes=True,
                    selected_tools=("codex", "copilot"),
                )

            self.assertEqual(conflict_status, 1)
            self.assertTrue((target / "CLAUDE.md").exists())
            self.assertTrue((target / ".claude/.gitignore").exists())
            self.assertTrue((target / ".claude/commands/forge-update-context.md").exists())
            self.assertEqual(claude_path.read_text(encoding="utf-8"), "Project operator notes.\n\n" + original)
            self.assertIn("manual review required", output.getvalue())

    def test_update_archives_and_replaces_legacy_agents_wrapper_preamble(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Agents Repo\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                run_init(
                    target=target,
                    profile="service",
                    selected_tools=("codex",),
                    dry_run=False,
                    assume_yes=True,
                )

            agents_path = target / "AGENTS.md"
            original = agents_path.read_text(encoding="utf-8")
            legacy_preamble = "# Legacy Forge Wrapper\n\nSee `.forge/context/00-meta` and `source_commit`.\n\n"
            agents_path.write_text(legacy_preamble + original, encoding="utf-8")

            preview = io.StringIO()
            with redirect_stdout(preview):
                dry_status = run_update(
                    target=target,
                    dry_run=True,
                    assume_yes=True,
                    selected_tools=None,
                )

            self.assertEqual(dry_status, 0)
            self.assertEqual(agents_path.read_text(encoding="utf-8"), legacy_preamble + original)
            self.assertIn("legacy wrapper archived and replaced", preview.getvalue())
            self.assertFalse((target / ".forge/context-archive/deprecated-root-wrappers/AGENTS.md").exists())

            with redirect_stdout(io.StringIO()):
                update_status = run_update(
                    target=target,
                    dry_run=False,
                    assume_yes=True,
                    selected_tools=None,
                )

            self.assertEqual(update_status, 0)
            self.assertEqual(
                (target / ".forge/context-archive/deprecated-root-wrappers/AGENTS.md").read_text(encoding="utf-8"),
                legacy_preamble + original,
            )
            updated = agents_path.read_text(encoding="utf-8")
            self.assertNotIn(".forge/context/00-meta", updated)
            self.assertNotIn("source_commit", updated)
            self.assertTrue(updated.startswith("<!-- BEGIN FORGE MANAGED BLOCK -->"))

            second_preview = io.StringIO()
            with redirect_stdout(second_preview):
                second_status = run_update(
                    target=target,
                    dry_run=True,
                    assume_yes=True,
                    selected_tools=None,
                )

            self.assertEqual(second_status, 0)
            rendered = second_preview.getvalue()
            self.assertIn("Created: 0", rendered)
            self.assertIn("Updated: 0", rendered)
            self.assertIn("Conflicts: 0", rendered)

    def test_update_archives_and_replaces_legacy_claude_wrapper_preamble(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Claude Repo\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                run_init(
                    target=target,
                    profile="service",
                    selected_tools=("codex", "claude"),
                    dry_run=False,
                    assume_yes=True,
                )

            claude_path = target / "CLAUDE.md"
            original = claude_path.read_text(encoding="utf-8")
            legacy_preamble = "# Legacy Claude Wrapper\n\nUse `.forge/context/modes` and `last_verified`.\n\n"
            claude_path.write_text(legacy_preamble + original, encoding="utf-8")

            preview = io.StringIO()
            with redirect_stdout(preview):
                dry_status = run_update(
                    target=target,
                    dry_run=True,
                    assume_yes=True,
                    selected_tools=None,
                )

            self.assertEqual(dry_status, 0)
            self.assertIn("legacy wrapper archived and replaced", preview.getvalue())
            self.assertFalse((target / ".forge/context-archive/deprecated-root-wrappers/CLAUDE.md").exists())

            with redirect_stdout(io.StringIO()):
                update_status = run_update(
                    target=target,
                    dry_run=False,
                    assume_yes=True,
                    selected_tools=None,
                )

            self.assertEqual(update_status, 0)
            updated = claude_path.read_text(encoding="utf-8")
            self.assertNotIn(".forge/context/modes", updated)
            self.assertNotIn("last_verified", updated)
            self.assertTrue((target / ".forge/context-archive/deprecated-root-wrappers/CLAUDE.md").exists())

    def test_update_preserves_unknown_unmanaged_wrapper_content_for_manual_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Review Repo\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                run_init(
                    target=target,
                    profile="service",
                    selected_tools=("codex",),
                    dry_run=False,
                    assume_yes=True,
                )

            agents_path = target / "AGENTS.md"
            original = agents_path.read_text(encoding="utf-8")
            agents_path.write_text("Project-specific operator notes.\n\n" + original, encoding="utf-8")

            output = io.StringIO()
            with redirect_stdout(output):
                status = run_update(
                    target=target,
                    dry_run=False,
                    assume_yes=True,
                    selected_tools=None,
                )

            self.assertEqual(status, 1)
            self.assertEqual(agents_path.read_text(encoding="utf-8"), "Project-specific operator notes.\n\n" + original)
            self.assertIn("manual review required", output.getvalue())

    def test_installed_context_templates_include_hardened_update_and_verify_instructions(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Service Repo\n\nTemplate content checks.\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                status = run_init(
                    target=target,
                    profile="service",
                    selected_tools=("codex", "claude"),
                    dry_run=False,
                    assume_yes=True,
                )

            self.assertEqual(status, 0)
            update_skill = (target / ".forge/skills/forge-update-context/SKILL.md").read_text(encoding="utf-8")
            update_mode = (target / ".forge/runtime/modes/update-context.md").read_text(encoding="utf-8")
            verify_skill = (target / ".forge/skills/forge-verify-context/SKILL.md").read_text(encoding="utf-8")
            verify_mode = (target / ".forge/runtime/modes/verify-context.md").read_text(encoding="utf-8")
            command = (target / ".claude/commands/forge-update-context.md").read_text(encoding="utf-8")

            _assert_contains_all(
                self,
                update_skill,
                (
                    "Cross-file updates are allowed",
                    "Do not modify application code.",
                    "`.forge/runtime/`",
                    "`.forge/generated/`",
                    "`.forge/context-archive/`",
                    "`.forge/context-patches/`",
                    "not active source of truth by default",
                    "This workflow is not v2-only.",
                ),
            )
            _assert_contains_all(
                self,
                update_mode,
                (
                    "`.forge/context/*.md` only.",
                    "Cross-file updates are allowed when required to keep active context consistent.",
                    "This is not scope creep. It is active context consistency.",
                    "Do not read `.forge/generated/` by default or treat it as active evidence by default.",
                    "Do not promote archive facts as confirmed",
                    "For workspace layout",
                ),
            )
            _assert_contains_all(
                self,
                verify_skill,
                (
                    "read-only",
                    "must not modify files",
                    "Do not modify `.forge/context`.",
                    "recommend `forge-update-context` when safe updates are needed",
                ),
            )
            _assert_contains_all(
                self,
                verify_mode,
                (
                    "This workflow is read-only.",
                    "Must not modify files.",
                    "Do not modify `.forge/context`.",
                    "Do not treat `.forge/generated/` or `.forge/context-archive/` as active source of truth.",
                    "Recommend running `forge-update-context` when safe active-context updates are needed.",
                    "This workflow is not v2-only.",
                    "Active profile context files under `.forge/context/`",
                    "For workspace layout",
                ),
            )
            self.assertNotIn("00-meta/context-manifest.md", verify_mode)
            self.assertNotIn("knowledge/decisions/", verify_mode)
            self.assertNotIn("source_commit", verify_mode)
            self.assertNotIn("last_verified", verify_mode)
            _assert_contains_all(
                self,
                command,
                (
                    "Update active context only under `.forge/context/`.",
                    "Do not modify application code",
                    "`.forge/runtime/`",
                    "`.forge/generated/`",
                    "Report changed context files",
                ),
            )

    def test_runtime_config_still_uses_generated_output_and_context_patch_dirs(self) -> None:
        files = _build_init_files(
            target_root=Path("/tmp/example"),
            profile="service",
            selected_tools=("codex",),
            ui_language="en",
        )
        config = files[".forge/forge.config.yaml"]
        self.assertIn("output_dir: .forge/generated", config)
        self.assertIn("patch_dir: .forge/context-patches", config)

    def test_update_preserves_source_when_deprecated_runtime_archive_target_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Service Repo\n\nDeprecated runtime archive conflict.\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                run_init(
                    target=target,
                    profile="service",
                    selected_tools=("codex",),
                    dry_run=False,
                    assume_yes=True,
                )

            _seed_deprecated_runtime_paths(target)
            edited = target / ".forge/context/modes/ask.md"
            edited.write_text(edited.read_text(encoding="utf-8") + "\nuser edit\n", encoding="utf-8")
            archive_target = target / DEPRECATED_RUNTIME_ARCHIVE_ROOT / "modes"
            archive_target.mkdir(parents=True, exist_ok=True)
            (archive_target / "ask.md").write_text("existing archive\n", encoding="utf-8")

            output = io.StringIO()
            with redirect_stdout(output):
                status = run_update(
                    target=target,
                    dry_run=False,
                    assume_yes=True,
                    selected_tools=None,
                )

            self.assertEqual(status, 1)
            self.assertTrue((target / ".forge/context/modes").exists())
            self.assertEqual((archive_target / "ask.md").read_text(encoding="utf-8"), "existing archive\n")
            rendered = output.getvalue()
            self.assertIn("deprecated runtime archive target already exists", rendered)
            self.assertIn(f"{DEPRECATED_RUNTIME_ARCHIVE_ROOT}/modes", rendered)
            self.assertIn("Update stopped with conflicts", rendered)

    def test_fresh_init_never_creates_deprecated_runtime_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Service Repo\n\nFresh init runtime paths.\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                status = run_init(
                    target=target,
                    profile="service",
                    selected_tools=("codex",),
                    dry_run=False,
                    assume_yes=True,
                )

            self.assertEqual(status, 0)
            self.assertFalse((target / ".forge/context/00-meta").exists())
            self.assertFalse((target / ".forge/context/modes").exists())
            self.assertTrue((target / ".forge/runtime/meta").exists())
            self.assertTrue((target / ".forge/runtime/modes").exists())

    def test_migrate_context_on_v2_is_no_op(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Service Repo\n\nAlready v2.\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                run_init(
                    target=target,
                    profile="service",
                    selected_tools=("codex",),
                    dry_run=False,
                    assume_yes=True,
                )

            output = io.StringIO()
            with redirect_stdout(output):
                status = run_migrate_context(target=target, dry_run=False)

            self.assertEqual(status, 0)
            self.assertFalse((target / LEGACY_CONTEXT_ARCHIVE_ROOT).exists())
            self.assertIn("already uses numbered v2 context files", output.getvalue())
            self.assertIn("Files changed: none", output.getvalue())

    def test_migrate_context_on_mixed_does_not_clean_up_or_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Mixed Repo\n\nMigration mixed layout.\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                run_init(
                    target=target,
                    profile="service",
                    selected_tools=("codex",),
                    dry_run=False,
                    assume_yes=True,
                )

            overview = target / ".forge/context/01-service-overview.md"
            overview_before = overview.read_text(encoding="utf-8")
            legacy_product = target / ".forge/context/01-core/product.md"
            legacy_product.parent.mkdir(parents=True, exist_ok=True)
            legacy_product.write_text("legacy product\n", encoding="utf-8")

            output = io.StringIO()
            with redirect_stdout(output):
                status = run_migrate_context(target=target, dry_run=False)

            self.assertEqual(status, 0)
            self.assertTrue(legacy_product.exists())
            self.assertEqual(overview.read_text(encoding="utf-8"), overview_before)
            self.assertFalse((target / LEGACY_CONTEXT_ARCHIVE_ROOT).exists())
            self.assertIn("mixed layout detected", output.getvalue().lower())

    def test_migrate_context_on_empty_or_unknown_writes_no_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / ".forge/context").mkdir(parents=True)
            (target / ".forge/runtime/modes").mkdir(parents=True)
            (target / ".forge/runtime/modes/ask.md").write_text("# ask\n", encoding="utf-8")
            (target / ".forge/adapter.md").write_text("adapter\n", encoding="utf-8")
            (target / ".forge/forge.config.yaml").write_text("forge:\n  version: \"1\"\n", encoding="utf-8")

            output = io.StringIO()
            with redirect_stdout(output):
                status = run_migrate_context(target=target, dry_run=False)

            self.assertEqual(status, 0)
            self.assertFalse((target / LEGACY_CONTEXT_ARCHIVE_ROOT).exists())
            rendered = output.getvalue().lower()
            self.assertIn("migration cannot be safely performed", rendered)
            self.assertIn("review `.forge/context` manually", rendered)
            self.assertIn("forge update --dry-run", rendered)
            self.assertIn("files changed: none", rendered)

    def test_migrate_context_conflict_stops_before_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Legacy Repo\n\nConflict behavior.\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                run_init(
                    target=target,
                    profile="service",
                    selected_tools=("codex",),
                    dry_run=False,
                    assume_yes=True,
                )

            _convert_repo_to_legacy_layout(target, profile="service")
            conflict_path = target / LEGACY_CONTEXT_ARCHIVE_ROOT / "01-core"
            conflict_path.parent.mkdir(parents=True, exist_ok=True)
            conflict_path.write_text("different\n", encoding="utf-8")

            before_context = _snapshot_tree(target / ".forge/context")
            before_manifest = (target / ".forge/forge-install.yaml").read_text(encoding="utf-8")

            output = io.StringIO()
            with redirect_stdout(output):
                status = run_migrate_context(target=target, dry_run=False)

            self.assertEqual(status, 1)
            self.assertEqual(conflict_path.read_text(encoding="utf-8"), "different\n")
            self.assertEqual(before_context, _snapshot_tree(target / ".forge/context"))
            self.assertEqual((target / ".forge/forge-install.yaml").read_text(encoding="utf-8"), before_manifest)
            rendered = output.getvalue()
            self.assertIn("Migration mode: apply", rendered)
            self.assertIn("Migration: not run", rendered)
            self.assertIn("Files changed: none", rendered)
            self.assertNotIn("Migration: completed", rendered)
            self.assertNotIn("rerunning `forge init`", rendered)
            self.assertIn("before rerunning `forge migrate-context`", rendered)

    def test_migrate_context_writes_expected_service_v2_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Legacy Service\n\nService migration files.\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                run_init(
                    target=target,
                    profile="service",
                    selected_tools=("codex",),
                    dry_run=False,
                    assume_yes=True,
                )

            _convert_repo_to_legacy_layout(target, profile="service")

            with redirect_stdout(io.StringIO()):
                run_migrate_context(target=target, dry_run=False)

            for rel_path in SERVICE_V2_CONTEXT_FILES:
                self.assertTrue((target / rel_path).exists(), rel_path)

    def test_migrate_context_writes_expected_workspace_v2_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Legacy Workspace\n\nWorkspace migration files.\n", encoding="utf-8")
            (target / "services" / "payments").mkdir(parents=True)
            (target / "services" / "payments" / "README.md").write_text("payments\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                run_init(
                    target=target,
                    profile="workspace",
                    selected_tools=("codex",),
                    dry_run=False,
                    assume_yes=True,
                )

            _convert_repo_to_legacy_layout(target, profile="workspace")

            with redirect_stdout(io.StringIO()):
                run_migrate_context(target=target, dry_run=False)

            for rel_path in WORKSPACE_V2_CONTEXT_FILES:
                self.assertTrue((target / rel_path).exists(), rel_path)

    def test_manifestless_adoption_empty_or_unknown_reports_legacy_v1_consistently(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / ".forge/context").mkdir(parents=True)
            (target / ".forge/runtime/modes").mkdir(parents=True)
            (target / ".forge/runtime/modes/ask.md").write_text("# ask\n", encoding="utf-8")
            (target / ".forge/adapter.md").write_text("adapter\n", encoding="utf-8")
            (target / ".forge/forge.config.yaml").write_text("forge:\n  version: \"1\"\n", encoding="utf-8")

            output = io.StringIO()
            with redirect_stdout(output):
                status = run_update(
                    target=target,
                    dry_run=True,
                    assume_yes=True,
                    selected_tools=None,
                )

            self.assertEqual(status, 0)
            self.assertFalse((target / ".forge/forge-install.yaml").exists())
            self.assertEqual(_detect_context_layout(target, "service"), CONTEXT_LAYOUT_EMPTY_OR_UNKNOWN)

            rendered = output.getvalue()
            self.assertIn("Detected Forge profile: service", rendered)
            self.assertIn("Detected context profile version: legacy-v1", rendered)
            self.assertIn("Detected context layout: empty-or-unknown", rendered)
            self.assertIn("Migration: not applied automatically", rendered)
            self.assertIn("User-owned context: preserved", rendered)
            self.assertFalse((target / ".forge/context/00-index.md").exists())


    def test_update_preserves_legacy_context_and_manifest_stays_legacy(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Legacy Repo\n\nLegacy context preservation test.\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                status = run_init(
                    target=target,
                    profile="service",
                    selected_tools=("codex",),
                    dry_run=False,
                    assume_yes=True,
                )
            self.assertEqual(status, 0)

            manifest_path = target / ".forge/forge-install.yaml"
            legacy_manifest = manifest_path.read_text(encoding="utf-8").replace(
                'context_profile_version: "2"\n',
                "",
            )
            manifest_path.write_text(legacy_manifest, encoding="utf-8")

            for rel_path in (
                ".forge/context/00-index.md",
                ".forge/context/01-service-overview.md",
                ".forge/context/99-open-questions.md",
            ):
                path = target / rel_path
                if path.exists():
                    path.unlink()

            legacy_product = target / ".forge/context/01-core/product.md"
            legacy_unknowns = target / ".forge/context/knowledge/unknowns.md"
            legacy_product.parent.mkdir(parents=True, exist_ok=True)
            legacy_unknowns.parent.mkdir(parents=True, exist_ok=True)
            legacy_product.write_text("legacy product\n", encoding="utf-8")
            legacy_unknowns.write_text("legacy unknowns\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                update_status = run_update(
                    target=target,
                    dry_run=False,
                    assume_yes=True,
                    selected_tools=None,
                )

            self.assertEqual(update_status, 0)
            self.assertTrue(legacy_product.exists())
            self.assertTrue(legacy_unknowns.exists())
            self.assertFalse((target / ".forge/context/00-index.md").exists())

            manifest = load_manifest(manifest_path)
            self.assertEqual(manifest.context_profile_version, CONTEXT_PROFILE_VERSION_LEGACY)

    def test_update_preserves_mixed_layout_without_cleanup(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Mixed Repo\n\nMixed preservation.\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                run_init(
                    target=target,
                    profile="service",
                    selected_tools=("codex",),
                    dry_run=False,
                    assume_yes=True,
                )

            legacy_product = target / ".forge/context/01-core/product.md"
            legacy_product.parent.mkdir(parents=True, exist_ok=True)
            legacy_product.write_text("legacy product\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                status = run_update(
                    target=target,
                    dry_run=False,
                    assume_yes=True,
                    selected_tools=None,
                )

            self.assertEqual(status, 0)
            self.assertTrue(legacy_product.exists())
            self.assertTrue((target / ".forge/context/00-index.md").exists())

    def test_update_reports_mixed_layout_without_cleanup(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Mixed Repo\n\nMixed reporting.\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                run_init(
                    target=target,
                    profile="service",
                    selected_tools=("codex",),
                    dry_run=False,
                    assume_yes=True,
                )

            (target / ".forge/context/01-core").mkdir(parents=True, exist_ok=True)

            output = io.StringIO()
            with redirect_stdout(output):
                status = run_update(
                    target=target,
                    dry_run=False,
                    assume_yes=True,
                    selected_tools=None,
                )

            self.assertEqual(status, 0)
            rendered = output.getvalue()
            self.assertIn("Detected context layout: mixed", rendered)
            self.assertIn("no cleanup performed for mixed layouts", rendered)

    def test_manifestless_damaged_workspace_layout_stays_unclassified(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Workspace Repo\n\nDamaged workspace install.\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                run_init(
                    target=target,
                    profile="workspace",
                    selected_tools=("codex",),
                    dry_run=False,
                    assume_yes=True,
                )

            (target / ".forge/forge-install.yaml").unlink()
            (target / ".forge/workspace.yaml").unlink()

            output = io.StringIO()
            with redirect_stdout(output):
                status = run_update(
                    target=target,
                    dry_run=True,
                    assume_yes=True,
                    selected_tools=None,
                )

            self.assertEqual(status, 0)
            rendered = output.getvalue()
            self.assertIn("Detected context layout: empty-or-unknown", rendered)
            self.assertIn("context layout could not be safely classified", rendered)
            self.assertFalse((target / ".forge/forge-install.yaml").exists())
            for rel_path in WORKSPACE_V2_CONTEXT_FILES:
                self.assertTrue((target / rel_path).exists(), rel_path)

    def test_missing_evidence_routes_to_open_questions_without_fake_api_or_db_claims(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Sparse Repo\n\nMinimal repo for evidence checks.\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                status = run_init(
                    target=target,
                    profile="service",
                    selected_tools=("codex",),
                    dry_run=False,
                    assume_yes=True,
                )
            self.assertEqual(status, 0)

            api_contracts = (target / ".forge/context/04-interfaces-and-contracts.md").read_text(encoding="utf-8")
            data_model = (target / ".forge/context/05-data-and-persistence.md").read_text(encoding="utf-8")
            integrations = (target / ".forge/context/07-integrations-and-dependencies.md").read_text(encoding="utf-8")
            open_questions = (target / ".forge/context/99-open-questions.md").read_text(encoding="utf-8")

            self.assertIn("No direct evidence found in bounded init scan.", api_contracts)
            self.assertIn("No direct evidence found in bounded init scan.", data_model)
            self.assertIn("No direct evidence found in bounded init scan.", integrations)
            self.assertIn("Service API contracts were not directly evidenced", open_questions)
            self.assertIn("Data model and database details were not directly evidenced", open_questions)
            self.assertIn("Integration dependencies were not directly evidenced", open_questions)
            self.assertNotIn("openapi", api_contracts.lower())
            self.assertNotIn("schema.prisma", data_model.lower())

    def test_legacy_manifest_without_context_profile_version_loads_safely(self) -> None:
        manifest = load_manifest_text(
            "\n".join(
                [
                    'manifest_version: "1"',
                    'forge_version: "1.1.0rc1"',
                    'profile: "service"',
                    "selected_tools:",
                    "  - codex",
                    'installed_from: "git+https://example.com/forge.git"',
                    'installed_at: "2026-01-01T00:00:00Z"',
                    'template_revision: "1.1.0rc1"',
                    'source_revision: "1.1.0rc1"',
                    "managed_paths:",
                    "  - .forge/adapter.md",
                    "user_owned_paths:",
                    "  - .forge/context/01-core/",
                    "local_only_paths:",
                    "  - .forge/temp/",
                    "managed_file_hashes:",
                    "  .forge/adapter.md: abc123",
                ]
            )
            + "\n"
        )

        self.assertEqual(manifest.context_profile_version, CONTEXT_PROFILE_VERSION_LEGACY)
        self.assertEqual(manifest.profile, "service")

    def test_repo_contains_no_wrong_runtime_ops_path_typo(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        wrong_path = "/".join(("src", "forge_context-engine", "runtime_ops.py"))
        for path in repo_root.rglob("*"):
            if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts or path == Path(__file__):
                continue
            try:
                content = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            self.assertNotIn(wrong_path, content, f"found wrong path reference in {path}")

    def test_docs_do_not_present_legacy_layout_as_fresh_default(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        doc_paths = [
            repo_root / "README.md",
            repo_root / "docs/getting-started.md",
            repo_root / "docs/workflow.md",
            repo_root / "specs/runtime-install-update.md",
            repo_root / "specs/context-initialization.md",
            repo_root / "specs/context-validation.md",
            repo_root / "specs/platform-context.md",
        ]
        forbidden = re.compile(r"fresh[^\n]{0,40}default[^\n]{0,30}layout[^\n]{0,80}01-core/", re.IGNORECASE)
        for path in doc_paths:
            content = path.read_text(encoding="utf-8")
            self.assertFalse(forbidden.search(content), f"legacy fresh-default wording found in {path}")

        self.assertIn("v2 service profile with numbered files", (repo_root / "README.md").read_text(encoding="utf-8"))
        self.assertIn("v2 numbered service context files", (repo_root / "docs/getting-started.md").read_text(encoding="utf-8"))

    def test_active_runtime_assets_do_not_reference_old_runtime_paths(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        roots = [
            repo_root / "runtime",
            repo_root / "src/forge_context_engine/runtime_templates/base",
        ]
        forbidden = (".forge/context/00-meta", ".forge/context/modes")
        for root in roots:
            for path in root.rglob("*"):
                if not path.is_file():
                    continue
                content = path.read_text(encoding="utf-8")
                for token in forbidden:
                    self.assertNotIn(token, content, f"stale runtime path {token} found in {path}")

    def test_active_runtime_assets_do_not_reference_legacy_generated_context_path(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        roots = [
            repo_root / "src/forge_context_engine/runtime_templates/base/skills",
            repo_root / "src/forge_context_engine/runtime_templates/base/.forge/runtime",
            repo_root / "src/forge_context_engine/runtime_templates/base/.claude/commands",
        ]
        for root in roots:
            for path in root.rglob("*"):
                if not path.is_file():
                    continue
                content = path.read_text(encoding="utf-8")
                self.assertNotIn(".forge/context/generated", content, f"legacy generated path found in {path}")

    def test_active_runtime_assets_do_not_reference_forbidden_legacy_wrapper_markers(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        roots = [
            repo_root / "src/forge_context_engine/runtime_templates/base/skills",
            repo_root / "src/forge_context_engine/runtime_templates/base/.forge/runtime",
            repo_root / "src/forge_context_engine/runtime_templates/base/.claude/commands",
            repo_root / "src/forge_context_engine/runtime_templates/base/AGENTS.md",
            repo_root / "src/forge_context_engine/runtime_templates/base/CLAUDE.md",
            repo_root / "src/forge_context_engine/runtime_templates/base/.github/copilot-instructions.md",
        ]
        forbidden = (
            ".forge/context/00-meta",
            ".forge/context/modes",
            "01-core/",
            "knowledge/inferred.md",
            "knowledge/confirmations.md",
            "source_commit",
            "last_verified",
            ".forge/context/generated",
        )
        for root in roots:
            paths = [root] if root.is_file() else list(root.rglob("*"))
            for path in paths:
                if not path.is_file():
                    continue
                content = path.read_text(encoding="utf-8")
                for token in forbidden:
                    self.assertNotIn(token, content, f"legacy marker {token} found in {path}")

    def test_active_specs_do_not_present_legacy_per_card_freshness_fields(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        specs = [
            repo_root / "specs/context-initialization.md",
            repo_root / "specs/context-validation.md",
        ]
        forbidden = ("source_commit", "last_verified")
        for path in specs:
            content = path.read_text(encoding="utf-8")
            for token in forbidden:
                self.assertNotIn(token, content, f"legacy per-card freshness field {token} found in active spec {path}")


if __name__ == "__main__":
    unittest.main()
