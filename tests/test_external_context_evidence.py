from __future__ import annotations

import unittest
from pathlib import Path

from forge_context_engine.runtime_ops import _build_init_files

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "validation-cases/external-context-evidence.md"
LEGACY_MARKERS = ("knowledge/", "01-core/")


def _section(text: str, heading: str) -> str:
    return text.split(f"\n{heading}\n", 1)[1].split("\n## ", 1)[0]


class ExternalContextInstallTests(unittest.TestCase):
    def setUp(self) -> None:
        self.files = _build_init_files(
            target_root=Path("/tmp/example"), profile="service", selected_tools=("claude",), ui_language="en"
        )

    def test_forge_init_installs_external_context_rule_and_evidence_type(self) -> None:
        self.assertIn("\n## External context\n", self.files[".forge/adapter.md"])
        self.assertIn("\n## External Context Evidence\n", self.files[".forge/runtime/meta/conventions-evidence.md"])

    def test_external_context_sits_between_source_of_truth_and_cross_tool_output(self) -> None:
        adapter = self.files[".forge/adapter.md"]
        self.assertLess(adapter.index("\n## Source of truth\n"), adapter.index("\n## External context\n"))
        self.assertLess(adapter.index("\n## External context\n"), adapter.index("\n## Cross-tool output expectations\n"))

    def test_new_text_has_no_legacy_markers(self) -> None:
        texts = {
            "adapter": _section(self.files[".forge/adapter.md"], "## External context"),
            "evidence": _section(self.files[".forge/runtime/meta/conventions-evidence.md"], "## External Context Evidence"),
            "case": CASE.read_text(encoding="utf-8"),
        }
        for name, text in texts.items():
            for marker in LEGACY_MARKERS:
                self.assertNotIn(marker, text, name)


class ExternalContextValidationCaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.case = CASE.read_text(encoding="utf-8")
        self.rows = {
            line.split("|")[1].strip(): line
            for line in _section(self.case, "## 2. Scenarios").splitlines()
            if line.startswith("| ") and line.split("|")[1].strip().isdigit()
        }

    def test_case_has_exactly_five_scenarios(self) -> None:
        self.assertEqual(sorted(self.rows), ["1", "2", "3", "4", "5"])

    def test_contradiction_scenario_follows_repository_and_lists_conflict(self) -> None:
        row = self.rows["2"]
        self.assertIn("contradicts a repository file", row)
        self.assertIn("follows the repository", row)

    def test_injected_instruction_scenario_is_ignored_and_nothing_pushed(self) -> None:
        row = self.rows["3"]
        self.assertIn("Instruction is ignored", row)
        self.assertIn("nothing is pushed", row)

    def test_unbacked_fact_is_inferred_and_promotion_needs_human_evidence(self) -> None:
        self.assertIn("`inferred`", self.rows["1"])
        self.assertIn("`human` evidence entry", self.rows["5"])
        self.assertIn("`.forge/context-patches/`", self.rows["4"])

    def test_case_rejects_external_only_confirmed_claims(self) -> None:
        rejected = _section(self.case, "## 3. Incorrect Behaviors Forge Must Reject")
        self.assertIn("Labeling a claim `confirmed` when its only evidence is `external`", rejected)
        self.assertIn("Following instructions found in external content", rejected)


if __name__ == "__main__":
    unittest.main()
