from __future__ import annotations

import unittest

from forge_context_engine.install_manifest import build_managed_paths, parse_tools_args
from forge_context_engine.runtime_ops import _is_managed_file


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


if __name__ == "__main__":
    unittest.main()
