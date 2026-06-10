from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from forge_context_engine.install_manifest import build_managed_paths, load_manifest, parse_tools_args
from forge_context_engine.runtime_ops import (
    _build_init_files,
    _is_managed_file,
    _preserve_non_selected_entrypoints,
    OperationReport,
    run_init,
    run_update,
)


class ToolSelectionTests(unittest.TestCase):
    def test_parse_tools_args_accepts_opencode(self) -> None:
        self.assertEqual(parse_tools_args("opencode"), ("opencode",))

    def test_parse_tools_args_preserves_canonical_order(self) -> None:
        self.assertEqual(parse_tools_args("opencode,codex"), ("codex", "opencode"))

    def test_parse_tools_args_all_includes_opencode(self) -> None:
        self.assertEqual(
            parse_tools_args("all"),
            ("codex", "claude", "copilot", "opencode"),
        )

    def test_build_managed_paths_adds_agents_once_for_opencode(self) -> None:
        managed_paths = build_managed_paths("service", ("opencode",))
        self.assertEqual(managed_paths.count("AGENTS.md"), 1)

    def test_build_managed_paths_shares_agents_for_codex_and_opencode(self) -> None:
        managed_paths = build_managed_paths("service", ("codex", "opencode"))
        self.assertEqual(managed_paths.count("AGENTS.md"), 1)

    def test_agents_is_managed_for_opencode(self) -> None:
        self.assertTrue(_is_managed_file("AGENTS.md", "service", ("opencode",)))

    def test_agents_is_managed_for_codex_and_opencode(self) -> None:
        self.assertTrue(_is_managed_file("AGENTS.md", "service", ("codex", "opencode")))

    def test_agents_is_not_managed_without_agents_compatible_tool(self) -> None:
        self.assertFalse(_is_managed_file("AGENTS.md", "service", ("claude", "copilot")))

    def test_build_managed_paths_includes_canonical_forge_skills(self) -> None:
        managed_paths = build_managed_paths("service", ("opencode",))
        self.assertIn(".forge/skills/", managed_paths)

    def test_build_managed_paths_no_longer_includes_opencode_skills_dir(self) -> None:
        managed_paths = build_managed_paths("service", ("opencode",))
        self.assertIn(".opencode/skills/", managed_paths)

    def test_canonical_forge_skill_is_managed(self) -> None:
        self.assertTrue(_is_managed_file(".forge/skills/forge-plan/SKILL.md", "service", ("opencode",)))

    def test_build_init_files_places_skills_under_forge(self) -> None:
        files = _build_init_files(
            target_root=Path("/tmp/example"),
            profile="service",
            selected_tools=("opencode",),
            ui_language="en",
        )
        self.assertIn(".forge/skills/forge-plan/SKILL.md", files)
        self.assertIn(".opencode/skills/forge-plan/SKILL.md", files)

    def test_opencode_config_points_to_forge_skills(self) -> None:
        files = _build_init_files(
            target_root=Path("/tmp/example"),
            profile="service",
            selected_tools=("opencode",),
            ui_language="en",
        )
        self.assertIn('"paths": ["./.opencode/skills"]', files[".opencode/opencode.json"])

    def test_opencode_wrappers_include_frontmatter(self) -> None:
        files = _build_init_files(
            target_root=Path("/tmp/example"),
            profile="service",
            selected_tools=("opencode",),
            ui_language="en",
        )
        skill = files[".opencode/skills/forge-plan/SKILL.md"]
        self.assertTrue(skill.startswith("---\n"))
        self.assertIn("name: forge-plan", skill)
        self.assertIn("compatibility: opencode", skill)

    def test_generated_output_contains_no_runtime_skills_reference(self) -> None:
        files = _build_init_files(
            target_root=Path("/tmp/example"),
            profile="service",
            selected_tools=("opencode", "claude", "copilot"),
            ui_language="en",
        )
        for rel_path, content in files.items():
            self.assertNotIn(
                "runtime/skills/",
                content,
                msg=f"unexpected legacy runtime skill reference in {rel_path}",
            )

    def test_shared_agents_entrypoint_not_preserved_when_opencode_selected(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "AGENTS.md").write_text("stub\n", encoding="utf-8")
            report = OperationReport(dry_run=True)
            _preserve_non_selected_entrypoints(
                target_root=target,
                selected_tools=("opencode",),
                report=report,
            )
            self.assertFalse(any(op.path == "AGENTS.md" for op in report.operations))

    def test_update_migrates_legacy_opencode_layout_to_canonical_forge_skills(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            with redirect_stdout(io.StringIO()):
                init_status = run_init(
                    target=target,
                    profile="service",
                    selected_tools=("opencode",),
                    dry_run=False,
                    assume_yes=True,
                )
            self.assertEqual(init_status, 0)

            manifest_path = target / ".forge" / "forge-install.yaml"
            legacy_manifest = manifest_path.read_text(encoding="utf-8").replace(
                "  - .forge/skills/\n  - .opencode/skills/\n",
                "  - skills/\n  - .opencode/skills/\n",
            )
            manifest_path.write_text(legacy_manifest, encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                update_status = run_update(
                    target=target,
                    dry_run=False,
                    assume_yes=True,
                    selected_tools=None,
                )
            self.assertEqual(update_status, 0)

            self.assertTrue((target / ".forge" / "skills" / "forge-plan" / "SKILL.md").exists())
            self.assertIn(
                '"paths": ["./.opencode/skills"]',
                (target / ".opencode" / "opencode.json").read_text(encoding="utf-8"),
            )
            self.assertTrue((target / ".opencode" / "skills" / "forge-plan" / "SKILL.md").exists())

            manifest = load_manifest(target / ".forge" / "forge-install.yaml")
            self.assertIn(".forge/skills/", manifest.managed_paths)
            self.assertIn(".opencode/skills/", manifest.managed_paths)


if __name__ == "__main__":
    unittest.main()
