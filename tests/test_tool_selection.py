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


def _assert_contains_all(testcase: unittest.TestCase, text: str, phrases: tuple[str, ...]) -> None:
    for phrase in phrases:
        testcase.assertIn(phrase, text)


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

    def test_build_managed_paths_includes_copilot_skills_dir(self) -> None:
        managed_paths = build_managed_paths("service", ("codex", "copilot"))
        self.assertIn(".github/skills/", managed_paths)
        self.assertNotIn(".github/prompts/", managed_paths)

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

    def test_build_init_files_exports_copilot_skills_from_canonical_templates(self) -> None:
        files = _build_init_files(
            target_root=Path("/tmp/example"),
            profile="service",
            selected_tools=("codex", "copilot"),
            ui_language="en",
        )
        self.assertIn(".github/copilot-instructions.md", files)
        self.assertIn(".github/skills/forge-update-context/SKILL.md", files)
        self.assertIn(".github/skills/forge-verify-context/SKILL.md", files)
        self.assertEqual(
            files[".github/skills/forge-update-context/SKILL.md"],
            files[".forge/skills/forge-update-context/SKILL.md"],
        )
        self.assertNotIn(".github/prompts/forge-update-context.prompt.md", files)

    def test_base_templates_do_not_include_legacy_copilot_prompt_wrappers(self) -> None:
        files = iter_template_files("base")
        self.assertFalse(any(rel_path.startswith(".github/prompts/") for rel_path in files), files.keys())

    def test_build_init_files_includes_update_context_skill_and_claude_wrapper(self) -> None:
        files = _build_init_files(
            target_root=Path("/tmp/example"),
            profile="service",
            selected_tools=("codex", "claude"),
            ui_language="en",
        )
        self.assertIn(".forge/skills/forge-update-context/SKILL.md", files)
        self.assertIn(".forge/runtime/modes/update-context.md", files)
        self.assertIn(".claude/.gitignore", files)
        self.assertIn(".claude/commands/forge-update-context.md", files)
        _assert_contains_all(
            self,
            files[".claude/.gitignore"],
            (
                "settings.local.json",
                "*.local.json",
                "tmp/",
                "cache/",
                "logs/",
                "sessions/",
                "!commands/",
                "!commands/**",
            ),
        )

    def test_update_context_uses_canonical_base_template_locations_only(self) -> None:
        files = iter_template_files("base")
        self.assertIn("skills/forge-update-context/SKILL.md", files)
        self.assertIn(".forge/runtime/modes/update-context.md", files)
        self.assertIn(".claude/commands/forge-update-context.md", files)
        self.assertNotIn(".forge/skills/forge-update-context/SKILL.md", files)

    def test_update_context_canonical_templates_include_hardening_semantics(self) -> None:
        files = iter_template_files("base")
        skill = files["skills/forge-update-context/SKILL.md"]
        mode = files[".forge/runtime/modes/update-context.md"]
        command = files[".claude/commands/forge-update-context.md"]

        _assert_contains_all(
            self,
            skill,
            (
                "Cross-file updates are allowed",
                "minimal, directly related",
                "`.forge/context/`",
                "Do not modify application code.",
                "`.forge/runtime/`",
                "`.forge/generated/`",
                "`.forge/context-archive/`",
                "`.forge/context-patches/`",
                "not active source of truth by default",
                "legacy-derived or needing confirmation",
                "This workflow is not v2-only.",
                "manifest and index routing",
                "No target file list",
            ),
        )
        _assert_contains_all(
            self,
            mode,
            (
                "## allowed writes",
                "`.forge/context/*.md` only.",
                "## forbidden writes",
                "Application code.",
                "`.forge/runtime/`",
                "`.forge/generated/`",
                "`.forge/context-archive/`",
                "`.forge/context-patches/`",
                "Cross-file updates are allowed when required to keep active context consistent.",
                "This is not scope creep. It is active context consistency.",
                "Do not read `.forge/generated/` by default or treat it as active evidence by default.",
                "Do not promote archive facts as confirmed",
                "This workflow is not v2-only.",
                "For v2 service layout",
                "For workspace layout",
                "For future layouts",
            ),
        )
        _assert_contains_all(
            self,
            command,
            (
                "Use shared skill `.forge/skills/forge-update-context/SKILL.md`",
                "Update active context only under `.forge/context/`.",
                "Do not modify application code",
                "`.forge/runtime/`",
                "`.forge/generated/`",
                "`.forge/context-archive/`",
                "Report changed context files",
            ),
        )

    def test_build_init_files_includes_generated_readme_and_no_legacy_generated_dir(self) -> None:
        files = _build_init_files(
            target_root=Path("/tmp/example"),
            profile="service",
            selected_tools=("codex",),
            ui_language="en",
        )
        self.assertIn(".forge/generated/README.md", files)
        self.assertIn(".forge/context-patches/README.md", files)
        self.assertIn(".forge/context-archive/README.md", files)
        self.assertNotIn(".forge/context/generated/README.md", files)
        for rel_path, content in files.items():
            self.assertNotIn(".forge/context/generated/", content, msg=f"unexpected legacy generated path in {rel_path}")

    def test_forge_gitignore_uses_local_hygiene_policy(self) -> None:
        files = _build_init_files(
            target_root=Path("/tmp/example"),
            profile="service",
            selected_tools=("codex",),
            ui_language="en",
        )
        gitignore = files[".forge/.gitignore"]
        _assert_contains_all(
            self,
            gitignore,
            (
                "/cache/",
                "/temp/",
                "/generated/**",
                "!/generated/README.md",
                "/context-patches/**",
                "!/context-patches/README.md",
                "/context-archive/**",
                "!/context-archive/README.md",
                "/forge.local.yaml",
            ),
        )
        self.assertNotIn(".github/skills", gitignore)

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
            self.assertNotIn(".forge/context/generated", content, msg=f"unexpected legacy generated path in {rel_path}")

    def test_update_context_skill_preserves_write_boundaries(self) -> None:
        files = _build_init_files(
            target_root=Path("/tmp/example"),
            profile="service",
            selected_tools=("codex", "claude"),
            ui_language="en",
        )
        skill = files[".forge/skills/forge-update-context/SKILL.md"]
        mode = files[".forge/runtime/modes/update-context.md"]
        _assert_contains_all(
            self,
            skill,
            (
                "Do not modify application code.",
                "`.forge/runtime/`",
                "`.forge/generated/`",
                "`.forge/context-archive/`",
                "`.forge/context-patches/`",
                "Cross-file updates are allowed",
                "not active source of truth by default",
                "This workflow is not v2-only.",
            ),
        )
        _assert_contains_all(
            self,
            mode,
            (
                "## forbidden writes",
                "Application code.",
                "`.forge/runtime/`",
                "`.forge/generated/`",
                "`.forge/context-archive/`",
                "`.forge/context-patches/`",
                "Cross-file updates are allowed when required to keep active context consistent.",
            ),
        )

    def test_verify_context_templates_remain_read_only_and_recommend_update_context(self) -> None:
        files = _build_init_files(
            target_root=Path("/tmp/example"),
            profile="service",
            selected_tools=("codex",),
            ui_language="en",
        )
        skill = files[".forge/skills/forge-verify-context/SKILL.md"]
        mode = files[".forge/runtime/modes/verify-context.md"]
        _assert_contains_all(
            self,
            skill,
            (
                "read-only",
                "must not modify files",
                "Do not modify `.forge/context`.",
                "Do not treat `.forge/generated/` or `.forge/context-archive/` as active source of truth.",
                "recommend `forge-update-context` when safe updates are needed",
            ),
        )
        _assert_contains_all(
            self,
            mode,
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
        self.assertNotIn("00-meta/context-manifest.md", mode)
        self.assertNotIn("knowledge/decisions/", mode)
        self.assertNotIn("source_commit", mode)
        self.assertNotIn("last_verified", mode)

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

    def test_detect_tools_recognizes_copilot_skills_signal(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / ".github" / "skills").mkdir(parents=True)
            self.assertEqual(_detect_tools(target), ("copilot",))

    def test_default_init_installs_agents_and_copilot_without_claude(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Repo\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                status = run_init(
                    target=target,
                    profile="service",
                    selected_tools=parse_tools_args(None),
                    dry_run=False,
                    assume_yes=True,
                )

            self.assertEqual(status, 0)
            self.assertTrue((target / "AGENTS.md").exists())
            self.assertTrue((target / ".github/copilot-instructions.md").exists())
            self.assertTrue((target / ".github/skills/forge-update-context/SKILL.md").exists())
            self.assertTrue((target / ".github/skills/forge-verify-context/SKILL.md").exists())
            self.assertTrue((target / ".forge/skills/forge-update-context/SKILL.md").exists())
            self.assertTrue((target / ".forge/skills/forge-verify-context/SKILL.md").exists())
            self.assertFalse((target / ".github/prompts").exists())
            self.assertTrue((target / ".forge/generated/README.md").exists())
            self.assertTrue((target / ".forge/context-patches/README.md").exists())
            self.assertTrue((target / ".forge/context-archive/README.md").exists())
            self.assertFalse((target / "CLAUDE.md").exists())
            self.assertFalse((target / ".claude").exists())

    def test_default_workspace_init_uses_same_shared_tool_policy(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Workspace\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                status = run_init(
                    target=target,
                    profile="workspace",
                    selected_tools=parse_tools_args(None),
                    dry_run=False,
                    assume_yes=True,
                )

            self.assertEqual(status, 0)
            self.assertTrue((target / "AGENTS.md").exists())
            self.assertTrue((target / ".github/copilot-instructions.md").exists())
            self.assertTrue((target / ".github/skills/forge-update-context/SKILL.md").exists())
            self.assertFalse((target / "CLAUDE.md").exists())
            self.assertFalse((target / ".claude").exists())

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
