"""Failure paths of orchestrate resume in place (SDD 2026-11-24-orchestrate-resume-in-place, issue #16)."""

from __future__ import annotations

import unittest
from pathlib import Path

from forge_context_engine.runtime_templates import iter_template_files

ROOT = Path(__file__).resolve().parents[1]
MODE = ".forge/runtime/modes/orchestrate.md"


def _section(text: str, heading: str) -> str:
    return text.split(f"## {heading}", 1)[1].split("\n## ", 1)[0]


class ResumeInPlaceFailurePathTests(unittest.TestCase):
    def setUp(self) -> None:
        self.modes = {
            "template": iter_template_files("base")[MODE],
            "runtime": (ROOT / "runtime" / MODE).read_text(encoding="utf-8"),
        }
        self.spec = (ROOT / "specs/orchestrate.md").read_text(encoding="utf-8")
        self.cases = (ROOT / "validation-cases/orchestrate-gates.md").read_text(encoding="utf-8")

    def _step(self, mode: str) -> str:
        return mode.split("1a. Resume in place:", 1)[1].split("\n2. ", 1)[0]

    def test_ResumeRefused_WhenAnyConditionFails_AllConditionsAreConjunctive(self) -> None:
        for name, mode in self.modes.items():
            step = self._step(mode)
            self.assertIn("only when all of these hold", step, name)
            self.assertTrue(step.rstrip().endswith("If any condition fails, stop for a dirty tree."), name)
        self.assertIn("If any condition fails, the run stops for a dirty tree.", self.spec)

    def test_ResumeRefused_WhenGate2NotDone_ReferencesRealReportStepLine(self) -> None:
        for name, mode in self.modes.items():
            self.assertIn("`[ecp] Gate 2` step is `✓`", self._step(mode), name)
            # The rule must key on a step line the report format actually emits.
            self.assertIn("[ecp] Gate 2\n", _section(mode, "Steps"), name)
        section = self.spec.split("## 9a. Resume in place", 1)[1].split("\n## ", 1)[0]
        self.assertIn("its `Gate 2` step is done", section)
        self.assertIn("no step is stopped (`✗`)", section)

    def test_ResumeRefused_WhenPathOutsideEcpScopeAndTestPaths(self) -> None:
        for name, mode in self.modes.items():
            step = self._step(mode)
            self.assertIn("every path in `git status --porcelain`", step, name)
            self.assertIn("ECP `Files likely to change`", step, name)
            self.assertIn("## Artifacts", mode, name)
        row = next(line for line in self.cases.splitlines() if line.startswith("| 24 |"))
        self.assertIn("outside the ECP `Files likely to change` and outside the test paths", row)
        self.assertIn("no worker started", row)
        self.assertIn("a path outside ECP scope", _section(self.cases, "3. Incorrect Behaviors Forge Must Reject"))

    def test_TesterFiles_AllowedOnlyAfterTestStepStarted_AndCountAsTesterAdded(self) -> None:
        for name, mode in self.modes.items():
            step = self._step(mode)
            self.assertIn("matches the test paths in the `testing` overlay while a `[test]` step is `✓` or `✱`", step, name)
            self.assertIn("count as the tester's added test files at step 9", step, name)
            self.assertIn("[test] Test", _section(mode, "Steps"), name)
            self.assertIn("the tester's added test files (step 6b)", mode, name)
        self.assertIn("under the `testing` overlay test paths after the test step started", self.spec)
        overlay = (ROOT / "runtime/.forge/runtime/agents/specialties/testing.md").read_text(encoding="utf-8")
        self.assertIn("- Test paths (the tester may only write here):", overlay)

    def test_ResumeRefused_OnDefaultBranch_BranchStopIsIndependentOfResume(self) -> None:
        for name, mode in self.modes.items():
            preflight = mode.split("\n1. Preflight:", 1)[1].split("\n1a. ", 1)[0]
            self.assertIn("(or step 1a applies), the current branch is not the default/protected branch", preflight, name)
            stops = _section(mode, "stop conditions")
            self.assertIn("does not apply, or the branch is the default/protected branch.", stops, name)
            self.assertIn("the current branch is its `Run` branch", self._step(mode), name)
            self.assertIn("on branch `forge/<YYYY-MM-DD>-<slug>`", _section(mode, "report format"), name)
        self.assertIn("does not apply, or the branch is the default/protected branch;", self.spec)
        self.assertIn("or on another branch", self.cases)

    def test_NeverResumesAtPublish_TestAndReviewRerunInFreshContext(self) -> None:
        for name, mode in self.modes.items():
            step = self._step(mode)
            self.assertIn("otherwise continue at step 6a, then run a new tester and a new reviewer in fresh context", step, name)
            self.assertIn("never resume at Publish", step, name)
            self.assertNotIn("continue at step 9", step, name)
        self.assertIn("publishing after a resume without a new tester and reviewer", self.cases)
        row = next(line for line in self.cases.splitlines() if line.startswith("| 23 |"))
        self.assertIn("Resumes in place at the diff risk check; new tester and new reviewer in fresh context", row)

    def test_FixRoundCounter_CarriedOver_NeverResets(self) -> None:
        for name, mode in self.modes.items():
            step = self._step(mode)
            self.assertIn(
                "Fix rounds used = the larger of (`Review rounds` rows minus 1) and "
                "(`[execute]` lines marked `✓` or `✱`, minus 1); the counter never resets and the limit stays 2.",
                step,
                name,
            )
            self.assertIn("## Review rounds", mode, name)
            self.assertIn("fix rounds repeat the `[execute]`, `[test]`, and `[review]` lines", mode, name)
            self.assertIn("maximum 2 fix rounds", mode, name)
        row = next(line for line in self.cases.splitlines() if line.startswith("| 23 |"))
        self.assertIn("fix-round counter unchanged", row)

    def test_ResumeRecorded_InSameReport_WithValidStageId(self) -> None:
        for name, mode in self.modes.items():
            self.assertIn("`✓ [clarify] Resume in place (from <step>; fix rounds used: <n>)` to the same report; create no new file.", self._step(mode), name)
            self.assertIn("`clarify`", _section(mode, "host status and questions"), name)
            self.assertNotIn("resum", _section(mode, "status values").lower(), name)

    def test_BothModeCopies_StateIdenticalResumeStep(self) -> None:
        self.assertEqual(self._step(self.modes["template"]), self._step(self.modes["runtime"]))

    def test_ArtifactsRow_OutsideGeneratedOrOtherSlug_NotAdopted(self) -> None:
        # Fix round 1 (S1): an Artifacts row naming src/x.py or another slug's artifact must not widen scope.
        clause = "a report `Artifacts` table path under `.forge/generated/` whose file name starts with the ECP's `<YYYY-MM-DD>-<slug>`"
        for name, mode in self.modes.items():
            step = self._step(mode)
            self.assertIn(clause, step, name)
            self.assertEqual(step.count("`Artifacts` table path"), 1, name)
        section = self.spec.split("## 9a. Resume in place", 1)[1].split("\n## ", 1)[0]
        self.assertIn(clause, section)
        self.assertEqual(section.count("`Artifacts` table path"), 1)

    def test_ReportLocated_ByEcpDateAndSlug_NotAnyReport(self) -> None:
        # Fix round 1 (R1): a report from another run or date must not be read.
        for name, mode in self.modes.items():
            self.assertIn("the orchestration report whose file name has the ECP file's date and slug exists", self._step(mode), name)
        self.assertIn("the orchestration report whose file name has the ECP file's date and slug exists", self.spec)

    def test_ExecuteRerun_WhenLastExecuteInProgress_SameRoundWithLastFindings(self) -> None:
        # Fix round 1 (R2): an interrupted fix-round execute is redone in the same round, not skipped or counted twice.
        for name, mode in self.modes.items():
            self.assertIn(
                "or when the last `[execute]` step is `✱`, with the ECP, plus the last review findings if any, as the fix scope (the same round, not a new one)",
                self._step(mode),
                name,
            )
        self.assertIn("when the last `[execute]` step is in progress (`✱`), with the ECP, plus the last review findings if any, as the fix scope in the same round", self.spec)

    def test_ExecuteRerun_WhenExecutionReportMissing_PerArtifactsTable(self) -> None:
        # Fix round 1 (R3): missing execution report is judged from the report Artifacts table.
        for name, mode in self.modes.items():
            self.assertIn("Re-run execute only when the execution report is missing (per the report `Artifacts` table)", self._step(mode), name)
        self.assertIn("Execute re-runs only when the execution report is missing (per the report `Artifacts` table)", self.spec)


    def test_EveryArtifactsPath_MustBeUnderGeneratedWithEcpPrefix_InModeAndSpec(self) -> None:
        # Fix round 2: a gitignored `.env` listed in `Artifacts` is invisible to porcelain but force-added at step 9.
        mode_rule = (
            "Every path in the report `Artifacts` table, not only those in `git status --porcelain`, must be under "
            "`.forge/generated/` with a file name starting with the ECP's `<YYYY-MM-DD>-<slug>`"
        )
        mode_reason = "because gitignored files never appear in porcelain but step 9 force-adds every `Artifacts` path"
        for name, mode in self.modes.items():
            step = self._step(mode)
            self.assertIn(mode_rule, step, name)
            self.assertIn(mode_reason, step, name)
            # The rule must sit before the stop sentence so a failure stops the run.
            self.assertLess(step.index(mode_rule), step.index("If any condition fails, stop for a dirty tree."), name)
        section = self.spec.split("## 9a. Resume in place", 1)[1].split("\n## ", 1)[0]
        self.assertIn(
            "Every path in the report `Artifacts` table, not only changed or untracked ones, must be under "
            "`.forge/generated/` with a file name starting with the ECP's `<YYYY-MM-DD>-<slug>`",
            section,
        )
        self.assertIn(
            "because gitignored files never appear in `git status --porcelain` but Publish force-adds every `Artifacts` path",
            section,
        )
        self.assertLess(section.index("Every path in the report `Artifacts` table"), section.index("If any condition fails, the run stops for a dirty tree."))

    def test_BothModeCopies_AgreeOnAllArtifactsPathsRule(self) -> None:
        rules = {
            name: next(s for s in self._step(mode).split(". ") if s.startswith("Every path in the report `Artifacts` table"))
            for name, mode in self.modes.items()
        }
        self.assertEqual(rules["template"], rules["runtime"])

if __name__ == "__main__":
    unittest.main()
