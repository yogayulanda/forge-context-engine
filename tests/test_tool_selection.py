from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from forge_context_engine.install_manifest import build_managed_paths, load_manifest, parse_tools_args
from forge_context_engine.runtime_ops import (
    _build_init_files,
    _detect_tools,
    _is_managed_file,
    _preserve_non_selected_entrypoints,
    OperationReport,
    run_init,
    run_update,
)
from forge_context_engine.runtime_templates import iter_template_files


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

    def test_build_init_files_includes_update_context_skill_and_claude_wrapper(self) -> None:
        files = _build_init_files(
            target_root=Path("/tmp/example"),
            profile="service",
            selected_tools=("codex", "claude"),
            ui_language="en",
        )
        self.assertIn(".forge/skills/forge-update-context/SKILL.md", files)
        self.assertIn(".forge/runtime/modes/update-context.md", files)
        self.assertIn(".claude/commands/forge-update-context.md", files)

    def test_update_context_uses_canonical_base_template_locations_only(self) -> None:
        files = iter_template_files("base")
        self.assertIn("skills/forge-update-context/SKILL.md", files)
        self.assertIn(".forge/runtime/modes/update-context.md", files)
        self.assertIn(".claude/commands/forge-update-context.md", files)
        self.assertNotIn(".forge/skills/forge-update-context/SKILL.md", files)

    def test_build_init_files_includes_generated_readme_and_no_legacy_generated_dir(self) -> None:
        files = _build_init_files(
            target_root=Path("/tmp/example"),
            profile="service",
            selected_tools=("codex",),
            ui_language="en",
        )
        self.assertIn(".forge/generated/README.md", files)
        self.assertNotIn(".forge/context/generated/README.md", files)
        for rel_path, content in files.items():
            self.assertNotIn(".forge/context/generated/", content, msg=f"unexpected legacy generated path in {rel_path}")

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

    def test_update_context_skill_preserves_write_boundaries(self) -> None:
        files = _build_init_files(
            target_root=Path("/tmp/example"),
            profile="service",
            selected_tools=("codex", "claude"),
            ui_language="en",
        )
        skill = files[".forge/skills/forge-update-context/SKILL.md"]
        mode = files[".forge/runtime/modes/update-context.md"]
        self.assertIn("Do not modify application code.", skill)
        self.assertIn("`.forge/generated/`", skill)
        self.assertIn("## forbidden writes", mode)
        self.assertIn("Application code.", mode)
        self.assertIn("`.forge/context-patches/`", mode)

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


    def test_detect_tools_recognizes_opencode_config_or_skills_signals(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / ".opencode").mkdir(parents=True)
            (target / ".opencode" / "opencode.json").write_text("{}", encoding="utf-8")
            self.assertEqual(_detect_tools(target), ("opencode",))

        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / ".opencode" / "skills").mkdir(parents=True)
            self.assertEqual(_detect_tools(target), ("opencode",))

    def test_manifestless_adoption_detects_opencode_from_skills_signal_and_records_managed_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# OpenCode Repo\n", encoding="utf-8")
            (target / ".forge" / "context" / "modes").mkdir(parents=True)
            (target / ".forge" / "context" / "modes" / "ask.md").write_text("# ask\n", encoding="utf-8")
            (target / ".forge" / "adapter.md").write_text("adapter\n", encoding="utf-8")
            (target / ".forge" / "forge.config.yaml").write_text("forge:\n  version: \"1\"\n", encoding="utf-8")
            (target / ".opencode" / "skills" / "legacy-skill").mkdir(parents=True)
            (target / ".opencode" / "skills" / "legacy-skill" / "SKILL.md").write_text(
                "legacy\n",
                encoding="utf-8",
            )

            with redirect_stdout(io.StringIO()):
                status = run_update(
                    target=target,
                    dry_run=False,
                    assume_yes=True,
                    selected_tools=None,
                )

            self.assertEqual(status, 0)
            manifest = load_manifest(target / ".forge" / "forge-install.yaml")
            self.assertEqual(manifest.selected_tools, ("opencode",))
            self.assertIn(".opencode/skills/", manifest.managed_paths)
            self.assertIn(".opencode/opencode.json", manifest.managed_paths)
            self.assertTrue((target / ".opencode" / "opencode.json").exists())
            self.assertTrue((target / ".opencode" / "skills" / "forge-plan" / "SKILL.md").exists())


if __name__ == "__main__":
    unittest.main()
